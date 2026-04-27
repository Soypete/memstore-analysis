# MemPalace Skill

Query the MemPalace semantic memory system.

## Usage

```
/mempalace <query> [--top-k N] [--stats]
```

## Examples

```
/mempalace executor
/mempalace database --top-k 5
/mempalace --stats
```

## Options

- `<query>` - Search term to find in semantic index
- `--top-k N` - Number of results to return (default: 10)
- `--stats` - Show MemPalace statistics

## What it does

MemPalace uses semantic hashing to route files to wings/rooms. It's fast (SQLite) and deterministic.

Search to find file paths organized by:
- wing (project/directory)
- room (subdirectory topic)

Database location: ~/.mempalace/knowledge_graph.sqlite3