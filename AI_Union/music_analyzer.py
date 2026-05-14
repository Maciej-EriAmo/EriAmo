# music_analyzer.py v8.0.0 [15-AXES MIGRATION]
# -*- coding: utf-8 -*-
"""
Analizator Muzyczny EriAmo v8.0.0
PEŁNA MIGRACJA do architektury 15-osiowej (union_config.py)

Zmiany względem v5.9.1:
- Usunięto nieistniejące osie: emocje, affections, etyka, improwizacja
- Mapowanie cech na 15 osi (8 Plutchik + 7 metafizycznych)
- Naprawiono literówkę: przestrzen → przestrzeń
"""

import numpy as np
from union_config import AXES, DIMENSION, EPHEMERAL_AXES, PERSISTENT_AXES, Colors


class MusicAnalyzer:
    """
    Analizator przekształcający cechy muzyczne na wektory wpływu 15D.
    
    Model 15 osi:
    - Biologiczne (0-7): radość, smutek, strach, gniew, miłość, wstręt, zaskoczenie, akceptacja
    - Metafizyczne (8-14): logika, wiedza, czas, kreacja, byt, przestrzeń, chaos
    """
    
    # Mapowanie nazw osi na indeksy
    AXES_MAP = {axis: i for i, axis in enumerate(AXES)}
    AXES_COUNT = DIMENSION  # 15
    
    # ═══════════════════════════════════════════════════════════════════════════
    # WSPÓŁCZYNNIKI MAPOWANIA CECH MUZYCZNYCH NA 15 OSI
    # ═══════════════════════════════════════════════════════════════════════════
    
    COEFFICIENTS = {
        # ═══════════════════════════════════════════════════════════════════════
        # LOGIKA (indeks 8) - Struktura, forma, porządek
        # ═══════════════════════════════════════════════════════════════════════
        "FUGA": (8, 7.0),           # Szczyt logiki muzycznej
        "KANON": (8, 5.0),          # Ścisła imitacja
        "MENUET": (8, 2.5),         # Forma taneczna
        "ZLOZONY": (8, 3.0),        # Złożona struktura
        "MATH": (8, 8.0),           # Math rock
        "JAZZ": (8, 6.0),           # Złożona harmonia
        "PUNK": (8, -2.0),          # Prostota
        "PROSTY": (8, -1.0),        # Minimalna struktura
        
        # ═══════════════════════════════════════════════════════════════════════
        # WIEDZA (indeks 9) - Tradycja, historia, erudycja
        # ═══════════════════════════════════════════════════════════════════════
        "BAROQUE": (9, 3.0),
        "KLASYCYZM": (9, 4.0),
        "ROMANTYZM": (9, 4.0),
        "HISTORYCZNY": (9, 5.0),
        
        # ═══════════════════════════════════════════════════════════════════════
        # CZAS (indeks 10) - Tempo, rytm, puls
        # ═══════════════════════════════════════════════════════════════════════
        "ALLEGRO": (10, 3.0),
        "PRESTO": (10, 5.0),
        "ADAGIO": (10, -3.0),
        "ROCK": (10, 4.0),
        "POP": (10, 2.0),
        
        # ═══════════════════════════════════════════════════════════════════════
        # KREACJA (indeks 11) - Twórczość, improwizacja, nowatorstwo
        # ═══════════════════════════════════════════════════════════════════════
        "IMPROWIZACJA": (11, 4.0),
        "PROG_ROCK": (11, 7.0),
        "EKSPERYMENTALNY": (11, 6.0),
        "AVANT_GARDE": (11, 8.0),
        
        # ═══════════════════════════════════════════════════════════════════════
        # BYT (indeks 12) - Fizyczność, obecność, ciężar
        # ═══════════════════════════════════════════════════════════════════════
        "LIVE": (12, 5.0),
        "RAW": (12, 4.0),
        "ACOUSTIC": (12, 3.0),
        "BASS": (12, 4.0),
        "HEAVY": (12, 5.0),
        "SYNTH": (12, -2.0),
        "DIGITAL": (12, -3.0),
        "LOFI": (12, 2.0),
        
        # ═══════════════════════════════════════════════════════════════════════
        # PRZESTRZEŃ (indeks 13) - Reverb, głębia, rozmach
        # ═══════════════════════════════════════════════════════════════════════
        "AMBIENT": (13, 4.0),
        "REVERB": (13, 3.0),
        "ORKIESTROWY": (13, 5.0),
        "KOSMICZNY": (13, 8.0),
        "ECHO": (13, 4.0),
        "STEREO": (13, 2.0),
        "KATEDRALNY": (13, 6.0),
        
        # ═══════════════════════════════════════════════════════════════════════
        # CHAOS (indeks 14) - Entropia, nieprzewidywalność
        # ═══════════════════════════════════════════════════════════════════════
        "CHAOS": [
            (8, -6.0),    # Burzy logikę
            (11, 4.0),    # Rodzi kreatywność
            (14, 10.0)    # Maksymalny chaos
        ],
        "DISSONANCE": (14, 3.0),
        "NOISE": (14, 5.0),
        "HARMONIA": (14, -3.0),  # Przeciwieństwo chaosu
        
        # ═══════════════════════════════════════════════════════════════════════
        # RADOŚĆ (indeks 0) - Pozytywne emocje, energia
        # ═══════════════════════════════════════════════════════════════════════
        "WESOLY": (0, 5.0),
        "RADOSC": (0, 6.0),
        "EUFORIA": (0, 10.0),
        "EKSTAZA": (0, 15.0),
        "TRIUMF": (0, 8.0),
        
        # ═══════════════════════════════════════════════════════════════════════
        # SMUTEK (indeks 1) - Melancholia, żal
        # ═══════════════════════════════════════════════════════════════════════
        "MELANCHOLIA": (1, 5.0),
        "SMUTEK": (1, 6.0),
        "LAMENTOSO": (1, 8.0),
        "TRAGEDIA": (1, 10.0),
        "NOSTALGICZNY": (1, 4.0),
        "REQUIEM": [
            (1, 7.0),     # Smutek
            (12, 4.0),    # Byt (śmiertelność)
            (13, 5.0)     # Przestrzeń (sakralność)
        ],
        
        # ═══════════════════════════════════════════════════════════════════════
        # STRACH (indeks 2) - Lęk, niepokój, napięcie
        # ═══════════════════════════════════════════════════════════════════════
        "DARK": (2, 4.0),
        "HORROR": (2, 7.0),
        "SUSPENSE": (2, 5.0),
        "DRAMATYCZNY": [
            (2, 3.0),     # Strach/napięcie
            (3, 2.0)      # Gniew/intensywność
        ],
        
        # ═══════════════════════════════════════════════════════════════════════
        # GNIEW (indeks 3) - Agresja, moc, intensywność
        # ═══════════════════════════════════════════════════════════════════════
        "GNIEW": (3, 8.0),
        "AGRESJA": (3, 10.0),
        "CON_FUOCO": (3, 6.0),
        "HEAVY_METAL": [
            (3, 6.0),     # Gniew
            (12, 5.0),    # Byt (ciężar)
            (10, 5.0)     # Czas (szybkość)
        ],
        "PUNK_ROCK": [
            (3, 5.0),     # Gniew (bunt)
            (14, 4.0),    # Chaos
            (10, 6.0)     # Czas (szybkość)
        ],
        
        # ═══════════════════════════════════════════════════════════════════════
        # MIŁOŚĆ (indeks 4) - Czułość, ciepło, bliskość
        # ═══════════════════════════════════════════════════════════════════════
        "DOLCE": (4, 3.0),
        "INTYMNA": (4, 5.0),
        "ROMANTYCZNY": (4, 6.0),
        "BALLADA": [
            (4, 5.0),     # Miłość
            (1, 3.0)      # Smutek (tęsknota)
        ],
        
        # ═══════════════════════════════════════════════════════════════════════
        # WSTRĘT (indeks 5) - Obrzydzenie, odrzucenie, moralność
        # ═══════════════════════════════════════════════════════════════════════
        "SATANIC": [
            (5, 5.0),     # Wstręt (moralny)
            (14, 6.0),    # Chaos
            (2, 4.0)      # Strach
        ],
        "GRINDCORE": [
            (5, 4.0),     # Wstręt
            (3, 6.0),     # Gniew
            (14, 5.0)     # Chaos
        ],
        
        # ═══════════════════════════════════════════════════════════════════════
        # ZASKOCZENIE (indeks 6) - Nowość, nieoczekiwane
        # ═══════════════════════════════════════════════════════════════════════
        "ZASKAKUJACY": (6, 5.0),
        "UNEXPECTED": (6, 4.0),
        "TWIST": (6, 6.0),
        
        # ═══════════════════════════════════════════════════════════════════════
        # AKCEPTACJA (indeks 7) - Spokój, zgoda, harmonia wewnętrzna
        # ═══════════════════════════════════════════════════════════════════════
        "SPOKOJ": (7, 5.0),
        "MEDYTACYJNY": (7, 6.0),
        "ZEN": (7, 7.0),
        "SACRED": [
            (7, 5.0),     # Akceptacja (duchowość)
            (4, 3.0),     # Miłość
            (13, 4.0)     # Przestrzeń (sakralność)
        ],
        
        # ═══════════════════════════════════════════════════════════════════════
        # ZŁOŻONE GATUNKI (mapowanie na wiele osi)
        # ═══════════════════════════════════════════════════════════════════════
        
        "POWER_METAL": [
            (0, 6.0),     # Radość (pozytywna energia)
            (12, 4.0),    # Byt (moc)
            (10, 5.0),    # Czas (szybkość)
            (8, 3.0)      # Logika (struktura)
        ],
        
        "REGGAE": [
            (7, 4.0),     # Akceptacja (laid back)
            (0, 3.0),     # Radość (positive vibes)
            (10, -2.0)    # Czas (wolniejszy)
        ],
        
        "BLUES": [
            (1, 5.0),     # Smutek
            (4, 3.0),     # Miłość (tęsknota)
            (12, 3.0)     # Byt (autentyczność)
        ],
        
        "HEROIC": [
            (0, 5.0),     # Radość (triumf)
            (3, 3.0),     # Gniew (siła)
            (13, 4.0)     # Przestrzeń (epickość)
        ],
        
        "WZNIOSLY": [
            (7, 5.0),     # Akceptacja
            (4, 4.0),     # Miłość
            (13, 5.0)     # Przestrzeń
        ],
        
        "CHWALA": [
            (0, 7.0),     # Radość
            (7, 4.0),     # Akceptacja
            (13, 5.0)     # Przestrzeń
        ],
        
        "EPIC": [
            (0, 4.0),     # Radość
            (13, 6.0),    # Przestrzeń
            (12, 4.0)     # Byt
        ],
        
        "FOLK": [
            (7, 3.0),     # Akceptacja (tradycja)
            (9, 4.0),     # Wiedza (historia)
            (12, 3.0)     # Byt (autentyczność)
        ],
        
        "ELEKTRONIKA": [
            (11, 5.0),    # Kreacja
            (13, 4.0),    # Przestrzeń
            (12, -2.0)    # Byt (cyfrowy)
        ],
    }

    def __init__(self, core=None, logger=None):
        """
        Args:
            core: Referencja do EriAmoCore (opcjonalna)
            logger: Logger do zapisu stanów (opcjonalny)
        """
        self.core = core
        self.logger = logger

    def calculate_change_vector(self, features: list) -> np.ndarray:
        """
        Oblicza wektor zmiany 15D na podstawie listy cech muzycznych.
        
        Args:
            features: Lista cech np. ['HEAVY_METAL', 'PRESTO', 'RAW']
            
        Returns:
            np.ndarray: Wektor 15-wymiarowy
        """
        F = np.zeros(self.AXES_COUNT)
        recognized = []
        unknown = []
        
        for f in features:
            key = f.upper().strip()
            if key in self.COEFFICIENTS:
                entry = self.COEFFICIENTS[key]
                
                # Obsługa pojedynczej krotki lub listy krotek
                if isinstance(entry, list):
                    for idx, val in entry:
                        F[idx] += val
                else:
                    idx, val = entry
                    F[idx] += val
                    
                recognized.append(key)
            else:
                unknown.append(key)
        
        if unknown and self.core:
            self._log(f"[UWAGA] Nierozpoznane cechy: {unknown}", "YELLOW")
            
        return F

    def analyze_and_shift(self, features: list, description: str, mode: str = "!teach"):
        """
        Analizuje cechy i aplikuje zmianę do rdzenia.
        
        Args:
            features: Lista cech muzycznych
            description: Opis zdarzenia
            mode: "!teach" (pełna zmiana) lub "!simulate" (10% siły)
        """
        if self.core:
            self.core.apply_time_based_decay()
            
        F_base = self.calculate_change_vector(features)
        scale = 0.1 if mode == "!simulate" else 1.0
        F_final = F_base * scale

        # Oblicz kompresję ontologiczną (jeśli core dostępny)
        is_compressed = False
        cos_alpha = 0.0
        
        if self.core and hasattr(self.core, 'check_ontological_compression'):
            is_compressed, cos_alpha = self.core.check_ontological_compression(F_base)
        
        emotion = self._get_emotion_interpretation(cos_alpha, F_final)

        # Aplikuj zmiany do rdzenia
        if self.core:
            for i, axis in enumerate(AXES):
                if F_final[i] != 0:
                    self.core.shift_axis(axis, "INCREMENT", F_final[i])

        # Logowanie
        self._log(f"\n{'='*50}", "CYAN")
        if is_compressed:
            self._log(f"ANALIZA (KOMPRESJA): {description}", "GRAY")
            self._log(f"Tożsamość potwierdzona (cos α = {cos_alpha:.4f}).", "GRAY")
        else:
            self._log(f"ANALIZA (NOWOŚĆ): {description}", "GREEN")
            self._log(f"Zmiana trajektorii (cos α = {cos_alpha:.4f}).", "YELLOW")
        
        self._log(f"{'='*50}", "CYAN")
        self._log(f"Cechy: {features}", "WHITE")
        self._log(f"Interpretacja: {emotion}", "MAGENTA")
        
        # Zapis do loggera (jeśli dostępny)
        if self.logger:
            self.logger.log_state(
                self.core, F_final, cos_alpha, 
                emotion, description, mode, 
                compressed=is_compressed
            )

    def _get_emotion_interpretation(self, cos_alpha: float, F_vector: np.ndarray) -> str:
        """
        Interpretuje emocjonalny charakter muzyki na podstawie wektora 15D.
        """
        # Znajdź dominującą oś
        dominant_idx = np.argmax(np.abs(F_vector))
        dominant_axis = AXES[dominant_idx]
        dominant_val = F_vector[dominant_idx]
        
        # Interpretacje dla każdej osi
        interpretations = {
            'radość': "Radość / Euforia" if dominant_val > 0 else "Brak radości",
            'smutek': "Smutek / Melancholia" if dominant_val > 0 else "Brak smutku",
            'strach': "Strach / Napięcie" if dominant_val > 0 else "Spokój",
            'gniew': "Gniew / Agresja" if dominant_val > 0 else "Łagodność",
            'miłość': "Miłość / Czułość" if dominant_val > 0 else "Chłód",
            'wstręt': "Wstręt / Odrzucenie" if dominant_val > 0 else "Akceptacja",
            'zaskoczenie': "Zaskoczenie / Nowość" if dominant_val > 0 else "Przewidywalność",
            'akceptacja': "Akceptacja / Spokój" if dominant_val > 0 else "Odrzucenie",
            'logika': "Logika / Struktura" if dominant_val > 0 else "Chaos",
            'wiedza': "Erudycja / Tradycja" if dominant_val > 0 else "Nowatorstwo",
            'czas': "Szybkość / Energia" if dominant_val > 0 else "Wolność / Spokój",
            'kreacja': "Kreatywność / Innowacja" if dominant_val > 0 else "Konwencja",
            'byt': "Fizyczność / Obecność" if dominant_val > 0 else "Eteryczność",
            'przestrzeń': "Przestrzeń / Głębia" if dominant_val > 0 else "Kameralność",
            'chaos': "Chaos / Entropia" if dominant_val > 0 else "Harmonia"
        }
        
        base_interpretation = interpretations.get(dominant_axis, "Neutralny")
        
        # Dodaj kontekst z cos_alpha
        if cos_alpha > 0.98:
            return f"{base_interpretation} (Harmonia Całkowita)"
        elif cos_alpha > 0.6:
            return f"{base_interpretation} (Zgodność)"
        elif cos_alpha > 0.2:
            return f"{base_interpretation} (Nowość)"
        elif cos_alpha > -0.2:
            return f"{base_interpretation} (Neutralność)"
        else:
            return f"{base_interpretation} (Konflikt)"

    def _log(self, message: str, color: str = "WHITE"):
        """Helper do logowania z kolorami."""
        color_map = {
            "CYAN": Colors.CYAN,
            "GREEN": Colors.GREEN,
            "YELLOW": Colors.YELLOW,
            "RED": Colors.RED,
            "MAGENTA": Colors.MAGENTA,
            "WHITE": Colors.WHITE,
            "GRAY": Colors.DIM,
        }
        c = color_map.get(color, Colors.RESET)
        print(f"{c}{message}{Colors.RESET}")

    def get_feature_info(self, feature_name: str) -> dict:
        """Zwraca informacje o cesze muzycznej."""
        key = feature_name.upper()
        if key not in self.COEFFICIENTS:
            return {"exists": False}
            
        entry = self.COEFFICIENTS[key]
        
        if isinstance(entry, list):
            # Wieloosiowa cecha
            axes_affected = [(AXES[idx], val) for idx, val in entry]
            return {
                "exists": True,
                "name": key,
                "multi_axis": True,
                "axes": axes_affected,
                "is_ephemeral": any(AXES[idx] in EPHEMERAL_AXES for idx, _ in entry)
            }
        else:
            idx, val = entry
            return {
                "exists": True,
                "name": key,
                "axis": AXES[idx],
                "value": val,
                "is_ephemeral": AXES[idx] in EPHEMERAL_AXES
            }

    def list_all_features(self) -> dict:
        """Zwraca wszystkie cechy pogrupowane według osi."""
        grouped = {axis: [] for axis in AXES}
        
        for feature, entry in self.COEFFICIENTS.items():
            if isinstance(entry, list):
                # Wieloosiowa - dodaj do głównej osi (pierwszej)
                idx, val = entry[0]
            else:
                idx, val = entry
                
            axis = AXES[idx]
            grouped[axis].append((feature, val))
        
        # Sortuj po wartości
        for axis in grouped:
            grouped[axis].sort(key=lambda x: x[1], reverse=True)
            
        return grouped

    def get_axes_summary(self) -> str:
        """Zwraca podsumowanie modelu 15 osi."""
        summary = [
            "=" * 60,
            "MODEL 15 OSI - Music Analyzer v8.0.0",
            "=" * 60,
            "",
            "OSIE BIOLOGICZNE (Plutchik, 0-7):",
        ]
        
        for i, axis in enumerate(AXES[:8]):
            eph = "⚡" if axis in EPHEMERAL_AXES else "  "
            summary.append(f"  [{i}] {axis:12s} {eph}")
        
        summary.append("")
        summary.append("OSIE METAFIZYCZNE (8-14):")
        
        for i, axis in enumerate(AXES[8:], start=8):
            eph = "⚡" if axis in EPHEMERAL_AXES else "  "
            summary.append(f"  [{i}] {axis:12s} {eph}")
        
        summary.append("")
        summary.append("⚡ = efemeryczna (szybko wygasa)")
        summary.append("=" * 60)
        
        return "\n".join(summary)


# ═══════════════════════════════════════════════════════════════════════════════
# TEST
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("TEST: Music Analyzer v8.0.0 (15 osi)")
    print("=" * 60)
    
    analyzer = MusicAnalyzer()
    
    # Podsumowanie modelu
    print(analyzer.get_axes_summary())
    
    # Test 1: Heavy Metal
    print("\n[TEST 1] Heavy Metal:")
    vec = analyzer.calculate_change_vector(['HEAVY_METAL', 'PRESTO', 'RAW'])
    print(f"  Wektor: {vec}")
    print(f"  Dominanta: {AXES[np.argmax(vec)]} = {np.max(vec):.1f}")
    
    # Test 2: Ambient
    print("\n[TEST 2] Ambient:")
    vec = analyzer.calculate_change_vector(['AMBIENT', 'MEDYTACYJNY', 'KOSMICZNY'])
    print(f"  Wektor: {vec}")
    print(f"  Dominanta: {AXES[np.argmax(vec)]} = {np.max(vec):.1f}")
    
    # Test 3: Info o cesze
    print("\n[TEST 3] Info o POWER_METAL:")
    info = analyzer.get_feature_info('POWER_METAL')
    print(f"  {info}")
    
    print("\n✅ Testy zakończone!")