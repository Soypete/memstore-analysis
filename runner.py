"""
Experiment Runner - Execute tasks across all memory systems.

This module provides a unified interface to run the same task
across LLMWiki, Graphify, and MemPalace for fair comparison.
"""

import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

from .interfaces import (
    MemorySystem,
    MemoryResult,
    ExperimentResult,
    ResultQuality,
    Scope,
)
from .systems import LLMWikiAdapter, GraphifyAdapter, MemPalaceAdapter


# Task definitions
class TaskType:
    """Standard experiment tasks."""

    REPO_NAVIGATION = "repo_navigation"
    ARCHITECTURE_UNDERSTANDING = "architecture_understanding"
    PATTERN_RETRIEVAL = "pattern_retrieval"
    CROSS_ARTIFACT_REASONING = "cross_artifact_reasoning"
    INGEST_NEW = "ingest_new"
    UPDATE_CONCEPT = "update_concept"


@dataclass
class Task:
    """A single experiment task."""

    id: str
    type: str
    query: str
    scope: str = Scope.ALL
    expected_answer: Optional[str] = None

    # For write tasks
    input_content: Optional[str] = None
    metadata: Optional[dict] = field(default_factory=dict)


# Standard task suite
TASK_SUITE = [
    # Repo Navigation
    Task(
        id="rn-001",
        type=TaskType.REPO_NAVIGATION,
        query="Find how I implemented authentication in another repo",
    ),
    Task(
        id="rn-002",
        type=TaskType.REPO_NAVIGATION,
        query="Where is the auth handler located?",
    ),
    # Architecture Understanding
    Task(
        id="au-001",
        type=TaskType.ARCHITECTURE_UNDERSTANDING,
        query="What depends on this module?",
    ),
    Task(
        id="au-002",
        type=TaskType.ARCHITECTURE_UNDERSTANDING,
        query="Why does this exist?",
    ),
    # Pattern Retrieval
    Task(
        id="pr-001",
        type=TaskType.PATTERN_RETRIEVAL,
        query="Show my preferred Go project layout",
    ),
    Task(
        id="pr-002",
        type=TaskType.PATTERN_RETRIEVAL,
        query="Find prior CLI patterns I've used",
    ),
    # Cross-Artifact Reasoning
    Task(
        id="ca-001",
        type=TaskType.CROSS_ARTIFACT_REASONING,
        query="Compare design doc vs implementation",
    ),
    Task(
        id="ca-002",
        type=TaskType.CROSS_ARTIFACT_REASONING,
        query="Find contradictions between documents",
    ),
    # Write Tasks
    Task(
        id="wn-001",
        type=TaskType.INGEST_NEW,
        query="Ingest new repo",
        input_content="<repo_path>",
    ),
    Task(
        id="uc-001",
        type=TaskType.UPDATE_CONCEPT,
        query="Update concept",
        input_content="<content>",
    ),
]


class ExperimentRunner:
    """Run experiments across all systems."""

    def __init__(
        self,
        llmwiki_path: Optional[Path] = None,
        graphify_path: Optional[Path] = None,
        mempalace_path: Optional[Path] = None,
    ):
        """Initialize runner with system paths."""
        self.systems: dict[str, MemorySystem] = {}

        if llmwiki_path:
            self.systems["LLMWiki"] = LLMWikiAdapter(llmwiki_path)

        if graphify_path:
            self.systems["Graphify"] = GraphifyAdapter(graphify_path)

        if mempalace_path:
            self.systems["MemPalace"] = MemPalaceAdapter(mempalace_path)

    def run_task(
        self,
        system_name: str,
        task: Task,
        phase: str = "baseline",
    ) -> ExperimentResult:
        """Run a single task on a specific system."""
        system = self.systems.get(system_name)
        if not system:
            raise ValueError(f"Unknown system: {system_name}")

        start_time = time.time()
        turns = 0
        search_ops = 0

        # Execute based on task type
        if task.type in [
            TaskType.REPO_NAVIGATION,
            TaskType.ARCHITECTURE_UNDERSTANDING,
            TaskType.PATTERN_RETRIEVAL,
            TaskType.CROSS_ARTIFACT_REASONING,
        ]:
            # Read-only tasks
            results = system.search_memory(task.query, task.scope)
            search_ops = 1
            turns = 1

        elif task.type in [TaskType.INGEST_NEW, TaskType.UPDATE_CONCEPT]:
            # Write tasks
            if task.input_content:
                system.write_memory(task.input_content, task.metadata or {})
            search_ops = 1
            turns = 1

        else:
            raise ValueError(f"Unknown task type: {task.type}")

        latency = time.time() - start_time

        # Determine result quality (would need human evaluation in practice)
        # For now, mark as partial if we got results
        quality = ResultQuality.PARTIAL if results else ResultQuality.INCORRECT

        return ExperimentResult(
            date=datetime.now(),
            system=system_name,
            phase=phase,
            task=task.id,
            steps_taken=[f"search_memory({task.query})"],
            observations=f"Got {len(results)} results",
            turns=turns,
            search_ops=search_ops,
            latency_seconds=latency,
            notes="",
            result_quality=quality,
            surprises_failures="",
            hypothesis_update="",
        )

    def run_suite(
        self,
        systems: list[str],
        phase: str = "baseline",
        tasks: list[Task] = None,
    ) -> list[ExperimentResult]:
        """Run full task suite across specified systems."""
        tasks = tasks or TASK_SUITE
        results = []

        for task in tasks:
            for system_name in systems:
                if system_name not in self.systems:
                    print(f"Skipping {system_name} - not configured")
                    continue

                print(f"Running {task.id} on {system_name}...")
                result = self.run_task(system_name, task, phase)
                results.append(result)

        return results

    def export_results(self, results: list[ExperimentResult], output_path: Path):
        """Export results to CSV."""
        import csv

        with open(output_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "date",
                    "system",
                    "phase",
                    "task",
                    "turns",
                    "search_ops",
                    "latency_ms",
                    "result_quality",
                ]
            )

            for r in results:
                writer.writerow(
                    [
                        r.date.isoformat(),
                        r.system,
                        r.phase,
                        r.task,
                        r.turns,
                        r.search_ops,
                        int(r.latency_seconds * 1000),
                        r.result_quality.value,
                    ]
                )

        print(f"Exported {len(results)} results to {output_path}")


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Run experiments")
    parser.add_argument("--system", choices=["LLMWiki", "Graphify", "MemPalace", "all"])
    parser.add_argument("--phase", default="baseline")
    parser.add_argument("--output", type=Path, default=Path("results.csv"))

    args = parser.parse_args()

    # Initialize runner
    runner = ExperimentRunner()

    # Determine systems to run
    systems = [args.system] if args.system != "all" else list(runner.systems.keys())

    # Run tasks
    results = runner.run_suite(systems, args.phase)

    # Export
    runner.export_results(results, args.output)


if __name__ == "__main__":
    main()
