#!/usr/bin/env python3
"""Query all three memory systems for benchmarking."""

import sys
import argparse
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# Lazy imports to avoid slow Graphify init
GraphifyAdapter = None
LLMWikiAdapter = None
MemPalaceAdapter = None

def _lazy_imports():
    global GraphifyAdapter, LLMWikiAdapter, MemPalaceAdapter
    if GraphifyAdapter is None:
        from experiments.systems.graphify.adapter import GraphifyAdapter
        from experiments.systems.llmwiki.adapter import LLMWikiAdapter
        from experiments.systems.mempalace.adapter import MemPalaceAdapter


def benchmark_query(adapter_name: str, adapter, query: str, runs: int = 5):
    """Run a query benchmark."""
    print(f"\n=== {adapter_name} ===")
    times = []
    
    for i in range(runs):
        start = time.perf_counter()
        results = adapter.search_memory(query) if hasattr(adapter, 'search_memory') else adapter.search(query)
        elapsed = time.perf_counter() - start
        times.append(elapsed)
        print(f"  Run {i+1}: {elapsed:.3f}s - {len(results)} results")
    
    avg = sum(times) / len(times)
    print(f"  Average: {avg:.3f}s")
    return avg, times


def main():
    global GraphifyAdapter, LLMWikiAdapter, MemPalaceAdapter
    _lazy_imports()
    
    parser = argparse.ArgumentParser(description="Query memory systems")
    parser.add_argument("query", nargs="?", default="executor", help="Query string")
    parser.add_argument("--runs", type=int, default=5, help="Number of benchmark runs")
    parser.add_argument("--system", choices=["graphify", "llmwiki", "mempalace", "all"], 
                        default="all", help="Which system to query")
    parser.add_argument("--stats", action="store_true", help="Show system stats")
    args = parser.parse_args()

    adapters = {}
    
    # Only create adapters as needed
    def get_adapter(name, cls, path):
        if name not in adapters:
            try:
                adapters[name] = cls(path)
            except Exception as e:
                print(f"{name} error: {e}")
        return adapters.get(name)

    if args.stats:
        print("\n=== SYSTEM STATS ===")
        # Stats - don't load Graphify (too slow)
        for name, cls, path in [
            ("LLMWiki", LLMWikiAdapter, Path.home() / "code/wiki"),
            ("MemPalace", MemPalaceAdapter, Path.home() / ".mempalace"),
        ]:
            if args.system in ("all", name.lower()):
                try:
                    adapter = get_adapter(name, cls, path)
                    stats = adapter.get_stats()
                    print(f"{name}: {stats}")
                except Exception as e:
                    print(f"{name}: error - {e}")
        print("Graphify: (skip - loads full graph)")
    
    # Exit after stats if that's all we wanted
    if args.stats and not args.query:
        sys.exit(0)

    if args.query:
        print(f"\n=== QUERY: '{args.query}' ===")
        total_time = 0
        
        # Query - populate adapters
        query_systems = []
        if args.system in ("graphify", "all"):
            query_systems.append(("Graphify", GraphifyAdapter, Path.home() / "code"))
        if args.system in ("llmwiki", "all"):
            query_systems.append(("LLMWiki", LLMWikiAdapter, Path.home() / "code/wiki"))
        if args.system in ("mempalace", "all"):
            query_systems.append(("MemPalace", MemPalaceAdapter, Path.home() / ".mempalace"))
        
        for name, cls, path in query_systems:
            adapter = get_adapter(name, cls, path)
            if adapter:
                avg, _ = benchmark_query(name, adapter, args.query, args.runs)
                total_time += avg
        
        print(f"\n=== TOTAL AVG: {total_time:.3f}s ===")


if __name__ == "__main__":
    main()