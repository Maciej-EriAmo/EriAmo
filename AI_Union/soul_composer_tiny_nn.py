# soul_composer_tiny_nn.py
# -*- coding: utf-8 -*-
"""
Tiny Neural Networks dla SoulComposer v8.1
Używa TYLKO NumPy - małe modele neuronowe (~10KB każdy)
Implementuje: wariacje melodyczne, progresje trójdźwięków, różnorodność
"""

import numpy as np
import random
import os


def sigmoid(x):
    return 1 / (1 + np.exp(-np.clip(x, -500, 500)))


def tanh(x):
    return np.tanh(x)


def softmax(logits, temperature=1.0):
    logits = np.array(logits) / temperature
    exp_logits = np.exp(logits - np.max(logits))
    return exp_logits / exp_logits.sum()


# ═══════════════════════════════════════════════════════════════════════════════
# TINY NEURAL NETWORKS
# ═══════════════════════════════════════════════════════════════════════════════

class TinyChordNet:
    def __init__(self):
        self.w1 = np.random.randn(15 + 8, 32) * 0.1
        self.b1 = np.zeros(32)
        self.w2 = np.random.randn(32, 16) * 0.1
        self.b2 = np.zeros(16)
        self.w3 = np.random.randn(16, 8) * 0.1
        self.b3 = np.zeros(8)

    def forward(self, emotions, prev_onehot):
        x = np.concatenate([emotions, prev_onehot])
        h1 = tanh(np.dot(x, self.w1) + self.b1)
        h2 = tanh(np.dot(h1, self.w2) + self.b2)
        return np.dot(h2, self.w3) + self.b3

    def save(self, path):
        np.savez(path, w1=self.w1, b1=self.b1, w2=self.w2, b2=self.b2, w3=self.w3, b3=self.b3)

    def load(self, path):
        data = np.load(path)
        self.w1 = data['w1']; self.b1 = data['b1']
        self.w2 = data['w2']; self.b2 = data['b2']
        self.w3 = data['w3']; self.b3 = data['b3']


class TinyMelodyNet:
    def __init__(self):
        self.w1 = np.random.randn(15 + 12, 32) * 0.1   # 12 możliwych nut w oktawie
        self.b1 = np.zeros(32)
        self.w2 = np.random.randn(32, 16) * 0.1
        self.b2 = np.zeros(16)
        self.w3 = np.random.randn(16, 12) * 0.1
        self.b3 = np.zeros(12)

    def forward(self, emotions, prev_note_onehot):
        x = np.concatenate([emotions, prev_note_onehot])
        h1 = tanh(np.dot(x, self.w1) + self.b1)
        h2 = tanh(np.dot(h1, self.w2) + self.b2)
        return np.dot(h2, self.w3) + self.b3

    def save(self, path):
        np.savez(path, w1=self.w1, b1=self.b1, w2=self.w2, b2=self.b2, w3=self.w3, b3=self.b3)

    def load(self, path):
        data = np.load(path)
        self.w1 = data['w1']; self.b1 = data['b1']
        self.w2 = data['w2']; self.b2 = data['b2']
        self.w3 = data['w3']; self.b3 = data['b3']


class TinyTriadNet:
    def __init__(self):
        self.w1 = np.random.randn(15 + 8, 24) * 0.1
        self.b1 = np.zeros(24)
        self.w2 = np.random.randn(24, 12) * 0.1
        self.b2 = np.zeros(12)
        self.w3 = np.random.randn(12, 8) * 0.1
        self.b3 = np.zeros(8)

    def forward(self, emotions, context):
        x = np.concatenate([emotions, context])
        h1 = tanh(np.dot(x, self.w1) + self.b1)
        h2 = tanh(np.dot(h1, self.w2) + self.b2)
        return np.dot(h2, self.w3) + self.b3

    def save(self, path):
        np.savez(path, w1=self.w1, b1=self.b1, w2=self.w2, b2=self.b2, w3=self.w3, b3=self.b3)

    def load(self, path):
        data = np.load(path)
        self.w1 = data['w1']; self.b1 = data['b1']
        self.w2 = data['w2']; self.b2 = data['b2']
        self.w3 = data['w3']; self.b3 = data['b3']


class TinyDiversityNet:
    def __init__(self):
        self.w1 = np.random.randn(15, 16) * 0.1
        self.b1 = np.zeros(16)
        self.w2 = np.random.randn(16, 1) * 0.1
        self.b2 = np.zeros(1)

    def forward(self, emotions):
        h1 = tanh(np.dot(emotions, self.w1) + self.b1)
        return sigmoid(np.dot(h1, self.w2) + self.b2)[0]

    def save(self, path):
        np.savez(path, w1=self.w1, b1=self.b1, w2=self.w2, b2=self.b2)

    def load(self, path):
        data = np.load(path)
        self.w1 = data['w1']; self.b1 = data['b1']
        self.w2 = data['w2']; self.b2 = data['b2']


# ═══════════════════════════════════════════════════════════════════════════════
# WRAPPER
# ═══════════════════════════════════════════════════════════════════════════════

class SoulComposerTinyNN:
    MODEL_DIR = "tiny_models"

    def __init__(self):
        self.chord_net = TinyChordNet()
        self.melody_net = TinyMelodyNet()
        self.triad_net = TinyTriadNet()
        self.diversity_net = TinyDiversityNet()

        os.makedirs(self.MODEL_DIR, exist_ok=True)
        self._try_load_models()
        print("[TinyNN] Wszystkie modele zainicjalizowane!")

    def _try_load_models(self):
        paths = {
            'chord': os.path.join(self.MODEL_DIR, 'chord_net.npz'),
            'melody': os.path.join(self.MODEL_DIR, 'melody_net.npz'),
            'triad': os.path.join(self.MODEL_DIR, 'triad_net.npz'),
            'diversity': os.path.join(self.MODEL_DIR, 'diversity_net.npz'),
        }
        for name, path in paths.items():
            if os.path.exists(path):
                getattr(self, f'{name}_net').load(path)
                print(f"[TinyNN] Wczytano {name}_net")
            else:
                print(f"[TinyNN] Losowe wagi dla {name}_net")

    def save_models(self):
        self.chord_net.save(os.path.join(self.MODEL_DIR, 'chord_net.npz'))
        self.melody_net.save(os.path.join(self.MODEL_DIR, 'melody_net.npz'))
        self.triad_net.save(os.path.join(self.MODEL_DIR, 'triad_net.npz'))
        self.diversity_net.save(os.path.join(self.MODEL_DIR, 'diversity_net.npz'))
        print("[TinyNN] Modele zapisane!")

    def _emotions_to_vector(self, metrics: dict) -> np.ndarray:
        from union_config import UnionConfig
        return np.array([metrics.get(axis, 0.0) for axis in UnionConfig.AXES], dtype=np.float32)

    def predict_next_chord(self, metrics: dict, prev_chord_idx: int) -> int:
        emotions = self._emotions_to_vector(metrics)
        prev_onehot = np.zeros(8)
        prev_onehot[prev_chord_idx] = 1.0

        logits = self.chord_net.forward(emotions, prev_onehot)

        chaos = metrics.get('chaos', 0.0)
        kreacja = metrics.get('kreacja', 0.0)
        temperature = 0.8 + 0.8 * (chaos / 9.0) + 0.4 * (kreacja / 9.0)

        probs = softmax(logits, temperature)
        return np.random.choice(8, p=probs)

    def predict_next_note(self, metrics: dict, prev_note_idx: int) -> int:
        emotions = self._emotions_to_vector(metrics)
        prev_onehot = np.zeros(12)
        prev_onehot[prev_note_idx] = 1.0

        logits = self.melody_net.forward(emotions, prev_onehot)

        chaos = metrics.get('chaos', 0.0)
        kreacja = metrics.get('kreacja', 0.0)
        temperature = 0.8 + 0.8 * (chaos / 9.0) + 0.4 * (kreacja / 9.0)

        probs = softmax(logits, temperature)
        return np.random.choice(12, p=probs)

    def calculate_diversity_factor(self, metrics: dict) -> float:
        emotions = self._emotions_to_vector(metrics)
        return float(self.diversity_net.forward(emotions))
