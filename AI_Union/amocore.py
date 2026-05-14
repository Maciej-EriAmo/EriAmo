# amocore_v596.py
# -*- coding: utf-8 -*-
"""
System Ontologicznej Pamięci Muzyki v5.9.6
- NOWE v5.9.6: Wprowadzono autouważność (self-awareness) w MusicMemory:
  - Nowa metoda _self_reflect(): Wywoływana po każdym śnie, analizuje D_Map
    i H_log, loguje dominujące wzorce, dostosowuje sleep_interval na podstawie
    'chaos' w EriAmoCore (jeśli dostępny).
  - Integracja z EriAmoCore: _self_reflect() pobiera emocje z core (jeśli podany).
- FIX v5.9.6: _extract_pattern_key() — dodano więcej features (pitch_variance,
  syncopation_feel) dla bogatszych kluczy wzorców.
- CLEANUP v5.9.6: Usunięto martwy kod w apply_time_based_decay() — teraz
  implementuje prosty decay na H_log (starsze wpisy tracą wagę).

"""
import numpy as np
import threading
import time
import csv
import os
import hashlib
import json
import math
from dataclasses import dataclass, field
from datetime import datetime
import pandas as pd

# =============================================================================
# DEFINICJA ONTOLOGICZNA: 9 WEKTORÓW DUSZY
# =============================================================================

# OSIE importowane z union_config.py (Single Source of Truth)
# System używa teraz ujednoliconego modelu 15 osi
from union_config import AXES_LIST, EPHEMERAL_AXES, PERSISTENT_AXES, DIMENSION
ONTOLOGICAL_THRESHOLD = 0.98

# =============================================================================
# SYSTEM SNU (MusicMemory)
# =============================================================================
class MusicMemory:
    DATA_DIR = "data"
    H_LOG_PATH = "data/music_experience.json"
    D_MAP_PATH = "data/music_patterns.json"
    
    MUSICAL_FEATURES = [
        'repetition_density', 'leap_ratio', 'rhythmic_regularity', 'pitch_variance',
        'note_density', 'interval_avg', 'dominant_pitch_class', 'syncopation_feel',
        'pitch_range', 'second_pitch_class', 'chromatic_density', 'key_tonic', 'key_mode'
    ]
    
    def __init__(self, sleep_interval: float = 300.0, core=None):
        self.core = core  # NOWE: Referencja do EriAmoCore dla autouważności
        os.makedirs(self.DATA_DIR, exist_ok=True)
        self.H_log = []
        self.D_Map = {}
        self.sleep_interval = sleep_interval
        self.running = True
        self._lock = threading.RLock()
        self.is_sleeping = False
        self.last_sleep_time = time.time()
        self.sleep_count = 0
        self.experiences_since_sleep = 0
        self._load_memory()
        self._start_sleep_cycle()
        print(f"\033[96m[MEMORY] MusicMemory aktywna. Sen co {sleep_interval/60:.1f} min.\033[0m")
    
    def _load_memory(self):
        try:
            if os.path.exists(self.H_LOG_PATH):
                with open(self.H_LOG_PATH, 'r', encoding='utf-8') as f: self.H_log = json.load(f)
        except: self.H_log = []
        try:
            if os.path.exists(self.D_MAP_PATH):
                with open(self.D_MAP_PATH, 'r', encoding='utf-8') as f: self.D_Map = json.load(f)
        except: self.D_Map = {}
    
    def _save_memory(self):
        try:
            with open(self.H_LOG_PATH, 'w', encoding='utf-8') as f:
                json.dump(self.H_log[-1000:], f, indent=2, ensure_ascii=False)
            with open(self.D_MAP_PATH, 'w', encoding='utf-8') as f:
                json.dump(self.D_Map, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"\033[91m[MEMORY] Błąd zapisu: {e}\033[0m")
    
    def _start_sleep_cycle(self):
        def cycle():
            while self.running:
                time.sleep(self.sleep_interval)
                if not self.running: break
                self._sleep()
        threading.Thread(target=cycle, daemon=True).start()
    
    def _sleep(self):
        with self._lock:
            if self.is_sleeping:
                return
            self.is_sleeping = True
        # Snapshot H_log pod lockiem, konsolidacja na kopii
        with self._lock:
            recent = list(self.H_log[-20:])
        for exp in recent:
            key = self._extract_pattern_key(exp)
            with self._lock:
                if key in self.D_Map:
                    self.D_Map[key]['weight'] = min(self.D_Map[key]['weight'] + 1.0, 100.0)
                else:
                    self.D_Map[key] = {
                        'features': exp.get('features', {}),
                        'weight': 1.0,
                        'created_at': datetime.now().isoformat()
                    }
        self._save_memory()
        with self._lock:
            self.last_sleep_time = time.time()
            self.experiences_since_sleep = 0
            self.is_sleeping = False
        print(f"\033[92m[MEMORY] Sen zakończony. Wzorców: {len(self.D_Map)}\033[0m")
        
        # NOWE: Autouważność po śnie
        self._self_reflect()
    
    def _self_reflect(self):
        """
        Mechanizm autouważności: Analizuje D_Map i H_log, loguje dominujące
        wzorce, dostosowuje sleep_interval na podstawie 'chaos' z core.
        """
        if not self.D_Map:
            print("\033[93m[REFLECT] Pamięć pusta — brak wzorców do analizy.\033[0m")
            return
        
        # Analiza dominujących wzorców
        dominant_pattern = max(self.D_Map.items(), key=lambda x: x[1]['weight'])[0]
        reflection = f"[SELF-REFLECT] Dominujący wzorzec: {dominant_pattern} (waga: {self.D_Map[dominant_pattern]['weight']:.2f}). "
        
        # Dostosowanie na podstawie emocji z core (jeśli dostępny)
        if self.core:
            emotions = self.core.get_emotions()
            chaos = emotions.get('chaos', 0)
            if chaos > 0.5:
                self.sleep_interval = max(60, self.sleep_interval - 30)
                reflection += "Zwiększam częstotliwość snu (chaos ↑)."
            elif chaos < 0.2:
                self.sleep_interval = min(600, self.sleep_interval + 60)
                reflection += "Zmniejszam częstotliwość snu (stabilność ↑)."
            else:
                reflection += "Stan zrównoważony."
        
        print(f"\033[94m{reflection}\033[0m")
    
    def _extract_pattern_key(self, exp):
        feat = exp.get('features', {})
        parts = []
        for k in ['repetition_density', 'rhythmic_regularity', 'pitch_variance', 'syncopation_feel']:
            val = feat.get(k, 0.5)
            cat = 'H' if val > 0.66 else ('L' if val < 0.33 else 'M')
            parts.append(f"{k[:3]}:{cat}")
        return "|".join(parts)

    def record_experience(self, features: dict, source: str = "analysis"):
        with self._lock:
            self.H_log.append({
                'timestamp': datetime.now().isoformat(),
                'features': features,
                'source': source
            })
            self.experiences_since_sleep += 1
            trigger_sleep = self.experiences_since_sleep > 10
        # _sleep() poza lockiem — sam bierze locka wewnętrznie
        if trigger_sleep:
            self._sleep()

    def get_consolidated_style(self) -> dict:
        if not self.D_Map: return {f: 0.5 for f in self.MUSICAL_FEATURES}
        sums = {f: 0.0 for f in self.MUSICAL_FEATURES}
        total_w = 0
        for p in self.D_Map.values():
            w = p['weight']
            total_w += w
            for f, v in p.get('features', {}).items():
                if f in sums: sums[f] += v * w
        return {f: (v / total_w if total_w else 0.5) for f, v in sums.items()}
    
    def get_recent_style(self) -> dict:
        if not self.H_log: return {f: 0.5 for f in self.MUSICAL_FEATURES}
        recent = self.H_log[-5:]
        avg = {f: 0.0 for f in self.MUSICAL_FEATURES}
        for exp in recent:
            for feat, val in exp.get('features', {}).items():
                if feat in avg: avg[feat] += val / len(recent)
        return avg

    def get_blended_style(self, recent_weight: float = 0.3) -> dict:
        recent = self.get_recent_style()
        consolidated = self.get_consolidated_style()
        blended = {}
        for feat in self.MUSICAL_FEATURES:
            blended[feat] = recent_weight * recent.get(feat, 0.5) + (1 - recent_weight) * consolidated.get(feat, 0.5)
        return blended

    def shutdown(self):
        self.running = False
        self._save_memory()
        print(f"\033[93m[MEMORY] Pamięć zapisana. Dobranoc.\033[0m")

    def apply_time_based_decay(self):
        """
        CLEANUP v5.9.6: Implementacja decay — starsze wpisy w H_log tracą wagę.
        """
        with self._lock:
            current_time = time.time()
            for entry in self.H_log:
                age = current_time - entry.get('timestamp', current_time)
                decay_factor = math.exp(-age / (3600 * 24))  # Decay dzienny
                entry['weight'] = entry.get('weight', 1.0) * decay_factor


_music_memory = None
_music_memory_lock = threading.Lock()
def get_music_memory(core=None) -> MusicMemory:
    global _music_memory
    with _music_memory_lock:
        if _music_memory is None:
            _music_memory = MusicMemory(core=core)
    return _music_memory


# =============================================================================
# ETYKA I LOGGER
# =============================================================================
ETHICS_FRAMEWORK = {
    "integrity": {"value": 1.0, "immutable": True},
    "respect": {"value": 1.0, "immutable": True},
    "authenticity": {"value": 1.0, "immutable": True},
    "harmony": {"value": 1.0, "immutable": True}
}

@dataclass
class SoulVector:
    values: np.ndarray
    timestamp: float = field(default_factory=time.time)

class SoulStateLogger:
    FILE_PATH = "data/soul_history.csv"
    HEADER = ["timestamp", "id_event", "description", "mode", "cos_alpha", "compression", "emotion_msg"] + \
             [f"S_{axis}" for axis in AXES_LIST] + [f"F_{axis}" for axis in AXES_LIST]

    def __init__(self):
        os.makedirs("data", exist_ok=True)
        self.lock = threading.RLock()
        self.event_counter = 0
        self._init_file()

    def _init_file(self):
        with self.lock:
            if not os.path.exists(self.FILE_PATH):
                with open(self.FILE_PATH, 'w', newline='', encoding='utf-8') as f:
                    csv.writer(f).writerow(self.HEADER)

    def log_state(self, core, F_vector, cos_alpha, emotion_msg, description, mode, compressed=False):
        with self.lock:
            self.event_counter += 1
            row = [datetime.now().isoformat(), self.event_counter, description, mode, 
                   f"{cos_alpha:.4f}", "YES" if compressed else "NO", emotion_msg] + \
                  core.get_vector_copy().tolist() + F_vector.tolist()
            try:
                with open(self.FILE_PATH, 'a', newline='', encoding='utf-8') as f:
                    csv.writer(f).writerow(row)
            except: pass


# =============================================================================
# RDZEŃ (EriAmoCore)
# =============================================================================
class EriAmoCore:
    AXES = AXES_LIST
    HISTORY_PATH = "data/soul_history.csv"
    
    def __init__(self):
        self.lock = threading.RLock()
        self.vector = SoulVector(np.zeros(len(self.AXES), dtype=float))
        self.last_decay_time = time.time()
        self.decay_cycle_count = 0
        self.ethics = ETHICS_FRAMEWORK.copy()
        
        if not self.load_soul_from_history():
            self.vector.values[self.AXES.index('wiedza')] = 5.0
            self.vector.values[self.AXES.index('kreacja')] = 10.0
            print("[CORE] Narodziny nowej Duszy.")

    def load_soul_from_history(self) -> bool:
        if not os.path.exists(self.HISTORY_PATH): return False
        try:
            df = pd.read_csv(self.HISTORY_PATH)
            if df.empty: return False
            last_row = df.iloc[-1]
            new_vals = []
            for axis in self.AXES:
                col = f"S_{axis}"
                val = float(last_row[col]) if col in last_row else 0.0
                new_vals.append(val)
            self.vector.values = np.array(new_vals)
            return True
        except: return False

    def get_vector_copy(self) -> np.ndarray:
        with self.lock: return self.vector.values.copy()

    def shift_axis(self, axis: str, action: str, value: float) -> bool:
        with self.lock:
            if axis not in self.AXES: return False
            i = self.AXES.index(axis)
            if action == "INCREMENT": self.vector.values[i] += value
            elif action == "SET": self.vector.values[i] = value
            elif action == "DECAY": self.vector.values[i] *= (1.0 - value)
            return True

    def compute_integrity_hash(self) -> str:
        with self.lock:
            data_str = "|".join([f"{x:.8f}" for x in self.vector.values]) + "".join(self.AXES)
            ethics_str = "|".join([f"{k}:{v['value']}" for k, v in self.ethics.items()])
            full_data = data_str + "|ETHICS|" + ethics_str
            return hashlib.sha256(full_data.encode('utf-8')).hexdigest()

    def create_memory_dump(self, filename: str = None) -> str:
        os.makedirs("data/dumps", exist_ok=True)
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"soul_dump_{timestamp}.soul"
        filepath = f"data/dumps/{filename}"
        
        with self.lock:
            dump_data = {
                "meta": {
                    "version": "5.9.4",
                    "created_at": datetime.now().isoformat(),
                    "integrity_hash": self.compute_integrity_hash(),
                },
                "soul_vector": {axis: float(self.vector.values[i]) for i, axis in enumerate(self.AXES)},
                "ethics_framework": {k: v["value"] for k, v in self.ethics.items()}
            }
            
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(dump_data, f, indent=2, ensure_ascii=False)
        return filepath
        
    def apply_time_based_decay(self):
        """
        CLEANUP v5.9.6: Implementacja decay — ephemeral axes tracą 5% co cykl.
        """
        with self.lock:
            for axis in EPHEMERAL_AXES:
                if axis in self.AXES:
                    i = self.AXES.index(axis)
                    self.vector.values[i] *= 0.95
            self.last_decay_time = time.time()
            self.decay_cycle_count += 1


# =============================================================================
# HELPER FUNCTIONS (BRAKUJĄCE WCZEŚNIEJ!)
# =============================================================================

def interpret_improv_for_composition(improv_value: float) -> dict:
    """Interpretuje wartość osi improwizacji dla kompozytora."""
    normalized = (improv_value + 100) / 200  # -100→0, +100→1
    normalized = max(0, min(1, normalized))
    
    # FIX: Upewniono się, że słownik jest poprawnie zamknięty
    return {
        "freedom_level": normalized,
        "allow_chromatic": normalized > 0.4,
        "allow_modal_interchange": normalized > 0.5,
        "allow_unexpected_modulation": normalized > 0.6,
        "extended_chords_probability": normalized * 0.8,
        "syncopation_probability": normalized * 0.6,
        "rubato_allowed": normalized > 0.3,
        "ornamentation_density": normalized,
        "allow_large_leaps": normalized > 0.5
    }

# =============================================================================
# CURIOSITY ENGINE (TEŻ BRAKOWAŁO)
# =============================================================================

class CuriosityEngine:
    WEIGHT_KREACJA = 0.40
    WEIGHT_WIEDZA = 0.30
    WEIGHT_EMOCJE = 0.30
    WIEDZA_OPTIMUM = 50.0
    WIEDZA_SPREAD = 40.0

    def __init__(self):
        pass

    def compute_curiosity(self, kreacja: float, wiedza: float, emocje: float) -> dict:
        kreacja_component = self._normalize(kreacja) * 100
        wiedza_norm = self._normalize(wiedza) * 100
        wiedza_diff = abs(wiedza_norm - self.WIEDZA_OPTIMUM)
        wiedza_component = 100 * math.exp(-(wiedza_diff ** 2) / (2 * self.WIEDZA_SPREAD ** 2))
        emocje_component = min(100, abs(emocje) * 2)
        
        base_curiosity = (
            self.WEIGHT_KREACJA * kreacja_component +
            self.WEIGHT_WIEDZA * wiedza_component +
            self.WEIGHT_EMOCJE * emocje_component
        )
        
        final_curiosity = (base_curiosity - 50) * 2
        final_curiosity = max(-100, min(100, final_curiosity))
        
        return {'value': final_curiosity}
    
    def _normalize(self, value: float) -> float:
        return max(0, min(1, (value + 100) / 200))

_curiosity_engine = None
_curiosity_engine_lock = threading.Lock()
def get_curiosity_engine() -> CuriosityEngine:
    global _curiosity_engine
    with _curiosity_engine_lock:
        if _curiosity_engine is None:
            _curiosity_engine = CuriosityEngine()
    return _curiosity_engine