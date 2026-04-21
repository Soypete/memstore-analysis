#!/bin/bash
# Stop all experiment watchers

echo "=== Stopping Experiment Watchers ==="

pkill -f "graphify watch" && echo "Graphify stopped" || echo "Graphify not running"
pkill -f "python.*experiments.*llmwiki" && echo "LLMWiki stopped" || echo "LLMWiki not running"
pkill -f "python.*experiments.*mempalace" && echo "MemPalace stopped" || echo "MemPalace not running"

echo "Done"