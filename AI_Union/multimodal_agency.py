# -*- coding: utf-8 -*-
"""
multimodal_agency.py v3.4.0
Zarządza autonomicznymi agentami.

ZMIANY v3.4.0:
- WYŁĄCZONO: Haiku, Fraktale rysowane, Muzyka autonomiczna
  (podsystemy wyłączone na żądanie — boredom loop i creative loop
   pozostają aktywne ale nie generują artefaktów kreatywnych)
"""
import threading
import time
import random
import sys
import traceback

try:
    from union_config import Colors
except ImportError:
    class Colors:
        MAGENTA = "\033[35m"; CYAN = "\033[36m"; RESET = "\033[0m"
        YELLOW = "\033[33m"; GREEN = "\033[32m"; RED = "\033[31m"

class MultimodalAgency:
    def __init__(self, union_core, verbose=False, **kwargs):
        self.core = union_core
        self.verbose = verbose
        self.running = False
        self.threads = []
        
        self.boredom_level = 0.0
        self.last_stimulus_time = time.time()
        
        # === WYŁĄCZONO v3.4.0 ===
        self.music_available = False
        self.music_system = None

    def start(self):
        self.running = True
        self.threads = [
            threading.Thread(target=self._boredom_loop, daemon=True, name="BoredomThread"),
        ]
        for t in self.threads: t.start()

    def stop(self): self.running = False

    def stimulate(self, stimulus_text):
        self.last_stimulus_time = time.time()
        self.boredom_level = max(0.0, self.boredom_level - 0.8)

    def _boredom_loop(self):
        while self.running:
            time.sleep(5)
            if time.time() - self.last_stimulus_time > 15:
                self.boredom_level = min(1.0, self.boredom_level + 0.05)
            # v3.4.0: Boredom tracked but no spontaneous art generated