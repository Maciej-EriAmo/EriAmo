# eriamo/quantum_emotions.py

import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Tuple
import json

@dataclass
class EmotionalAmplitude:
    """
    Pojedyncza emocja jako amplituda kwantowa
    
    amplitude: liczba zespolona (magnitude + phase)
    |amplitude|² = prawdopodobieństwo
    arg(amplitude) = faza (interference)
    """
    name: str
    amplitude: complex
    
    @property
    def probability(self) -> float:
        """Prawdopodobieństwo tej emocji"""
        return abs(self.amplitude) ** 2
    
    @property
    def magnitude(self) -> float:
        """Siła emocji (bez fazy)"""
        return abs(self.amplitude)
    
    @property
    def phase(self) -> float:
        """Faza [0, 2π) - wpływa na interference"""
        return np.angle(self.amplitude)
    
    def __repr__(self):
        return f"{self.name}: {self.magnitude:.3f}∠{np.degrees(self.phase):.1f}°"


class QuantumEmotionalState:
    """
    15-wymiarowy Reality Sphere jako quantum state
    
    |Ψ⟩ = Σ α_i e^(iφ_i) |emotion_i⟩
    """
    
    DIMENSIONS = [
        # Plutchik's 8
        'joy', 'trust', 'fear', 'surprise',
        'sadness', 'disgust', 'anger', 'anticipation',
        # Metaphysical 7
        'logic', 'knowledge', 'time', 'creation',
        'being', 'space', 'chaos',
        # Wewnętrzny wymiar QuantumBridge — energia rozpadów emocjonalnych.
        # Obecny w DIMENSIONS aby emotional_interference nie rzucało KeyError.
        # Niewidoczny dla AII: sync_to_aii pomija vacuum przy zapisie do context_vector.
        'vacuum'
    ]
    
    def __init__(self):
        """Initialize w równej superpozycji (vacuum startuje od zera)"""
        n = len(self.DIMENSIONS)
        # Superpozycja bez vacuum — vacuum akumuluje energię dopiero przez rozpad
        uniform_amplitude = 1.0 / np.sqrt(n - 1)
        
        self.amplitudes: Dict[str, complex] = {
            dim: (0.0 + 0j) if dim == 'vacuum'
            else uniform_amplitude * np.exp(1j * np.random.uniform(0, 2*np.pi))
            for dim in self.DIMENSIONS
        }
        
    def normalize(self):
        """Ensure Σ|α|² = 1 (kwantowy warunek)"""
        total_prob = sum(abs(amp)**2 for amp in self.amplitudes.values())
        norm_factor = np.sqrt(total_prob)
        
        if norm_factor > 1e-10:  # Avoid division by zero
            self.amplitudes = {
                dim: amp / norm_factor
                for dim, amp in self.amplitudes.items()
            }
    
    def set_emotion(self, emotion: str, magnitude: float, phase: float = 0.0):
        """
        Ustaw konkretną emocję
        
        Args:
            emotion: nazwa emocji
            magnitude: siła [0, 1]
            phase: faza w radianach [0, 2π]
        """
        if emotion not in self.DIMENSIONS:
            raise ValueError(f"Unknown emotion: {emotion}")
        
        self.amplitudes[emotion] = magnitude * np.exp(1j * phase)
        self.normalize()
    
    def get_probabilities(self) -> Dict[str, float]:
        """Zwróć rozkład prawdopodobieństwa"""
        return {
            dim: abs(amp)**2
            for dim, amp in self.amplitudes.items()
        }
    
    def measure(self) -> str:
        """
        Kwantowy pomiar - kolaps do jednej emocji
        
        Returns:
            Wybrana emocja (probabilistycznie)
        """
        probs = self.get_probabilities()
        emotions = list(probs.keys())
        probabilities = list(probs.values())
        
        # Probabilistic choice
        chosen = np.random.choice(emotions, p=probabilities)
        
        # KOLAPS: po pomiarze stan się zmienia
        # (opcjonalnie - możesz to wyłączyć dla non-destructive measurement)
        # self.collapse_to(chosen)
        
        return chosen
    
    def collapse_to(self, emotion: str):
        """Kolaps funkcji falowej do jednej emocji"""
        self.amplitudes = {
            dim: 1.0 if dim == emotion else 0.0
            for dim in self.DIMENSIONS
        }
    
    def dominant_emotion(self) -> Tuple[str, float]:
        """Najsilniejsza emocja (bez kolapsu)"""
        probs = self.get_probabilities()
        emotion = max(probs.items(), key=lambda x: x[1])
        return emotion
    
    def entropy(self) -> float:
        """
        Shannon entropy - miara niepewności
        
        H = -Σ p_i log(p_i)
        
        High entropy = confused/uncertain
        Low entropy = clear emotional state
        """
        probs = self.get_probabilities()
        # Avoid log(0)
        entropy = -sum(
            p * np.log2(p) if p > 1e-10 else 0
            for p in probs.values()
        )
        return entropy
    
    def __repr__(self):
        probs = self.get_probabilities()
        top_3 = sorted(probs.items(), key=lambda x: x[1], reverse=True)[:3]
        return f"Emotional State: {', '.join(f'{e}={p:.2%}' for e, p in top_3)}"