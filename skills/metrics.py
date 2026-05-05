#!/usr/bin/env python3
"""Skill metrics tracking - logs to JSONL file."""

import json
import time
from datetime import datetime
from pathlib import Path


METRICS_FILE = Path.home() / ".opencode" / "skill_metrics.jsonl"


def log_skill_call(skill_name: str, query: str, latency_ms: float, results_count: int, error: str = None):
    """Log a skill call to metrics file."""
    METRICS_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    entry = {
        "skill": skill_name,
        "query": query[:200],  # Truncate long queries
        "latency_ms": round(latency_ms, 2),
        "results": results_count,
        "error": error,
        "timestamp": datetime.now().isoformat()
    }
    
    with open(METRICS_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")
    
    return entry


def get_metrics_summary():
    """Get summary of skill usage from metrics file."""
    if not METRICS_FILE.exists():
        return {"total_calls": 0}
    
    import json
    calls = []
    with open(METRICS_FILE) as f:
        for line in f:
            try:
                calls.append(json.loads(line))
            except:
                pass
    
    if not calls:
        return {"total_calls": 0}
    
    # Group by skill
    by_skill = {}
    for c in calls:
        skill = c.get("skill", "unknown")
        if skill not in by_skill:
            by_skill[skill] = {"count": 0, "total_latency": 0, "total_results": 0}
        by_skill[skill]["count"] += 1
        by_skill[skill]["total_latency"] += c.get("latency_ms", 0)
        by_skill[skill]["total_results"] += c.get("results", 0)
    
    # Add averages
    for skill, data in by_skill.items():
        if data["count"] > 0:
            data["avg_latency_ms"] = data["total_latency"] / data["count"]
            data["avg_results"] = data["total_results"] / data["count"]
    
    return {
        "total_calls": len(calls),
        "by_skill": by_skill,
        "first_call": calls[0].get("timestamp") if calls else None,
        "last_call": calls[-1].get("timestamp") if calls else None
    }


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--summary":
        print(json.dumps(get_metrics_summary(), indent=2))
    else:
        print(f"Metrics file: {METRICS_FILE}")
        print(f"Usage: python metrics.py --summary")