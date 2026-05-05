# Mind Maps vs AI Harnesses: A Comparative Analysis of Memory Indexing Systems for AI Coding Assistants

## A Comparative Experimental Analysis

**Author:** Pete Williams  
**Date:** May 2026  
**Version:** 1.0

---

## Abstract

This white paper presents the results of a systematic evaluation of three memory system architectures for AI coding assistants:
- **LLMWiki** (AI Harness) — LLM-maintained markdown wiki
- **Graphify** (Mind Map) — Knowledge graph extracted from code
- **MemPalace** (AI Harness) — Semantic routing via SPO hashing

We measure data size, query latency, and storage efficiency across 10 standardized tasks. Our findings:

- **Graphify** (Mind Map): Largest data (3.7GB, 1.2M nodes, 6.9M edges) but slowest queries (35s) due to full graph load
- **MemPalace** (AI Harness): Smallest footprint (8.8MB), fastest queries (34ms) using incremental SQLite indexing
- **LLMWiki** (AI Harness): Moderate (33.9MB, 2.2s) with human-readable markdown

The semantic overlay experiment (adding typed ontology) was not fully wired up, leaving room for future work.

---

## 1. Introduction

### 1.1 The Problem

Modern AI coding assistants need memory systems that can index and retrieve relevant context. Two architectural patterns have emerged:

1. **Mind Maps (Graph-based)** — Systems like Graphify extract explicit relationship graphs from code (AST, imports, function calls). Think: "nodes and edges"
2. **AI Harnesses (LLM-based)** — Systems like LLMWiki and MemPalace use LLMs to synthesize, route, and retrieve context. Think: "prompt engineering + embeddings"

A fundamental question: **Which approach provides better indexing and retrieval for AI coding assistants?**

**Use case:** Context preservation — keeping codebase or cross-microservice context available without loading all files. Think "context saver" for AI assistants working across large codebases.

### 1.2 Research Question

> **Do explicit graph structures (mind maps) outperform LLM-based approaches (AI harnesses) for code retrieval in AI assistants?**

### 1.3 Hypothesis

- Mind maps should provide **faster** retrieval (graph traversal vs LLM synthesis)
- AI harnesses should provide **richer** context (LLM understanding)
- Both should improve with semantic overlays (typed entities, constraints)

---

## 2. Systems Under Test

### 2.1 LLMWiki

- **Type:** Markdown-based persistent wiki
- **Maintenance:** LLM-generated content
- **View:** Obsidian as materialization layer
- **Semantic layer:** Implicit (wikilinks, categories)

### 2.2 Graphify

- **Type:** Graph extraction from code/docs
- **Relationships:** Extracted, inferred, ambiguous (with confidence tags)
- **Integration:** Native OpenCode skill

### 2.3 MemPalace

- **Type:** Semantic routing via SPO hashing
- **Storage:** SQLite metadata + vector narrowing (ChromaDB)
- **Design:** Wing/Room/Drawer hierarchy

---

## 3. Methodology

### 3.1 Two-Phase Evaluation (Partial)

| Phase | Description | Status |
|-------|-------------|--------|
| **Phase A (Baseline)** | Evaluate each system as designed | ✅ Complete |
| **Phase B (Semantic)** | Introduce shared semantic model (typed entities, relationships, provenance) | ⚠️ Not wired up |

**Note:** The semantic overlay was designed but not implemented in this iteration. Both baseline and semantic phases use the same underlying system, so results are identical. Future work includes implementing the ontology layer.

### 3.2 Shared Constraints

- Same corpus
- Same model backend (via Spark proxy)
- Same agent interface
- Same evaluation tasks

### 3.3 Task Suite

| Category | Task ID | Query |
|----------|---------|-------|
| Repo Navigation | rn1 | Find how I implemented authentication in another repo |
| Repo Navigation | rn2 | Where is user authorization handled? |
| Architecture Understanding | au1 | What depends on this module? |
| Architecture Understanding | au2 | Why does this component exist? |
| Pattern Retrieval | pr1 | Show my preferred Go project layout |
| Pattern Retrieval | pr2 | Find prior CLI patterns I've used |
| Cross-Artifact Reasoning | ca1 | Compare design doc vs implementation |
| Cross-Artifact Reasoning | ca2 | Find contradictions in my notes |
| Write Operations | wo1 | Ingest new repo: https://github.com/soypete/dotfiles |
| Write Operations | wo2 | Update concept: semantic routing |

### 3.4 Metrics

| Metric | Description |
|--------|-------------|
| **Turns to Answer** | Agent iterations required |
| **Search Ops** | Number of retrieval calls |
| **Latency** | Time to usable answer (ms) |
| **Token Cost** | Total tokens consumed |
| **Traversal Quality** | Relevance of navigation (excellent/good/partial/poor) |
| **Explainability** | Can system justify answer (full/partial/none) |
| **Result Quality** | Correct/Partial/Incorrect |

---

## 4. Results

### 4.1 System Size Comparison

| System | Data Size | Total Items | Structure |
|--------|-----------|-------------|-----------|
| LLMWiki | 33.9 MB | 12,215 pages | Flat (drawers) |
| Graphify | **3.7 GB** | 1,249,838 nodes, 6,939,779 edges | Graph (nodes+edges) |
| MemPalace | 8.8 MB | 23,866 items, 1,268 wings, 2,799 rooms | Hierarchical |

### 4.2 Query Latency (scaled comparison)

Query: "authentication" (top 5 results)

| System | Data (GB) | Latency (s) | Results | Notes |
|--------|-----------|-------------|---------|-------|
| MemPalace | 0.01 | **0.03** | 5 | SQLite + semantic hash |
| LLMWiki | 0.03 | 2.3 | 5 | Grep + index search |
| Graphify | 3.6 | 35.7 | 5 | Full graph load (1 node hop) |

### 4.3 Latency per GB

| System | Latency/GB (s) | Efficiency |
|--------|---------------|------------|
| MemPalace | **2.7** | Best — minimal overhead |
| LLMWiki | 76.7 | Moderate |
| Graphify | 9.9 | Poor at scale — loads entire graph |

**Key insight:** MemPalace's incremental indexing (only new items) keeps both data size and latency low. Graphify's full-codebase analysis creates a 3.6GB graph requiring 35s to load per query.

### 4.3 Performance Metrics (benchmark run)

| System | Phase | Tasks | Avg Turns | Avg Search Ops | Avg Latency (ms) |
|--------|-------|-------|-----------|----------------|------------------|
| LLMWiki | Baseline | 10 | 1.0 | 1.0 | 4 |
| LLMWiki | Semantic | 10 | 1.0 | 1.0 | 4 |
| Graphify | Baseline | 10 | 1.0 | 1.0 | 0 |
| Graphify | Semantic | 10 | 1.0 | 1.0 | 0 |
| MemPalace | Baseline | 8 | 1.0 | 1.0 | 9 |
| MemPalace | Semantic | 8 | 1.0 | 1.0 | 5 |

**Note:** Benchmark shows 1-turn simple queries. The real search test above shows actual latency under load.

### 4.4 Key Findings

1. **Graphify is largest** (3.7GB, 1.2M nodes, 6.9M edges) because it analyzed the **entire existing codebase** — every function, class, import. This causes slow queries (35s) due to full graph load.
2. **MemPalace is fastest** (34ms) with smallest footprint (8.8MB) using SQLite + semantic hashing — stores incremental new items only.
3. **LLMWiki is moderate** (2.2s) with human-readable markdown (33.9MB) — good for documentation, slower for code search.
4. **Storage efficiency**: MemPalace stores 23K items in 8.8MB vs Graphify's 1.2M items in 3.7GB

### 4.5 Why Graphify is Slow

Graphify parses the entire codebase into a massive graph. Query latency includes:
- Loading 3.7GB JSON graph into memory
- Building NetworkX graph structure
- Running traversal algorithms

**Mitigation**: Index/query only relevant subgraphs instead of loading full graph.

### 4.3 Quality Metrics

*[Insert quality heatmap from analysis]*

### 4.4 Category Analysis

*[Insert task category breakdown]*

---

## 5. Analysis

### 5.1 What Works

- **Incremental indexing wins** — MemPalace's approach of only indexing new items keeps queries fast (34ms)
- **Full-graph analysis is expensive** — Graphify's comprehensive analysis creates massive graphs (3.7GB) with slow queries (35s)
- **Human-readable has value** — LLMWiki's markdown is useful for documentation even if slower (2.2s)

### 5.2 System-Specific Insights

**LLMWiki (AI Harness):** 
- Human-readable markdown output
- Good for exploratory documentation queries
- Moderate latency (2.2s)

**Graphify (Mind Map):**
- Most comprehensive structure extraction (1.2M nodes)
- Good for batch analysis (not real-time queries)
- Requires optimization for real-time use

**MemPalace (AI Harness):**
- Fastest query latency (34ms)
- Hierarchical organization (wings/rooms)
- Best for real-time code navigation

### 5.3 When Semantics Help vs Hurt

**Help:**
- Complex multi-hop queries
- Cross-repository reasoning
- Contradiction detection

**Hurt:**
- Simple keyword lookups (overhead > benefit)
- Rapid prototyping scenarios
- Small corpora (<100 files)

---

## 6. Limitations

1. **Corpus constraints** — Results may vary with different codebases
2. **Task set bias** — 10 tasks cannot capture all use cases
3. **Evaluation subjectivity** — Quality ratings require human judgment
4. **Model dependency** — Results tied to specific LLM backend

---

## 7. Conclusions

### 7.1 Answer to Research Question

**Preliminary findings:**

- **Mind Maps (Graphify)** provide fastest retrieval but limited semantic depth
- **AI Harnesses (LLMWiki, MemPalace)** provide richer context at higher latency
- The comparison is currently shallow (1-turn queries only)

**The semantic overlay experiment was not completed**, so we cannot yet answer whether explicit ontology improves retrieval. This is the primary direction for future work.

### 7.2 Recommendations

| Scenario | Recommended System |
|----------|-------------------|
| Fast code navigation | Graphify |
| Rich documentation | LLMWiki |
| Deterministic lookups | MemPalace |
| Full knowledge graph | Any + Semantic Overlay (future) |

### 7.3 Future Work

- **Implement semantic overlay** — Add typed entities and relationships to enable Phase B
- Expand task suite to 50+ tasks with multi-turn conversations
- Add human quality evaluation
- Test with multiple model backends

---

## 8. Appendices

### A. Raw Data Tables

*[Link to results/ directory]*

### B. Task Prompts

*[Full prompt text for each task]*

### C. System Configurations

```
Model Gateway: http://referb:8000/v1
Model: qwen2.5-coder-32b-instruct
API Key: local-dev
```

---

## References

1. Karpathy, A. (2024). LLMWiki. https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
2. Graphify. https://github.com/safishamsi/graphify
3. MemPalace. https://github.com/milla-jovovich/mempalace

---

*Generated: May 2026*
*Experiment Code: https://github.com/soypete/experiments*