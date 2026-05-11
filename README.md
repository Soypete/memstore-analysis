# Documentation

## TL;DR

This repository contains an experiment evaluating three storage architectures for context retrieval in AI coding assistants: LLMWiki (markdown-based), Graphify (graph-based), and MemPalace (database-style indexed retrieval). The study measures storage size and query latency to determine which architecture performs best for AI-assisted development workflows.

**Key Finding**: Database-style indexed retrieval (MemPalace) achieves millisecond-level latency with megabyte-scale storage, significantly outperforming full graph materialization approaches that require second-level latency and gigabyte-scale storage.

## Repository Navigation

```
experiments/
├── whitepaper.md          # Full whitepaper with complete analysis
├── docs/
│   ├── README.md          # This file
│   └── figures/           # Charts and visualizations
├── experiment/            # Experiment configuration and logs
├── analysis/              # Analysis scripts and raw data
├── results/               # Collected metrics from system tests
│   ├── llmwiki/           # LLMWiki system results
│   ├── graphify/          # Graphify system results
│   └── mempalace/         # MemPalace system results
├── systems/               # System implementations
├── corpus/                # Test corpus specification
└── interfaces/            # Shared agent contract
```

## Quick Links

- [Whitepaper](./whitepaper.md) - Full paper with methodology and results
- [Results](../results/) - Raw experimental data
- [Systems](../systems/) - Implementation code for each system