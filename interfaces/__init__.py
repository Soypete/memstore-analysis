"""Interfaces package - shared contracts for experiment adapters."""

from .agent_contract import (
    MemorySystem,
    MemoryResult,
    MemoryItem,
    Link,
    PathExplanation,
    TraversalStep,
    SystemStats,
    RelationType,
    Scope,
    ResultQuality,
    ExperimentResult,
)

__all__ = [
    "MemorySystem",
    "MemoryResult",
    "MemoryItem",
    "Link",
    "PathExplanation",
    "TraversalStep",
    "SystemStats",
    "RelationType",
    "Scope",
    "ResultQuality",
    "ExperimentResult",
]
