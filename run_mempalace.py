#!/usr/bin/env python3
import sys
from pathlib import Path

BASE = Path(__file__).parent.parent
sys.path.insert(0, str(BASE))

PALACE_PATH = Path.home() / ".mempalace"
CORPUS_PATH = Path.home() / "code"

from experiments.systems.mempalace.adapter import MemPalaceAdapter
adapter = MemPalaceAdapter(PALACE_PATH)
watcher = adapter.start_watcher(CORPUS_PATH)
print("MemPalace watching...", flush=True)

import time
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    watcher.stop()
    print("Stopped", flush=True)