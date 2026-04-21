#!/bin/bash
# Multi-store session saver
# Called by opencode on session end to write to all 3 memory systems

set -e

SESSION_ID="${1:-session}"
TRANSCRIPT_PATH="${2:-}"
PALACE_PATH="${MEMPALACE_PATH:-$HOME/.mempalace}"

echo "[multi-store] Saving session $SESSION_ID"

# Extract conversation content from transcript if provided
CONTENT=""
if [ -n "$TRANSCRIPT_PATH" ] && [ -f "$TRANSCRIPT_PATH" ]; then
    # Extract assistant messages (the model responses we want to remember)
    CONTENT=$(cat "$TRANSCRIPT_PATH" | python3 -c "
import sys, json
for line in sys.stdin:
    try:
        entry = json.loads(line)
        msg = entry.get('message', {})
        if isinstance(msg, dict) and msg.get('role') == 'assistant':
            content = msg.get('content', '')
            if isinstance(content, str):
                print(content)
            elif isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get('type') == 'text':
                        print(block.get('text', ''))
    except: pass
" 2>/dev/null || echo "")
fi

if [ -z "$CONTENT" ]; then
    echo "[multi-store] No content to save"
    exit 0
fi

# 1. Save to MemPalace
echo "[multi-store] Saving to MemPalace..."
python3 -m mempalace.mcp_server --palace "$PALACE_PATH" \
    mempalace_add_drawer \
    --content "$CONTENT" \
    --wing "experiments" \
    --room "sessions" 2>/dev/null || true

# 2. Save to LLMWiki (markdown file)
WIKI_PATH="${LLMWIKI_PATH:-$HOME/wiki}"
if [ -d "$WIKI_PATH" ]; then
    echo "[multi-store] Saving to LLMWiki..."
    SESSION_FILE="$WIKI_PATH/wiki/sessions/$SESSION_ID.md"
    mkdir -p "$(dirname "$SESSION_FILE")"
    cat > "$SESSION_FILE" << EOF
# Session: $SESSION_ID

$CONTENT

---
Saved: $(date -Iseconds)
EOF
fi

# 3. Save to Graphify (if configured)
GRAPHIFY_PATH="${GRAPHIFY_PATH:-$HOME/.graphify}"
if [ -d "$GRAPHIFY_PATH" ]; then
    echo "[multi-store] Saving to Graphify..."
    # TODO: implement Graphify write
    true
fi

echo "[multi-store] Done"