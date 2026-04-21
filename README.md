# experiments

Living lab notebook for testing: **Do Semantic Models Turn File-Based Systems into Knowledge Graphs?**

---

## Quick Links

| Section | Description |
|---------|-------------|
| [EXPERIMENT_PLAN.md](./EXPERIMENT_PLAN.md) | Full experiment design |
| [corpus/](./corpus/) | Test corpus specification |
| [interfaces/](./interfaces/) | Shared agent contract |
| [logs/](./logs/) | Experiment log entries |
| [results/](./results/) | Collected metrics |

---

## Systems Under Test

| System | Description | Link |
|--------|-------------|------|
| **LLMWiki** | Markdown-based persistent wiki | [Karpathy gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f), view in Obsidian |
| **Graphify** | Graph extraction from code/docs | [safishamsi/graphify](https://github.com/safishamsi/graphify) |
| **MemPalace** | Semantic routing via SPO hashing | [mempalace](./systems/mempalace/) |

---

## Current Phase

**Status**: `deployment` — Setting up external dependencies

See [DEPLOYMENT.md](./DEPLOYMENT.md) for installation instructions.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Experiment Runner                         │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │ LLMWiki     │  │ Graphify    │  │ MemPalace   │          │
│  │ Adapter     │  │ Adapter     │  │ Adapter     │          │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘          │
│         │                │                │                  │
│         └────────────────┼────────────────┘                  │
│                          ▼                                   │
│              ┌─────────────────────┐                         │
│              │   Agent Contract    │                         │
│              │  (shared interface) │                         │
│              └─────────────────────┘                         │
│                          │                                   │
│         ┌────────────────┼────────────────┐                 │
│         ▼                ▼                ▼                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Model     │  │   Corpus    │  │   Storage   │         │
│  │  Gateway    │  │   (shared)  │  │  (homelab)  │         │
│  │ (Spark)     │  │             │  │             │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

---

## Storage Architecture (Homelab)

See [HOMELAB.md](./HOMELAB.md) for detailed storage plan.

- **Longhorn** block storage for persistent state
- **SeaweedFS** object storage for large artifacts (graphs, transcripts)
- **Model Gateway** via Spark proxy (OpenAI-compatible API)

---

## Getting Started

1. Clone this repo
2. Review [EXPERIMENT_PLAN.md](./EXPERIMENT_PLAN.md)
3. Define your test corpus in `corpus/`
4. Begin Phase A (baseline testing)

---

## Contributing

- Use conventional commits (`fix:`, `feat:`, `docs:`)
- Log experiments in `logs/` using the template
- Add results to `results/`