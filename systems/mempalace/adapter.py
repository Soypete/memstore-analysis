"""
MemPalace Adapter - implements MemorySystem protocol.

MemPalace features:
- Semantic routing via SPO (Subject-Predicate-Object) hashing
- SQLite for metadata + vector narrowing (ChromaDB)
- Wing/Room/Drawer hierarchy
- MCP server for remote access
"""

from datetime import datetime
from pathlib import Path
from typing import Optional, Callable

try:
    import watchdog
    from watchdog.observers import Observer
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False

import chromadb

from ...interfaces import (
    MemoryResult,
    MemoryItem,
    Link,
    PathExplanation,
    SystemStats,
)


class MemPalaceAdapter:
    """Adapter for MemPalace-style systems."""

    def __init__(
        self,
        palace_path: Optional[Path] = None,
    ):
        """
        Initialize MemPalace adapter.

        Args:
            palace_path: Path to palace directory (default: ~/.mempalace)
        """
        self.palace_path = palace_path or Path.home() / ".mempalace"

    def _get_collection(self):
        """Get the ChromaDB collection."""
        client = chromadb.PersistentClient(path=str(self.palace_path))
        return client.get_collection("mempalace_drawers")

    def search_memory(
        self,
        query: str,
        scope: str = "all",
        top_k: int = 10,
    ) -> list[MemoryResult]:
        """
        Search using MemPalace's semantic routing.

        Uses:
        - SPO hashing for exact matches
        - ChromaDB for vector similarity
        - SQLite for metadata filtering
        """
        try:
            col = self._get_collection()
        except Exception:
            return []

        where = {}
        if scope != "all":
            if scope == "wing":
                where = {"wing": {"$exists": True}}
            elif scope == "room":
                where = {"room": {"$exists": True}}

        try:
            results = col.query(
                query_texts=[query],
                n_results=top_k,
                where=where if where else None,
                include=["documents", "metadatas", "distances"],
            )
        except Exception:
            return []

        memory_results = []
        for doc, meta, dist in zip(
            results.get("documents", [[]])[0],
            results.get("metadatas", [[]])[0],
            results.get("distances", [[]])[0],
        ):
            memory_results.append(
                MemoryResult(
                    id=meta.get("source_file", "unknown"),
                    content=doc,
                    score=round(1 - dist, 3),
                    source=meta.get("source_file", "unknown"),
                    created_at=datetime.fromisoformat(
                        meta.get("created_at", datetime.now().isoformat())
                    ),
                )
            )

        return memory_results

    def read_memory(self, id: str) -> Optional[MemoryItem]:
        """Read by source file path or drawer ID."""
        try:
            col = self._get_collection()
            result = col.get(where={"source_file": id})
            if result["documents"]:
                return MemoryItem(
                    id=id,
                    content=result["documents"][0],
                    metadata=result["metadatas"][0] if result["metadatas"] else {},
                    links=[],
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                )
        except Exception:
            pass
        return None

    def explain_path(self, query_or_id: str) -> PathExplanation:
        """Explain semantic routing path."""
        return PathExplanation(
            query=query_or_id,
            steps=[],
            total_hops=0,
            confidence=0.0,
        )

    def write_memory(
        self,
        input: str,
        metadata: dict,
    ) -> str:
        """
        Write to palace using mining/ingestion.

        MemPalace uses:
        - miner.py for project files
        - convo_miner.py for transcripts
        """
        try:
            col = self._get_collection()
            doc_id = f"manual_{datetime.now().timestamp()}"
            col.upsert(
                ids=[doc_id],
                documents=[input],
                metadatas=[
                    {
                        "source_file": doc_id,
                        "wing": metadata.get("wing", "default"),
                        "room": metadata.get("room", "manual"),
                        "created_at": datetime.now().isoformat(),
                    }
                ],
            )
            return doc_id
        except Exception as e:
            raise RuntimeError(f"Failed to write: {e}")

    def link_memory(
        self,
        source_id: str,
        target_id: str,
        relation: str,
    ) -> bool:
        """Create semantic link (stored in knowledge graph)."""
        return False

    def get_stats(self) -> SystemStats:
        """Get palace statistics from ChromaDB."""
        try:
            col = self._get_collection()
            count = col.count()

            metas = col.get(include=["metadatas"])["metadatas"]
            wings = set(m.get("wing") for m in metas if m.get("wing"))
            rooms = set(m.get("room") for m in metas if m.get("room"))

            return SystemStats(
                total_items=count,
                total_links=0,
                wings=len(wings),
                rooms=len(rooms),
                drawers=count,
                storage_size_bytes=0,
            )
        except Exception:
            return SystemStats(
                total_items=0,
                total_links=0,
                wings=0,
                rooms=0,
                drawers=0,
                storage_size_bytes=0,
            )

    def mine_project(self, project_path: Path) -> dict:
        """
        Mine a project for semantic content.

        Uses mempalace CLI internally.
        """
        from mempalace.mempalace.miner import mine as _mine

        return _mine(str(project_path), str(self.palace_path))

    def create_wing(self, name: str, description: str = "") -> str:
        """Create a new wing (person/project)."""
        return name

    def create_room(self, wing: str, name: str, description: str = "") -> str:
        """Create a new room (topic) within a wing."""
        return name

    def get_entity_relationships(self, entity_id: str) -> list[dict]:
        """
        Get all relationships for an entity from knowledge graph.

        Returns list of {subject, predicate, object, valid_from, valid_to}
        """
        return []

    def start_watcher(self, watch_path: Path, on_change: Optional[Callable] = None):
        """
        Start watching a directory for changes and auto-mine.

        On file change, mines the file to MemPalace.
        """
        if not WATCHDOG_AVAILABLE:
            raise RuntimeError("watchdog not installed: pip install watchdog")

        watcher = MemPalaceWatcher(self, watch_path, on_change)
        watcher.start()
        return watcher


class MemPalaceWatcher:
    """Watcher for MemPalace file changes."""

    def __init__(self, adapter: MemPalaceAdapter, watch_path: Path, on_change: Optional[Callable] = None):
        self.adapter = adapter
        self.watch_path = watch_path
        self.on_change = on_change
        self._observer = None
        self._seen = set()

    def start(self):
        """Start watching."""
        from watchdog.events import FileSystemEventHandler
        self.watch_path.mkdir(parents=True, exist_ok=True)

        class FileHandler(FileSystemEventHandler):
            def __init__(w_self, watcher):
                super().__init__()
                w_self.watcher = watcher

            def on_created(w_self, event):
                if event.is_directory:
                    return
                w_self._handle(Path(event.src_path), "created")

            def on_modified(w_self, event):
                if event.is_directory:
                    return
                w_self._handle(Path(event.src_path), "modified")

            def _handle(w_self, path: Path, event_type: str):
                if path.suffix not in {'.py', '.js', '.ts', '.go', '.rs', '.md', '.txt'}:
                    return
                if event_type == "created" and str(path) in w_self.watcher._seen:
                    return
                w_self.watcher._seen.add(str(path))

                print(f"MemPalace: {event_type} {path.name}", flush=True)
                try:
                    w_self.watcher.adapter.mine_project(path.parent)
                    if w_self.watcher.on_change:
                        w_self.watcher.on_change(path, event_type)
                except Exception as e:
                    print(f"MemPalace watch error: {e}", flush=True)

        handler = FileHandler(self)
        self._observer = Observer()
        self._observer.schedule(handler, str(self.watch_path), recursive=True)
        self._observer.start()

    def stop(self):
        """Stop watching."""
        if self._observer:
            self._observer.stop()
            self._observer.join()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.stop()
