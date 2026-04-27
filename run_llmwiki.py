#!/usr/bin/env python3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from experiments.systems.llmwiki.adapter import LLMWikiAdapter

WIKI_PATH = Path.home() / "code/wiki"
CORPUS_PATH = Path.home() / "code"

wiki = LLMWikiAdapter(WIKI_PATH)
watcher = wiki.start_watcher(CORPUS_PATH)
print("LLMWiki watching...", flush=True)

import time
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    watcher.stop()
    print("Stopped", flush=True)