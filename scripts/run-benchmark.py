#!/usr/bin/env python3
"""
Benchmark Runner for Knowledge Graph Experiment

Runs the task suite against all three systems (LLMWiki, Graphify, MemPalace)
and collects metrics for white paper analysis.

Usage:
    python run-benchmark.py --system <llmwiki|graphify|mempalace|all> --phase <baseline|semantic|all>
    python run-benchmark.py --all  # Run everything
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

RESULTS_DIR = Path(__file__).parent.parent / "results"
LOGS_DIR = Path(__file__).parent.parent / "logs"


@dataclass
class TaskResult:
    task_id: str
    system: str
    phase: str
    timestamp: str
    
    turns: int
    search_ops: int
    latency_ms: float
    tokens: int
    
    traversal_quality: str  # excellent/good/partial/poor
    explainability: str     # full/partial/none
    result_quality: str     # correct/partial/incorrect
    
    error: Optional[str] = None
    notes: Optional[str] = None


# Add parent to path for imports
import os
script_dir = os.path.dirname(os.path.abspath(__file__))  # scripts/
experiments_dir = os.path.dirname(script_dir)  # experiments/
opensrc_dir = os.path.dirname(experiments_dir)  # opencode/
sys.path.insert(0, opensrc_dir)

# Adapter imports - use full module path
try:
    from experiments.systems.llmwiki.adapter import LLMWikiAdapter
    from experiments.systems.graphify.adapter import GraphifyAdapter
    from experiments.systems.mempalace.adapter import MemPalaceAdapter
    ADAPTERS_AVAILABLE = True
except ImportError as e:
    ADAPTERS_AVAILABLE = False
    print(f"Warning: Adapters not available: {e}")

# Default paths (configurable via args)
DEFAULT_WIKI_PATH = Path.home() / "wiki"
DEFAULT_GRAPH_PATH = Path.home() / "graphify-out" / "graph.json"
DEFAULT_PALACE_PATH = Path.home() / ".mempalace"


def get_adapter(system: str, config: dict):
    """Get adapter instance for system."""
    if system == "llmwiki":
        return LLMWikiAdapter(
            wiki_path=config.get("wiki_path", DEFAULT_WIKI_PATH),
            schema_path=config.get("schema_path"),
            raw_sources_path=config.get("raw_sources_path"),
        )
    elif system == "graphify":
        return GraphifyAdapter(
            graph_path=config.get("graph_path", DEFAULT_GRAPH_PATH),
            corpus_path=config.get("corpus_path"),
        )
    elif system == "mempalace":
        return MemPalaceAdapter(
            palace_path=config.get("palace_path", DEFAULT_PALACE_PATH),
        )
    return None


# Task definitions from EXPERIMENT_PLAN.md Section 7
TASKS = {
    "repo_navigation": [
        {"id": "rn1", "query": "Find how I implemented authentication in another repo"},
        {"id": "rn2", "query": "Where is user authorization handled?"},
    ],
    "architecture_understanding": [
        {"id": "au1", "query": "What depends on this module?"},
        {"id": "au2", "query": "Why does this component exist?"},
    ],
    "pattern_retrieval": [
        {"id": "pr1", "query": "Show my preferred Go project layout"},
        {"id": "pr2", "query": "Find prior CLI patterns I've used"},
    ],
    "cross_artifact_reasoning": [
        {"id": "ca1", "query": "Compare design doc vs implementation"},
        {"id": "ca2", "query": "Find contradictions in my notes"},
    ],
    "write_operations": [
        {"id": "wo1", "query": "Ingest new repo: https://github.com/soypete/dotfiles"},
        {"id": "wo2", "query": "Update concept: semantic routing"},
    ],
}


def get_all_tasks():
    """Flatten all tasks into a single list."""
    all_tasks = []
    for category, tasks in TASKS.items():
        for task in tasks:
            all_tasks.append({**task, "category": category})
    return all_tasks


def run_task(system: str, task: dict, phase: str, adapter_config: dict = None) -> TaskResult:
    """Execute a single task against a system and collect metrics."""
    
    start_time = time.time()
    turns = 0
    search_ops = 0
    tokens = 0
    
    adapter = get_adapter(system, adapter_config or {})
    
    # Execute task based on category
    query = task["query"]
    category = task.get("category", "unknown")
    
    # Read operations
    if category in ["repo_navigation", "architecture_understanding", "pattern_retrieval", "cross_artifact_reasoning"]:
        if adapter:
            try:
                results = adapter.search_memory(query, top_k=5)
                search_ops = 1
                turns = 1
            except Exception as e:
                return TaskResult(
                    task_id=task["id"],
                    system=system,
                    phase=phase,
                    timestamp=datetime.now().isoformat(),
                    turns=-1, search_ops=-1, latency_ms=-1, tokens=-1,
                    traversal_quality="error", explainability="error", result_quality="error",
                    error=str(e),
                )
    
    # Write operations
    elif category == "write_operations":
        if adapter:
            try:
                adapter.write_memory(query, {"title": task["id"], "category": "benchmark"})
                search_ops = 1
                turns = 1
            except Exception as e:
                return TaskResult(
                    task_id=task["id"],
                    system=system,
                    phase=phase,
                    timestamp=datetime.now().isoformat(),
                    turns=-1, search_ops=-1, latency_ms=-1, tokens=-1,
                    traversal_quality="error", explainability="error", result_quality="error",
                    error=str(e),
                )
    
    latency_ms = (time.time() - start_time) * 1000
    
    return TaskResult(
        task_id=task["id"],
        system=system,
        phase=phase,
        timestamp=datetime.now().isoformat(),
        turns=turns,
        search_ops=search_ops,
        latency_ms=latency_ms,
        tokens=tokens,
        traversal_quality="pending",
        explainability="pending",
        result_quality="pending",
    )


def save_result(result: TaskResult):
    """Save a single task result to JSON."""
    results_dir = RESULTS_DIR / result.system
    results_dir.mkdir(exist_ok=True)
    
    phase_dir = results_dir / result.phase
    phase_dir.mkdir(exist_ok=True)
    
    filepath = phase_dir / f"{result.task_id}.json"
    with open(filepath, "w") as f:
        json.dump(asdict(result), f, indent=2)
    
    print(f"  → Saved: {filepath}")


def run_benchmark(system: str, phase: str, tasks: list | None = None, adapter_config: dict | None = None):
    """Run benchmark for a specific system and phase."""
    
    if tasks is None:
        tasks = get_all_tasks()
    
    print(f"\n{'='*60}")
    print(f"Benchmark: {system} | Phase: {phase}")
    print(f"{'='*60}")
    
    results = []
    for task in tasks:
        print(f"\nTask {task['id']}: {task['query'][:50]}...")
        
        try:
            result = run_task(system, task, phase)
            save_result(result)
            results.append(result)
        except Exception as e:
            print(f"  ERROR: {e}")
            result = TaskResult(
                task_id=task["id"],
                system=system,
                phase=phase,
                timestamp=datetime.now().isoformat(),
                turns=-1,
                search_ops=-1,
                latency_ms=-1,
                tokens=-1,
                traversal_quality="error",
                explainability="error",
                result_quality="error",
                error=str(e),
            )
            save_result(result)
            results.append(result)
    
    return results


def generate_summary(results: list) -> dict:
    """Generate summary statistics from results."""
    
    valid_results = [r for r in results if r.turns >= 0]
    
    if not valid_results:
        return {"error": "No valid results"}
    
    return {
        "total_tasks": len(results),
        "successful": len(valid_results),
        "failed": len(results) - len(valid_results),
        "avg_turns": sum(r.turns for r in valid_results) / len(valid_results),
        "avg_search_ops": sum(r.search_ops for r in valid_results) / len(valid_results),
        "avg_latency_ms": sum(r.latency_ms for r in valid_results) / len(valid_results),
        "total_tokens": sum(r.tokens for r in valid_results),
        "quality_breakdown": {
            "traversal": {},
            "explainability": {},
            "result": {},
        }
    }


def main():
    parser = argparse.ArgumentParser(description="Run knowledge graph benchmarks")
    parser.add_argument("--system", choices=["llmwiki", "graphify", "mempalace", "all"], 
                        default="all", help="System to benchmark")
    parser.add_argument("--phase", choices=["baseline", "semantic", "all"],
                        default="all", help="Experiment phase")
    parser.add_argument("--tasks", nargs="*", help="Specific task IDs to run")
    parser.add_argument("--output", help="Output JSON file for results")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    # System path configs
    parser.add_argument("--wiki-path", type=Path, default=DEFAULT_WIKI_PATH,
                        help="Path to LLMWiki directory")
    parser.add_argument("--graph-path", type=Path, default=DEFAULT_GRAPH_PATH,
                        help="Path to Graphify graph.json")
    parser.add_argument("--palace-path", type=Path, default=DEFAULT_PALACE_PATH,
                        help="Path to MemPalace directory")
    
    args = parser.parse_args()
    
    # Determine what to run
    systems = ["llmwiki", "graphify", "mempalace"] if args.system == "all" else [args.system]
    phases = ["baseline", "semantic"] if args.phase == "all" else [args.phase]
    
    # Build adapter config
    adapter_config = {
        "llmwiki": {"wiki_path": args.wiki_path},
        "graphify": {"graph_path": args.graph_path},
        "mempalace": {"palace_path": args.palace_path},
    }
    
    # Filter tasks if specified
    all_tasks = get_all_tasks()
    if args.tasks:
        all_tasks = [t for t in all_tasks if t["id"] in args.tasks]
    
    print(f"\nStarting benchmark run: {datetime.now().isoformat()}")
    print(f"Systems: {systems}")
    print(f"Phases: {phases}")
    print(f"Tasks: {len(all_tasks)}")
    
    all_results = []
    for system in systems:
        for phase in phases:
            config = adapter_config.get(system, {})
            results = run_benchmark(system, phase, all_tasks, config)
            all_results.extend(results)
    
    # Generate summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    
    for system in systems:
        sys_results = [r for r in all_results if r.system == system]
        summary = generate_summary(sys_results)
        print(f"\n{system.upper()}:")
        print(f"  Tasks: {summary.get('total_tasks', 0)}")
        if "avg_turns" in summary:
            print(f"  Avg Turns: {summary['avg_turns']:.1f}")
            print(f"  Avg Search Ops: {summary['avg_search_ops']:.1f}")
            print(f"  Avg Latency: {summary['avg_latency_ms']:.0f}ms")
    
    # Save combined results
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert to dicts for JSON serialization
        output_data = {
            "timestamp": datetime.now().isoformat(),
            "config": {"systems": systems, "phases": phases, "task_count": len(all_tasks)},
            "results": [asdict(r) for r in all_results],
        }
        
        with open(output_path, "w") as f:
            json.dump(output_data, f, indent=2)
        
        print(f"\nResults saved to: {output_path}")
    
    print(f"\nBenchmark complete: {datetime.now().isoformat()}")


if __name__ == "__main__":
    main()