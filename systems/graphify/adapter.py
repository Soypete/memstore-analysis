"""
Graphify Adapter - implements MemorySystem protocol.

Graphify extracts knowledge graphs from code/docs:
- AST extraction for code (tree-sitter)
- Semantic extraction via LLM for docs/images
- Confidence tags: EXTRACTED, INFERRED, AMBIGUOUS
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from ...interfaces import (
    MemoryResult,
    MemoryItem,
    Link,
    PathExplanation,
    SystemStats,
    TraversalStep,
)


class GraphifyAdapter:
    """Adapter for Graphify-style systems."""

    def __init__(
        self,
        graph_path: Path,
        corpus_path: Optional[Path] = None,
    ):
        """
        Initialize Graphify adapter.

        Args:
            graph_path: Path to graph.json
            corpus_path: Path to source corpus
        """
        self.graph_path = graph_path
        self.corpus_path = corpus_path
        self._graph_data: Optional[dict] = None

    def _load_graph(self) -> dict:
        """Load graph JSON if not already loaded."""
        if self._graph_data is not None:
            return self._graph_data

        graph_json = self.graph_path
        if self.graph_path.is_dir():
            graph_json = self.graph_path / "graph.json"

        if not graph_json.exists():
            return {"nodes": [], "edges": [], "links": []}

        with open(graph_json) as f:
            self._graph_data = json.load(f)
        return self._graph_data

    def search_memory(
        self,
        query: str,
        scope: str = "all",
        top_k: int = 10,
    ) -> list[MemoryResult]:
        """
        Search graph using graphify query.

        Graphify supports:
        - Natural language queries
        - DFS traversal
        - Token budget limiting
        """
        graph_json = self.graph_path.parent / "graph.json"
        if not graph_json.exists():
            return []

        import json
        import subprocess
        import networkx as nx
        from networkx.readwrite import json_graph

        with open(graph_json) as f:
            data = json.load(f)

        try:
            G = json_graph.node_link_graph(data, edges='links')
        except Exception:
            return []

        query_lower = query.lower()
        terms = [t for t in query_lower.split() if len(t) > 2]

        scored = []
        for nid, ndata in G.nodes(data=True):
            label = ndata.get('label', '').lower()
            score = sum(1 for t in terms if t in label)
            if score > 0 or not terms:
                scored.append((score, nid, ndata))

        scored.sort(key=lambda x: x[0], reverse=True)

        results = []
        for _, nid, ndata in scored[:top_k]:
            results.append(
                MemoryResult(
                    id=nid,
                    content=ndata.get('label', nid),
                    score=float(scored[0][0]) / max(len(terms), 1) if terms else 0.5,
                    source=ndata.get('source_file', 'graph'),
                    created_at=datetime.now(),
                )
            )

        return results

    def read_memory(self, id: str) -> Optional[MemoryItem]:
        """Read a node from the graph by ID."""
        graph = self._load_graph()
        for node in graph.get("nodes", []):
            if node.get("id") == id:
                return MemoryItem(
                    id=id,
                    content=node.get("label", ""),
                    metadata=node,
                    links=[],
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                )
        return None

    def explain_path(self, query_or_id: str) -> PathExplanation:
        """
        Explain graph traversal path.

        Graphify provides path tracing between nodes.
        """
        graph_json = self.graph_path.parent / "graph.json"
        if not graph_json.exists():
            return PathExplanation(
                query=query_or_id,
                steps=[],
                total_hops=0,
                confidence=0.0,
            )

        import json
        import networkx as nx
        from networkx.readwrite import json_graph

        with open(graph_json) as f:
            data = json.load(f)

        try:
            G = json_graph.node_link_graph(data, edges='links')
        except Exception:
            return PathExplanation(
                query=query_or_id,
                steps=[],
                total_hops=0,
                confidence=0.0,
            )

        query_lower = query_or_id.lower()
        terms = [t for t in query_lower.split() if len(t) > 2]

        scored = []
        for nid in G.nodes():
            label = G.nodes[nid].get('label', '').lower()
            score = sum(1 for t in terms if t in label)
            scored.append((score, nid))

        scored.sort(key=lambda x: x[0], reverse=True)

        if not scored or scored[0][0] == 0:
            return PathExplanation(
                query=query_or_id,
                steps=[],
                total_hops=0,
                confidence=0.0,
            )

        start_node = scored[0][1]

        steps = []
        visited = {start_node}
        for neighbor in G.neighbors(start_node):
            edge_data = G.edges[start_node, neighbor]
            steps.append(
                TraversalStep(
                    from_id=start_node,
                    to_id=neighbor,
                    relation=edge_data.get('relation', 'connected'),
                    reason=f"Edge confidence: {edge_data.get('confidence', 'unknown')}",
                )
            )

        return PathExplanation(
            query=query_or_id,
            steps=steps,
            total_hops=len(steps),
            confidence=0.5,
        )

    def write_memory(
        self,
        input: str,
        metadata: dict,
    ) -> str:
        """
        Write new content (re-run graphify on updated corpus).

        Graphify doesn't have traditional "write" - you rebuild the graph.
        For now, we add a node to the existing graph if it exists.
        """
        graph_json = self.graph_path.parent / "graph.json"
        node_id = metadata.get("id", f"manual_{datetime.now().timestamp()}")

        if graph_json.exists():
            import json
            with open(graph_json) as f:
                data = json.load(f)

            new_node = {
                "id": node_id,
                "label": metadata.get("title", input[:50]),
                "file_type": "document",
                "source_file": metadata.get("source_file", "manual"),
            }
            data.setdefault("nodes", []).append(new_node)

            with open(graph_json, 'w') as f:
                json.dump(data, f, indent=2)

            return node_id
        else:
            return node_id

    def link_memory(
        self,
        source_id: str,
        target_id: str,
        relation: str,
    ) -> bool:
        """
        Add edge to graph.

        Graphify edges have types:
        - extracted (from code)
        - inferred (LLM guess, with confidence)
        - ambiguous (flagged for review)
        """
        graph_json = self.graph_path.parent / "graph.json"
        if not graph_json.exists():
            return False

        import json
        with open(graph_json) as f:
            data = json.load(f)

        new_edge = {
            "source": source_id,
            "target": target_id,
            "relation": relation,
            "confidence": "INFERRED",
            "confidence_score": 0.7,
            "weight": 1.0,
        }
        data.setdefault("links", []).append(new_edge)

        with open(graph_json, 'w') as f:
            json.dump(data, f, indent=2)

        self._graph_data = None
        return True

    def get_stats(self) -> SystemStats:
        """Get graph statistics."""
        graph = self._load_graph()

        nodes = graph.get("nodes", [])
        edges = graph.get("edges", []) or graph.get("links", [])

        return SystemStats(
            total_items=len(nodes),
            total_links=len(edges),
            wings=0,
            rooms=0,
            drawers=0,
            storage_size_bytes=self.graph_path.stat().st_size if self.graph_path.exists() else 0,
        )

    # === Graphify-specific methods ===

    def build_graph(
        self,
        corpus_path: Path,
        mode: str = "default",
    ) -> dict:
        """
        Build graph from corpus.

        Args:
            corpus_path: Path to source files
            mode: "default" or "deep" (more inferred edges)
        """
        # TODO: Implement - call graphify CLI
        raise NotImplementedError("Graphify build not yet implemented")

    def get_god_nodes(self) -> list[dict]:
        """Get highest-degree nodes (what everything connects through)."""
        graph = self._load_graph()
        # TODO: Calculate node degrees, return top N
        raise NotImplementedError("Graphify god nodes not yet implemented")

    def get_communities(self) -> list[list[str]]:
        """Get Leiden community clusters."""
        graph = self._load_graph()
        # TODO: Extract community membership
        raise NotImplementedError("Graphify communities not yet implemented")
