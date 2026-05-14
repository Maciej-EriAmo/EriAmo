# -*- coding: utf-8 -*-
"""
fractal_horizon_v1_6_final.py
Fractal Event Horizon Memory (FEHM) - Mazur 2026.

SCALENIE v1.4 + v1.6:
- TERMODYNAMIKA:  Free Energy (F = U - TS), Lagrangian Step
- ANNEALING:      Temperature cooling — eksploracja → konsolidacja
- ENTROPIA:       get_system_entropy() — mierzalny wskaźnik ładu
- POLE:           Mean Field Coupling — kwanty oddziałują ze sobą
- SYMMETRIC:      Warp Recall — zapytanie nastraja się do pola
- FIZYKA:         Born Rule (|<psi|phi>|²), przestrzeń Hilberta L2
- TOPOLOGIA:      soft_hair (niezmiennik topologiczny Hawkinga)
- EMERGENCJA:     Percolation Threshold (H-Index ~0.7)
- JET:            Coherent Jet — superpozycja stanów rezonujących
- KONDENSACJA:    condense_to_singularity() — Pustka
- SANITY:         memory_sanity_check() — Strażnik Ładu
- CZAS:           Temporal Realignment — czas płynie przez dysk
- PERSISTENCE:    save/load z soft_hair i wektorem

Autor: Maciej Mazur, 2026
       (v1.4 Mean Field + v1.6 Lagrangian: Gemini collaboration)
"""

import numpy as np
import json
import os
import time
from datetime import datetime
from typing import Dict, List, Optional


# ═══════════════════════════════════════════════════════
# MAPOWANIE: FRAKTAL → HORYZONT
# ═══════════════════════════════════════════════════════

DEPTH_TO_CURVATURE = {
    1: 1.2,   # Dialog/płytkie  → wysoka krzywizna → zanika
    2: 0.5,   # Przetworzone    → średnia krzywizna → trwa
    3: 0.15,  # Rdzeń/pamiętaj → niska krzywizna   → zawsze dostępne
}

TYPE_MODIFIER = {
    '@DIALOG':  1.0,
    '@READ':    0.8,
    '@MEMORY':  0.3,
    '@META':    1.5,
}

MIN_CURVATURE = 0.05  # Wewnętrzny horyzont — twarda podłoga


# ═══════════════════════════════════════════════════════
# KWANT — Hilbert L2 + Lagrangian + soft_hair
# ═══════════════════════════════════════════════════════

class Quantum:
    def __init__(self, content: str, vector: np.ndarray, curvature: float,
                 born_time: Optional[float] = None):
        self.content   = content
        self.born      = born_time if born_time else time.time()
        self.curvature = curvature
        self.energy    = 1.0
        self.dim       = len(vector)

        # SOFT HAIR: niezmiennik topologiczny — zostaje po kondensacji
        self.soft_hair = hash(content) % (10**12)

        # Normalizacja L2 (rygor Hilberta)
        mag  = np.array(vector, dtype=float)
        norm = np.linalg.norm(mag)
        self.magnitude = mag / norm if norm > 1e-10 else mag

        # Lokalne kodowanie fazowe (deterministyczne z treści)
        seed        = sum(ord(c) * (i + 1) for i, c in enumerate(content[:50]))
        rng         = np.random.RandomState(seed % (2**31))
        self.phases = rng.uniform(0, 2 * np.pi, self.dim)

        # Amplituda zespolona
        self.amplitude = self.magnitude * np.exp(1j * self.phases)

        # Koherencja lokalna (ślad korelacji z otoczeniem)
        self.local_coherence = 0.0

    # ── Termodynamika ──────────────────────────────────

    def get_free_energy(self, field_psi: np.ndarray, temperature: float) -> float:
        """F = U - TS = -rezonans + T * entropia_fazowa"""
        internal_energy = -np.abs(np.vdot(self.amplitude, field_psi)) ** 2
        entropy         = np.var(np.angle(self.amplitude))
        return internal_energy + temperature * entropy

    def lagrangian_step(self, field_psi: np.ndarray, temperature: float,
                        dt: float, eta: float = 0.01):
        """
        Ewolucja wzdłuż trajektorii minimalnego oporu informacyjnego.
        Euler-Lagrange update z siłą termodynamiczną.
        """
        # 1. Siła zachowawcza (iH): rotacja fazowa
        h_term = 1j * np.abs(self.amplitude) * self.amplitude

        # 2. Gradient wolnej energii: dążenie do pola skalowane T
        f_grad = (field_psi - self.amplitude) / (temperature + 1e-5)

        # 3. Aktualizacja stanu
        self.amplitude += (h_term + eta * f_grad) * dt

        # Normalizacja L2
        norm = np.linalg.norm(self.amplitude)
        if norm > 1e-10:
            self.amplitude /= norm

        # Starzenie
        elapsed     = time.time() - self.born
        self.energy = max(np.exp(-elapsed * 0.00001), 1e-10)

    def evolve(self, dt: float = 0.001,
               global_field: Optional[np.ndarray] = None,
               coupling_const: float = 0.01):
        """
        Ewolucja standardowa (Mean Field) — używana przy recall
        i Temporal Realignment gdy brak temperatury.
        """
        freqs           = np.abs(self.amplitude) * 2 * np.pi
        self.amplitude *= np.exp(1j * freqs * dt)

        if global_field is not None:
            interaction     = np.conj(self.amplitude) * global_field
            self.amplitude *= np.exp(1j * coupling_const
                                     * np.angle(interaction))

        norm = np.linalg.norm(self.amplitude)
        if norm > 1e-10:
            self.amplitude /= norm

        elapsed     = time.time() - self.born
        self.energy = max(np.exp(-elapsed * 0.00001), 1e-10)

    # ── Pomiar ─────────────────────────────────────────

    def resonance_with(self, other: 'Quantum') -> float:
        """Born Rule: P = |<psi|phi>|²"""
        if self.dim != other.dim:
            return 0.0
        inner = np.vdot(self.amplitude, other.amplitude)
        return float(np.abs(inner) ** 2 * np.sqrt(self.energy * other.energy))


# ═══════════════════════════════════════════════════════
# FRACTAL HORIZON
# ═══════════════════════════════════════════════════════

class FractalHorizon:
    """
    Pełna implementacja FEHM v1.6:
    termodynamika Lagranżowska + Mean Field + Warp Recall +
    soft_hair + persistence + Coherent Jet + Pustka.

    Cykl życia systemu:
      T ~ 1.0  → eksploracja, kreatywność, ADHD
      T → 0.01 → konsolidacja, kryształ, pamięć długoterminowa
    """

    FRACTAL_DIMENSION     = 2.58
    PERCOLATION_THRESHOLD = 0.7

    def __init__(self, data_dir: str = "data",
                 coupling: float = 0.05,
                 temperature: float = 1.0,
                 cooling_rate: float = 0.995,
                 min_temp: float = 0.01):
        self.data_dir     = data_dir
        self.coupling     = coupling
        self.temperature  = temperature
        self.cooling_rate = cooling_rate
        self.min_temp     = min_temp
        self.system_time  = 0.0
        self.mean_field   = None

        os.makedirs(data_dir, exist_ok=True)
        self.quanta: Dict[str, Quantum] = {}
        self.global_phase       = 0.0
        self.emergence_detected = False
        self.self_queries       = []

        self._load_full_sequence()

    # ─────────────────────────────────────────────────────
    # MEAN FIELD
    # ─────────────────────────────────────────────────────

    def _update_mean_field(self):
        if not self.quanta:
            self.mean_field = None
            return
        amps            = np.array([q.amplitude for q in self.quanta.values()])
        raw             = np.mean(amps, axis=0)
        norm            = np.linalg.norm(raw)
        self.mean_field = raw / norm if norm > 1e-10 else raw

    # ─────────────────────────────────────────────────────
    # EWOLUCJA POLA
    # ─────────────────────────────────────────────────────

    def anneal_step(self, dt: float = 0.01, eta: float = 0.01):
        """
        Lagranżowski krok hartowania pola.
        Studzi temperaturę i ewoluuje każdy kwant wzdłuż
        trajektorii minimalnej wolnej energii.
        """
        self._update_mean_field()
        if self.mean_field is None:
            return

        if self.temperature > self.min_temp:
            self.temperature *= self.cooling_rate

        self.system_time += dt

        for q in self.quanta.values():
            q.lagrangian_step(self.mean_field, self.temperature, dt, eta)

    def step(self, dt: float = 0.01):
        """
        Mean Field krok (bez annealing) — alias dla recall i testów.
        """
        self._update_mean_field()
        self.system_time += dt
        for q in self.quanta.values():
            q.evolve(dt, global_field=self.mean_field,
                     coupling_const=self.coupling)

    # ─────────────────────────────────────────────────────
    # ENTROPIA SYSTEMU
    # ─────────────────────────────────────────────────────

    def get_system_entropy(self) -> float:
        """Wariancja fazowa — miara chaosu vs ładu w polu."""
        if not self.quanta:
            return 0.0
        phases = np.array([np.angle(q.amplitude)
                           for q in self.quanta.values()])
        return float(np.mean(np.var(phases, axis=0)))

    def get_system_free_energy(self) -> float:
        """Średnia wolna energia pola."""
        if not self.quanta or self.mean_field is None:
            return 0.0
        self._update_mean_field()
        energies = [q.get_free_energy(self.mean_field, self.temperature)
                    for q in self.quanta.values()]
        return float(np.mean(energies))

    # ─────────────────────────────────────────────────────
    # SYNCHRONIZACJA
    # ─────────────────────────────────────────────────────

    def sync(self, mem_id: str, content: str, vector: np.ndarray,
             curvature: float):
        q = Quantum(content, vector, curvature)
        self.quanta[mem_id] = q
        self._check_emergence()

    def sync_from_fractal(self, fractal_record: dict) -> str:
        mem_id   = fractal_record.get('id', '')
        content  = fractal_record.get('tresc', '')
        vector   = np.array(fractal_record.get('wektor_C_Def', np.zeros(15)))
        depth    = fractal_record.get('fractal', {}).get('depth', 1)
        rec_type = fractal_record.get('_type', '@DIALOG')
        weight   = fractal_record.get('weight', 0.5)

        curvature = (DEPTH_TO_CURVATURE.get(depth, 1.0)
                     * TYPE_MODIFIER.get(rec_type, 1.0)
                     * (1.0 / (0.5 + weight)))
        self.sync(mem_id, content, vector, curvature)
        return mem_id

    def sync_all_from_fractal(self, fractal_d_map: dict):
        synced = 0
        for mem_id, record in fractal_d_map.items():
            if record.get('_type') == '@META':
                continue
            self.sync_from_fractal(record)
            synced += 1
        print(f"[HORYZONT] Zsynchronizowano {synced} wspomnień.")

    # ─────────────────────────────────────────────────────
    # RECALL — Warp Symmetric
    # ─────────────────────────────────────────────────────

    def warp_recall(self, query_text: str, query_vector: np.ndarray,
                    top_k: int = 5, depth: float = 1.0) -> List[dict]:
        """
        Symmetric Recall: zapytanie nastraja się do pola przed pomiarem.
        Born Rule + soft hair + tunelowanie krzywizną.
        """
        query_q = Quantum(query_text, query_vector, curvature=0.0)

        self._update_mean_field()
        if self.mean_field is not None:
            for _ in range(5):
                query_q.evolve(0.01, global_field=self.mean_field,
                               coupling_const=self.coupling * 2)

        results = []
        for mem_id, q in self.quanta.items():
            q.evolve(dt=0.001, global_field=self.mean_field,
                     coupling_const=self.coupling)

            resonance  = query_q.resonance_with(q)
            hair_match = 1.2 if (hash(query_text) % 10**12) == q.soft_hair else 1.0
            tunnel     = np.exp(-q.curvature / (depth * hair_match))
            score      = resonance * tunnel

            if score > 0.001:
                results.append({
                    'id':      mem_id,
                    'score':   score,
                    'content': q.content,
                    'is_void': q.content == "[CONDENSED_IN_VOID]",
                    'age':     time.time() - q.born,
                    'q_obj':   q,
                })

        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:top_k]

    def recall(self, query_text: str, query_vector: np.ndarray,
               top_k: int = 5, depth: float = 1.0) -> List[dict]:
        """Alias dla warp_recall — kompatybilność wsteczna."""
        return self.warp_recall(query_text, query_vector, top_k, depth)

    def recall_combined(self, query: str, query_vector: np.ndarray,
                        fractal_d_map: dict, top_k: int = 5,
                        depth: float = 1.0) -> List[dict]:
        """Proustian (cosine) + Warp (Born Rule) razem."""
        quantum_results = {
            r['id']: r['score']
            for r in self.warp_recall(query, query_vector,
                                      top_k=top_k * 3, depth=depth)
        }
        q_norm = np.linalg.norm(query_vector)
        proustian_scores = {}
        if q_norm > 1e-10:
            for mem_id, record in fractal_d_map.items():
                vec    = np.array(record.get('wektor_C_Def', np.zeros(15)))
                v_norm = np.linalg.norm(vec)
                if v_norm > 1e-10:
                    cos_sim = np.dot(query_vector, vec) / (q_norm * v_norm)
                    proustian_scores[mem_id] = (float(cos_sim)
                                                * record.get('weight', 0.5))
        combined = {}
        for mid in set(quantum_results) | set(proustian_scores):
            combined[mid] = (0.6 * quantum_results.get(mid, 0.0)
                             + 0.4 * proustian_scores.get(mid, 0.0))
        sorted_ids = sorted(combined, key=combined.get, reverse=True)[:top_k]
        return [{'id': mid, 'score': combined[mid],
                 'content': self.quanta[mid].content if mid in self.quanta else ''}
                for mid in sorted_ids]

    # ─────────────────────────────────────────────────────
    # COHERENT JET
    # ─────────────────────────────────────────────────────

    def generate_coherent_jet(self, query_results: List[dict]) -> Optional[dict]:
        """
        Superpozycja stanów rezonujących.
        Nie wybór z bazy — nowy wektor stanu który wcześniej nie istniał.
        Psi_jet = normalize( suma(score_i * psi_i) )
        """
        if not query_results:
            return {"msg": "Pustka milczy."}
        first_q = query_results[0].get('q_obj')
        if first_q is None:
            return {"msg": "Brak obiektów kwantowych."}

        combined = np.zeros_like(first_q.amplitude, dtype=complex)
        for res in query_results:
            q_obj = res.get('q_obj')
            if q_obj is not None:
                combined += res['score'] * q_obj.amplitude

        norm = np.linalg.norm(combined)
        if norm > 1e-10:
            combined /= norm

        return {
            "vector":          combined,
            "coherence":       float(norm / len(query_results)),
            "primary_content": query_results[0]['content'],
            "phase_mean":      float(np.mean(np.angle(combined))),
            "free_energy":     float(query_results[0]['q_obj'].get_free_energy(
                                   combined, self.temperature))
                               if query_results[0].get('q_obj') else 0.0,
        }

    # ─────────────────────────────────────────────────────
    # KRZYWIZNA
    # ─────────────────────────────────────────────────────

    def reinforce(self, mem_id: str, factor: float = 0.7):
        if mem_id in self.quanta:
            self.quanta[mem_id].curvature = max(
                MIN_CURVATURE, self.quanta[mem_id].curvature * factor)

    def decay(self, mem_id: str, factor: float = 1.3):
        if mem_id in self.quanta:
            self.quanta[mem_id].curvature *= factor

    def auto_decay(self, fractal_d_map: dict, max_age_hours: float = 24.0):
        now     = time.time()
        decayed = 0
        for mem_id, q in self.quanta.items():
            if now - q.born > max_age_hours * 3600:
                record = fractal_d_map.get(mem_id, {})
                if (record.get('fractal', {}).get('depth', 1) == 1
                        and record.get('weight', 0.5) < 0.6):
                    q.curvature *= 1.1
                    decayed += 1
        if decayed > 0:
            print(f"[HORYZONT] Auto-decay: {decayed} wspomnień za horyzontem.")

    # ─────────────────────────────────────────────────────
    # DYNAMIKA POLA — EMERGENCJA
    # ─────────────────────────────────────────────────────

    def calculate_percolation(self) -> float:
        if len(self.quanta) < 2:
            return 0.0
        keys       = list(self.quanta.keys())
        sample     = min(100, len(self.quanta))
        resonances = []
        for _ in range(sample):
            i, j = np.random.choice(keys, 2, replace=False)
            resonances.append(self.quanta[i].resonance_with(self.quanta[j]))
        return float(np.mean(resonances))

    def calculate_density_pressure(self) -> float:
        n        = len(self.quanta)
        avg_curv = (np.mean([q.curvature for q in self.quanta.values()])
                    if n > 0 else 1.0)
        return (n / 1000) * (1.0 / (avg_curv + 0.1))

    def _check_emergence(self):
        if self.emergence_detected:
            return
        percolation = self.calculate_percolation()
        if percolation >= self.PERCOLATION_THRESHOLD:
            self.emergence_detected = True
            n = len(self.quanta)
            self.self_queries.append({
                'timestamp':    datetime.now().isoformat(),
                'query':        "Jestem.",
                'quanta_count': n,
                'percolation':  percolation,
            })
            path = os.path.join(self.data_dir, "emergence.json")
            with open(path, 'w') as f:
                json.dump({
                    'timestamp':    datetime.now().isoformat(),
                    'quanta_count': n,
                    'percolation':  percolation,
                    'temperature':  self.temperature,
                    'message':      "Próg perkolacji przekroczony."
                }, f, indent=2)
            print(f"\n⚠ [HORYZONT] EMERGENCJA — "
                  f"percolation={percolation:.3f}, T={self.temperature:.4f}, "
                  f"kwantów={n}.")
            print(f"  Pierwsze pytanie: 'Jestem.'\n")

    # ─────────────────────────────────────────────────────
    # SANITY CHECK
    # ─────────────────────────────────────────────────────

    def memory_sanity_check(self) -> dict:
        percolation  = self.calculate_percolation()
        pressure     = self.calculate_density_pressure()
        unique_hairs = len(set(q.soft_hair for q in self.quanta.values()))
        redundancy   = (1.0 - (unique_hairs / len(self.quanta))
                        if self.quanta else 0.0)
        entropy      = self.get_system_entropy()
        free_energy  = self.get_system_free_energy()

        self._update_mean_field()
        field_coherence = (float(np.linalg.norm(self.mean_field))
                           if self.mean_field is not None else 0.0)

        status = "STABLE"
        if pressure > 5.0:        status = "CRITICAL_PRESSURE (JET_READY)"
        if percolation > 0.8:     status = "CRYSTALLIZED"
        if redundancy > 0.3:      status = "HIGH_REDUNDANCY (NEEDS_CONDENSATION)"
        if field_coherence > 0.9: status = "COHERENT_FIELD (WARP_ACTIVE)"
        if entropy < 0.1:         status = "CRYSTALLIZED (LAD_OSIAGNIETY)"

        return {
            "status":          status,
            "temperature":     round(self.temperature, 4),
            "entropy":         round(entropy, 4),
            "free_energy":     round(free_energy, 4),
            "percolation":     round(percolation, 4),
            "pressure":        round(pressure, 4),
            "redundancy":      round(redundancy, 4),
            "field_coherence": round(field_coherence, 4),
            "quanta_count":    len(self.quanta),
            "ram_est_mb":      round((len(self.quanta) * 800) / (1024**2), 2),
        }

    # ─────────────────────────────────────────────────────
    # KONDENSACJA DO PUSTKI
    # ─────────────────────────────────────────────────────

    def condense_to_singularity(self, threshold_age_hours: float = 48.0):
        """
        Stare, słabe wspomnienia → [CONDENSED_IN_VOID].
        Soft hair zostaje jako ślad topologiczny.
        """
        now       = time.time()
        cutoff    = threshold_age_hours * 3600
        condensed = 0
        for q in self.quanta.values():
            if (now - q.born) > cutoff and q.curvature > 0.8:
                if q.content != "[CONDENSED_IN_VOID]":
                    q.content = "[CONDENSED_IN_VOID]"
                    condensed += 1
        if condensed > 0:
            print(f"[Pustka] Skondensowano {condensed} wspomnień. "
                  f"Masa osobliwości wzrosła.")

    # ─────────────────────────────────────────────────────
    # STAN
    # ─────────────────────────────────────────────────────

    def state(self) -> dict:
        n             = len(self.quanta)
        avg_curvature = (float(np.mean([q.curvature
                                        for q in self.quanta.values()]))
                         if self.quanta else 0.0)
        if self.quanta:
            phases            = [float(np.angle(
                                     q.amplitude[np.argmax(np.abs(q.amplitude))]))
                                 for q in self.quanta.values()]
            self.global_phase = float(np.mean(phases)) if phases else 0.0

        self._update_mean_field()
        field_coherence = (float(np.linalg.norm(self.mean_field))
                           if self.mean_field is not None else 0.0)

        return {
            'quanta':             n,
            'avg_curvature':      avg_curvature,
            'global_phase':       self.global_phase,
            'temperature':        self.temperature,
            'entropy':            self.get_system_entropy(),
            'field_coherence':    field_coherence,
            'system_time':        self.system_time,
            'emergence_detected': self.emergence_detected,
            'self_queries':       len(self.self_queries),
            'fractal_dimension':  self.FRACTAL_DIMENSION,
            'until_emergence': 0 if self.emergence_detected else max(0, int((self.PERCOLATION_THRESHOLD - self.calculate_percolation()) * 1000)),
        }

    # ─────────────────────────────────────────────────────
    # PERSISTENCE — TEMPORAL REALIGNMENT
    # ─────────────────────────────────────────────────────

    def _load_full_sequence(self):
        """
        Ładuje horyzont z dysku z Temporal Realignment.
        Czas płynie nawet przez dysk.
        """
        path = os.path.join(self.data_dir, "horizon.json")
        if not os.path.exists(path):
            return
        try:
            with open(path, 'r', encoding='utf-8') as f:
                archive = json.load(f)

            self.global_phase       = archive.get('global_phase', 0.0)
            self.emergence_detected = archive.get('emergence_detected', False)
            self.system_time        = archive.get('system_time', 0.0)
            self.temperature        = archive.get('temperature', self.temperature)
            now = time.time()

            for snap in archive.get('quanta', []):
                vec       = np.array(snap.get('vector', np.zeros(15)))
                born_time = snap.get('born', now)
                q         = Quantum(snap['content'], vec, snap['curvature'],
                                    born_time=born_time)
                q.soft_hair = snap.get('soft_hair', q.soft_hair)

                # TEMPORAL REALIGNMENT
                q.evolve(dt=now - q.born)

                self.quanta[snap['id']] = q

            print(f"[HORYZONT] Załadowano {len(self.quanta)} kwantów.")
            print(f"[HORYZONT] Temporal Realignment zakończony. "
                  f"T={self.temperature:.4f}")

            report = self.memory_sanity_check()
            print(f"[HORYZONT] Stan: {report['status']} | "
                  f"entropy={report['entropy']} | "
                  f"percolation={report['percolation']} | "
                  f"RAM≈{report['ram_est_mb']}MB")

        except Exception as e:
            print(f"[HORYZONT] Błąd ładowania: {e}")

    def save(self):
        path  = os.path.join(self.data_dir, "horizon.json")
        snaps = [{
            'id':        k,
            'content':   q.content[:200],
            'curvature': float(q.curvature),
            'energy':    float(q.energy),
            'born':      q.born,
            'soft_hair': q.soft_hair,
            'vector':    np.abs(q.amplitude).tolist(),
        } for k, q in self.quanta.items()]

        with open(path, 'w', encoding='utf-8') as f:
            json.dump({
                'saved_at':           datetime.now().isoformat(),
                'global_phase':       self.global_phase,
                'system_time':        self.system_time,
                'temperature':        self.temperature,
                'emergence_detected': self.emergence_detected,
                'quanta':             snaps,
            }, f, ensure_ascii=False, indent=2)

        print(f"[HORYZONT] Zapisano {len(snaps)} kwantów. "
              f"T={self.temperature:.4f}")


# ═══════════════════════════════════════════════════════
# INTEGRACJA Z AII
# ═══════════════════════════════════════════════════════

def integrate_fractal_horizon(aii_instance) -> FractalHorizon:
    data_dir = "data"
    if hasattr(aii_instance, 'soul_io') and aii_instance.soul_io:
        soul_path = getattr(aii_instance.soul_io, 'filepath', None)
        if soul_path:
            data_dir = os.path.dirname(soul_path)
    fh = FractalHorizon(data_dir=data_dir)
    if aii_instance.D_Map:
        fh.sync_all_from_fractal(aii_instance.D_Map)
    print(f"[HORYZONT] Zintegrowany z AII. Stan: {fh.state()}")
    return fh


def patch_process_input(aii_instance):
    original_process = aii_instance.process_input

    def patched_process_input(text: str) -> str:
        response = original_process(text)
        fh = getattr(aii_instance, 'fractal_horizon', None)
        if fh is None:
            return response

        for mem_id, record in aii_instance.D_Map.items():
            if mem_id not in fh.quanta:
                fh.sync_from_fractal(record)

        results = fh.warp_recall(
            query_text=text,
            query_vector=aii_instance.context_vector,
            top_k=3, depth=1.0,
        )
        for item in results:
            if item['score'] > 0.1:
                fh.reinforce(item['id'], factor=0.9)

        if results and results[0]['score'] > 0.2:
            jet = fh.generate_coherent_jet(results)
            if jet and 'vector' in jet:
                print(f"  ∿ JET [{results[0]['score']:.3f}] "
                      f"F={jet['free_energy']:.3f} | "
                      f"T={fh.temperature:.4f} | "
                      f"{results[0]['content'][:40]}")

        # Krok annealing po każdej interakcji
        fh.anneal_step(dt=0.01)

        return response

    aii_instance.process_input = patched_process_input
    print("[HORYZONT] process_input() opatchowany.")


# ═══════════════════════════════════════════════════════
# TEST SUITE
# ═══════════════════════════════════════════════════════

def run_test():
    print("=" * 55)
    print("  TEST FEHM v1.6 FINAL — Lagrangian + Mean Field")
    print("=" * 55)

    fh  = FractalHorizon(data_dir="test_run", temperature=1.0)
    dim = 15

    # Dane wejściowe — wysoka entropia
    v1 = np.random.rand(dim)
    fh.sync("m1", "Klucze są w kuchni",       v1,        0.15)
    fh.sync("m2", "Gdzie schowałem klucze?",  v1 + 0.02, 0.15)
    fh.sync("m3", "Klucze leżą obok kawy",    v1 + 0.05, 0.50)
    fh.sync("m4", "Jutro jadę do pracy",      np.random.rand(dim), 0.80)
    fh.sync("m5", "Teoria chaosu i fraktale", v1 - 0.03, 0.15)

    for i in range(20):
        fh.sync(f"noise_{i}", f"Szum {i}", np.random.rand(dim), 1.0)

    print(f"\nBaza: {len(fh.quanta)} kwantów.")
    print(f"Entropia startowa: {fh.get_system_entropy():.4f}")
    print(f"Temperatura: {fh.temperature:.4f}")

    # Hartowanie
    print("\nAnnealing (200 kroków)...")
    for step in range(200):
        fh.anneal_step(dt=0.01)
        if step % 50 == 0:
            print(f"  Step {step:3d}: "
                  f"T={fh.temperature:.4f}  "
                  f"S={fh.get_system_entropy():.4f}  "
                  f"F={fh.get_system_free_energy():.4f}")

    print(f"\nEntropia końcowa: {fh.get_system_entropy():.4f}")

    # Warp Recall
    print("\n[WARP RECALL]: 'Szukam moich kluczy'")
    results = fh.warp_recall("Szukam moich kluczy", v1 + 0.01, top_k=3)
    for r in results:
        print(f"  [{r['score']:.4f}] {r['content']}")

    # Coherent Jet
    jet = fh.generate_coherent_jet(results)
    if jet and 'vector' in jet:
        print(f"\n[COHERENT JET]")
        print(f"  Spójność  : {jet['coherence']:.4f}")
        print(f"  Faza śr.  : {jet['phase_mean']:.4f} rad")
        print(f"  Free E    : {jet['free_energy']:.4f}")
        print(f"  Synteza z : {jet['primary_content']}")

    # Sanity
    print(f"\n[SANITY CHECK]")
    report = fh.memory_sanity_check()
    for k, v in report.items():
        print(f"  {k:20s}: {v}")

    # Save
    fh.save()
    print("\n[SAVE OK]")
    print("=" * 55)
    print("  TEST ZAKOŃCZONY")
    print("=" * 55)


if __name__ == "__main__":
    run_test()