# -*- coding: utf-8 -*-
"""
quantum_bridge.py v2.4.3 (QRM & Time Evolved)
Most między AII (wektory realne 15D) a systemem kwantowym (amplitudy zespolone).

Łączy:
  - AII.context_vector (np.float32[15], wartości [0,1])
  - QuantumEmotionalState (complex amplitudes z fazą)
  - Świadomość Czasu (Pustka / Vacuum, Dekoherencja QRM)

ZMIANY v2.4.3:
- FIX: vacuum przeniesiony do QuantumEmotionalState.DIMENSIONS w quantum_emotions.py
  (emotional_interference nie rzuca już KeyError — vacuum znany każdemu nowemu obiektowi)
- CLEANUP: usunięto ręczny guard vacuum z __init__ (już niepotrzebny)

ZMIANY v2.4.2:
- DODANO: fixed_trajectory — blokuje pętlę inercji (stan⟷predykcja)
- DODANO: to_dict_qrm / from_dict_qrm — aliasy dla union.py

ZMIANY v2.4.1:
- FIX: process_interference — vacuum znikał po każdym wywołaniu apply_interference
  które zwraca nowy obiekt QuantumEmotionalState bez wewnętrznego wymiaru vacuum.
  Teraz vacuum jest zachowany przed zastąpieniem obiektu i przywrócony po.

ZMIANY v2.4.0:
- FIX: list(PL_TO_EN.keys()) wywoływane w każdej iteracji każdej metody
  → stała modułu PL_NAMES, zero alokacji w hot path
- FIX: rank_candidates — walidacja długości wektora wektor_C_Def
  przez _aii._validate_mem_vec gdy dostępne
- BUMP: numeracja v1.1.0 → v2.4.0 dla zachowania ciągłości historii
  (v2.3.0 = BLEND redesign, v2.4.0 = QRM evolution + fixes)

Autor: Maciek (GitHub: Maciej615) & Gemini
"""

import numpy as np
import time
import math
from typing import Dict, List, Tuple, Optional

from quantum_emotions import QuantumEmotionalState
from emotional_interference import EmotionalInterference
from decision_maker import QuantumDecisionMaker


# ═══════════════════════════════════════════════════════════════════════════════
# MAPOWANIE OSI: POLSKI ↔ ANGIELSKI
# ═══════════════════════════════════════════════════════════════════════════════

PL_TO_EN: Dict[str, str] = {
    'radość':      'joy',           # 0
    'smutek':      'sadness',       # 1
    'strach':      'fear',          # 2
    'gniew':       'anger',         # 3
    'miłość':      'trust',         # 4
    'wstręt':      'disgust',       # 5
    'zaskoczenie': 'surprise',      # 6
    'akceptacja':  'anticipation',  # 7
    'logika':      'logic',         # 8
    'wiedza':      'knowledge',     # 9
    'czas':        'time',          # 10
    'kreacja':     'creation',      # 11
    'byt':         'being',         # 12
    'przestrzeń':  'space',         # 13
    'chaos':       'chaos',         # 14
}

EN_TO_PL: Dict[str, str] = {v: k for k, v in PL_TO_EN.items()}

# FIX v2.4.0: stała zamiast list(PL_TO_EN.keys()) w każdej iteracji
PL_NAMES: List[str] = list(PL_TO_EN.keys())


def _build_index_maps():
    pl_to_en_idx = {}
    en_to_pl_idx = {}
    en_dims = QuantumEmotionalState.DIMENSIONS
    for pl_idx, pl_name in enumerate(PL_NAMES):
        en_name = PL_TO_EN[pl_name]
        if en_name in en_dims:
            en_idx = en_dims.index(en_name)
            pl_to_en_idx[pl_idx] = en_idx
            en_to_pl_idx[en_idx] = pl_idx
    return pl_to_en_idx, en_to_pl_idx

PL_TO_EN_IDX, EN_TO_PL_IDX = _build_index_maps()


# ═══════════════════════════════════════════════════════════════════════════════
# GŁÓWNA KLASA MOSTU
# ═══════════════════════════════════════════════════════════════════════════════

class QuantumBridge:

    VACUUM_AMPLITUDE = 0.05

    # Tabela Dynamiki Czasowej: (szybkosc_inercji, wsp_rozpadu)
    DECAY_RATES = {
        'joy':          (0.8, 0.15),
        'sadness':      (0.8, 0.15),
        'fear':         (0.8, 0.20),
        'anger':        (0.8, 0.25),  # Gniew wypala się najszybciej
        'surprise':     (0.9, 0.30),
        'disgust':      (0.8, 0.15),
        'anticipation': (0.6, 0.05),
        'trust':        (0.6, 0.05),
        'logic':        (0.3, 0.01),  # Struktura jest twarda
        'knowledge':    (0.3, 0.01),
        'time':         (0.3, 0.01),
        'creation':     (0.3, 0.01),
        'being':        (0.3, 0.01),
        'space':        (0.3, 0.01),
        'chaos':        (0.5, 0.05)
    }

    def __init__(self, aii_instance, verbose: bool = True):
        self.aii = aii_instance
        self.verbose = verbose

        self.state = QuantumEmotionalState()
        self.interference = EmotionalInterference()
        self.decider = QuantumDecisionMaker(self.state, self.interference)

        # vacuum jest teraz w QuantumEmotionalState.DIMENSIONS — brak ręcznego dodawania

        self.phase_history: List[Dict[str, float]] = []
        self.max_history = 100
        # Opcja stałej predykcji — zapobiega pętli inercji gdzie stan i predykcja
        # sprzężone wzmacniają się wzajemnie z sesji na sesję.
        self.fixed_trajectory: Optional[Dict] = None

        self.sync_from_aii()

        if self.verbose:
            print(f"\033[96m[QUANTUM] Most aktywny. "
                  f"Entropy: {self.state.entropy():.2f} bits\033[0m")

    # ─────────────────────────────────────────────────────────────
    # KONWERSJA: AII ↔ Quantum
    # ─────────────────────────────────────────────────────────────

    def sync_from_aii(self):
        vec = self.aii.context_vector
        for pl_idx in range(len(vec)):
            en_idx = PL_TO_EN_IDX.get(pl_idx)
            if en_idx is None:
                continue
            en_name = PL_TO_EN[PL_NAMES[pl_idx]]  # FIX: PL_NAMES zamiast list(...)
            real_val = float(vec[pl_idx])
            magnitude = np.sqrt(max(0.0, real_val)) + self.VACUUM_AMPLITUDE
            current_amp = self.state.amplitudes.get(en_name, 0.0j)
            current_phase = np.angle(current_amp)
            self.state.amplitudes[en_name] = magnitude * np.exp(1j * current_phase)
        self.state.normalize()

    def sync_to_aii(self):
        probs = self.state.get_probabilities()
        for en_name, prob in probs.items():
            if en_name == 'vacuum':
                continue
            pl_name = EN_TO_PL.get(en_name)
            if pl_name is None:
                continue
            pl_idx = PL_NAMES.index(pl_name)  # FIX: PL_NAMES zamiast list(...)
            self.aii.context_vector[pl_idx] = np.clip(prob, 0.0, 1.0)

    # ─────────────────────────────────────────────────────────────
    # GŁÓWNE OPERACJE I INTERFERENCJA
    # ─────────────────────────────────────────────────────────────

    def process_interference(self, time_step: float = 0.1) -> Dict[str, float]:
        self.sync_from_aii()
        # FIX v2.4.1: apply_interference zwraca nowy QuantumEmotionalState
        # który nie zna wymiaru vacuum (wewnętrzny dla mostu, niewidoczny dla AII).
        # Zachowujemy wartość przed zastąpieniem obiektu i przywracamy po.
        vacuum_before = self.state.amplitudes.get('vacuum', 0.0 + 0j)
        self.state = self.interference.apply_interference(self.state, time_step=time_step)
        self.state.amplitudes['vacuum'] = vacuum_before
        resonance = self.interference.resonance_strength(self.state)

        phases = {dim: float(np.angle(self.state.amplitudes[dim])) for dim in self.state.DIMENSIONS}
        self.phase_history.append(phases)
        if len(self.phase_history) > self.max_history:
            self.phase_history.pop(0)

        self.sync_to_aii()

        active_probs = {k: v for k, v in self.state.get_probabilities().items() if k != 'vacuum'}
        dom_en = max(active_probs.items(), key=lambda x: x[1]) if active_probs else ('vacuum', 1.0)
        entropy = self.state.entropy()

        if self.verbose:
            dom_pl = EN_TO_PL.get(dom_en[0], dom_en[0])
            print(f"\033[35m[QUANTUM] {dom_pl.upper()} (prob={dom_en[1]:.1%}) | "
                  f"Vacuum: {self.state.get_probabilities().get('vacuum', 0.0):.1%} | "
                  f"Entropy: {entropy:.2f} bits\033[0m")

        return {
            'entropy': entropy,
            'resonance': resonance,
            'dominant_en': dom_en[0],
            'dominant_pl': EN_TO_PL.get(dom_en[0], dom_en[0]),
            'dominant_prob': dom_en[1],
        }

    def quantum_decide(self, situation: dict) -> dict:
        self.sync_from_aii()
        self.decider.emotional_state = self.state
        return self.decider.decide(situation, verify=True)

    def measure_emotion(self) -> Tuple[str, str]:
        self.sync_from_aii()
        en_emotion = self.state.measure()
        pl_emotion = EN_TO_PL.get(en_emotion, en_emotion)
        return en_emotion, pl_emotion

    def get_quantum_state(self) -> Dict[str, dict]:
        self.sync_from_aii()
        result = {}
        for en_name, amp in self.state.amplitudes.items():
            pl_name = EN_TO_PL.get(en_name, en_name)
            result[pl_name] = {
                'magnitude': float(abs(amp)),
                'phase_deg': float(np.degrees(np.angle(amp))),
                'probability': float(abs(amp) ** 2),
                'en_name': en_name,
            }
        return result

    def get_phase_coherence(self) -> float:
        if len(self.phase_history) < 2:
            return 1.0
        prev = self.phase_history[-2]
        curr = self.phase_history[-1]
        diffs = []
        for dim in self.state.DIMENSIONS:
            if dim in prev and dim in curr:
                diff = abs(curr[dim] - prev[dim])
                diff = min(diff, 2 * np.pi - diff)
                diffs.append(diff)
        if not diffs:
            return 1.0
        mean_diff = np.mean(diffs)
        coherence = 1.0 - (mean_diff / np.pi)
        return max(0.0, min(1.0, coherence))

    # ─────────────────────────────────────────────────────────────
    # RANKING I PREDYKCJA
    # ─────────────────────────────────────────────────────────────

    def rank_candidates(self, candidates: list, top_n: int = 5) -> list:
        if not candidates:
            return candidates
        self.sync_from_aii()
        predicted_state = self._predict_trajectory()

        ranked = []
        max_classical = max(c[0] for c in candidates[:top_n]) if candidates else 1.0

        for score, mid, entry in candidates[:top_n]:
            # FIX v2.4.0: _validate_mem_vec gdy aii dostępne — ochrona przed
            # wektorem złej długości ze starej pamięci po zmianie DIM
            if hasattr(self.aii, '_validate_mem_vec'):
                mem_vec = self.aii._validate_mem_vec(entry)
            else:
                mem_vec = np.array(entry.get('wektor_C_Def', np.zeros(15)))

            q_resonance  = self._memory_resonance(mem_vec)
            q_prediction = self._memory_trajectory_fit(mem_vec, predicted_state)
            q_phase      = self._memory_phase_alignment(mem_vec)

            classical_norm = score / max_classical if max_classical > 0 else 0
            final_score = (classical_norm * 0.50 + q_resonance * 0.25 +
                           q_prediction * 0.15 + q_phase * 0.10)
            final_score *= (0.5 + entry.get('weight', 0.5))
            ranked.append((final_score, mid, entry))

        for score, mid, entry in candidates[top_n:]:
            ranked.append((score / max_classical * 0.3, mid, entry))

        ranked.sort(key=lambda x: x[0], reverse=True)
        return ranked

    def _memory_resonance(self, mem_vec: np.ndarray) -> float:
        if np.sum(np.abs(mem_vec)) < 0.01: return 0.5
        sim_state = QuantumEmotionalState()
        for dim in sim_state.DIMENSIONS:
            sim_state.amplitudes[dim] = self.state.amplitudes.get(dim, 0j)
        for pl_idx, val in enumerate(mem_vec):
            if val < 0.01: continue
            en_idx = PL_TO_EN_IDX.get(pl_idx)
            if en_idx is None: continue
            en_name = PL_TO_EN[PL_NAMES[pl_idx]]  # FIX: PL_NAMES
            sim_state.amplitudes[en_name] += np.sqrt(val) * 0.2
        sim_state.normalize()
        return np.clip(0.5 + self.interference.resonance_strength(sim_state), 0.0, 1.0)

    def _predict_trajectory(self) -> dict:
        predicted = {}
        probs = self.state.get_probabilities()
        if len(self.phase_history) < 3:
            return probs
        recent = self.phase_history[-3:]
        for dim in self.state.DIMENSIONS:
            current_prob = probs.get(dim, 0.0)
            phases = [step.get(dim, 0.0) for step in recent]
            phase_diffs = [min(abs(phases[i] - phases[i-1]), 2*np.pi - abs(phases[i] - phases[i-1]))
                           for i in range(1, len(phases))]
            avg_phase_change = np.mean(phase_diffs) if phase_diffs else np.pi
            stability = 1.0 - (avg_phase_change / np.pi)
            predicted[dim] = current_prob * (1.0 + stability * 0.3)
        total = sum(predicted.values())
        if total > 0: predicted = {k: v/total for k, v in predicted.items()}
        return predicted

    def _memory_trajectory_fit(self, mem_vec: np.ndarray, predicted: dict) -> float:
        if np.sum(np.abs(mem_vec)) < 0.01: return 0.5
        mem_probs = {}
        mem_total = np.sum(np.abs(mem_vec)) + 1e-10
        for pl_idx, val in enumerate(mem_vec):
            if pl_idx < len(PL_NAMES):  # FIX: PL_NAMES
                en_name = PL_TO_EN[PL_NAMES[pl_idx]]
                mem_probs[en_name] = abs(val) / mem_total
        dot = sum(predicted.get(dim, 0.0) * mem_probs.get(dim, 0.0) for dim in self.state.DIMENSIONS)
        norm_p = sum(p**2 for p in predicted.values())
        norm_m = sum(m**2 for m in mem_probs.values())
        denom = np.sqrt(norm_p * norm_m)
        return np.clip(dot / denom, 0.0, 1.0) if denom >= 1e-10 else 0.5

    def _memory_phase_alignment(self, mem_vec: np.ndarray) -> float:
        if np.sum(np.abs(mem_vec)) < 0.01: return 0.5
        alignment, count = 0.0, 0
        for pl_idx, val in enumerate(mem_vec):
            if val < 0.05 or pl_idx >= len(PL_NAMES): continue  # FIX: PL_NAMES
            en_name = PL_TO_EN[PL_NAMES[pl_idx]]
            if en_name not in self.state.amplitudes: continue
            amp = self.state.amplitudes[en_name]
            alignment += val * abs(amp) * np.cos(np.angle(amp)) ** 2
            count += 1
        return np.clip(0.5 + alignment / count, 0.0, 1.0) if count > 0 else 0.5

    def emotional_veto_check(self, action_vector: np.ndarray) -> Tuple[bool, str]:
        sim_state = QuantumEmotionalState()
        for dim in sim_state.DIMENSIONS:
            sim_state.amplitudes[dim] = self.state.amplitudes.get(dim, 0j)
        for pl_idx, val in enumerate(action_vector):
            if val < 0.01: continue
            en_idx = PL_TO_EN_IDX.get(pl_idx)
            if en_idx is None: continue
            en_name = PL_TO_EN[PL_NAMES[pl_idx]]  # FIX: PL_NAMES
            sim_state.amplitudes[en_name] += np.sqrt(val) * 0.3
        sim_state.normalize()
        resonance = self.interference.resonance_strength(sim_state)
        return (False, f"Destrukcyjna interference ({resonance:.3f})") if resonance < -0.5 else (True, f"OK ({resonance:.3f})")

    # ─────────────────────────────────────────────────────────────
    # SERIALIZACJA QRM (Relacyjny Układ Odniesienia i Ewolucja Czasu)
    # ─────────────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        """Zapisuje stan kwantowy jako Węzeł Czasowy (Okno)."""
        data = {'interferences': {}, 'predicted_trajectory': {}, 'timestamp': time.time()}
        epsilon = 1e-12

        volatile_and_vacuum = ['joy', 'sadness', 'fear', 'anger', 'surprise', 'disgust', 'vacuum']
        non_volatile = [d for d in self.state.DIMENSIONS if d not in volatile_and_vacuum]

        ref_dim = max(non_volatile, key=lambda d: abs(self.state.amplitudes.get(d, 0j))) if non_volatile else 'logic'
        ref_amp = self.state.amplitudes.get(ref_dim, 1.0 + 0j)
        ref_mag = abs(ref_amp)

        if ref_mag < epsilon:
            ref_amp = 1.0 + 0j
            ref_mag = 1.0

        ref_phase = np.angle(ref_amp)
        data['ref_dim'] = ref_dim

        predicted_probs = self._predict_trajectory()
        # Gdy fixed_trajectory ustawione — użyj go (blokuje pętlę inercji)
        if self.fixed_trajectory is not None:
            predicted_probs = self.fixed_trajectory

        for dim in self.state.DIMENSIONS:
            amp = self.state.amplitudes.get(dim, 0.0 + 0j)
            mag = abs(amp)
            phase = np.angle(amp)

            rel_mag   = mag / ref_mag if ref_mag > epsilon else mag
            rel_phase = phase - ref_phase

            data['interferences'][dim] = {
                'rel_magnitude': rel_mag,
                'rel_phase':     rel_phase,
                'abs_magnitude': mag
            }
            data['predicted_trajectory'][dim]           = predicted_probs.get(dim, mag**2)
            data['predicted_trajectory'][dim + '_phase'] = phase

        data['entropy'] = float(self.state.entropy())
        return data

    def from_dict(self, data: dict):
        """Odtwarza stan i przepuszcza przez ewolucję czasową (Pustkę)."""
        if 'interferences' not in data:
            return

        ref_dim = data.get('ref_dim', 'logic')
        ref_interf = data['interferences'].get(ref_dim, {})
        ref_abs_mag = ref_interf.get('abs_magnitude', 1.0)
        ref_amp = ref_abs_mag * np.exp(1j * 0.0)

        self.state.amplitudes[ref_dim] = ref_amp

        for dim in self.state.DIMENSIONS:
            if dim == ref_dim:
                continue
            interf     = data['interferences'].get(dim, {})
            rel_mag    = interf.get('rel_magnitude', 0.0)
            rel_phase  = interf.get('rel_phase', 0.0)
            abs_mag    = interf.get('abs_magnitude', 0.0)

            mag   = abs_mag if dim == 'vacuum' else rel_mag * ref_abs_mag
            phase = np.angle(ref_amp) + rel_phase
            self.state.amplitudes[dim] = mag * np.exp(1j * phase)

        # ─────────────────────────────────────────────────────────
        # EWOLUCJA QRM W PUSTCE (ZAMKNIĘTE PUDEŁKO)
        # ─────────────────────────────────────────────────────────
        ostatni_zapis  = data.get('timestamp', time.time())
        obecny_czas    = time.time()
        delta_t_godziny = (obecny_czas - ostatni_zapis) / 3600.0

        if delta_t_godziny > 0.016:
            if self.verbose:
                print(f"\033[90m[TIME] Pustka trwała {delta_t_godziny:.2f}h. Aplikuję ewolucję QRM...\033[0m")

            vacuum_amp = self.state.amplitudes.get('vacuum', 0j)
            vacuum_mag = abs(vacuum_amp)

            for dim in self.state.DIMENSIONS:
                if dim == 'vacuum':
                    continue

                amp  = self.state.amplitudes[dim]
                mag  = abs(amp)
                faza = np.angle(amp)

                szybkosc_inercji, wsp_rozpadu = self.DECAY_RATES.get(dim, (0.5, 0.05))

                docelowe_prob  = data['predicted_trajectory'].get(dim, mag**2)
                docelowy_mag   = math.sqrt(max(0.0, docelowe_prob))
                docelowa_faza  = data['predicted_trajectory'].get(dim + '_phase', faza)

                # 1. Inercja Predykcyjna
                wsp_przyciagania = 1.0 - math.exp(-szybkosc_inercji * delta_t_godziny)
                mag_po_inercji   = mag + (docelowy_mag - mag) * wsp_przyciagania

                delta_faza = (docelowa_faza - faza) * (1.0 - math.exp(-0.05 * delta_t_godziny))
                nowa_faza  = faza + delta_faza

                # 2. Fizyka Rozpadu do Pustki
                decayed_mag = mag_po_inercji * math.exp(-wsp_rozpadu * delta_t_godziny)

                prob_lost   = (mag_po_inercji**2) - (decayed_mag**2)
                vacuum_prob = (vacuum_mag**2) + max(0.0, prob_lost)
                vacuum_mag  = math.sqrt(vacuum_prob)

                self.state.amplitudes[dim] = decayed_mag * np.exp(1j * nowa_faza)

            self.state.amplitudes['vacuum'] = vacuum_mag * np.exp(1j * 0.0)

        self.state.normalize()
        self.sync_to_aii()


    # Aliasy dla kompatybilności z union.py (może używać nazw _qrm)
    def to_dict_qrm(self) -> Dict:
        """Alias to_dict — kompatybilność z kodem używającym nazwy _qrm."""
        return self.to_dict()

    def from_dict_qrm(self, data: Dict, delta_t_godziny: Optional[float] = None):
        """
        Alias from_dict z opcjonalnym zewnętrznym delta_t (do testów).
        Gdy delta_t_godziny podane — nadpisuje obliczenie z timestampa.
        """
        if delta_t_godziny is not None:
            import time as _time
            data = dict(data)
            data['timestamp'] = _time.time() - delta_t_godziny * 3600.0
        self.from_dict(data)


# ═══════════════════════════════════════════════════════════════════════════════
# HELPER: integracja z AII
# ═══════════════════════════════════════════════════════════════════════════════
def integrate_quantum_bridge(aii_instance, verbose: bool = True) -> QuantumBridge:
    return QuantumBridge(aii_instance, verbose=verbose)