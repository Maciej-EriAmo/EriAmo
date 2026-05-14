# emotional_interference.py
# v1.1 — poprawki semantyczne

import copy
import numpy as np
from typing import Dict
from quantum_emotions import QuantumEmotionalState


class EmotionalInterference:
    """
    Modeluje jak emocje wpływają na siebie (interference).

    Konstruktywna: joy + trust → wzmocnienie
    Destruktywna:  joy + fear → napięcie
    """

    def __init__(self):
        # Macierz interferencji (można uczyć z doświadczenia)
        # interference[A][B] = jak silnie A wpływa na B
        self.interference_matrix = self._initialize_interference()

    def _initialize_interference(self) -> Dict[str, Dict[str, float]]:
        """
        Bazowa macierz interferencji.

        Wartości [-1, 1]:
        +1 = konstruktywna (wzmacniają się)
        -1 = destruktywna  (osłabiają się)
         0 = neutralna
        """
        dims = QuantumEmotionalState.DIMENSIONS
        interference = {dim: {d: 0.0 for d in dims} for dim in dims}

        positive_pairs = [
            ('joy', 'trust'), ('joy', 'anticipation'),
            ('trust', 'being'), ('logic', 'knowledge'),
            ('creation', 'anticipation'), ('space', 'time'),
        ]

        negative_pairs = [
            ('joy', 'sadness'), ('joy', 'fear'),
            ('trust', 'disgust'), ('logic', 'chaos'),
            ('being', 'chaos'), ('fear', 'trust'),
        ]

        for a, b in positive_pairs:
            interference[a][b] = 0.7
            interference[b][a] = 0.7

        for a, b in negative_pairs:
            interference[a][b] = -0.7
            interference[b][a] = -0.7

        return interference

    def apply_interference(self, state: QuantumEmotionalState,
                           time_step: float = 0.1) -> QuantumEmotionalState:
        """
        Zastosuj interference — emocje wpływają na siebie.

        FIX v1.1: Poprzednio new_state = QuantumEmotionalState() tworzył obiekt
        z 15 losowymi amplitudami zespolonymi, które były natychmiast w całości
        nadpisywane przez pętlę (wszystkie DIMENSIONS są pokryte). Losowa
        inicjalizacja była semantycznie myląca i marnowała CPU.
        Teraz używamy deepcopy stanu wejściowego jako nośnika struktury,
        a następnie nadpisujemy wszystkie amplitudy obliczonymi wartościami.
        Wynik numeryczny jest identyczny — zmiana jest semantyczna i czytelna.
        """
        new_state = copy.deepcopy(state)

        for emotion in state.DIMENSIONS:
            current_amp = state.amplitudes[emotion]
            influence = 0j

            for other_emotion in state.DIMENSIONS:
                if other_emotion == emotion:
                    continue
                other_amp = state.amplitudes[other_emotion]
                coupling = self.interference_matrix[other_emotion][emotion]
                influence += coupling * other_amp * time_step

            new_state.amplitudes[emotion] = current_amp + influence

        new_state.normalize()
        return new_state

    def resonance_strength(self, state: QuantumEmotionalState) -> float:
        """
        Mierz jak "rezonujące" są emocje — iloczyn skalarny amplitud zespolonych
        ważony macierzą interferencji.

        FIX v1.1: Poprzednio dedulikacja par używała `em1 >= em2` (porównanie
        stringów). Działało poprawnie (macierz symetryczna, każda para liczona raz),
        ale kolejność zależała od porządku leksykograficznego nazw, nie od
        kolejności w DIMENSIONS — kruche i nieczytelne.
        Teraz używamy indeksów: for i, em1 / for em2 in DIMENSIONS[i+1:].
        """
        total_resonance = 0.0
        dims = state.DIMENSIONS

        for i, em1 in enumerate(dims):
            for em2 in dims[i + 1:]:
                amp1 = state.amplitudes[em1]
                amp2 = state.amplitudes[em2]
                coupling = self.interference_matrix[em1][em2]

                interference = np.real(amp1 * np.conj(amp2)) * coupling
                total_resonance += interference

        return total_resonance