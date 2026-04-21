# Running the Experiment

This guide covers how to run all three memory systems on your code and evaluate them.

---

## Quick Start

### 1. Run Watchers to Capture Code

Start new OpenCode sessions and run each system in watch mode:

```bash
# Session 1: Graphify
/graphify ~/code
# (runs once, or use --watch if you want continuous updates)

# Session 2: LLMWiki
/llmwiki watch ~/code

# Session 3: MemPalace
/mempalace watch ~/code
```

### 2. Alternative: One-Time Ingest

If you don't need continuous updates:

```bash
# Graphify (one-time build)
/graphify ~/code

# LLMWiki (one-time ingest)
/llmwiki ~/code

# MemPalace (one-time mine)
/mempalace mine ~/code
```

---

## Where Data Goes

| System | Storage Location |
|--------|-----------------|
| Graphify | `~/code/graphify-out/graph.json` |
| LLMWiki | `~/code/wiki/` (raw/, wiki/, index.md, log.md) |
| MemPalace | `~/.mempalace/` (ChromaDB) |

---

## Evaluation Methods

### 1. Query Comparison

Ask the same question to all three systems and compare results:

```python
# Example: using the adapters
from experiments.systems.graphify.adapter import GraphifyAdapter
from experiments.systems.llmwiki.adapter import LLMWikiAdapter
from experiments.systems.mempalace.adapter import MemPalaceAdapter

# Graphify
g = GraphifyAdapter(Path("~/code/graphify-out/graph.json"))
g_results = g.search_memory("how does auth work")

# LLMWiki  
w = LLMWikiAdapter(Path("~/code/wiki"))
w_results = w.search_memory("how does auth work")

# MemPalace
m = MemPalaceAdapter(Path("~/.mempalace"))
m_results = m.search_memory("how does auth work")
```

### 2. Stats Comparison

```python
g_stats = g.get_stats()
w_stats = w.get_stats()  
m_stats = m.get_stats()

print(f"Graphify: {g_stats.total_items} nodes, {g_stats.total_links} edges")
print(f"LLMWiki: {w_stats.total_items} pages, {w_stats.drawers} drawers")
print(f"MemPalace: {m_stats.total_items} items, {m_stats.wings} wings, {m_stats.rooms} rooms")
```

### 3. Path Finding (Graphify only)

```python
# Find path between two concepts
path = g.explain_path("AuthModule")
# Returns: hops, confidence, traversal steps
```

### 4. Latency Measurement

```python
import time

start = time.time()
results = system.search_memory("your query")
elapsed = time.time() - start
print(f"Search took {elapsed:.3f}s")
```

### 5. Coverage Analysis

Check what % of your code is captured:

```bash
# Count files processed
wc -l ~/code/graphify-out/GRAPH_REPORT.md  # Graphify report

# Count wiki pages
find ~/code/wiki -name "*.md" | wc -l       # LLMWiki

# Count MemPalace items
m.get_stats().total_items                   # MemPalace
```

---

## Benchmark Tasks

Define a set of test queries to run against all systems:

| Task | Query |
|------|-------|
| Architecture | "What is the overall architecture?" |
| Find code | "Where is the auth handler?" |
| Trace dependency | "What does User model depend on?" |
| Find pattern | "Where do I use async/await?" |
| Documentation | "What APIs exist?" |

Run each query against all three systems and rate:
- **Relevance** (1-5): Did it return useful results?
- **Completeness** (1-5): Did it cover all relevant items?
- **Latency** (seconds): How fast was the response?

---

## Automated Benchmark Script

Create `scripts/benchmark.py`:

```python
#!/usr/bin/env python3
"""Run benchmark queries against all systems."""
import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from experiments.systems.graphify.adapter import GraphifyAdapter
from experiments.systems.llmwiki.adapter import LLMWikiAdapter  
from experiments.systems.mempalace.adapter import MemPalaceAdapter

QUERIES = [
    "authentication",
    "database",
    "api endpoints",
    "error handling",
    "tests",
]

def benchmark(system_name, adapter):
    results = []
    for q in QUERIES:
        start = time.time()
        hits = adapter.search_memory(q, top_k=5)
        elapsed = time.time() - start
        results.append({
            "query": q,
            "hits": len(hits),
            "time": elapsed,
        })
    return results

def main():
    graphify = GraphifyAdapter(Path.home() / "code/graphify-out/graph.json")
    llmwiki = LLMWikiAdapter(Path.home() / "code/wiki")
    mempalace = MemPalaceAdapter(Path.home() / ".mempalace")

    for name, adapter in [("Graphify", graphify), ("LLMWiki", llmwiki), ("MemPalace", mempalace)]:
        print(f"\n=== {name} ===")
        try:
            results = benchmark(name, adapter)
            for r in results:
                print(f"  {r['query']}: {r['hits']} hits in {r['time']:.3f}s")
        except Exception as e:
            print(f"  Error: {e}")

if __name__ == "__main__":
    main()
```

Run with:
```bash
python scripts/benchmark.py
```

---

## Watching During Session

For continuous capture during coding:

1. Start OpenCode in terminal 1
2. Run: `/llmwiki watch ~/code` or `/mempalace watch ~/code`
3. Code in your editor
4. Files are auto-ingested on save

To stop: Ctrl+C in the OpenCode session.

---

## Current Status (2026-04-21)

### ✅ LLMWiki - Working
- **What it does**: Copies code files to `wiki/raw/`, creates markdown summaries in `wiki/wiki/imported/`
- **Storage**: `~/code/wiki/` (raw/, wiki/, index.md, log.md)
- **Watch mode**: Working - captures file changes in real-time
- **Output**: Markdown files with frontmatter (title, category, created date)
- **Recent captures**: alembic migrations, env.py, add_feed.py

### ✅ Graphify - Working
- **What it does**: AST extraction → builds graph of code structure (functions, classes, imports)
- **Storage**: `~/code/pedro/pedro-bots/graphify-out/graph.json`
- **Output**: 202 nodes, 312 edges, 22 communities (for pedro-bots)
- **Files**: `graph.json`, `graph.html`, `GRAPH_REPORT.md`
- **Watch mode**: Working - auto-rebuilds on file changes (3s debounce)
- **Note**: Only indexes code files (.py, .js, .ts, .go, .rs) - not "semantic" in LLM sense

### ✅ MemPalace - Working
- **What it does**: Semantic hash routing (no vectors needed)
- **Storage**: `~/.mempalace/palace/knowledge_graph.sqlite3`
- **Watch mode**: Working - generates deterministic hash from file path → wing/room
- **Approach**: Hash-based routing (like Graphify), not vector search
- **Excludes**: /wiki/, /.mempalace/, /graphify-out/

### Scripts
- `./start_exp.sh` - Start all three watchers (watches `pedro-bots`)
- `./stop_exp.sh` - Stop all watchers

### What Each System Actually Does

| System | Method | Output |
|--------|--------|--------|
| **Graphify** | AST parsing | Nodes = functions/classes/files, Edges = imports/calls |
| **LLMWiki** | File copy + markdown | Wiki pages in Obsidian format |
| **MemPalace** | Vector embeddings | ChromaDB collection with semantic search |

---

## Known Issues

1. **MemPalace requires init first**: Must run `mempalace init .` before watch will mine files

---

## Next Steps

1. Run benchmark queries against all three
2. Compare results - relevance, latency, coverage
3. Document findings