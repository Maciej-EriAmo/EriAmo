# -*- coding: utf-8 -*-
"""
ontological_compression_15d.py
Moduł odpowiedzialny za weryfikację kompresji ontologicznej w przestrzeni 15D/21D.

Poprawki v8.3:
  - FIX: granica -0.4 należy teraz do NOWOŚCI (zmiana > na >= przy -THRESHOLD_CONVERGENCE)
  - FIX: dodano ochronę przed NaN/Inf w check_compression i interpret_alignment
  - USUNIĘTO: martwe DIMENSION_TYPES_15D/21D (deklarowały funkcjonalność, której nie było)
  - DOCS: udokumentowana decyzja ontologiczna: zerowy S = brak zdolności oceny kierunku
  - DOCS: ostrzeżenie o praktycznej nieosiągalności KOMPRESJI w 15D/21D przy progu 0.995

Pełna mapa stanów alignmentu — zamknięte przedziały:
    cos_alpha >= 0.995                      → KOMPRESJA
    [0.800,  0.995)                         → HARMONIA
    [0.400,  0.800)                         → KONWERGENCJA
    [-0.400, 0.400)   (granica: do NOWOŚCI) → NOWOŚĆ
    [-0.800, -0.400)                        → DYZONANS
    < -0.800                                → KONFLIKT
"""

import numpy as np


class OntologicalCompressor:
    """
    Sprawdza, czy nowy bodziec (F) jest 'kompresją' obecnego stanu (S),
    czyli czy leży na tej samej trajektorii w przestrzeni wielowymiarowej.

    Progi są skalibrowane dla testów v8.1. Przy przestrzeniach >=15D wartość
    THRESHOLD_COMPRESSION = 0.995 jest ekstremalnie restrykcyjna — oznacza kąt
    < 5.7 stopnia, co w praktyce odpowiada prawie identycznym wektorom (wrażliwość
    na szum numeryczny wysoka). Rozważ adaptacyjny próg przez Digital Proprioception.

    Decyzja ontologiczna: zerowy S (self.S_len < 1e-9) oznacza brak ukonstytuowanej
    tożsamości — system nie ma wektora odniesienia, więc nie może ocenić kierunku
    bodźca. Każdy F zwraca (False, 0.0). To poprawne filozoficznie jako stan przed
    pierwszym doświadczeniem, ale oznacza brak zdolności detekcji Konfliktu po resecie.
    """

    THRESHOLD_COMPRESSION = 0.995  # Tożsamość (~identyczny kierunek, kąt < 5.7°)
    THRESHOLD_HARMONY     = 0.800  # Zbieżność (kąt < 36.9°)
    THRESHOLD_CONVERGENCE = 0.400  # Granica konwergencji/nowości (kąt < 66.4°)
    # Poniżej -THRESHOLD_CONVERGENCE: Dyzonans i Konflikt (przeciwny kierunek)
    # Granica Dyzonansu/Konfliktu jest hard-coded na -0.8 (kąt > 143.1°)

    def __init__(self, current_vector):
        """
        Inicjalizuje kompresor obecnym stanem bytu (S).

        Args:
            current_vector (array-like | None): Wektor stanu (15D lub 21D).
                Jeśli None, inicjalizuje zerowym wektorem 15D (stan przed pierwszym doświadczeniem).
        """
        if current_vector is None:
            self.S = np.zeros(15)
        else:
            self.S = np.array(current_vector, dtype=float)

        norm_S = np.linalg.norm(self.S)
        if norm_S > 1e-9:
            self.S_norm = self.S / norm_S
            self.S_len  = norm_S
        else:
            self.S_norm = np.zeros_like(self.S)
            self.S_len  = 0.0

    def check_compression(self, F_vector):
        """
        Sprawdza relację geometryczną między wektorem bodźca (F) a stanem (S).

        Obsługuje wektory F o innej liczbie wymiarów niż S poprzez padding zerami.
        Chroni przed propagacją NaN/Inf — zwraca (False, 0.0) przy nieważnych danych.

        Args:
            F_vector (array-like): Wektor bodźca — może mieć dowolną liczbę wymiarów.

        Returns:
            tuple[bool, float]:
                - bool:  True jeśli cos_alpha >= THRESHOLD_COMPRESSION
                         (bodziec leży na tej samej trajektorii co stan)
                - float: cos_alpha w zakresie [-1.0, 1.0], lub 0.0 przy nieważnych danych
        """
        F = np.array(F_vector, dtype=float)

        # Ochrona przed NaN/Inf w danych wejściowych
        if not np.all(np.isfinite(F)):
            return False, 0.0

        # Dopasowanie wymiarów przez padding zerami
        if len(F) < len(self.S):
            F = np.pad(F, (0, len(self.S) - len(F)), 'constant')

        elif len(F) > len(self.S):
            # self.S_norm ma normę 1 — padding zerami jej nie zmienia
            padded_S = np.pad(self.S_norm, (0, len(F) - len(self.S)), 'constant')
            norm_F = np.linalg.norm(F)
            if norm_F < 1e-9:
                return False, 0.0
            cos_alpha = float(np.clip(np.dot(padded_S, F) / norm_F, -1.0, 1.0))
            if not np.isfinite(cos_alpha):
                return False, 0.0
            return cos_alpha >= self.THRESHOLD_COMPRESSION, cos_alpha

        # Gałąź główna: len(F) == len(self.S)
        norm_F = np.linalg.norm(F)
        if norm_F < 1e-9 or self.S_len < 1e-9:
            return False, 0.0

        cos_alpha = float(np.clip(np.dot(self.S_norm, F) / norm_F, -1.0, 1.0))
        if not np.isfinite(cos_alpha):
            return False, 0.0

        return cos_alpha >= self.THRESHOLD_COMPRESSION, cos_alpha

    def interpret_alignment(self, cos_alpha):
        """
        Zwraca semantyczną interpretację wartości cosinus alpha.

        Pełna mapa przedziałów (bez luk, bez nakładania):
            >= 0.995                    → KOMPRESJA     (Tożsamość)
            [0.800, 0.995)              → HARMONIA      (Zbieżność)
            [0.400, 0.800)              → KONWERGENCJA  (Umiarkowana zgodność)
            [-0.400, 0.400)             → NOWOŚĆ        (Ortogonalność)
            [-0.800, -0.400)            → DYZONANS      (Rozbieżność)
            < -0.800                    → KONFLIKT      (Przeciwieństwo)

        Granica -0.400 należy do NOWOŚCI (warunek: >= -THRESHOLD_CONVERGENCE).

        Args:
            cos_alpha (float): Cosinus kąta między S a F. Oczekiwany zakres [-1.0, 1.0].
                               Wartości NaN/Inf zwracają "BŁĄD (Nieważna wartość)".

        Returns:
            str: Nazwa kategorii alignmentu.
        """
        if not np.isfinite(cos_alpha):
            return "BŁĄD (Nieważna wartość)"

        if cos_alpha >= self.THRESHOLD_COMPRESSION:
            return "KOMPRESJA (Tożsamość)"
        elif cos_alpha >= self.THRESHOLD_HARMONY:
            return "HARMONIA (Zbieżność)"
        elif cos_alpha >= self.THRESHOLD_CONVERGENCE:
            return "KONWERGENCJA (Umiarkowana zgodność)"
        elif cos_alpha >= -self.THRESHOLD_CONVERGENCE:
            # FIX v8.3: zmiana > na >= — granica -0.4 należy do NOWOŚCI, nie DYZONANSU
            return "NOWOŚĆ (Ortogonalność)"
        elif cos_alpha >= -0.8:
            return "DYZONANS (Rozbieżność)"
        else:
            return "KONFLIKT (Przeciwieństwo)"