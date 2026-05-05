#!/usr/bin/env python3
"""
Analysis script for benchmark results.

Generates statistics and charts for white paper.

Usage:
    python analyze-results.py --input results/combined.json --charts --output docs/figures/
"""

import argparse
import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime

RESULTS_DIR = Path(__file__).parent.parent / "results"
OUTPUT_DIR = Path(__file__).parent.parent / "docs" / "figures"


def load_results(results_file: Path) -> list[dict]:
    """Load results from JSON file."""
    with open(results_file) as f:
        data = json.load(f)
    return data.get("results", [])


def aggregate_by_system_phase(results: list[dict]) -> dict:
    """Aggregate metrics by system and phase."""
    agg = defaultdict(lambda: defaultdict(list))
    
    for r in results:
        if r.get("turns", -1) < 0:
            continue
        agg[r["system"]][r["phase"]].append(r)
    
    return agg


def compute_stats(results_list: list[dict]) -> dict:
    """Compute statistics for a list of results."""
    if not results_list:
        return {"error": "No valid results"}
    
    turns = [r["turns"] for r in results_list if r.get("turns", -1) >= 0]
    search_ops = [r["search_ops"] for r in results_list if r.get("search_ops", -1) >= 0]
    latency = [r["latency_ms"] for r in results_list if r.get("latency_ms", -1) >= 0]
    tokens = [r["tokens"] for r in results_list if r.get("tokens", -1) >= 0]
    
    return {
        "count": len(results_list),
        "turns": {"avg": sum(turns)/len(turns) if turns else 0, "total": sum(turns)},
        "search_ops": {"avg": sum(search_ops)/len(search_ops) if search_ops else 0, "total": sum(search_ops)},
        "latency_ms": {"avg": sum(latency)/len(latency) if latency else 0, "total": sum(latency)},
        "tokens": {"avg": sum(tokens)/len(tokens) if tokens else 0, "total": sum(tokens)},
        "quality": {
            "traversal": defaultdict(int),
            "explainability": defaultdict(int),
            "result": defaultdict(int),
        }
    }


def compute_improvement(baseline: dict, semantic: dict) -> dict:
    """Compute improvement from baseline to semantic."""
    if not baseline or not semantic:
        return {}
    
    def safe_div(a, b):
        return (a - b) / b if b != 0 else 0
    
    return {
        "turns_reduction": safe_div(baseline["turns"]["avg"], semantic["turns"]["avg"]),
        "search_ops_reduction": safe_div(baseline["search_ops"]["avg"], semantic["search_ops"]["avg"]),
        "latency_improvement": safe_div(baseline["latency_ms"]["avg"], semantic["latency_ms"]["avg"]),
    }


def generate_markdown_table(agg: dict) -> str:
    """Generate markdown table of results."""
    lines = ["| System | Phase | Tasks | Avg Turns | Avg Search Ops | Avg Latency (ms) |", 
             "|--------|-------|-------|-----------|----------------|------------------|"]
    
    for system in ["llmwiki", "graphify", "mempalace"]:
        if system not in agg:
            continue
        for phase in ["baseline", "semantic"]:
            if phase not in agg[system]:
                continue
            stats = compute_stats(agg[system][phase])
            if "error" not in stats:
                lines.append(f"| {system} | {phase} | {stats['count']} | "
                           f"{stats['turns']['avg']:.1f} | {stats['search_ops']['avg']:.1f} | "
                           f"{stats['latency_ms']['avg']:.0f} |")
    
    return "\n".join(lines)


def generate_charts(results: list[dict], output_dir: Path):
    """Generate charts using matplotlib."""
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        print("Warning: matplotlib not available, skipping charts")
        return
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    systems = ["llmwiki", "graphify", "mempalace"]
    phases = ["baseline", "semantic"]
    
    # Prepare data
    data = {s: {p: [] for p in phases} for s in systems}
    for r in results:
        if r.get("turns", -1) >= 0:
            data[r["system"]][r["phase"]].append(r["turns"])
    
    # Chart 1: Turns comparison
    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(len(systems))
    width = 0.35
    
    baseline_means = [np.mean(data[s]["baseline"]) if data[s]["baseline"] else 0 for s in systems]
    semantic_means = [np.mean(data[s]["semantic"]) if data[s]["semantic"] else 0 for s in systems]
    
    ax.bar(x - width/2, baseline_means, width, label='Baseline', color='#3498db')
    ax.bar(x + width/2, semantic_means, width, label='Semantic', color='#e74c3c')
    
    ax.set_ylabel('Average Turns')
    ax.set_title('Turns to Answer: Baseline vs Semantic')
    ax.set_xticks(x)
    ax.set_xticklabels([s.capitalize() for s in systems])
    ax.legend()
    
    plt.tight_layout()
    plt.savefig(output_dir / "turns_comparison.png", dpi=150)
    plt.close()
    
    # Chart 2: Latency comparison
    latency_data = {s: {p: [] for p in phases} for s in systems}
    for r in results:
        if r.get("latency_ms", -1) >= 0:
            latency_data[r["system"]][r["phase"]].append(r["latency_ms"])
    
    fig, ax = plt.subplots(figsize=(10, 6))
    baseline_lat = [np.mean(latency_data[s]["baseline"]) if latency_data[s]["baseline"] else 0 for s in systems]
    semantic_lat = [np.mean(latency_data[s]["semantic"]) if latency_data[s]["semantic"] else 0 for s in systems]
    
    ax.bar(x - width/2, baseline_lat, width, label='Baseline', color='#3498db')
    ax.bar(x + width/2, semantic_lat, width, label='Semantic', color='#e74c3c')
    
    ax.set_ylabel('Latency (ms)')
    ax.set_title('Latency: Baseline vs Semantic')
    ax.set_xticks(x)
    ax.set_xticklabels([s.capitalize() for s in systems])
    ax.legend()
    
    plt.tight_layout()
    plt.savefig(output_dir / "latency_comparison.png", dpi=150)
    plt.close()
    
    # Chart 3: Quality heatmap
    quality_data = []
    for s in systems:
        for p in phases:
            phase_results = [r for r in results if r["system"] == s and r["phase"] == p]
            correct = sum(1 for r in phase_results if r.get("result_quality") == "correct")
            partial = sum(1 for r in phase_results if r.get("result_quality") == "partial")
            incorrect = sum(1 for r in phase_results if r.get("result_quality") == "incorrect")
            total = len(phase_results) or 1
            quality_data.append([correct/total*100, partial/total*100, incorrect/total*100])
    
    quality_data = np.array(quality_data).reshape(len(systems), len(phases), 3)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    im = ax.imshow(quality_data[:, :, 0], cmap='RdYlGn', aspect='auto')
    
    ax.set_xticks(np.arange(len(phases)))
    ax.set_yticks(np.arange(len(systems)))
    ax.set_xticklabels(phases)
    ax.set_yticklabels([s.capitalize() for s in systems])
    
    plt.colorbar(im, ax=ax, label='Correct %')
    ax.set_title('Result Quality: Correct Answers %')
    
    plt.tight_layout()
    plt.savefig(output_dir / "quality_heatmap.png", dpi=150)
    plt.close()
    
    print(f"Charts saved to: {output_dir}")


def main():
    parser = argparse.ArgumentParser(description="Analyze benchmark results")
    parser.add_argument("--input", type=Path, help="Input JSON file (from run-benchmark.py)")
    parser.add_argument("--charts", action="store_true", help="Generate charts")
    parser.add_argument("--output", type=Path, default=OUTPUT_DIR, help="Output directory for charts")
    parser.add_argument("--markdown", action="store_true", help="Output markdown table")
    
    args = parser.parse_args()
    
    if args.input:
        results = load_results(args.input)
    else:
        # Try to find latest combined results
        combined_files = sorted(RESULTS_DIR.glob("combined_*.json"), reverse=True)
        if combined_files:
            results = load_results(combined_files[0])
            print(f"Using: {combined_files[0]}")
        else:
            print("No results found. Run benchmarks first: python run-benchmark.py --all")
            return
    
    # Aggregate and compute stats
    agg = aggregate_by_system_phase(results)
    
    print("\n" + "="*60)
    print("RESULTS SUMMARY")
    print("="*60)
    
    for system in ["llmwiki", "graphify", "mempalace"]:
        if system not in agg:
            continue
        print(f"\n{system.upper()}:")
        for phase in ["baseline", "semantic"]:
            if phase not in agg[system]:
                continue
            stats = compute_stats(agg[system][phase])
            if "error" not in stats:
                print(f"  {phase}: {stats['count']} tasks, "
                      f"avg turns: {stats['turns']['avg']:.1f}, "
                      f"avg latency: {stats['latency_ms']['avg']:.0f}ms")
    
    # Generate markdown table
    if args.markdown or True:
        print("\n" + "="*60)
        print("COMPARISON TABLE")
        print("="*60)
        print(generate_markdown_table(agg))
    
    # Generate charts
    if args.charts:
        generate_charts(results, args.output)
    
    print("\nAnalysis complete!")


if __name__ == "__main__":
    main()