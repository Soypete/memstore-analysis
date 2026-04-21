#!/usr/bin/env python3
"""
Multi-store fetcher with eval metrics.
Queries all 3 memory systems and measures latency + quality.
"""

import json
import sys
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

sys.path.insert(0, "/Users/soypete/code/opensource/mempalace")

import chromadb
from mempalace.config import MempalaceConfig


# ============ LLMWiki implementation (inline) ============
class LLMWiki:
    """LLMWiki - Markdown-based wiki."""

    def __init__(self, wiki_path: Path):
        self.wiki_path = Path(wiki_path)
        self.raw_path = self.wiki_path / "raw"
        self.wiki_dir = self.wiki_path / "wiki"
        self.index_file = self.wiki_path / "index.md"

    def search(self, query: str, top_k: int = 10) -> list[dict]:
        results = []

        # Search index.md
        if self.index_file.exists():
            content = self.index_file.read_text()
            if query.lower() in content.lower():
                results.append({"file": "index.md", "content": content, "score": 0.3})

        # Grep through wiki files
        if self.wiki_dir.exists():
            try:
                grep_result = subprocess.run(
                    ["grep", "-r", "-l", "-i", query, str(self.wiki_dir)],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                for match in grep_result.stdout.strip().split("\n"):
                    if match and Path(match).exists():
                        content = Path(match).read_text()
                        filename = Path(match).stem.lower()
                        score = 0.9 if filename in query.lower() else 0.6
                        results.append(
                            {"file": Path(match).name, "content": content[:1000], "score": score}
                        )
            except Exception:
                pass

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]


# ============ FetchResult dataclass ============
@dataclass
class FetchResult:
    system: str
    query: str
    results: list
    latency_ms: float
    result_count: int
    top_score: float
    error: Optional[str] = None


def fetch_mempalace(query: str, top_k: int = 5, palace_path: str = None) -> FetchResult:
    start = time.time()
    palace_path = palace_path or MempalaceConfig().palace_path

    try:
        client = chromadb.PersistentClient(path=palace_path)
        col = client.get_collection("mempalace_drawers")

        results = col.query(
            query_texts=[query],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )

        docs = results.get("documents", [[]])[0]
        dists = results.get("distances", [[]])[0]
        metas = results.get("metadatas", [[]])[0]

        latency = (time.time() - start) * 1000
        top_score = round(1 - dists[0], 3) if dists else 0.0

        return FetchResult(
            system="MemPalace",
            query=query,
            results=[{"content": d, "score": round(1 - dist, 3)} for d, dist in zip(docs, dists)],
            latency_ms=latency,
            result_count=len(docs),
            top_score=top_score,
        )
    except Exception as e:
        return FetchResult(
            system="MemPalace",
            query=query,
            results=[],
            latency_ms=(time.time() - start) * 1000,
            result_count=0,
            top_score=0.0,
            error=str(e),
        )


def fetch_llmwiki(query: str, wiki_path: str = None) -> FetchResult:
    start = time.time()
    wiki_path = Path(wiki_path or os.environ.get("LLMWIKI_PATH", str(Path.home() / "wiki")))

    if not wiki_path.exists():
        wiki_path.mkdir(parents=True, exist_ok=True)

    try:
        wiki = LLMWiki(wiki_path)
        results = wiki.search(query, top_k=10)

        latency = (time.time() - start) * 1000
        top_score = results[0]["score"] if results else 0.0

        return FetchResult(
            system="LLMWiki",
            query=query,
            results=results,
            latency_ms=latency,
            result_count=len(results),
            top_score=top_score,
        )
    except Exception as e:
        return FetchResult(
            system="LLMWiki",
            query=query,
            results=[],
            latency_ms=(time.time() - start) * 1000,
            result_count=0,
            top_score=0.0,
            error=str(e),
        )


def fetch_graphify(query: str, graphify_path: str = None) -> FetchResult:
    start = time.time()
    graphify_path = Path(
        graphify_path or os.environ.get("GRAPHIFY_PATH", str(Path.home() / ".graphify"))
    )

    if not graphify_path.exists():
        return FetchResult(
            system="Graphify",
            query=query,
            results=[],
            latency_ms=0,
            result_count=0,
            top_score=0.0,
            error=f"Graphify not found at {graphify_path}",
        )

    latency = (time.time() - start) * 1000

    return FetchResult(
        system="Graphify",
        query=query,
        results=[],
        latency_ms=latency,
        result_count=0,
        top_score=0.0,
        error="Not implemented",
    )


def run_eval(queries: list[str], output_json: bool = False):
    results = {
        "timestamp": datetime.now().isoformat(),
        "queries": [],
        "summary": {"total_queries": len(queries), "systems": {}},
    }

    for query in queries:
        print(f"\n{'=' * 60}")
        print(f"Query: {query}")
        print(f"{'=' * 60}")

        query_results = {}

        for fetcher, name in [
            (fetch_mempalace, "MemPalace"),
            (fetch_llmwiki, "LLMWiki"),
            (fetch_graphify, "Graphify"),
        ]:
            result = fetcher(query)
            query_results[name] = result

            if result.error:
                print(f"  {name}: ERROR - {result.error}")
            else:
                print(
                    f"  {name}: {result.result_count} results in {result.latency_ms:.1f}ms (top: {result.top_score})"
                )

        results["queries"].append(
            {
                "query": query,
                "results": {
                    name: {
                        "latency_ms": r.latency_ms,
                        "count": r.result_count,
                        "top_score": r.top_score,
                    }
                    for name, r in query_results.items()
                },
            }
        )

    # Summary stats
    for name in ["MemPalace", "LLMWiki", "Graphify"]:
        latencies = [
            q["results"][name]["latency_ms"] for q in results["queries"] if name in q["results"]
        ]
        if latencies:
            results["summary"]["systems"][name] = {
                "avg_latency_ms": sum(latencies) / len(latencies),
                "min_latency_ms": min(latencies),
                "max_latency_ms": max(latencies),
            }

    if output_json:
        print("\n" + json.dumps(results, indent=2))
    else:
        print(f"\n{'=' * 60}")
        print("SUMMARY")
        print(f"{'=' * 60}")
        for name, stats in results["summary"]["systems"].items():
            print(f"  {name}: avg {stats['avg_latency_ms']:.1f}ms")

    return results


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Multi-store fetcher with eval")
    parser.add_argument("query", nargs="?", help="Query string")
    parser.add_argument("--queries", "-q", nargs="+", help="Multiple queries")
    parser.add_argument("--json", "-j", action="store_true", help="JSON output")
    parser.add_argument("--mempalace-path", help="MemPalace path")
    parser.add_argument("--wiki-path", help="LLMWiki path")
    parser.add_argument("--graphify-path", help="Graphify path")

    args = parser.parse_args()

    if args.mempalace_path:
        os.environ["MEMPALACE_PATH"] = args.mempalace_path
    if args.wiki_path:
        os.environ["LLMWIKI_PATH"] = args.wiki_path
    if args.graphify_path:
        os.environ["GRAPHIFY_PATH"] = args.graphify_path

    queries = args.queries or ([args.query] if args.query else [])
    if not queries:
        parser.print_help()
        return

    run_eval(queries, args.json)


if __name__ == "__main__":
    main()
