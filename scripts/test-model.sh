#!/bin/bash
# Quick test for vLLM model
# Usage: ./scripts/test-model.sh

echo "=== Testing vLLM Model ==="

echo -n "1. Listing models... "
MODELS=$(curl -s http://pedrogpt:8080/v1/models 2>/dev/null)
if [ $? -eq 0 ]; then
    echo "OK"
    echo "$MODELS" | python3 -m json.tool 2>/dev/null || echo "$MODELS"
else
    echo "FAIL"
    echo "Make sure Tailscale is running and can reach 100.87.122.109"
fi

echo ""
echo "2. Testing generation... "
curl -s http://pedrogpt:8080/v1/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3-coder-30b",
    "prompt": "Say hello in 3 words",
    "max_tokens": 20
  }' 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin)['choices'][0]['text'])" 2>/dev/null || echo "Generation failed - check model name"