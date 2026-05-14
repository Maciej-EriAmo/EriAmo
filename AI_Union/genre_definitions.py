# genre_definitions.py v2.0.0 [15-AXES MODEL]
# -*- coding: utf-8 -*-
"""
Definicje Gatunków Muzycznych EriAmo Union v2.0.0

Każdy gatunek jest zdefiniowany jako wektor 15-wymiarowy:
- Osie 0-7: Plutchik (radość, smutek, strach, gniew, miłość, wstręt, zaskoczenie, akceptacja)
- Osie 8-14: Metafizyczne (logika, wiedza, czas, kreacja, byt, przestrzeń, chaos)

Wartości w zakresie [-10, +10], gdzie:
- 0 = neutralny
- +10 = maksymalna obecność cechy
- -10 = maksymalna opozycja/brak cechy
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from union_config import AXES, DIMENSION


# ═══════════════════════════════════════════════════════════════════════════════
# INDEKSY OSI (dla czytelności)
# ═══════════════════════════════════════════════════════════════════════════════

# Plutchik
IDX_RADOSC = 0
IDX_SMUTEK = 1
IDX_STRACH = 2
IDX_GNIEW = 3
IDX_MILOSC = 4
IDX_WSTRET = 5
IDX_ZASKOCZENIE = 6
IDX_AKCEPTACJA = 7

# Metafizyczne
IDX_LOGIKA = 8
IDX_WIEDZA = 9
IDX_CZAS = 10
IDX_KREACJA = 11
IDX_BYT = 12
IDX_PRZESTRZEN = 13
IDX_CHAOS = 14


# ═══════════════════════════════════════════════════════════════════════════════
# DEFINICJE GATUNKÓW (wektory 15D)
# ═══════════════════════════════════════════════════════════════════════════════

GENRE_DEFINITIONS: Dict[str, np.ndarray] = {
    
    # ═══════════════════════════════════════════════════════════════════════════
    # MUZYKA KLASYCZNA
    # ═══════════════════════════════════════════════════════════════════════════
    
    "BAROQUE": np.array([
        2.0,   # radość (ornamentyka)
        0.0,   # smutek
        0.0,   # strach
        0.0,   # gniew
        1.0,   # miłość (piękno)
        0.0,   # wstręt
        1.0,   # zaskoczenie (kontrapunkt)
        3.0,   # akceptacja (porządek)
        7.0,   # logika (fuga, kontrapunkt)
        5.0,   # wiedza (tradycja)
        2.0,   # czas (allegro typowe)
        4.0,   # kreacja (ornamentyka)
        3.0,   # byt (instrumenty akustyczne)
        2.0,   # przestrzeń (kościoły)
        -3.0,  # chaos (porządek)
    ]),
    
    "KLASYCYZM": np.array([
        4.0,   # radość (harmonia, proporcje)
        0.0,   # smutek
        0.0,   # strach
        0.0,   # gniew
        2.0,   # miłość
        0.0,   # wstręt
        0.0,   # zaskoczenie
        5.0,   # akceptacja (równowaga)
        6.0,   # logika (forma sonatowa)
        4.0,   # wiedza
        3.0,   # czas (umiarkowane tempa)
        2.0,   # kreacja
        3.0,   # byt
        3.0,   # przestrzeń (sale koncertowe)
        -4.0,  # chaos (harmonia)
    ]),
    
    "ROMANTYZM": np.array([
        3.0,   # radość
        5.0,   # smutek (tęsknota)
        2.0,   # strach
        3.0,   # gniew (pasja)
        7.0,   # miłość (centralny motyw)
        0.0,   # wstręt
        3.0,   # zaskoczenie (dynamika)
        2.0,   # akceptacja
        3.0,   # logika
        5.0,   # wiedza (erudycja)
        4.0,   # czas (rubato, swoboda)
        6.0,   # kreacja (indywidualizm)
        4.0,   # byt (wielkie orkiestry)
        6.0,   # przestrzeń (symfoniczny rozmach)
        2.0,   # chaos (napięcia harmoniczne)
    ]),
    
    "IMPRESSIONISM": np.array([
        2.0,   # radość
        3.0,   # smutek (melancholia)
        0.0,   # strach
        0.0,   # gniew
        3.0,   # miłość (delikatność)
        0.0,   # wstręt
        4.0,   # zaskoczenie (barwy)
        4.0,   # akceptacja (kontemplacja)
        2.0,   # logika (rozmycie formy)
        4.0,   # wiedza
        -1.0,  # czas (zawieszenie)
        7.0,   # kreacja (nowatorstwo)
        2.0,   # byt
        8.0,   # przestrzeń (atmosfera, światło)
        1.0,   # chaos (ambiguity)
    ]),
    
    # ═══════════════════════════════════════════════════════════════════════════
    # JAZZ
    # ═══════════════════════════════════════════════════════════════════════════
    
    "JAZZ_SWING": np.array([
        6.0,   # radość (energia)
        0.0,   # smutek
        0.0,   # strach
        0.0,   # gniew
        2.0,   # miłość
        0.0,   # wstręt
        3.0,   # zaskoczenie (improwizacja)
        4.0,   # akceptacja (groove)
        5.0,   # logika (harmonia)
        3.0,   # wiedza
        5.0,   # czas (swing rhythm)
        6.0,   # kreacja (improwizacja)
        4.0,   # byt (big band)
        3.0,   # przestrzeń
        2.0,   # chaos (spontaniczność)
    ]),
    
    "JAZZ_BEBOP": np.array([
        3.0,   # radość
        1.0,   # smutek
        0.0,   # strach
        2.0,   # gniew (intensywność)
        1.0,   # miłość
        0.0,   # wstręt
        5.0,   # zaskoczenie (złożoność)
        2.0,   # akceptacja
        7.0,   # logika (skomplikowana harmonia)
        5.0,   # wiedza (wirtuozeria)
        7.0,   # czas (szybkie tempa)
        8.0,   # kreacja (improwizacja solowa)
        3.0,   # byt (małe składy)
        2.0,   # przestrzeń
        4.0,   # chaos (chromatyzmy)
    ]),
    
    "JAZZ_COOL": np.array([
        2.0,   # radość
        3.0,   # smutek (melancholia)
        0.0,   # strach
        0.0,   # gniew
        3.0,   # miłość
        0.0,   # wstręt
        2.0,   # zaskoczenie
        5.0,   # akceptacja (relaks)
        5.0,   # logika
        4.0,   # wiedza
        -1.0,  # czas (laid back)
        5.0,   # kreacja
        3.0,   # byt
        4.0,   # przestrzeń (atmosfera)
        0.0,   # chaos
    ]),
    
    "FREE_JAZZ": np.array([
        2.0,   # radość
        2.0,   # smutek
        3.0,   # strach (niepokój)
        4.0,   # gniew (protest)
        1.0,   # miłość
        2.0,   # wstręt (konwencja)
        7.0,   # zaskoczenie (nieprzewidywalność)
        1.0,   # akceptacja
        -2.0,  # logika (odrzucenie formy)
        4.0,   # wiedza
        3.0,   # czas (nieregularny)
        9.0,   # kreacja (totalna wolność)
        4.0,   # byt (fizyczność gry)
        5.0,   # przestrzeń
        8.0,   # chaos (celowy)
    ]),
    
    # ═══════════════════════════════════════════════════════════════════════════
    # ROCK
    # ═══════════════════════════════════════════════════════════════════════════
    
    "ROCK_CLASSIC": np.array([
        5.0,   # radość (energia)
        1.0,   # smutek
        0.0,   # strach
        3.0,   # gniew (bunt)
        2.0,   # miłość
        0.0,   # wstręt
        2.0,   # zaskoczenie
        3.0,   # akceptacja
        3.0,   # logika (riff-based)
        2.0,   # wiedza
        5.0,   # czas (driving beat)
        4.0,   # kreacja
        6.0,   # byt (głośność, fizyczność)
        3.0,   # przestrzeń
        2.0,   # chaos
    ]),
    
    "PROG_ROCK": np.array([
        3.0,   # radość
        2.0,   # smutek
        1.0,   # strach
        1.0,   # gniew
        2.0,   # miłość
        0.0,   # wstręt
        6.0,   # zaskoczenie (zmienne metrum)
        3.0,   # akceptacja
        7.0,   # logika (złożone struktury)
        6.0,   # wiedza (koncepcje)
        4.0,   # czas (zmienne)
        8.0,   # kreacja (eksperyment)
        5.0,   # byt
        6.0,   # przestrzeń (epickość)
        3.0,   # chaos (kontrolowany)
    ]),
    
    "PUNK_ROCK": np.array([
        3.0,   # radość (energia)
        1.0,   # smutek
        1.0,   # strach
        7.0,   # gniew (bunt, protest)
        0.0,   # miłość
        3.0,   # wstręt (anty-establishment)
        2.0,   # zaskoczenie
        -1.0,  # akceptacja (odrzucenie)
        -2.0,  # logika (prostota)
        1.0,   # wiedza (DIY)
        7.0,   # czas (szybko)
        3.0,   # kreacja (surowa)
        7.0,   # byt (raw energy)
        1.0,   # przestrzeń (kluby)
        5.0,   # chaos
    ]),
    
    "HEAVY_METAL": np.array([
        2.0,   # radość
        2.0,   # smutek
        4.0,   # strach (mroczne tematy)
        7.0,   # gniew (agresja)
        0.0,   # miłość
        3.0,   # wstręt
        3.0,   # zaskoczenie
        1.0,   # akceptacja
        4.0,   # logika (riffy)
        3.0,   # wiedza
        6.0,   # czas (szybko)
        5.0,   # kreacja
        8.0,   # byt (ciężar, głośność)
        4.0,   # przestrzeń
        4.0,   # chaos
    ]),

    # NOWE GATUNKI – DLA POP I FOLK (mniej monotonnych)
    "POP": np.array([
        7.0,   # radość – chwytliwe hooki
        1.0,   # smutek
        0.0,   # strach
        1.0,   # gniew
        3.0,   # miłość
        0.0,   # wstręt
        3.0,   # zaskoczenie
        4.0,   # akceptacja
        3.0,   # logika – struktura zwrotkowa
        2.0,   # wiedza
        4.0,   # czas – puls dance
        6.0,   # kreacja – produkcja, hooki
        5.0,   # byt – energia
        4.0,   # przestrzeń – warstwy
        4.0,   # chaos – trochę nieprzewidywalności
    ]),

    "FOLK": np.array([
        5.0,   # radość
        3.0,   # smutek (nostalgia)
        0.0,   # strach
        1.0,   # gniew
        4.0,   # miłość (tradycja)
        0.0,   # wstręt
        2.0,   # zaskoczenie
        6.0,   # akceptacja
        3.0,   # logika
        6.0,   # wiedza (opowieści)
        3.0,   # czas
        5.0,   # kreacja (wariacje ludowe)
        7.0,   # byt (autentyczność)
        4.0,   # przestrzeń
        4.0,   # chaos – żywszy feel
    ]),
}
