#!/bin/bash
# Start experiment watchers for all three memory systems
# Run this script in a terminal, then use OpenCode in another terminal

set -e

cleanup() {
    echo ""
    echo "=== Stopping watchers ==="
    kill $GRAPHIFY_PID 2>/dev/null || true
    kill $LLMWIKI_PID 2>/dev/null || true
    kill $MEMPALACE_PID 2>/dev/null || true
    exit 0
}
trap cleanup SIGINT SIGTERM

CORPUS_PATH="${1:-$HOME/code/pedro/pedro-bots}"
EXPERIMENTS_PATH="$(cd "$(dirname "$0")" && pwd)"
PARENT_PATH="$(dirname "$EXPERIMENTS_PATH")"
WIKI_PATH="$CORPUS_PATH/wiki"
PALACE_PATH="$HOME/.mempalace"

echo "=== Starting Experiment Watchers ==="
echo "Corpus: $CORPUS_PATH"
echo ""

# Create directories if needed
mkdir -p "$WIKI_PATH/raw" "$WIKI_PATH/wiki"
mkdir -p "$PALACE_PATH"

echo "1. Starting Graphify watch..."
# Graphify has built-in watch mode
graphify watch "$CORPUS_PATH" &
GRAPHIFY_PID=$!
echo "   PID: $GRAPHIFY_PID"

echo ""
echo "2. Starting LLMWiki watcher..."
# LLMWiki - use Python to run watcher
python3 -c "
import sys
sys.path.insert(0, '$PARENT_PATH')
from pathlib import Path
from experiments.systems.llmwiki.adapter import LLMWikiAdapter

wiki = LLMWikiAdapter(Path('$WIKI_PATH'))
watcher = wiki.start_watcher(Path('$CORPUS_PATH'))
print('   LLMWiki watching... (Ctrl+C to stop)')
try:
    import time
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    watcher.stop()
    print('   Stopped')
" &
LLMWIKI_PID=$!
echo "   PID: $LLMWIKI_PID"

echo ""
echo "3. Starting MemPalace watcher..."
python3 -c "
import sys
sys.path.insert(0, '$PARENT_PATH')
from pathlib import Path
from experiments.systems.mempalace.adapter import MemPalaceAdapter

adapter = MemPalaceAdapter(Path('$PALACE_PATH'))
watcher = adapter.start_watcher(Path('$CORPUS_PATH'))
print('   MemPalace watching... (Ctrl+C to stop)')
try:
    import time
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    watcher.stop()
    print('   Stopped')
" &
MEMPALACE_PID=$!
echo "   PID: $MEMPALACE_PID"

echo ""
echo "=== All watchers started ==="
echo "Graphify:   $GRAPHIFY_PID"
echo "LLMWiki:    $LLMWIKI_PID"
echo "MemPalace:  $MEMPALACE_PID"
echo ""
echo "Press Ctrl+C to stop all watchers"

# Wait for any process to exit
wait