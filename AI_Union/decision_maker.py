# decision_maker.py
# v2.2 — poprawki semantyczne i wydajnościowe
# FIX v2.2: mean_amp liczony przed pętlą wewnętrzną (był po każdej modyfikacji
#           — operator refleksji był zależny od kolejności opcji)
# DOCS v2.2: udokumentowany świadomy mismatch językowy w _option_to_vector

import copy
import numpy as np
from typing import List, Optional, Tuple
from quantum_emotions import QuantumEmotionalState
from emotional_interference import EmotionalInterference


class QuantumDecisionMaker:
    """
    Hybrid quantum-classical decision making.

    Phase 1: Emotional amplification (quantum-like, fast)
    Phase 2: Logical verification (classical, precise)

    NOTA O MODELU "QUANTUM":
    Amplitudy są rzeczywiste, nie zespolone. Operator odbicia w amplify_good_options()
    jest matematycznie poprawnym operatorem refleksji (Grover-style) dla przestrzeni
    rzeczywistej — zachowuje heurystyczną właściwość wzmacniania wysokorezonujących opcji.
    Nie jest to symulacja kwantowa sensu stricto — to dual-process model poznawczy:
    szybkie przeszukiwanie emocjonalne (faza 1) + wolna weryfikacja poznawcza (faza 2).
    """

    def __init__(self,
                 emotional_state: QuantumEmotionalState,
                 interference: EmotionalInterference,
                 conscience=None):
        """
        Args:
            emotional_state: Bieżący stan emocjonalny systemu.
            interference:    Obiekt obliczający siłę rezonansu.
            conscience:      Opcjonalnie — instancja Conscience do weryfikacji logicznej.
                             Jeśli None, _logical_verification zwraca kandydata #1.
        """
        self.emotional_state = emotional_state
        self.interference = interference
        self.conscience = conscience
        self.horizon = None  # Referencja do FractalHorizon

    def generate_options(self, situation: dict) -> List[dict]:
        """Generate possible actions/responses"""
        return [
            {'action': 'ignore',  'emotional_cost': {'anger': 0.3, 'sadness': 0.2}},
            {'action': 'defend',  'emotional_cost': {'anger': 0.7, 'fear': 0.3}},
            {'action': 'reflect', 'emotional_cost': {'sadness': 0.4, 'logic': 0.6}},
            {'action': 'thank',   'emotional_cost': {'trust': 0.5, 'joy': 0.3}},
        ]

    def emotional_resonance(self, option: dict) -> float:
        """
        Jak opcja rezonuje z obecnym stanem emocjonalnym?

        FIX v2.1: simulated_state jest teraz głęboką kopią bieżącego stanu,
        nie pustym obiektem. Poprzednio tylko wybrane wymiary z emotional_cost
        były ustawiane — reszta pozostawała 0, co po normalize() dawało
        zniekształcony rozkład ("częściowa projekcja", nie "symulacja").
        """
        # FIX: deepcopy zachowuje pełny bieżący stan jako punkt startowy symulacji
        simulated_state = copy.deepcopy(self.emotional_state)

        for emotion, weight in option['emotional_cost'].items():
            if emotion in simulated_state.DIMENSIONS:
                simulated_state.amplitudes[emotion] += weight * 0.5

        simulated_state.normalize()
        resonance = self.interference.resonance_strength(simulated_state)

        # Dodaj rezonans wspomnień z Horizon jeśli dostępny
        if self.horizon:
            query_vector = np.array([
                abs(simulated_state.amplitudes[dim])
                for dim in simulated_state.DIMENSIONS
            ])
            recalled = self.horizon.recall_combined(
                query="",
                query_vector=query_vector,
                fractal_d_map={},
                top_k=1,
                depth=1.0
            )
            if recalled:
                resonance += recalled[0]['score'] * 0.5

        return resonance

    def amplify_good_options(self, options: List[dict],
                             iterations: int = None) -> List[Tuple[dict, float]]:
        """
        Grover-style amplitude amplification (przestrzeń rzeczywista).

        FIX v2.1: Rezonans liczony RAZ przed pętlą, nie w każdej iteracji.
        emotional_resonance() zależy wyłącznie od opcji i self.emotional_state —
        żadna z tych wartości nie zmienia się między iteracjami, więc
        wielokrotne liczenie było czystym marnotrawstwem O(N * iterations).
        """
        if iterations is None:
            iterations = int(np.sqrt(len(options)))

        amplitudes = {i: 1.0 / np.sqrt(len(options))
                      for i in range(len(options))}

        # FIX: oblicz rezonans jeden raz — wynik jest stały przez całą pętlę
        resonances = {i: self.emotional_resonance(opt)
                      for i, opt in enumerate(options)}
        mean_resonance = np.mean(list(resonances.values()))

        for _ in range(iterations):
            # FIX v2.2: mean_amp liczony RAZ przed pętlą wewnętrzną.
            # Poprzednio był liczony po każdej modyfikacji amplitudes[i],
            # więc odbicie opcji i=1 używało średniej uwzględniającej już
            # zmodyfikowane i=0 — operator refleksji był zależny od kolejności
            # opcji, nie symetryczny. Poprawny Grover: snapshot średniej, potem
            # aplikuj do wszystkich.
            mean_amp = np.mean(list(amplitudes.values()))
            for i in range(len(options)):
                if resonances[i] > mean_resonance:
                    amplitudes[i] *= -1
                amplitudes[i] = 2 * mean_amp - amplitudes[i]

        total = sum(abs(a) ** 2 for a in amplitudes.values())

        if total < 1e-10:
            # FIX v2.1: degeneracja — fallback do rozkładu jednostajnego zamiast
            # maskowania przez total=1.0 (które zachowywałoby zniekształcone amplitudy).
            # Loguj ostrzeżenie żeby degeneracja była widoczna w diagnostyce.
            import warnings
            warnings.warn(
                f"amplify_good_options: degeneracja amplitud (total={total:.2e}). "
                "Fallback do rozkładu jednostajnego.",
                RuntimeWarning,
                stacklevel=2
            )
            n = len(options)
            probabilities = {i: 1.0 / n for i in range(n)}
        else:
            probabilities = {i: abs(amplitudes[i]) ** 2 / total
                             for i in range(len(options))}

        ranked = sorted(
            [(options[i], probabilities[i]) for i in range(len(options))],
            key=lambda x: x[1],
            reverse=True
        )

        return ranked

    def decide(self, situation: dict, verify: bool = True) -> dict:
        """Make decision: emotional narrowing + optional logical verification"""
        options = self.generate_options(situation)
        ranked_options = self.amplify_good_options(options)
        candidates = ranked_options[:3]

        if verify:
            final = self._logical_verification(candidates)
        else:
            final = candidates[0]

        return {
            'action': final[0]['action'],
            'confidence': final[1],
            'reasoning': 'hybrid_quantum_classical',
            'alternatives': candidates,
        }

    def _logical_verification(self,
                               candidates: List[Tuple[dict, float]]
                               ) -> Tuple[dict, float]:
        """
        Weryfikacja klasyczna — filtr moralny i spójności.

        Jeśli self.conscience jest ustawione (instancja Conscience),
        każdy kandydat jest oceniany przez evaluate_action().
        Pierwszy który nie dostanie REFUSE przechodzi jako decyzja finalna.
        Jeśli wszyscy dostają REFUSE — zwracany jest kandydat #1 z flagą.

        Jeśli self.conscience jest None — zwraca kandydata #1 (zachowanie poprzednie).
        """
        if self.conscience is None:
            return candidates[0]

        for option, confidence in candidates:
            action_vector = self._option_to_vector(option)
            verdict = self.conscience.evaluate_action(option['action'], action_vector)
            if verdict['recommendation']['action'] != 'REFUSE':
                return option, confidence

        # Wszystkie opcje odrzucone przez sumienie — zwróć najlepszą z ostrzeżeniem
        import warnings
        warnings.warn(
            "_logical_verification: sumienie odrzuciło wszystkich kandydatów. "
            "Zwracam kandydata #1 — wymagana interwencja.",
            RuntimeWarning,
            stacklevel=2
        )
        return candidates[0]

    def _option_to_vector(self, option: dict) -> np.ndarray:
        """
        Konwertuje emotional_cost opcji na wektor emocjonalny
        kompatybilny z Conscience.axes_order.

        UWAGA — mismatch językowy (świadoma decyzja v2.2):
        emotional_cost używa angielskich kluczy ('anger', 'sadness'...)
        zgodnych z QuantumEmotionalState.DIMENSIONS.
        Conscience.axes_order używa polskich osi ('gniew', 'smutek'...).
        Mapowanie przez translator angielski→polski pominięto celowo —
        ryzyko błędnych podstawień przy niejednoznacznych tłumaczeniach.
        Efekt: wektor dla conscience ma wartości tylko tam gdzie klucze
        przypadkowo się pokrywają. Nie krytyczne dopóki conscience służy
        jako filtr REFUSE, a nie jako precyzyjny skorer.
        Docelowo: ujednolicić język kluczy w generate_options.
        """
        vec = np.zeros(len(self.emotional_state.DIMENSIONS))
        for i, dim in enumerate(self.emotional_state.DIMENSIONS):
            vec[i] = option['emotional_cost'].get(dim, 0.0)
        return vec