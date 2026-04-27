#!/usr/bin/env python3
"""MemPalace skill handler for OpenCode."""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from experiments.systems.mempalace.adapter import MemPalaceAdapter


def main():
    parser = argparse.ArgumentParser(description="MemPalace query")
    parser.add_argument("query", nargs="?", default="", help="Search query")
    parser.add_argument("--top-k", type=int, default=10, help="Number of results")
    parser.add_argument("--stats", action="store_true", help="Show stats")
    args = parser.parse_args()

    adapter = MemPalaceAdapter(Path.home() / ".mempalace")

    if args.stats:
        stats = adapter.get_stats()
        print(f"MemPalace stats:")
        print(f"  Total items: {stats.total_items}")
        print(f"  Wings: {stats.wings}")
        print(f"  Rooms: {stats.rooms}")
        print(f"  Size: {stats.storage_size_bytes / 1024 / 1024:.1f} MB")
        return

    if not args.query:
        print("Usage: /mempalace <query> [--top-k N]")
        return

    results = adapter.search_memory(args.query, top_k=args.top_k)
    
    print(f"=== MemPalace results for '{args.query}' ({len(results)} found) ===\n")
    for r in results:
        print(f"  {r.id}")
        print(f"    {r.content}")
        print(f"    score: {r.score}")
        print()


if __name__ == "__main__":
    main()