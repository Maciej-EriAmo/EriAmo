# -*- coding: utf-8 -*-
"""
kurz.py v8.4.1
System odruchów w pełni zsynchronizowany z UnionConfig.

ZMIANY v8.4.1:
- Dodano scan_all() — zwraca pełny wektor emocjonalny ze wszystkimi trafionymi
  sektorami. Koszt identyczny z quick_scan (ta sama pętla), ale nie wyrzuca
  pozostałych wyników. Używane w głównej interakcji aii.py dla bogatszego vec_k.
- FIX: quick_scan nie wywołuje już text.lower() — pattern ma re.IGNORECASE,
  podwójne obniżanie było zbędną redundancją.
- quick_scan zostaje bez zmian dla /read, /remember, /activate (dominant sektor).

ZMIANY v8.4.0:
- BUGFIX: _seed_basic_triggers() miało tylko 6 osi na 15
  Dodano triggery dla: wstręt, zaskoczenie, wiedza, logika,
  czas, kreacja, byt, przestrzeń, chaos
"""
import re
import numpy as np
from union_config import UnionConfig

class Kurz:
    def __init__(self):
        self.SECTORS = UnionConfig.AXES
        self.TRIGGERS = {sector: [] for sector in self.SECTORS}
        self._seed_basic_triggers()
        self.compiled_patterns = {}
        self._recompile_patterns()

    def _seed_basic_triggers(self):
        """Triggery dla wszystkich 15 osi."""
        basic = {
            'radość': [
                'radość', 'szczęście', 'super', 'uśmiech', 'cieszę', 'wesoły',
                'śmiech', 'zabawa', 'hurra', 'świetnie', 'cudownie', 'doskonale',
                'radosny', 'euforia', 'entuzjazm', 'spełnienie',
            ],
            'smutek': [
                'smutek', 'płacz', 'żal', 'strata', 'smutno', 'smutny',
                'depresja', 'melancholia', 'tęsknota', 'żałoba', 'rozpacz',
                'boleśnie', 'cierpienie', 'łzy', 'płakać', 'zrezygnowany',
            ],
            'strach': [
                'strach', 'lęk', 'boję się', 'groza', 'przerażenie', 'panika',
                'straszny', 'straszne', 'niebezpiecznie', 'zagrożenie', 'horror',
                'przerażony', 'trwoga', 'fobie', 'niepokój', 'obawa',
            ],
            'gniew': [
                'gniew', 'złość', 'wkurzony', 'irytacja', 'wściekłość', 'furia',
                'wkurza', 'wnerwiać', 'nienawiść', 'zły', 'agresja',
                'wściekły', 'wkurwiony', 'zdenerwowany', 'frustracja',
            ],
            'miłość': [
                'miłość', 'kocham', 'troska', 'przywiązanie', 'kochać', 'serce',
                'czułość', 'romantyczny', 'zakochany', 'uczucie', 'bliskość',
                'kochanie', 'darzyć', 'uwielbiać', 'adorować', 'namiętność',
            ],
            'wstręt': [
                'wstręt', 'obrzydzenie', 'obrzydliwy', 'wstrętny', 'ohyda',
                'obrzydza', 'mdłości', 'wymiotować', 'plugawy', 'brudny',
                'śmierdzący', 'obleśny', 'obrzydliwość', 'odpychający', 'fuj',
                'niesmak', 'odrzucenie', 'toksyczny',
            ],
            'zaskoczenie': [
                'zaskoczenie', 'zaskoczony', 'nieoczekiwany', 'niespodziewany',
                'szok', 'wow', 'naprawdę', 'niemożliwe', 'nie do wiary',
                'zdumienie', 'zdumiony', 'zdumiewa', 'niezwykłe', 'dziwne',
                'niesamowite', 'o rany', 'ojej', 'nagle', 'niespodziewanie',
            ],
            'akceptacja': [
                'akceptacja', 'rozumiem', 'dobrze', 'zgoda', 'akceptuję',
                'przyjmuję', 'zgadzam się', 'tak jest', 'oczywiste',
                'naturalnie', 'pewnie', 'spokój', 'harmonia', 'równowaga',
            ],
            'wiedza': [
                'wiedza', 'wiedzieć', 'poznać', 'nauka', 'uczenie', 'rozumieć',
                'informacja', 'fakty', 'prawda', 'badanie', 'odkrycie', 'teoria',
                'dane', 'analiza', 'co to jest', 'jak działa', 'dlaczego',
                'wyjaśnij', 'powiedz mi', 'opowiedz', 'wytłumacz',
            ],
            'logika': [
                'logika', 'logiczny', 'rozumowanie', 'argument', 'dowód',
                'wnioskowanie', 'analiza', 'matematyka', 'algorytm', 'system',
                'struktura', 'zasada', 'reguła', 'definicja', 'kategoria',
                'klasyfikacja', 'porównanie', 'różnica', 'podobieństwo',
            ],
            'czas': [
                'czas', 'kiedy', 'teraz', 'przeszłość', 'przyszłość', 'historia',
                'wczoraj', 'jutro', 'dzisiaj', 'moment', 'chwila', 'epoka',
                'era', 'wiek', 'rok', 'godzina', 'sekunda', 'przemijanie',
                'wieczność', 'tymczasowy', 'dawno', 'wkrótce', 'trwanie',
            ],
            'kreacja': [
                'kreacja', 'tworzę', 'tworzy', 'tworzymy', 'tworzyć', 'twórczość',
                'sztuka', 'muzyka', 'malowanie', 'pisanie', 'projekt', 'pomysł',
                'innowacja', 'wynalazek', 'kompozycja', 'design', 'architektura',
                'poezja', 'literatura', 'film', 'fotografia', 'taniec', 'kreować',
                'tworzenie', 'artystyczny', 'kreatywny', 'stwarzać',
            ],
            'byt': [
                'byt', 'istnienie', 'istnieć', 'być', 'rzeczywistość', 'świadomość',
                'dusza', 'duch', 'sens', 'cel', 'filozofia', 'egzystencja',
                'tożsamość', 'kim jestem', 'ontologia', 'metafizyka', 'życie',
                'śmierć', 'transcendencja', 'nieskończoność', 'absolut',
            ],
            'przestrzeń': [
                'przestrzeń', 'kosmos', 'wszechświat', 'galaktyka', 'gwiazdy',
                'planeta', 'niebo', 'horyzont', 'dal', 'bezkres', 'otchłań',
                'głębia', 'szerokość', 'rozległość', 'pustynia', 'ocean',
                'powietrze', 'wolność', 'otwartość', 'przestronny',
            ],
            'chaos': [
                'chaos', 'bałagan', 'nieporządek', 'zamęt', 'zamieszanie',
                'entropia', 'losowość', 'przypadek', 'nieprzewidywalność',
                'turbulencja', 'kryzys', 'katastrofa', 'rozpad', 'dezorganizacja',
                'szaleństwo', 'absurd', 'bezład', 'anarchia', 'burza',
            ],
        }
        for sector, words in basic.items():
            if sector in self.TRIGGERS:
                self.TRIGGERS[sector].extend(words)

    def _recompile_patterns(self):
        self.compiled_patterns = {}
        for sector, words in self.TRIGGERS.items():
            if not words:
                continue
            sorted_words = sorted(list(set(words)), key=len, reverse=True)
            pattern_str = r'\b(' + '|'.join(map(re.escape, sorted_words)) + r')\b'
            self.compiled_patterns[sector] = re.compile(
                pattern_str, re.IGNORECASE | re.UNICODE
            )

    def scan_all(self, text):
        """
        Zwraca pełny wektor emocjonalny ze wszystkimi trafionymi sektorami.

        Koszt identyczny z quick_scan — ta sama pętla, po prostu nie wyrzucamy
        pozostałych wyników. Każde dopasowanie idzie na swoją oś.

        Użycie: główna interakcja aii.py — buduje bogaty vec_k zamiast
        jednej aktywnej osi. quick_scan zostaje dla /read, /remember,
        /activate gdzie wystarczy dominant sektor do indeksowania.

        Returns:
            np.ndarray: wektor [0.0, 1.0] per sektor, len = len(SECTORS)
        """
        vec = np.zeros(len(self.SECTORS))
        if not text or not text.strip():
            return vec
        for i, sector in enumerate(self.SECTORS):
            pattern = self.compiled_patterns.get(sector)
            if not pattern:
                continue
            matches = pattern.findall(text)  # IGNORECASE w pattern, .lower() zbędne
            if matches:
                vec[i] = min(1.0, len(matches) * 0.7)
        return vec

    def quick_scan(self, text):
        """Zwraca dominujący sektor i jego intensywność. Szybki sorter."""
        if not text or not text.strip():
            return None, 0.0
        best_sector, max_matches = None, 0
        for sector, pattern in self.compiled_patterns.items():
            matches = pattern.findall(text)  # FIX v8.4.1: IGNORECASE w pattern, .lower() zbędne
            if len(matches) > max_matches:
                max_matches = len(matches)
                best_sector = sector
        if best_sector:
            return best_sector, min(1.0, max_matches * 0.7)
        return None, 0.0

    def add_trigger(self, sector, word):
        if sector in self.TRIGGERS:
            if word.lower() not in self.TRIGGERS[sector]:
                self.TRIGGERS[sector].append(word.lower())
                return True
        return False

    def get_all_triggers_count(self):
        return sum(len(words) for words in self.TRIGGERS.values())