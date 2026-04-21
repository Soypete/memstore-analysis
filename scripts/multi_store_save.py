#!/usr/bin/env python3
"""
Multi-store session saver.
Writes session content to MemPalace, LLMWiki, and Graphify.
"""

import json
import sys
import os
import subprocess
from datetime import datetime
from pathlib import Path

sys.path.insert(0, "/Users/soypete/code/opensource/mempalace")

import chromadb
from mempalace.config import MempalaceConfig


# ============ LLMWiki implementation (inline) ============
class LLMWiki:
    """LLMWiki - Markdown-based wiki."""

    def __init__(self, wiki_path: Path):
        self.wiki_path = Path(wiki_path)
        self.raw_path = self.wiki_path / "raw"
        self.wiki_dir = self.wiki_path / "wiki"
        self.index_file = self.wiki_path / "index.md"

        self.raw_path.mkdir(parents=True, exist_ok=True)
        self.wiki_dir.mkdir(parents=True, exist_ok=True)

    def write(self, title: str, content: str, category: str = "general") -> str:
        safe_title = "".join(c if c.isalnum() or c in "- " else "_" for c in title)
        safe_title = safe_title.lower().replace(" ", "-")

        category_dir = self.wiki_dir / category
        category_dir.mkdir(parents=True, exist_ok=True)

        file_path = category_dir / f"{safe_title}.md"
        full_content = f"""---
title: {title}
category: {category}
created: {datetime.now().isoformat()}
---

{content}
"""
        file_path.write_text(full_content)
        return str(file_path)


# ============ Save functions ============
def get_palace_collection(palace_path: str):
    client = chromadb.PersistentClient(path=palace_path)
    return client.get_or_create_collection("mempalace_drawers")


def save_to_mempalace(content: str, session_id: str, palace_path: str = None):
    palace_path = palace_path or MempalaceConfig().palace_path
    col = get_palace_collection(palace_path)

    doc_id = f"session_{session_id}_{datetime.now().timestamp()}"
    col.upsert(
        ids=[doc_id],
        documents=[content],
        metadatas=[
            {
                "source_file": f"session:{session_id}",
                "wing": "experiments",
                "room": "sessions",
                "created_at": datetime.now().isoformat(),
            }
        ],
    )
    print(f"[MemPalace] Saved to {palace_path}")


def save_to_llmwiki(content: str, session_id: str, wiki_path: str = None):
    wiki_path = Path(wiki_path or os.environ.get("LLMWIKI_PATH", str(Path.home() / "wiki")))

    if not wiki_path.exists():
        wiki_path.mkdir(parents=True, exist_ok=True)

    wiki = LLMWiki(wiki_path)
    wiki.write(title=f"Session {session_id}", content=content, category="sessions")
    print(f"[LLMWiki] Saved to {wiki_path}")


def save_to_graphify(content: str, session_id: str, graphify_path: str = None):
    graphify_path = Path(
        graphify_path or os.environ.get("GRAPHIFY_PATH", str(Path.home() / ".graphify"))
    )

    if not graphify_path.exists():
        print(f"[Graphify] Graphify path {graphify_path} does not exist, skipping")
        return

    print(f"[Graphify] Saving to {graphify_path} (stub)")


def main():
    session_id = sys.argv[1] if len(sys.argv) > 1 else "unknown"
    transcript_path = sys.argv[2] if len(sys.argv) > 2 else None

    # Get content: either from transcript file, or from stdin, or args
    content = ""

    # Check for stdin
    if not sys.stdin.isatty():
        content = sys.stdin.read()

    # Override with transcript file if provided
    if transcript_path and Path(transcript_path).exists():
        with open(transcript_path) as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    msg = entry.get("message", {})
                    if isinstance(msg, dict) and msg.get("role") == "assistant":
                        c = msg.get("content", "")
                        if isinstance(c, str):
                            content += c + "\n\n"
                        elif isinstance(c, list):
                            for block in c:
                                if isinstance(block, dict) and block.get("type") == "text":
                                    content += block.get("text", "") + "\n\n"
                except:
                    pass

    if not content.strip():
        print("No content to save")
        return

    palace_path = os.environ.get("MEMPALACE_PATH")
    wiki_path = os.environ.get("LLMWIKI_PATH")
    graphify_path = os.environ.get("GRAPHIFY_PATH")

    print(f"[MultiStore] Saving session {session_id}")

    save_to_mempalace(content, session_id, palace_path)
    save_to_llmwiki(content, session_id, wiki_path)
    save_to_graphify(content, session_id, graphify_path)

    print("[MultiStore] Done")


if __name__ == "__main__":
    main()
