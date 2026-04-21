# Experiment Proposal

## *Do Semantic Models Turn File-Based Systems into Knowledge Graphs?*

---

## 1. Background & Motivation

Modern "AI memory" systems are converging on three patterns:

- Markdown/wiki-based synthesis (e.g. Karpathy's LLMWiki)
- Graph extraction from artifacts (e.g. Graphify)
- Semantic routing + retrieval layers (e.g. MemPalace)

At the same time, tools like Obsidian are increasingly used as a "graph layer" on top of files. However, there is ambiguity in the field:

> **Does storing files with links or visualizing connections constitute a knowledge graph?**

This experiment investigates whether **explicit semantic modeling (ontology + typed relations)** is the defining factor that elevates these systems into *true knowledge graphs capable of reasoning and efficient traversal*.

---

## 2. Hypothesis

> **A system becomes a functional knowledge graph only when semantic structure (entities, relationships, constraints) enables constrained traversal, inference, and explainable retrieval.**

More concretely:

- Semantic models should reduce:
  - number of agent turns
  - number of search operations
  - time-to-answer

- Semantic models should improve:
  - traversal quality
  - explainability
  - consistency of answers

---

## 3. Systems Under Test

### System A — LLMWiki

- Markdown-based persistent wiki
- Maintained by LLM
- Obsidian as materialization layer

### System B — Graphify

- Graph extraction from code/docs/media
- Relationships: extracted, inferred, ambiguous
- Native OpenCode integration

### System C — MemPalace

- Semantic routing via subject/predicate/object hashing
- SQLite metadata + vector narrowing
- Designed for targeted retrieval

---

## 4. Experimental Design

### 4.1 Two-Phase Evaluation

#### Phase A — Baseline Systems (No Explicit Ontology)

Evaluate each system as designed.

#### Phase B — Semantic Overlay

Introduce a shared semantic model across all systems:

- Typed entities
- Typed relationships
- Provenance
- Optional inference rules

This isolates the impact of **semantics vs structure alone**.

---

### 4.2 Shared Constraints

To ensure fairness:

- Same corpus
- Same model backend (via Spark proxy)
- Same agent interface
- Same evaluation tasks

---

## 5. Architecture

### 5.1 Model Gateway

All systems call a shared local inference endpoint:

- Spark-hosted models
- Reverse proxy (OpenAI-compatible interface)

This ensures:

- consistent latency
- consistent model behavior
- no system-specific bias

**Location**: Homelab (referb) via Spark

### 5.2 Agent Interface (Critical)

All systems must implement:

```go
search_memory(query, scope, top_k)
read_memory(id)
write_memory(input, metadata)
link_memory(source_id, target_id, relation)
explain_path(query_or_id)
```

This is the abstraction layer that allows fair comparison.

### 5.3 Adapters

- `llmwiki_adapter`
- `graphify_adapter`
- `mempalace_adapter`

Each adapter maps system behavior → shared interface.

---

## 6. Corpus

Use a realistic, consistent dataset:

- Open source repos (primary)
- Design docs / ADRs
- Blog drafts
- Notes / patterns
- Prior implementations

**Important constraint:**
Do not modify corpus per system.

---

## 7. Task Suite

### 7.1 Repo Navigation

- "Find how I implemented X in another repo"
- "Where is auth handled?"

### 7.2 Architecture Understanding

- "What depends on this module?"
- "Why does this exist?"

### 7.3 Pattern Retrieval

- "Show my preferred Go project layout"
- "Find prior CLI patterns"

### 7.4 Cross-Artifact Reasoning

- "Compare design doc vs implementation"
- "Find contradictions"

### 7.5 Write / Update Tasks

- ingest new repo
- update concept
- reconcile conflicting info

---

## 8. Metrics

### 8.1 Primary Metrics

| Metric            | Description                  |
| ----------------- | ---------------------------- |
| Turns to Answer   | Agent iterations required    |
| Search Ops        | Number of retrieval calls    |
| Latency           | Time to usable answer        |
| Token Cost        | Total tokens consumed        |
| Traversal Quality | Relevance of navigation      |
| Explainability    | Can system justify answer    |
| Write Integration | How well new data integrates |

### 8.2 Secondary Metrics

- Hallucination rate
- Duplicate concepts
- Contradiction detection
- Maintenance overhead
- Local-first compatibility

---

## 9. Semantic Model (Phase B)

### Entities

- Repository
- Module
- Function
- Pattern
- Workflow
- ADR
- Tool
- Model

### Relationships

- implements
- depends_on
- uses_pattern
- documents
- contradicts
- similar_to

### Provenance

- source file
- timestamp
- extraction method
- confidence

---

## 10. Implementation Plan

### Week 1 — Interface + Setup

- define agent contract
- set up model gateway
- prepare corpus

### Week 2 — Baseline Integration

- implement adapters
- run read-only tasks

### Week 3 — Write Integration

- enable ingestion + updates
- validate consistency

### Week 4 — Semantic Overlay

- apply ontology
- re-run tasks

### Week 5 — Benchmark + Logging

- run full task suite
- collect metrics

### Week 6 — Analysis

- compare Phase A vs Phase B
- document findings

---

## 11. Homelab Storage Architecture

### Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        referb (Homelab)                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐ │
│  │    Longhorn     │    │   SeaweedFS     │    │   Spark / LM   │ │
│  │  (Block Store)  │    │ (Object Store)  │    │  (Model Host)  │ │
│  │                 │    │                 │    │                 │ │
│  │ - SQLite dbs    │    │ - Graph JSON    │    │ - vLLM / SGL   │ │
│  │ - Chroma data   │    │ - Transcripts   │    │ - Embeddings   │ │
│  │ - Config/state  │    │ - Raw corpus    │    │ - Spark proxy  │ │
│  └────────┬────────┘    └────────┬────────┘    └────────┬────────┘ │
│           │                      │                      │          │
│           └──────────────────────┼──────────────────────┘          │
│                                  ▼                                   │
│                    ┌─────────────────────────┐                      │
│                    │   Network (LAN/vpn)     │                      │
│                    └─────────────────────────┘                      │
└─────────────────────────────────────────────────────────────────────┘
                               │
                               ▼ (client access)
┌─────────────────────────────────────────────────────────────────────┐
│                     Developer Machine (macOS)                       │
├─────────────────────────────────────────────────────────────────────┤
│  experiments/  →  connects to referb for:                          │
│    - Model API (Spark proxy)                                       │
│    - Storage (Longhorn/SeaweedFS mounts)                           │
└─────────────────────────────────────────────────────────────────────┘
```

### Storage Details

| Component | Technology | Purpose | Mount Path |
|-----------|------------|---------|------------|
| Database | Longhorn (PVC) | SQLite (MemPalace KG), ChromaDB | `/mnt/homelab/db` |
| Objects | SeaweedFS (S3) | Graph JSON, transcripts, large files | `/mnt/homelab/objects` |
| Corpus | SeaweedFS | Raw source files | `/mnt/homelab/corpus` |
| Models | Spark + vLLM | Inference endpoint | `http://referb:8000` |

### Model Gateway (Spark)

```yaml
# spark-proxy config
base_url: http://referb:8000/v1
api_key: local-dev
model: qwen2.5-coder-32b-instruct  # or configurable

# OpenAI-compatible
# Works with: OpenCode, Claude, any OpenAI client
```

### Connection Setup

```bash
# Mount homelab storage (macOS)
# Option 1: SeaweedFS S3 mount
brew install gcsfuse  # or seaweedfs client
seaweedfs mount -dir=/mnt/homelab -volume=/referb:8888

# Option 2: NFS
sudo mount -t nfs referb:/export/nfs /mnt/homelab

# Option 3: Shortcut (SSHFS for dev)
sshfs referb:/opt/experiments /mnt/homelab
```

### Access Patterns

| Operation | Storage | Network |
|-----------|---------|---------|
| Query (read) | SeaweedFS → local cache | Minimal |
| Ingest (write) | Buffer local → push to SeaweedFS | Burst |
| Model inference | Direct to Spark | Per-request latency critical |
| Embeddings | Generated locally or via Spark | Same as inference |

---

## 12. Experiment Log (Lab Notebook Section)

*(You will fill this out during execution)*

### Entry Template

**Date:**
**System:** (LLMWiki / Graphify / MemPalace)
**Phase:** (Baseline / Semantic)

**Task:**
What question or operation was performed?

**Steps Taken:**

- step 1
- step 2

**Observations:**
What actually happened?

**Metrics:**

- Turns:
- Search Ops:
- Latency:
- Notes:

**Result Quality:**

- Correct / Partial / Incorrect

**Surprises / Failures:**
What broke or behaved unexpectedly?

**Hypothesis Update:**
Does this support or contradict the thesis?

---

## 13. Expected Outcomes

### Likely Findings

- LLMWiki excels at synthesis but lacks strict semantics
- Graphify excels at structure but needs constraints for reasoning
- MemPalace enables efficient routing but needs ontology to become a full knowledge graph

### Core Insight

> **Graphs emerge from structure, but knowledge graphs emerge from semantics.**

---

## 14. Deliverables

- Experiment log (Notion + local `logs/`)
- Benchmark results table (`results/`)
- Final comparison matrix (`docs/final-comparison.md`)
- LinkedIn / Substack write-up

---

## 15. Final Write-Up Direction

The final narrative should answer:

- What is a knowledge graph *in practice*?
- Where do current tools fall short?
- What role does semantic modeling actually play?
- What should engineers build instead?

---

## 16. Deployment & Dependencies

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed installation and setup instructions.

### Quick Install

```bash
# Core dependencies
pip install openai pyyaml pandas

# Graphify
pip install 'graphifyy[video,office,mcp]'
graphify opencode install

# MemPalace
pip install mempalace chromadb
```

### External Systems Status

| System | Package | Adapter Status | Key Integration |
|--------|---------|----------------|-----------------|
| Graphify | `graphifyy` (PyPI) | ❌ Not implemented | CLI/MCP → graph.json |
| MemPalace | `mempalace` (PyPI) | 🟡 Partial | ChromaDB + miner |
| LLMWiki | Custom | ✅ Complete | Markdown files |

---

## 17. External PRs Needed

To fully integrate these systems with the experiment framework, the following contributions would be needed:

### Graphify (upstream: safishamsi/graphify)

1. **Programmatic API for graph queries**
   - Current: CLI-first, designed for AI assistant integration
   - Needed: Python library interface for direct graph.json queries
   - PR: Add `graphify.query()` function to core package

2. **Structured JSON output mode**
   - Current: Human-readable markdown reports
   - Needed: Machine-parseable JSON for automated experiments
   - PR: Add `--json` flag to query/path/explain commands

3. **Incremental update API**
   - Current: Full rebuild or manual cache management
   - Needed: `graphify.update(corpus_path, only_changed=True)`
   - PR: Expose update logic as public API

### MemPalace (upstream: milla-jovovich/mempalace)

1. **SPO Hashing as public API**
   - Current: Internal implementation, not exposed
   - Needed: `mempalace.hash_spo(subject, predicate, object)`
   - Issue/PR: Expose semantic routing layer

2. **Knowledge Graph edge creation**
   - Current: Mostly read-focused
   - Needed: `kg.add_edge(source, target, relation_type)`
   - PR: Add write operations to knowledge_graph.py

3. **Better error handling for missing collections**
   - Current: Silent failures in adapter
   - Needed: Clear errors, auto-initialization
   - PR: Graceful degradation / auto-create

### LLMWiki (custom implementation)

No upstream needed - fully self-contained.

---

## 18. Local Fork Integration

For development, you can use local forks:

```bash
# MemPalace (your fork at ../mempalace)
pip install -e ../mempalace

# Graphify (if you fork and modify)
git clone https://github.com/safishamsi/graphify
cd graphify
pip install -e .
```

---

## 19. Why This Matters

- Improves OpenCode workflows
- Reduces cognitive load when coding
- Enables reusable engineering knowledge
- Aligns with DDSO / ontology thesis