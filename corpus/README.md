# Test Corpus Specification

This directory defines the test corpus used across all three systems under test.

**Critical**: The same corpus must be used for all systems to ensure fair comparison.

---

## Corpus Structure

```
corpus/
├── repos/                    # Open source repos (cloned)
│   ├── mempalace/            # Your project
│   ├── ontology-go/          # Related project
│   └── [others]/             # Test repos
├── docs/                     # Design documents
│   ├── adrs/                 # Architecture Decision Records
│   └── design/               # Design docs
├── notes/                    # Personal notes, patterns
├── media/                    # Images, diagrams (for Graphify)
└── transcripts/              # Video/audio transcripts
```

---

## Corpus Requirements

### Repos (5-10 recommended)

- At least one you own and understand deeply (mempalace)
- One with clear architecture (go, python)
- One with good documentation
- Include varying sizes: small (1-2 files), medium, large

### Design Docs (10-20)

- ADRs in standard format
- Architecture diagrams (PNG/SVG)
- API specifications
- README files from repos

### Notes (20-50)

- Pattern collections
- CLI command notes
- Configuration snippets
- Prior implementation notes

### Media (optional, for Graphify)

- Screenshots of architecture
- Diagrams
- Whiteboard photos

---

## Adding Corpus Items

1. Add files to appropriate subdirectory
2. Update `corpus/manifest.yaml` with metadata
3. Run corpus validation

```bash
# Validate corpus structure
python -m experiments validate-corpus
```

---

## Manifest Format

```yaml
corpus:
  - id: "repo-mempalace"
    type: "repository"
    path: "repos/mempalace"
    description: "Main project - semantic memory system"
    tags: ["python", "sqlite", "chroma", "mcp"]

  - id: "doc-adr-001"
    type: "adr"
    path: "docs/adrs/001-use-chroma.md"
    description: "Decision to use ChromaDB for vector storage"

  - id: "note-cli-patterns"
    type: "note"
    path: "notes/cli-patterns.md"
    description: "Common CLI patterns I use"
```

---

## Sharing Corpus

Corpus lives on homelab storage (SeaweedFS):

```
/mnt/homelab/corpus/
```

All systems mount this same directory:

- LLMWiki: reads from `corpus/`
- Graphify: runs on `corpus/repos/`
- MemPalace: mines from `corpus/`

---

## Actual Corpus (User's Code)

Instead of synthetic test data, we use your real code:

```
~/code/
├── go/        # Go projects
├── pedro/     # Personal projects
├── misc/      # Misc utilities
└── opensource # Open source contributions
```

This is the corpus for all three systems. Each system ingests the same `~/code/` directory.

---

## Constraints

1. **Never modify corpus per system** - each system sees the same data
2. **Immutable sources** - once added, don't change source files
3. **Versioned** - track corpus version in manifest
4. **Clean** - no secrets, no large binaries (use git LFS or SeaweedFS)