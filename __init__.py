"""
experiments - Lab notebook for testing: Do Semantic Models Turn File-Based Systems into Knowledge Graphs?
"""

__version__ = "0.1.0"

from .runner import ExperimentRunner, Task, TASK_SUITE, TaskType
from .interfaces import (
    MemorySystem,
    MemoryResult,
    MemoryItem,
    Link,
    PathExplanation,
    SystemStats,
    RelationType,
    Scope,
    ResultQuality,
    ExperimentResult,
)

__all__ = [
    "ExperimentRunner",
    "Task",
    "TASK_SUITE",
    "TaskType",
    "MemorySystem",
    "MemoryResult",
    "MemoryItem",
    "Link",
    "PathExplanation",
    "SystemStats",
    "RelationType",
    "Scope",
    "ResultQuality",
    "ExperimentResult",
]
