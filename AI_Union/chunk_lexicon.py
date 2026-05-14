# -*- coding: utf-8 -*-
"""
chunk_lexicon.py v1.1.0
Pełna zaawansowana architektura językowa.
Autor: Maciej A. Mazur & Claude

FIX: Naprawiono brak metody from_dict w klasie LanguageChunk.
ZMIANY: Obsługa flagi verbose dla cichego uczenia.
"""

import numpy as np
import json
import time
import re
import os
from typing import Dict, List, Optional
from union_config import UnionConfig, Colors

class LanguageChunk:
    def __init__(self, text: str, frequency: int = 1, emotional_vector: Optional[np.ndarray] = None):
        self.text = text.lower().strip()
        self.words = self.text.split()
        self.length = len(self.words)
        self.frequency = frequency
        self.emotional_vector = emotional_vector if emotional_vector is not None else np.zeros(UnionConfig.DIMENSION)
        self.last_seen = time.time()
        self.priming_strength = 0.0

    def update_priming(self):
        current_time = time.time()
        decay = np.exp(-(current_time - self.last_seen) / 60.0)
        self.priming_strength = min(1.0, self.priming_strength * decay + 0.3)
        self.last_seen = current_time

    def get_boost(self): return 1.0 + self.priming_strength

    def to_dict(self):
        return {
            'text': self.text, 'frequency': self.frequency,
            'emotional_vector': self.emotional_vector.tolist(),
            'priming_strength': self.priming_strength
        }

    @classmethod
    def from_dict(cls, data):
        """Kluczowa metoda deserializacji."""
        vec = np.array(data.get('emotional_vector', [0.0]*UnionConfig.DIMENSION))
        c = cls(data['text'], data.get('frequency', 1), vec)
        c.priming_strength = data.get('priming_strength', 0.0)
        return c

class ChunkLexicon:
    def __init__(self, chunk_file: str = "data/chunks.json"):
        self.chunk_file = chunk_file
        self.chunks: Dict[str, LanguageChunk] = {}
        self.load()

    @property
    def total_chunks(self): return len(self.chunks)

    def extract_chunks_from_text(self, text: str):
        words = re.sub(r'[^\w\s]', '', text.lower()).split()
        for n in range(2, 6):
            for i in range(len(words) - n + 1):
                phrase = ' '.join(words[i:i+n])
                if phrase in self.chunks:
                    self.chunks[phrase].frequency += 1
                    self.chunks[phrase].update_priming()
                else:
                    self.chunks[phrase] = LanguageChunk(phrase)

    def analyze_text_chunks(self, text: str, verbose: bool = True) -> dict:
        words = text.lower().split()
        if not words: return {"coverage": 0.0, "emotional_vector": np.zeros(UnionConfig.DIMENSION), "chunks_found": []}
        
        found = []
        covered = set()
        sorted_keys = sorted(self.chunks.keys(), key=lambda x: self.chunks[x].length, reverse=True)
        for pk in sorted_keys:
            c_obj = self.chunks[pk]
            for i in range(len(words) - c_obj.length + 1):
                if words[i:i+c_obj.length] == c_obj.words:
                    idx_range = set(range(i, i + c_obj.length))
                    if not (idx_range & covered):
                        found.append(c_obj); covered.update(idx_range); c_obj.update_priming()

        coverage = len(covered) / len(words)
        
        # Wyświetlanie Match-logów tylko jeśli verbose=True (rozmowa)
        if verbose and coverage > 0:
            print(f"{Colors.GREEN} [CHUNKS]{Colors.RESET} Match: {Colors.YELLOW}{[c.text for c in found]}{Colors.RESET} ({coverage:.0%})")

        return {
            'coverage': coverage,
            'chunks_found': [c.text for c in found],
            'emotional_vector': np.mean([c.emotional_vector for c in found], axis=0) if found else np.zeros(UnionConfig.DIMENSION)
        }

    def get_statistics(self): return {"total": self.total_chunks}
    
    def save(self):
        os.makedirs(os.path.dirname(self.chunk_file), exist_ok=True)
        with open(self.chunk_file, 'w', encoding='utf-8') as f:
            json.dump({'chunks': {t: c.to_dict() for t, c in self.chunks.items()}}, f, indent=2)

    def load(self):
        if os.path.exists(self.chunk_file):
            try:
                with open(self.chunk_file, 'r', encoding='utf-8') as f:
                    d = json.load(f).get('chunks', {})
                    for t, c in d.items(): self.chunks[t] = LanguageChunk.from_dict(c)
            except: pass