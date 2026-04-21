# Deployment Guide

This guide covers deploying the three memory systems under test: **LLMWiki**, **Graphify**, and **MemPalace**.

> **Important**: All systems must run on the **same machine** for fair comparison. This ensures:
> - Same model backend (pedrogpt)
> - Same filesystem latency
> - Same network conditions
> - Controlled variables

---

## Machine Requirements

### Experiment Machine (Primary)

All three systems installed and configured:
- `pip install graphifyy mempalace chromadb pandas`
- OpenCode skills installed for all three systems
- Access to pedrogpt:8080 (llama.cpp)
- Local corpus at `experiments/corpus/`

### OpenCode Skills

All three systems are integrated as OpenCode skills:

| System | Command | Skill File |
|--------|---------|------------|
| Graphify | `/graphify` | `~/.config/opencode/skills/graphify/SKILL.md` |
| LLMWiki | `/llmwiki` | `~/.config/opencode/skills/llmwiki/SKILL.md` |
| MemPalace | `/mempalace` | `~/.config/opencode/skills/mempalace/SKILL.md` |

Install commands:
```bash
# Graphify (installed via graphify CLI)
graphify opencode install

# LLMWiki and MemPalace (manual - see sections below)
```

---

## System Overview

| System | Package | Installation | Key Dependencies |
|--------|---------|--------------|------------------|
| **Graphify** | `graphifyy` (PyPI) | `pip install graphifyy` | tree-sitter, faster-whisper (optional), Claude/AI assistant |
| **MemPalace** | `mempalace` (PyPI) | `pip install mempalace` | ChromaDB, faster-whisper (optional) |
| **LLMWiki** | Custom | N/A (markdown structure) | None |

---

## 1. Graphify Deployment

### Installation

```bash
pip install 'graphifyy[video,office,mcp]'
```

### OpenCode Integration

```bash
graphify opencode install
```

This creates:
- Skill file: `~/.config/opencode/skills/graphify/SKILL.md`
- Plugin hook: `~/.config/opencode/plugins/graphify.js`
- Config: `~/.config/opencode/opencode.json` (updated)

### Usage

**In OpenCode:**
```
/graphify ./corpus
/graphify ./corpus --mode deep
/graphify query "auth flow"
/graphify path "AuthModule" "Database"
```

**CLI:**
```bash
graphify query "auth flow" --graph graphify-out/graph.json
graphify path "DigestAuth" "Response"
graphify explain "SwinTransformer"
```

**MCP Server:**
```bash
python -m graphify.serve graphify-out/graph.json
```

### Output Structure

```
corpus/
├── raw/                     # Your source files
├── graphify-out/
│   ├── graph.json          # Raw graph data (for experiments)
│   ├── graph.html          # Interactive visualization
│   ├── GRAPH_REPORT.md     # Audit report
│   └── obsidian/           # Obsidian vault (--obsidian)
```

### Experiment Adapter

`systems/graphify/adapter.py` implements MemorySystem protocol:
- `search_memory()` - Query graph.json
- `read_memory()` - Get node by ID
- `write_memory()` - Trigger graph rebuild
- `link_memory()` - Add edge to graph
- `explain_path()` - Trace traversal path

**Status**: Methods raise `NotImplementedError` - needs implementation

---

## 2. MemPalace Deployment

### Installation

```bash
pip install mempalace
```

### Local Development (Using Fork)

Since you have the fork at `../mempalace`, you can install in development mode:

```bash
cd ../mempalace
pip install -e ".[dev]"
```

Or install from experiments directory:

```bash
pip install -e ../mempalace
```

### Setup

```bash
# Initialize a palace
mempalace init ~/palaces/experiments

# Mine a project
mempalace mine ~/code/myproject

# Or mine conversations
mempalace mine ~/chats/ --mode convos
```

### MCP Server (Optional)

```bash
mempalace mcp start
```

### Integration with Experiment Adapter

Current adapter at `systems/mempalace/adapter.py` needs:
- SPO hashing implementation (Phase B)
- Link creation to actual knowledge graph
- Proper import of `mempalace.mempalace.miner`

---

## 3. LLMWiki Deployment

LLMWiki is a custom markdown-based system. No external package needed.

### Directory Structure

```
experiments/
└── wikis/
    └── {system_name}/
        ├── raw/           # Immutable sources (read-only)
        ├── wiki/          # LLM-maintained markdown pages
        ├── index.md       # Content catalog (by category)
        ├── log.md         # Chronological operation log
        └── AGENTS.md      # Schema/instructions for LLM
```

### Viewing in Obsidian

1. Open Obsidian
2. "Open folder as vault" → select `wikis/{system_name}/`
3. Use Obsidian features:
   - Graph view (Cmd+G) to see connections
   - Dataview for queries over frontmatter
   - Search (Cmd+Shift+F)
   - Image handling with Web Clipper

### Storage Location

Wiki is stored as plain markdown files. Options:
- **Local**: `experiments/wikis/{name}/`
- **Shared**: Mount homelab storage, symlink to local

### Setup Script

```python
# scripts/setup_llmwiki.py
from pathlib import Path

def create_llmwiki(root: Path):
    (root / "raw").mkdir(parents=True, exist_ok=True)
    (root / "wiki").mkdir(parents=True, exist_ok=True)
    
    # Create index.md
    index = root / "index.md"
    if not index.exists():
        index.write_text("# Wiki Index\n\n## Categories\n")
    
    # Create AGENTS.md
    agents = root / "AGENTS.md"
    if not agents.exists():
        agents.write_text("""# Agent Instructions

## Writing new pages
- Use markdown
- Include frontmatter with title, category, created date
- Update index.md with links

## Linking
- Use [[category/filename]] wikilink syntax
""")
```

---

## 4. Shared Infrastructure

### Model Gateway

All systems use **your local llama.cpp (pedrogpt)** for consistent model comparison. This ensures:
- Same model across all systems (no API variability)
- No dependency on external services
- Reproducible results

```bash
# Verify connectivity to model gateway
curl http://pedrogpt:8080/v1/models
```

Config in `config/model-gateway.yaml`:
```yaml
model_gateway:
  base_url: "http://pedrogpt:8080/v1"
  api_key: "EMPTY"
  default_model: "qwen3-coder-30b"  # Or your preferred model
```

> **Note**: OpenCode uses minimax by default. For experiments, we'll configure systems to use pedrogpt directly, not OpenCode's built-in model.

### Storage (Homelab)

For persistent data across experiments:

```bash
# Option 1: SeaweedFS S3 mount
seaweedfs mount -dir=/mnt/homelab -volume=/referb:8888

# Option 2: NFS
sudo mount -t nfs referb:/export/nfs /mnt/homelab

# Option 3: SSHFS (development)
sshfs referb:/opt/experiments /mnt/homelab
```

---

## 5. External Dependencies Summary

### Required pip Packages

```txt
# Core
openai>=1.0.0

# MemPalace
mempalace
chromadb

# Graphify
graphifyy

# Optional (for full features)
graphifyy[video]    # Video/audio transcription
graphifyy[office]   # Office document support
graphifyy[mcp]      # MCP server mode
faster-whisper      # Local transcription

# Experiment running
pandas              # Results analysis
pyyaml              # Config parsing
```

### AI Assistant Required

One of:
- OpenCode (recommended for experiments)
- Claude Code
- OpenAI Codex
- Cursor

---

## 6. Adapter Integration Details

### Graphify Adapter - Implementation Required

**Current State**: All methods raise `NotImplementedError`

**Required Implementations**:

1. `search_memory()` - Query graph.json
   - Option A: Subprocess call to `graphify query`
   - Option B: Parse graph.json directly
   - Option C: MCP server + client

2. `read_memory()` - Get node by ID

3. `explain_path()` - Trace traversal path

4. `write_memory()` - Trigger graph rebuild

5. `link_memory()` - Add edge to graph.json

6. `build_graph()` - Extract from corpus
   - Call: `graphify ./corpus`
   - Output: `graphify-out/graph.json`

### MemPalace Adapter - Integration Required

**Current State**: Search/read/write work, some features stubbed

**Required Integrations**:

1. `mine_project()` - Currently imports from `mempalace.mempalace.miner`
   - May need adjustment for local fork import path

2. `link_memory()` - Currently returns False
   - Needs actual KG edge creation

3. `get_entity_relationships()` - Currently returns []
   - Query knowledge_graph.py for SPO triples

4. SPO Hashing - Phase B feature
   - Implement subject/predicate/object hashing
   - Enable semantic routing

### LLMWiki Adapter - Complete

**Current State**: Fully implemented

**Optional Enhancements**:
- LLM-powered page generation
- Auto-linking via semantic similarity
- Consistency checking

---

## 7. Testing Checklist

After deployment, verify:

- [ ] `pip install graphifyy` succeeds
- [ ] `pip install mempalace` succeeds
- [ ] `graphify --version` works
- [ ] `mempalace --version` works
- [ ] Model gateway responds: `curl http://pedrogpt:8080/v1/models`
- [ ] LLMWiki directory structure created
- [ ] All three adapters import without errors

---

## 8. Next Steps

1. **Deploy dependencies** on your machine
2. **Verify connectivity** to model gateway (pedrogpt)
3. **Test each system independently** with small corpus
4. **Implement Graphify adapter** methods (critical gap)
5. **Integrate MemPalace** fully with local fork
6. **Run baseline experiments** (Phase A)