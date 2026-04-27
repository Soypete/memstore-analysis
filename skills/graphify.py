#!/usr/bin/env python3
"""Graphify skill handler for OpenCode."""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from experiments.systems.graphify.adapter import GraphifyAdapter


def main():
    parser = argparse.ArgumentParser(description="Graphify query")
    parser.add_argument("query", nargs="?", default="", help="Search query")
    parser.add_argument("--top-k", type=int, default=10, help="Number of results")
    parser.add_argument("--stats", action="store_true", help="Show stats")
    args = parser.parse_args()

    adapter = GraphifyAdapter(Path.home() / "code")

    if args.stats:
        print("Graphify: (loads full graph - use manual inspection)")
        print("Graph location: ~/code/graphify-out/graph.json")
        return

    if not args.query:
        print("Usage: /graphify <query> [--top-k N]")
        return

    results = adapter.search_memory(args.query, top_k=args.top_k)
    
    print(f"=== Graphify results for '{args.query}' ({len(results)} found) ===\n")
    for r in results:
        print(f"  {r.id}")
        print(f"    {r.content[:100]}")
        print(f"    source: {r.source}")
        print()


if __name__ == "__main__":
    main()