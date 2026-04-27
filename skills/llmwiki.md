# LLMWiki Skill

Query the LLMWiki system for documentation about your code.

## Usage

```
/llmwiki <query> [--top-k N] [--stats]
```

## Examples

```
/llmwiki executor
/llmwiki authentication --top-k 5
/llmwiki --stats
```

## Options

- `<query>` - Search term to find in wiki pages
- `--top-k N` - Number of results to return (default: 10)
- `--stats` - Show LLMWiki statistics

## What it does

LLMWiki converts your code files to markdown wiki pages. Search to find:
- Documentation about specific modules
- Code comments and docstrings
- Test files

Wiki location: ~/code/wiki/wiki/