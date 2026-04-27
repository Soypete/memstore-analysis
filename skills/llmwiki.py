#!/usr/bin/env python3
"""LLMWiki skill handler for OpenCode."""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from experiments.systems.llmwiki.adapter import LLMWikiAdapter


def main():
    parser = argparse.ArgumentParser(description="LLMWiki query")
    parser.add_argument("query", nargs="?", default="", help="Search query")
    parser.add_argument("--top-k", type=int, default=10, help="Number of results")
    parser.add_argument("--stats", action="store_true", help="Show stats")
    args = parser.parse_args()

    adapter = LLMWikiAdapter(Path.home() / "code/wiki")

    if args.stats:
        stats = adapter.get_stats()
        print(f"LLMWiki stats:")
        print(f"  Total items: {stats.total_items}")
        print(f"  Drawers: {stats.drawers}")
        print(f"  Size: {stats.storage_size_bytes / 1024 / 1024:.1f} MB")
        return

    if not args.query:
        print("Usage: /llmwiki <query> [--top-k N]")
        return

    results = adapter.search_memory(args.query, top_k=args.top_k)
    
    print(f"=== LLMWiki results for '{args.query}' ({len(results)} found) ===\n")
    for r in results:
        print(f"  {r.id}")
        print(f"    {r.content[:150]}...")
        print()


if __name__ == "__main__":
    main()