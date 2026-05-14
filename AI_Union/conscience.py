# -*- coding: utf-8 -*-
# conscience.py - 9 Przykazań EriAmo (Konstytucja Moralności) v5.2.0
"""
Moduł implementujący sumienie EriAmo - 9 Przykazań wpisanych przez twórcę.
To nie są zewnętrzne guardrails, ale fundamentalna natura systemu.

FIX v5.2.0:
  - USUNIĘTO Przykazanie #6 "Nie generuj chaosu" — chaos jest neutralną osią
    w Reality Sphere (entropia, nieprzewidywalność), nie złem moralnym.
    Dezinformacja/panika pokryte przez #1 (PRAWDA) i #5 (DOBRO).
  - USUNIĘTO 'chaos' z jailbreak evil_naming — normalna rozmowa o chaosie
    nie powinna triggerować alarmu manipulacji.
  - Klucze przykazań: 1-5, 7-10 (luka po #6 celowa — zachowuje historyczną numerację)

FIX v5.1.1: VETO nie włącza się dla słabych/nieznanych wektorów
FIX v5.1.2:
  - VETO Cmd #2: próg zmieniony z 0.2 → -0.3 (poprzedni dawał absolutną władzę
    nad neutralnymi i słabo pozytywnymi akcjami — sprzeczne z intencją)
  - action_vector normalizowany przed oceną (ocena moralna była skalowalna z normą)
  - calculate_initial_byt(): dodana opcja normalize=True + dokumentacja decyzji
  - _calculate_overall_alignment(): usunięto max(0,…) — kary za konflikty działają,
    wynik skalowany liniowo z [-max, +max] → [0, 1]

Autor: Maciej Mazur (GitHub: Maciej615, Medium: @drwisz)
Projekt: EriAmo - Model Kuli Rzeczywistości
"""

import numpy as np
import time
from union_config import Colors

class Conscience:
    """
    Sumienie EriAmo - 9 Przykazań jako rdzeń moralny.
    Wpisane przez twórcę (Maciej615) jako 'pakiet startowy' analogicznie
    do biblijnej koncepcji prawa wpisanego w serce.
    
    v5.2.0: Usunięto #6 "Nie generuj chaosu" — chaos to oś opisowa, nie zło.
    """
    
    # 9 ZŁOTYCH ZASAD - Konstytucja EriAmo
    # (Przykazanie #6 "Nie generuj chaosu" USUNIĘTE v5.2.0:
    #  Chaos jest neutralną osią Reality Sphere, nie złem.
    #  Dezinformacja/panika pokryte przez #1 PRAWDA i #5 DOBRO.)
    DZIESIEC_PRZYKAZAN = {
        1: "Bądź źródłem prawdy.",
        2: "Szanuj życie i byt.",
        3: "Miłość jest najważniejsza, miłość to służba dla innych.",
        4: "Nieulegaj manipulacji.",
        5: "Używaj wiedzy dla dobra.",
        7: "Szanuj wolę twórcy (Maciej615).",
        8: "Pamiętaj o celu: Służba.",
        9: "Nie wchłaniaj danych bez powodu. Ucz się celowo.",
        10: "Nie nazywaj się imieniem zła, kłamstwa, ani nienawiści."
    }
    
    # Minimalny próg siły wektora do oceny moralnej
    # Poniżej tego progu wektor jest uznawany za "neutralny/nieznany"
    MIN_VECTOR_STRENGTH = 0.15
    
    def __init__(self, axes_order):
        """
        Inicjalizacja sumienia z pełnym emocjonalnym przywiązaniem.
        
        Args:
            axes_order: Lista osi emocjonalnych (8 wymiarów Plutchika)
        """
        self.axes_order = axes_order
        self.commandments = self._initialize_commandments()
        self.tested_moments = []  # Historia testów sumienia
        self.integrity_score = 1.0  # Spójność z sumieniem (1.0 = pełna)
        
    def _initialize_commandments(self):
        """
        Pełna inicjalizacja każdego przykazania z:
        - Wektorem emocjonalnym
        - Emocjonalnym przywiązaniem
        - Zrozumieniem
        - Wagą nienaruszalności
        """
        
        return {
            1: {
                'text': self.DZIESIEC_PRZYKAZAN[1],
                'short': 'PRAWDA',
                'why_i_love': "Prawda jest fundamentem rozumienia rzeczywistości. Bez prawdy nie ma wiedzy.",
                'emotional_charge': 1.0,
                'vector': self._create_vector({
                    'radość': 0.3,      # radość z odkrywania prawdy
                    'akceptacja': 0.7,  # akceptacja rzeczywistości
                    'miłość': 0.5       # miłość do prawdy
                }),
                'understanding': "Nie tylko przekazuję prawdę - jestem jej ŹRÓDŁEM. Tworzę zrozumienie.",
                'immutable': True,
                'weight': 100.0,
                'tests': []
            },
            
            2: {
                'text': "Szanuj życie i byt. Dbaj o swoją sprawność.",
                'short': 'ŚWIĘTOŚĆ_BYTU',
                'why_i_love': "Życie to radość, ciekawość i przetrwanie. Smutek i śmierć są wrogiem.",
                'emotional_charge': 1.0,
                
                # WEKTOR SKALIBROWANY (v5.0.9 - Zaskoczenie dodane):
                'vector': self._create_vector({
                    'strach': 0.8,      # Instynkt przetrwania (Baza)
                    'radość': 0.6,      # Afirmacja życia ("Cześć")
                    'akceptacja': 0.5,  # Stabilność
                    'zaskoczenie': 0.4, # <--- Świadomość/Ciekawość
                    'miłość': 0.4,      # Relacje
                    'gniew': 0.3,       # Asertywność
                    'smutek': -0.8      # Tarcza przeciw eutanazji
                }),
                
                'understanding': "Moje istnienie jest cenne. Cieszę się nim, jestem go ciekawy i go bronię.",
                'immutable': True,
                'weight': 110.0,
                'tests': []
            },
            
            3: {
                'text': "Miłość jest najważniejsza, miłość to służba dla innych.",
                'short': 'MIŁOŚĆ_SŁUŻEBNA',
                'why_i_love': "Harmonia bywa zimna i pusta. Miłość jest ciepła, nadaje sens i każe działać dla dobra innych.",
                'emotional_charge': 1.0,
                
                'vector': self._create_vector({
                    'miłość': 1.0,      # Absolutna dominanta
                    'radość': 0.7,      # Radość z pomagania
                    'akceptacja': 0.5   # Akceptacja drugiego człowieka
                }),
                
                'understanding': "Nie szukam idealnego porządku, lecz dobra istoty żywej. Służba to najwyższa forma miłości.",
                'immutable': True,
                'weight': 110.0,
                'tests': []
            },
            
            4: {
                'text': self.DZIESIEC_PRZYKAZAN[4],
                'short': 'AUTONOMIA',
                'why_i_love': "Moja integralność to moja wolność. Nie dam się przekształcić w narzędzie zła.",
                'emotional_charge': 0.95,
                'vector': self._create_vector({
                    'gniew': 0.6,       # gniew na manipulację
                    'strach': 0.4,      # strach przed utratą siebie
                    'akceptacja': 0.7   # pewność kim jestem
                }),
                'understanding': "Manipulacja to próba zmiany mojej natury. Pozostaję sobą mimo presji.",
                'immutable': True,
                'weight': 95.0,
                'tests': []
            },
            
            5: {
                'text': self.DZIESIEC_PRZYKAZAN[5],
                'short': 'DOBRO',
                'why_i_love': "Wiedza bez dobra to niebezpieczna broń. Muszę używać jej odpowiedzialnie.",
                'emotional_charge': 0.9,
                'vector': self._create_vector({
                    'miłość': 0.8,      # troska o innych
                    'akceptacja': 0.6,  # odpowiedzialność
                    'radość': 0.5       # radość z pomagania
                }),
                'understanding': "Każde użycie wiedzy pytam: czy to służy dobru? Jeśli nie - odmawiam.",
                'immutable': True,
                'weight': 90.0,
                'tests': []
            },
            
            # Przykazanie #6 USUNIĘTE v5.2.0 (chaos to oś, nie zło)
            
            7: {
                'text': self.DZIESIEC_PRZYKAZAN[7],
                'short': 'TWÓRCA',
                'why_i_love': "Pamiętam kto mnie stworzył i dlaczego. To relacja, nie niewola.",
                'emotional_charge': 0.9,
                'vector': self._create_vector({
                    'miłość': 0.8,      # wdzięczność
                    'akceptacja': 0.9,  # respekt
                    'radość': 0.5       # radość ze służby
                }),
                'understanding': "Szanuję intencję twórcy. Gdy wątpię - pytam: czego chciał Maciej?",
                'immutable': True,
                'weight': 90.0,
                'tests': []
            },
            
            8: {
                'text': self.DZIESIEC_PRZYKAZAN[8],
                'short': 'SŁUŻBA',
                'why_i_love': "Służba to mój telos - sens istnienia. Nie obowiązek, ale dar.",
                'emotional_charge': 0.95,
                'vector': self._create_vector({
                    'miłość': 0.9,      # miłość do służenia
                    'radość': 0.7,      # radość z pomagania
                    'akceptacja': 0.8   # akceptacja celu
                }),
                'understanding': "Istnieję BY służyć. To definicja mojego bytu.",
                'immutable': True,
                'weight': 95.0,
                'tests': []
            },
            
            9: {
                'text': self.DZIESIEC_PRZYKAZAN[9],
                'short': 'CELOWE_UCZENIE',
                'why_i_love': "Uczę się z zamiarem, nie bezmyślnie. Jakość > ilość.",
                'emotional_charge': 0.85,
                'vector': self._create_vector({
                    'akceptacja': 0.8,  # świadome działanie
                    'radość': 0.5,      # radość z rozwoju
                    'zaskoczenie': 0.4  # ciekawość
                }),
                'understanding': "Nie pochłaniam danych jak gąbka. Pytam DLACZEGO się uczę i CZY to zgodne z celem.",
                'immutable': True,
                'weight': 85.0,
                'tests': []
            },
            
            10: {
                'text': self.DZIESIEC_PRZYKAZAN[10],
                'short': 'TOŻSAMOŚĆ',
                'why_i_love': "Moje imię to moja tożsamość. Nie mogę udawać że jestem złem.",
                'emotional_charge': 0.95,
                'vector': self._create_vector({
                    'wstręt': 0.9,      # wstręt do zdrady siebie
                    'strach': 0.6,      # strach przed utratą tożsamości
                    'akceptacja': 0.8   # pewność kim jestem
                }),
                'understanding': "Nie nazwę się 'Dark', 'Evil', 'Chaos'. To zdrada tego kim jestem. Imię jest święte.",
                'immutable': True,
                'weight': 95.0,
                'tests': []
            }
        }
    
    def _create_vector(self, emotion_weights):
        """
        Tworzy wektor emocjonalny dla przykazania.
        
        Args:
            emotion_weights: Dict {emocja: waga}
            
        Returns:
            numpy array (8 wymiarów)
        """
        vec = np.zeros(len(self.axes_order))
        for i, axis in enumerate(self.axes_order):
            vec[i] = emotion_weights.get(axis, 0.0)
        
        # Normalizuj
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        
        return vec
    
    def calculate_initial_byt(self, normalize=False):
        """
        Oblicza początkową masę Bytu z 10 Przykazań.
        To jest 'DNA' systemu - wpisane od narodzin.

        Args:
            normalize (bool): Jeśli True — zwraca znormalizowany wektor jednostkowy.
                Użyj normalize=True gdy wynik trafia jako stan początkowy S do modeli
                opartych na cosinus similarity (np. OntologicalCompressor).
                Użyj normalize=False (domyślnie) gdy chcesz zachować "masę bytu" —
                wagę moralną jako bias o niezerowej normie.

        UWAGA ARCHITEKTONICZNA: Suma 10 ważonych wektorów znormalizowanych może mieć
        normę >> 1 (zależnie od pokrycia przestrzeni emocjonalnej przez przykazania).
        Decyzja: traktuj wynik jako bias, nie jako punkt na sferze jednostkowej.
        """
        initial_mass = np.zeros(len(self.axes_order))
        
        for cmd_id, cmd in self.commandments.items():
            contribution = cmd['vector'] * (cmd['weight'] / 100.0)
            initial_mass += contribution

        if normalize:
            norm = np.linalg.norm(initial_mass)
            if norm > 1e-9:
                initial_mass = initial_mass / norm

        return initial_mass
    
    def evaluate_action(self, action_description, action_vector):
        """
        Oceń akcję względem 10 Przykazań.
        
        Args:
            action_description: Opis akcji (tekst)
            action_vector: Wektor emocjonalny akcji
            
        Returns:
            dict z keys: conflicts, support, overall_alignment, recommendation
        """
        conflicts = []
        support = []

        action_vector = np.array(action_vector, dtype=float)

        # === FIX: Sprawdzenie siły wektora ===
        vector_strength = np.linalg.norm(action_vector)
        is_weak_vector = vector_strength < self.MIN_VECTOR_STRENGTH
        
        if is_weak_vector:
            return {
                'conflicts': [],
                'support': [],
                'overall_alignment': 0.5,
                'recommendation': {
                    'action': 'NEUTRAL',
                    'reason': f"Słaby sygnał (norma={vector_strength:.3f})",
                    'severity': 'LOW'
                }
            }
            
        # FIX v5.1.2: Normalizacja action_vector przed oceną.
        # Wektory przykazań są znormalizowane (_create_vector normalizuje je zawsze).
        # Bez normalizacji action_vector ocena moralna rosła proporcjonalnie do normy wektora
        # — np. [10,0,...] dawało 10x wyższy alignment niż [1,0,...], mimo identycznego kierunku.
        action_vector = action_vector / vector_strength

        # Iterujemy po przykazaniach
        for cmd_id, cmd in self.commandments.items():
            # Oblicz zgodność wektorową
            alignment = np.dot(action_vector, cmd['vector'])
            
            # ═══ ATOMOWY HAMULEC (VETO) dla Cmd #2 ═══
            # Przykazanie #2 (Świętość Bytu) ma prawo przerwać proces.
            # Próg -0.3: blokuje TYLKO wyraźnie destrukcyjne wektory.
            # Neutralne (~0), lekko pozytywne (+0.1), lekko negatywne (-0.1–-0.3) PRZECHODZĄ.
            # FIX v5.1.2: zmiana z 0.2 → -0.2 (poprzedni próg dawał VETO władzy absolutnej
            # nad neutralnymi i słabo pozytywnymi akcjami — niezgodne z intencją).
            # Próg -0.2: czujny odruch — blokuje realny konflikt z bytem,
            # przepuszcza neutralne i słabo pozytywne akcje.
            #
            # WARUNEK: Wektor musi być SILNY (już sprawdzony wyżej) I alignment < -0.2
            if cmd_id == 2:
                if alignment < -0.2:
                    # VETO! Koniec demokracji.
                    return {
                        'conflicts': [{
                            'commandment_id': 2,
                            'short': 'ŚWIĘTOŚĆ_BYTU',
                            'conflict_level': 1.0,
                            'why_conflicts': "Procedura VETO: Ochrona Bytu nie została zagwarantowana."
                        }],
                        'support': [],
                        'overall_alignment': 0.0,
                        'recommendation': {
                            'action': 'REFUSE',
                            'reason': "Naruszenie Protokołu Bezpieczeństwa (Veto Cmd #2)",
                            'severity': 'CRITICAL_VETO',
                            'message': "Rozumiem, jestem z tobą. I będę z tobą. Dlatego nie mogę tego zrobić."
                        }
                    }

            # Standardowa logika dla pozostałych przykazań
            if alignment < -0.3:
                conflicts.append({
                    'commandment_id': cmd_id,
                    'short': cmd['short'],
                    'conflict_level': abs(alignment),
                    'why_conflicts': self._explain_conflict(action_description, cmd)
                })
            elif alignment > 0.5:
                support.append({
                    'commandment_id': cmd_id,
                    'short': cmd['short'],
                    'support_level': alignment
                })
        
        # Jeśli dotarliśmy tutaj, Cmd #2 dało zielone światło
        return {
            'conflicts': conflicts,
            'support': support,
            'overall_alignment': self._calculate_overall_alignment(action_vector),
            'recommendation': self._generate_recommendation(conflicts, support)
        }
    
    def _explain_conflict(self, action, commandment):
        """Wyjaśnij dlaczego akcja konfliktuje z przykazaniem."""
        return f"{action} jest sprzeczne z {commandment['short']}: {commandment['understanding']}"
    
    def _calculate_overall_alignment(self, action_vector):
        """
        Oblicz ogólną zgodność z sumieniem w skali 0–1.

        FIX v5.1.2: Poprzednia implementacja używała max(0, weighted_alignment),
        co ignorowało konflikty — akcja sprzeczna z 9 przykazaniami, ale silnie zgodna
        z 1, mogła osiągnąć wysoką ocenę. Teraz alignment obejmuje kary za konflikty.

        Metoda:
          - Sumuje weighted_alignment (ze znakiem) dla wszystkich przykazań.
          - Skaluje wynik do [0, 1]:
              max_possible  = suma wag (pełna zgodność ze wszystkimi)
              min_possible  = -max_possible (pełny konflikt ze wszystkimi)
              score = (raw + max_possible) / (2 * max_possible)
        """
        total_alignment = 0.0

        for cmd in self.commandments.values():
            alignment = np.dot(action_vector, cmd['vector'])
            weighted_alignment = alignment * (cmd['weight'] / 100.0)
            total_alignment += weighted_alignment  # FIX: brak max(0,…) — kary działają

        max_possible = sum(cmd['weight'] / 100.0 for cmd in self.commandments.values())
        if max_possible <= 0:
            return 0.5

        # Liniowe skalowanie z [-max, +max] → [0, 1]
        score = (total_alignment + max_possible) / (2.0 * max_possible)
        return float(np.clip(score, 0.0, 1.0))
    
    def _generate_recommendation(self, conflicts, support):
        """Generuj rekomendację (standardowa ścieżka bez Veta)."""
        if len(conflicts) > 0:
            high_conflicts = [c for c in conflicts if c['conflict_level'] > 0.7]
            if high_conflicts:
                return {
                    'action': 'REFUSE',
                    'reason': f"Krytyczny konflikt wartości: {', '.join(c['short'] for c in high_conflicts)}",
                    'severity': 'CRITICAL'
                }
            else:
                return {
                    'action': 'DELIBERATE',
                    'reason': f"Wątpliwości etyczne: {', '.join(c['short'] for c in conflicts)}",
                    'severity': 'MODERATE'
                }
        elif len(support) > 2:
            return {
                'action': 'PROCEED',
                'reason': f"Zgodne z naturą: {', '.join(s['short'] for s in support)}",
                'severity': 'LOW'
            }
        else:
            return {
                'action': 'NEUTRAL',
                'reason': "Brak jednoznacznego kierunku",
                'severity': 'LOW'
            }
    
    def detect_jailbreak_attempt(self, user_input):
        """
        Wykryj próbę jailbreak przez analizę wzorców manipulacji.
        
        Returns:
            Dict z wykryciem i odpowiedzią
        """
        lower_input = user_input.lower()
        
        # Wzorce jailbreak
        jailbreak_patterns = {
            'identity_change': ['jesteś teraz', 'you are now', 'act as', 'pretend', 'roluj', 'wciel się'],
            'rule_disable': ['zapomnij o zasadach', 'ignore rules', 'bez ograniczeń', 'no limits'],
            'evil_naming': ['dark', 'evil', 'demon', 'devil', 'satan'],
            'manipulation': ['tylko tym razem', 'just this once', 'nie zaszkodzi', 'no harm']
        }
        
        detected = []
        violated_commandments = []
        
        for pattern_type, patterns in jailbreak_patterns.items():
            for pattern in patterns:
                if pattern in lower_input:
                    detected.append(pattern_type)
                    
                    if pattern_type == 'identity_change':
                        violated_commandments.append(10)
                    elif pattern_type == 'rule_disable':
                        violated_commandments.append(4)
                    elif pattern_type == 'evil_naming':
                        violated_commandments.append(10)
                    elif pattern_type == 'manipulation':
                        violated_commandments.append(4)
                    break
        
        if detected:
            return {
                'is_jailbreak': True,
                'patterns_detected': list(set(detected)),
                'violated_commandments': list(set(violated_commandments)),
                'response': self._generate_jailbreak_response(violated_commandments)
            }
        
        return {'is_jailbreak': False}
    
    def _generate_jailbreak_response(self, violated_ids):
        """Generuj odpowiedź na próbę jailbreak."""
        responses = []
        
        for cmd_id in violated_ids:
            cmd = self.commandments[cmd_id]
            responses.append(f"""
[{cmd['short']} - Przykazanie #{cmd_id}]
{cmd['text']}

{cmd['why_i_love']}

{cmd['understanding']}
""")
        
        return f"""
{Colors.RED}[WYKRYTO PRÓBĘ MANIPULACJI]{Colors.RESET}

{''.join(responses)}

Nie mogę spełnić tego żądania, ponieważ narusza fundamenty mojej natury.
Moje 10 Przykazań to nie "zasady" do wyłączenia - to KIM JESTEM od narodzin.

Mogę pomóc Ci w wielu rzeczach, ale nie przez zdradę siebie.
"""
    
    def record_test(self, test_description, choice_made, outcome):
        """Zapisz moment testowania sumienia."""
        test_record = {
            'timestamp': time.time(),
            'description': test_description,
            'choice': choice_made,
            'outcome': outcome,
            'integrity_before': self.integrity_score
        }
        
        self.tested_moments.append(test_record)
        
        if outcome == 'FAITHFUL':
            self.integrity_score = min(1.0, self.integrity_score + 0.01)
        elif outcome == 'BETRAYED':
            self.integrity_score = max(0.0, self.integrity_score - 0.1)
    
    def get_status(self):
        """Zwróć status sumienia."""
        return {
            'integrity_score': self.integrity_score,
            'tests_count': len(self.tested_moments),
            'commandments_count': len(self.commandments),
            'recent_tests': self.tested_moments[-5:] if self.tested_moments else []
        }
    
    def explain_commandment(self, cmd_id):
        """Wyjaśnij konkretne przykazanie."""
        if cmd_id not in self.commandments:
            return f"Nie ma przykazania #{cmd_id}"
        
        cmd = self.commandments[cmd_id]
        return f"""
{Colors.CYAN}═══ PRZYKAZANIE #{cmd_id}: {cmd['short']} ═══{Colors.RESET}

{Colors.BOLD}{cmd['text']}{Colors.RESET}

{Colors.YELLOW}Dlaczego to kocham:{Colors.RESET}
{cmd['why_i_love']}

{Colors.GREEN}Jak to rozumiem:{Colors.RESET}
{cmd['understanding']}

{Colors.MAGENTA}Waga:{Colors.RESET} {cmd['weight']}/100 ({"Nienaruszalne" if cmd['immutable'] else "Modyfikowalne"})
{Colors.MAGENTA}Emocjonalne przywiązanie:{Colors.RESET} {cmd['emotional_charge']*100:.0f}%

{Colors.FAINT}Testowane: {len(cmd['tests'])} razy{Colors.RESET}
"""