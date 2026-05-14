# production_music_system.py
# -*- coding: utf-8 -*-
"""
PRODUKCYJNA INTEGRACJA - System Muzyczny EriAmo
Soul Composer v8.1 + Tiny NN + Menuet Generator + Mechanizm RL + QUANTUM
"""

import os
import sys
import time
import numpy as np
from typing import Dict, Optional, List, Tuple
from datetime import datetime

try:
    from aii import AII
    print("[MUSIC-SYSTEM] ✓ Zaimportowano AII")
except ImportError:
    print("[ERROR] Brak modułu 'aii'.")
    sys.exit(1)

try:
    from soul_composer import SoulComposerV8
    print("[MUSIC-SYSTEM] ✓ Zaimportowano SoulComposerV8")
except ImportError:
    print("[ERROR] Brak modułu 'soul_composer'")
    sys.exit(1)

try:
    from union_config import UnionConfig, Colors
    print("[MUSIC-SYSTEM] ✓ Zaimportowano UnionConfig")
except ImportError:
    class Colors:
        MAGENTA = "\033[35m"; CYAN = "\033[36m"; RESET = "\033[0m"
        YELLOW = "\033[33m"; GREEN = "\033[32m"; RED = "\033[31m"

try:
    from soul_composer_tiny_nn import SoulComposerTinyNN
    NN_AVAILABLE = True
    print("[MUSIC-SYSTEM] ✓ Zaimportowano TinyNN")
except ImportError:
    NN_AVAILABLE = False
    print("[MUSIC-SYSTEM] ⚠ TinyNN niedostępne")

try:
    from menuet_generator_enhanced import MenuetGeneratorEnhanced
    MENUET_AVAILABLE = True
    print("[MUSIC-SYSTEM] ✓ Zaimportowano MenuetGenerator")
except ImportError:
    MENUET_AVAILABLE = False
    print("[MUSIC-SYSTEM] ⚠ MenuetGenerator niedostępny")


class CompositionEvaluator:
    def __init__(self):
        self.evaluation_history = []
    
    def evaluate_composition(self, composition: dict, metrics: dict, composition_type: str = "generic") -> dict:
        scores = {}
        scores['structural_coherence'] = self._evaluate_structure(composition)
        scores['melodic_diversity'] = self._evaluate_melody_diversity(composition)
        scores['emotional_match'] = self._evaluate_emotional_match(composition, metrics)
        scores['complexity'] = self._evaluate_complexity(composition, metrics)
        
        if composition_type == "menuet":
            scores['menuet_style'] = self._evaluate_menuet_style(composition)
            weights = {'structural_coherence': 0.3, 'melodic_diversity': 0.2, 'emotional_match': 0.2, 'complexity': 0.1, 'menuet_style': 0.2}
        else:
            weights = {'structural_coherence': 0.25, 'melodic_diversity': 0.3, 'emotional_match': 0.3, 'complexity': 0.15}
        
        reward = sum(scores.get(k, 0) * weights[k] for k in weights)
        feedback = self._generate_feedback(scores, reward)
        
        evaluation = {
            'timestamp': datetime.now().isoformat(), 'type': composition_type,
            'reward': reward, 'scores': scores, 'feedback': feedback
        }
        self.evaluation_history.append(evaluation)
        return evaluation
    
    def _evaluate_structure(self, composition: dict) -> float:
        melody, harmony = composition.get('melody', []), composition.get('harmony', [])
        if not melody or not harmony or len(melody) != len(harmony): return 0.3
        score = 0.5
        if len(melody) in [8, 16, 32, 64]: score += 0.3
        if len(melody) >= 16: score += 0.2
        return min(1.0, score)
    
    def _evaluate_melody_diversity(self, composition: dict) -> float:
        melody = composition.get('melody', [])
        if not melody: return 0.3
        all_pitches = [n.get('pitch', 60) for m in melody for n in m if n.get('type') == 'note']
        if len(all_pitches) < 2: return 0.3
        pitch_diversity = min(1.0, len(set(all_pitches)) / 12.0)
        range_score = min(1.0, (max(all_pitches) - min(all_pitches)) / 24.0)
        changes = [abs(all_pitches[i+1] - all_pitches[i]) for i in range(len(all_pitches)-1)]
        contour_score = min(1.0, (np.mean(changes) if changes else 0) / 5.0)
        return pitch_diversity * 0.4 + range_score * 0.3 + contour_score * 0.3
    
    def _evaluate_emotional_match(self, composition: dict, metrics: dict) -> float:
        return 0.6  # Uproszczone dla brevity, pełna logika ujęta w architekturze
    
    def _evaluate_complexity(self, composition: dict, metrics: dict) -> float:
        return 0.5 + (0.2 if metrics.get('kreacja', 0) > 0.7 else 0)
    
    def _evaluate_menuet_style(self, composition: dict) -> float:
        melody = composition.get('melody', [])
        score = 0.5
        if len(melody) in [16, 32, 64]: score += 0.3
        measure_totals = [sum(n.get('duration', 0) for n in m) for m in melody]
        if measure_totals and 2.5 <= np.mean(measure_totals) <= 3.5: score += 0.2
        return min(1.0, score)
    
    def _generate_feedback(self, scores: dict, reward: float) -> str:
        quality = "Doskonała" if reward > 0.8 else ("Dobra" if reward > 0.6 else ("Przeciętna" if reward > 0.4 else "Słaba"))
        return f"{quality} kompozycja (reward: {reward:.3f})."

class ProductionMusicSystem:
    def __init__(self, aii_instance, logger=None):
        print(f"\n{Colors.CYAN}{'='*70}\nINICJALIZACJA PRODUKCYJNEGO SYSTEMU MUZYCZNEGO (QRM Ready)\n{'='*70}{Colors.RESET}\n")
        self.aii = aii_instance
        self.logger = logger
        
        print("[1/4] Inicjalizacja SoulComposer...")
        self.composer = SoulComposerV8(self.aii, logger) if hasattr(sys.modules[__name__], 'SoulComposerV8') else None
        
        print("[2/4] Inicjalizacja Neural Networks...")
        self.nn = SoulComposerTinyNN() if NN_AVAILABLE else None
        
        print("[3/4] Inicjalizacja Menuet Generator...")
        self.menuet_gen = MenuetGeneratorEnhanced(self.composer, self.nn) if MENUET_AVAILABLE else None
        
        print("[4/4] Inicjalizacja Evaluator...")
        self.evaluator = CompositionEvaluator()
        print(f"\n{Colors.GREEN}✓ System gotowy!{Colors.RESET}\n")
    
    def compose_menuet(self, key='C', minor=False, use_nn=True) -> dict:
        if not self.menuet_gen:
            print(f"{Colors.RED}[ERROR] Menuet Generator niedostępny{Colors.RESET}")
            return {'error': 'MenuetGenerator not available'}
            
        print(f"\n{Colors.CYAN}{'='*70}\nKOMPONOWANIE MENUETU ({key} {'moll' if minor else 'dur'})\n{'='*70}{Colors.RESET}\n")
        
        # Pobierz klasyczne emocje
        if hasattr(self.aii, 'get_emotions'):
            metrics = self.aii.get_emotions()
        else:
            metrics = {ax: float(self.aii.context_vector[i]) for i, ax in enumerate(getattr(self.aii, 'AXES_ORDER', []))}
        
        # POBIERZ FIZYKĘ KWANTOWĄ Z RDZENIA
        quantum_state = {'vacuum': 0.0, 'coherence': 1.0}
        if hasattr(self.aii, 'quantum') and self.aii.quantum:
            vacuum_amp = self.aii.quantum.state.amplitudes.get('vacuum', 0j)
            quantum_state['vacuum'] = abs(vacuum_amp)**2
            quantum_state['coherence'] = self.aii.quantum.get_phase_coherence()
            
        dominant = max(metrics.items(), key=lambda x: x[1]) if metrics else ("neutralny", 0)
        print(f"[EMOCJE] Dominanta: {dominant[0].upper()} ({dominant[1]:.2f})")
        print(f"[QUANTUM] Vacuum: {quantum_state['vacuum']:.2f} | Coherence: {quantum_state['coherence']:.2f}")
        
        composition = self.menuet_gen.generate_full_menuet(
            metrics=metrics,
            quantum_state=quantum_state,
            use_nn_variations=use_nn,
            key=key,
            minor=minor
        )
        
        print(f"\n{Colors.MAGENTA}[RL] Ocena kompozycji...{Colors.RESET}")
        evaluation = self.evaluator.evaluate_composition(composition, metrics, composition_type='menuet')
        reward = evaluation['reward']
        print(f"{Colors.MAGENTA}[RL] Reward: {reward:.3f} | {evaluation['feedback']}{Colors.RESET}")
        
        memory_id = f"Menuet_Q_{key}{'m' if minor else ''}_{int(time.time())}"
        
        if hasattr(self.aii, 'D_Map'):
            self.aii.D_Map[memory_id] = {
                "tresc": f"Kwantowy Menuet {key} {'moll' if minor else 'dur'} (reward: {reward:.3f})",
                "wektor_C_Def": self.aii.context_vector.tolist() if hasattr(self.aii, 'context_vector') else [],
                "_type": "@MUSIC",
                "weight": reward,  
                "time": time.time(),
                "metadata": {"genre": "menuet", "quantum": quantum_state, "evaluation": evaluation}
            }
            self.aii.last_winner_id = memory_id
            if hasattr(self.aii, 'save'): self.aii.save()
        
        return {'composition': composition, 'evaluation': evaluation, 'memory_id': memory_id, 'metrics': metrics}
    
    def compose_freestyle(self, genre='generic', bars=8, use_nn=True) -> dict:
        print(f"\n{Colors.CYAN}{'='*70}\nKOMPONOWANIE FREESTYLE ({genre.upper()})\n{'='*70}{Colors.RESET}\n")
        
        metrics = self.aii.get_emotions() if hasattr(self.aii, 'get_emotions') else {}
        paths = self.composer.compose_new_work(genre) if self.composer else []
        
        pseudo_reward = 0.5 + (0.1 if metrics.get('logika', 0) > 0.7 else 0) + (0.15 if metrics.get('kreacja', 0) > 0.6 else 0)
        evaluation = {
            'timestamp': datetime.now().isoformat(), 'type': 'freestyle',
            'reward': pseudo_reward, 'scores': {'estimated': pseudo_reward},
            'feedback': f"Utwór {genre} wygenerowany."
        }
        
        print(f"\n{Colors.MAGENTA}[RL] Szacowany reward: {pseudo_reward:.3f}{Colors.RESET}")
        memory_id = f"Freestyle_{genre}_{int(time.time())}"
        
        if hasattr(self.aii, 'D_Map'):
            self.aii.D_Map[memory_id] = {
                "tresc": f"Freestyle {genre} (reward: {pseudo_reward:.3f})",
                "wektor_C_Def": self.aii.context_vector.tolist() if hasattr(self.aii, 'context_vector') else [],
                "_type": "@MUSIC",
                "weight": pseudo_reward,
                "time": time.time(),
                "metadata": {"genre": genre, "paths": paths, "evaluation": evaluation}
            }
            if hasattr(self.aii, 'save'): self.aii.save()
            
        return {'paths': paths, 'evaluation': evaluation, 'memory_id': memory_id, 'metrics': metrics}

    def get_rl_statistics(self) -> dict:
        if not hasattr(self.aii, 'D_Map'): return {'count': 0, 'avg_reward': 0, 'max_reward': 0, 'min_reward': 0}
        music_entries = {k: v for k, v in self.aii.D_Map.items() if v.get('_type') == '@MUSIC'}
        if not music_entries: return {'count': 0, 'avg_reward': 0, 'max_reward': 0, 'min_reward': 0}
        rewards = [e.get('weight', 0.5) for e in music_entries.values()]
        return {'count': len(music_entries), 'avg_reward': np.mean(rewards), 'max_reward': np.max(rewards), 'min_reward': np.min(rewards)}

if __name__ == "__main__":
    # Test stub dla Production System
    class DummyAII:
        context_vector = np.array([0]*15)
        AXES_ORDER = ['radość', 'smutek']
        D_Map = {}
        def get_emotions(self): return {'logika': 0.8, 'smutek': 0.1}
        class DummyQuantum:
            class State: amplitudes = {'vacuum': np.sqrt(0.8) * np.exp(1j * 0)}
            def get_phase_coherence(self): return 0.2
        quantum = DummyQuantum()
        
    print("TEST: Uruchamianie Produkcyjnego Systemu Muzycznego (z atrapą rdzenia).")
    sys = ProductionMusicSystem(DummyAII())
    if sys.menuet_gen:
        res = sys.compose_menuet(use_nn=False)
        print("Menuet testowy zakończony.")