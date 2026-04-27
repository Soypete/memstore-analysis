# Graphify Skill

Query the Graphify knowledge graph for your code.

## Usage

```
/graphify <query> [--top-k N] [--stats]
```

## Examples

```
/graphify executor
/graphify authentication --top-k 5
/graphify --stats
```

## Options

- `<query>` - Search term to find in the code graph
- `--top-k N` - Number of results to return (default: 10)
- `--stats` - Show Graphify statistics

## What it does

Graphify builds a knowledge graph from your code using AST parsing. It finds:
- Functions and classes (nodes)
- Import/call relationships (edges)

Query it to find code related to a concept, trace dependencies, or understand architecture.