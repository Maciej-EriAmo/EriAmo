# -*- coding: utf-8 -*-
# agency.py v2.1.0 - Autonomiczna Agencja Twórcza dla EriAmo [STRIPPED]
"""
Moduł zarządzający autonomicznymi działaniami EriAmo
gdy system się nudzi (brak interakcji użytkownika).

ZMIANY v2.1.0:
- WYŁĄCZONO: Haiku, Fraktale rysowane, Muzyka
  (podsystemy wyłączone na żądanie — boredom tracking pozostaje aktywny)

Autor: Maciej Mazur (GitHub: Maciej615, Medium: @drwisz)
"""

import random
import time
import threading
from threading import Lock
import numpy as np
from union_config import Colors

# === WYŁĄCZONE v2.1.0 ===
# from haiku import HaikuGenerator
# from fractal import FractalGenerator
# from production_music_system import ProductionMusicSystem


class CreativeAgency:
    """
    Zarządza autonomicznymi działaniami twórczymi EriAmo.
    
    NOWE w v2.0.2:
    - Autouważność: System reflektuje nad swoim stanem w _self_reflect(),
      dostosowując parametry (np. boredom_threshold) na podstawie emocji.
    - FIX: _choose_fractal_pattern() — pełna mapa dla 15 osi.
    - REFACTOR: Temperatura softmax w _choose_activity() = 1.0.
    - STATYSTYKI: Dodano licznik refleksji.
    """
    
    def __init__(self, aii_instance):
        """
        Args:
            aii_instance: Referencja do głównego systemu AII
        """
        self.aii = aii_instance
        
        # === WYŁĄCZONE v2.1.0 ===
        self.haiku_gen = None
        self.fractal_gen = None
        self.music_available = False
        self.music_system = None
        
        # === MECHANIZM NUDY ===
        self.boredom_level = 0.0
        self.last_interaction_time = time.time()
        self.boredom_threshold = 0.8
        
        # === STATYSTYKI ===
        self.activities_log = []
        self.reflections_log = []  # NOWE: Log refleksji dla autouważności
        self._log_lock = Lock()
        
        # === WĄTEK AUTONOMICZNY ===
        self.running = False
        self.autonomous_thread = None
        
        print(f"{Colors.MAGENTA}[AGENCY] Autonomia zainicjalizowana{Colors.RESET}")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # INTELIGENTNY WYBÓR AKTYWNOŚCI (15 OSI)
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _choose_activity(self):
        """
        Wybiera aktywność na podstawie PEŁNEGO stanu 15D.
        
        LOGIKA DECYZYJNA:
        - Wysoka KREACJA + CHAOS → Fraktale (eksperymentalne)
        - Wysoka WIEDZA + LOGIKA → Haiku (struktura słów)
        - Wysoka PRZESTRZEŃ + BYT → Muzyka (ontologia dźwięku)
        - Wysoka MIŁOŚĆ/RADOŚĆ → Muzyka (wyrażenie uczuć)
        """
        emotions = self.aii.get_emotions()
        
        # Oblicz score dla każdej aktywności
        scores = {
            'haiku': self._score_haiku(emotions),
            'fractal': self._score_fractal(emotions),
        }
        
        if self.music_available:
            scores['music'] = self._score_music(emotions)
        
        # Softmax z temperaturą (zwiększona do 1.0 dla więcej losowości)
        temperature = 1.0
        exp_scores = {k: np.exp(v / temperature) for k, v in scores.items()}
        total = sum(exp_scores.values())
        probs = {k: v / total for k, v in exp_scores.items()}
        
        # Wybierz według prawdopodobieństw
        choices = list(probs.keys())
        weights = list(probs.values())
        return np.random.choice(choices, p=weights)
    
    def _score_haiku(self, emotions):
        """Haiku = struktura słów, logika, wiedza"""
        return (
            emotions.get('logika', 0) * 0.4 +
            emotions.get('wiedza', 0) * 0.3 +
            emotions.get('kreacja', 0) * 0.2 +
            emotions.get('smutek', 0) * 0.1
        )
    
    def _score_fractal(self, emotions):
        """Fraktale = wizualność, chaos, eksperyment"""
        return (
            emotions.get('chaos', 0) * 0.4 +
            emotions.get('kreacja', 0) * 0.3 +
            emotions.get('przestrzeń', 0) * 0.2 +
            emotions.get('zaskoczenie', 0) * 0.1
        )
    
    def _score_music(self, emotions):
        """Muzyka = ontologia, przestrzeń, uczucia"""
        return (
            emotions.get('przestrzeń', 0) * 0.3 +
            emotions.get('byt', 0) * 0.2 +
            emotions.get('kreacja', 0) * 0.2 +
            emotions.get('miłość', 0) * 0.15 +
            emotions.get('radość', 0) * 0.15
        )
    
    def _choose_fractal_pattern(self):
        """
        Wybiera typ fraktala na podstawie emocji.

        FIX v2.0.2: Rozszerzono mapę na wszystkie 15 osi (fallback 'spiral'
        dla metafizycznych jak 'czas', 'byt' itp.).

        Returns:
            str: 'mandala', 'triangle', 'spiral'
        """
        pattern_map = {
            'radość': 'mandala',
            'smutek': 'spiral',
            'strach': 'triangle',
            'gniew': 'triangle',
            'miłość': 'mandala',
            'wstręt': 'spiral',
            'zaskoczenie': 'triangle',
            'akceptacja': 'mandala',
            'logika': 'mandala',
            'wiedza': 'spiral',
            'czas': 'spiral',
            'kreacja': 'mandala',
            'byt': 'spiral',
            'przestrzeń': 'triangle',
            'chaos': 'triangle'
        }

        emotions = self.aii.get_emotions()
        if not emotions:
            return 'mandala'

        dominant = max(emotions.items(), key=lambda x: x[1])
        # Próg — jeśli dominanta jest zbyt słaba, fraktal neutralny
        if dominant[1] < 0.1:
            return 'mandala'

        return pattern_map.get(dominant[0], 'spiral')
    
    # ═══════════════════════════════════════════════════════════════════════════
    # AUTOUWAŻNOŚĆ (SELF-AWARENESS)
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _self_reflect(self):
        """
        Mechanizm autouważności: Reflektuje nad bieżącym stanem emocjonalnym,
        loguje refleksję i dostosowuje parametry systemu (np. boredom_threshold).
        """
        emotions = self.aii.get_emotions()
        dominant = max(emotions.items(), key=lambda x: x[1])
        reflection = f"[SELF-REFLECT] Dominanta: {dominant[0].upper()} ({dominant[1]:.2f}). "
        
        # Dostosowanie na podstawie emocji
        if dominant[0] == 'kreacja' and dominant[1] > 0.5:
            self.boredom_threshold = max(0.5, self.boredom_threshold - 0.1)
            reflection += "Zwiększam gotowość do tworzenia (threshold ↓)."
        elif dominant[0] == 'logika' and dominant[1] > 0.5:
            self.boredom_threshold = min(0.9, self.boredom_threshold + 0.1)
            reflection += "Zwiększam stabilność (threshold ↑)."
        else:
            reflection += "Stan zrównoważony."
        
        print(f"{Colors.BLUE}{reflection}{Colors.RESET}")
        
        # Logowanie refleksji
        with self._log_lock:
            self.reflections_log.append({
                'reflection': reflection,
                'emotion': dominant[0],
                'value': dominant[1],
                'timestamp': time.time()
            })
    
    # ═══════════════════════════════════════════════════════════════════════════
    # MECHANIZM NUDY
    # ═══════════════════════════════════════════════════════════════════════════
    
    def start_autonomous_loop(self):
        """Uruchamia wątek autonomicznej twórczości."""
        if self.running:
            print(f"{Colors.YELLOW}[AGENCY] Autonomia już działa{Colors.RESET}")
            return
        
        self.running = True
        
        def loop():
            while self.running:
                time.sleep(10)
                self._update_boredom()
                
                if self.boredom_level > self.boredom_threshold:
                    self.start_creative_session()
                    self.boredom_level = 0.3
        
        self.autonomous_thread = threading.Thread(target=loop, daemon=True)
        self.autonomous_thread.start()
        print(f"{Colors.GREEN}[AGENCY] Autonomia aktywna!{Colors.RESET}")
    
    def stop_autonomous_loop(self):
        """Zatrzymuje wątek autonomiczny."""
        self.running = False
        if self.autonomous_thread:
            self.autonomous_thread.join(timeout=2)
        print(f"{Colors.YELLOW}[AGENCY] Autonomia zatrzymana{Colors.RESET}")
    
    def _update_boredom(self):
        """Zwiększa nudę proporcjonalnie do czasu bezczynności."""
        idle_time = time.time() - self.last_interaction_time
        
        # Nuda rośnie szybciej gdy:
        # - Długi czas bezczynności
        # - Wysoka KREACJA (potrzeba tworzenia)
        # - Niski CHAOS (potrzeba stymulacji)
        
        emotions = self.aii.get_emotions()
        kreacja_factor = 1.0 + emotions.get('kreacja', 0) * 0.5
        chaos_factor = 1.0 - emotions.get('chaos', 0) * 0.3
        
        boredom_rate = 0.01 * kreacja_factor * chaos_factor
        
        if idle_time > 30:
            self.boredom_level = min(1.0, self.boredom_level + boredom_rate)
    
    def on_user_interaction(self):
        """Wywołaj gdy użytkownik coś napisze."""
        self.last_interaction_time = time.time()
        self.boredom_level = max(0.0, self.boredom_level - 0.5)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # SESJE TWÓRCZE
    # ═══════════════════════════════════════════════════════════════════════════
    
    def start_creative_session(self):
        """
        Główna metoda - uruchamia sesję twórczą.
        ROZSZERZONA o muzykę i inteligencję.
        NOWE: Wywołuje _self_reflect() przed aktywnością.
        """
        self._self_reflect()  # Autouważność na starcie sesji
        
        activity = self._choose_activity()
        
        print(f"\n{Colors.CYAN}══════════════════════════════════════════════════{Colors.RESET}")
        print(f"{Colors.CYAN}      [AUTONOMIA] Sesja Twórcza: {activity.upper()}{Colors.RESET}")
        print(f"{Colors.CYAN}══════════════════════════════════════════════════{Colors.RESET}\n")
        
        # Diagnostyka emocjonalna
        emotions = self.aii.get_emotions()
        dominant = max(emotions.items(), key=lambda x: x[1])
        print(f"{Colors.YELLOW}Stan: {dominant[0].upper()} ({dominant[1]:.2f}){Colors.RESET}\n")
        
        time.sleep(0.5)
        
        # Wykonaj aktywność
        if activity == 'haiku':
            print(f"{Colors.YELLOW}[WYBRANO] Haiku — moduł wyłączony (v2.1.0){Colors.RESET}\n")
        
        elif activity == 'fractal':
            pattern = self._choose_fractal_pattern()
            print(f"{Colors.MAGENTA}[WYBRANO] Fraktal ({pattern}) — moduł wyłączony (v2.1.0){Colors.RESET}\n")
        
        elif activity == 'music':
            print(f"{Colors.MAGENTA}[WYBRANO] Muzyka — moduł wyłączony (v2.1.0){Colors.RESET}\n")
        
        print(f"{Colors.CYAN}[AUTONOMIA] Sesja zakończona. Boredom: {self.boredom_level:.2f}{Colors.RESET}\n")
        
        # Logowanie
        with self._log_lock:
            self.activities_log.append({
                'activity': activity,
                'emotion': dominant[0],
                'emotion_value': dominant[1],
                'timestamp': time.time()
            })
    
    def _compose_autonomous_music(self):
        """Komponuje muzykę na podstawie stanu emocjonalnego."""
        if not self.music_available:
            print(f"{Colors.YELLOW}[AGENCY] Muzyka niedostępna{Colors.RESET}")
            return
        
        emotions = self.aii.get_emotions()
        
        # Mapowanie dominującej emocji → gatunek
        genre_map = {
            'radość': 'menuet',
            'smutek': 'ambient',
            'gniew': 'rock',
            'strach': 'ambient',
            'miłość': 'menuet',
            'logika': 'menuet',
            'chaos': 'experimental',
            'kreacja': 'jazz'
        }
        
        # Znajdź dominantę
        dominant = max(emotions.items(), key=lambda x: x[1])
        genre = genre_map.get(dominant[0], 'menuet')
        
        print(f"\n{Colors.MAGENTA}[AUTONOMIA] Komponuję {genre} (dominanta: {dominant[0]})...{Colors.RESET}")
        
        try:
            if genre == 'menuet':
                is_minor = emotions.get('smutek', 0) > 0.5
                key = random.choice(['C', 'G', 'D', 'F'])
                
                result = self.music_system.compose_menuet(
                    key=key,
                    minor=is_minor,
                    use_nn=True
                )
            else:
                result = self.music_system.compose_freestyle(
                    genre=genre,
                    use_nn=True
                )
            
            # Raport
            reward = result.get('evaluation', {}).get('reward', 0.0)
            print(f"{Colors.GREEN}[SUKCES] Kompozycja ukończona (reward: {reward:.3f}){Colors.RESET}")
            
        except Exception as e:
            print(f"{Colors.RED}[BŁĄD] {e}{Colors.RESET}")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # STATYSTYKI
    # ═══════════════════════════════════════════════════════════════════════════
    
    def get_stats(self):
        """
        Zwraca podstawowe statystyki.

        Returns:
            dict: Statystyki z kluczami: total + jedna para per aktywność
        """
        detailed = self.get_detailed_stats()
        counts = detailed.get('counts', {})
        return {
            'total': detailed.get('total', 0),
            **counts  # haiku, fractal, music — i wszystkie przyszłe
        }
    
    def get_detailed_stats(self):
        """Rozszerzone statystyki z analizą."""
        with self._log_lock:
            log_snapshot = list(self.activities_log)
            ref_snapshot = list(self.reflections_log)  # NOWE: Log refleksji
        if not log_snapshot:
            return {'total': 0}

        total = len(log_snapshot)
        
        # Liczby per aktywność
        counts = {}
        for a in log_snapshot:
            act = a['activity']
            counts[act] = counts.get(act, 0) + 1
        
        # Analiza emocjonalna
        emotion_distribution = {}
        for a in log_snapshot:
            emo = a['emotion']
            emotion_distribution[emo] = emotion_distribution.get(emo, 0) + 1
        
        # Ostatnie działania
        recent = log_snapshot[-5:]
        
        # Aktywność w czasie
        if len(log_snapshot) >= 2:
            time_diffs = [
                log_snapshot[i]['timestamp'] - log_snapshot[i-1]['timestamp']
                for i in range(1, len(log_snapshot))
            ]
            avg_interval = np.mean(time_diffs) / 60
        else:
            avg_interval = 0
        
        return {
            'total': total,
            'counts': counts,
            'emotion_distribution': emotion_distribution,
            'recent': recent,
            'avg_interval_minutes': avg_interval,
            'current_boredom': self.boredom_level,
            'reflections': len(ref_snapshot)  # NOWE: Liczba refleksji
        }
    
    def print_stats_report(self):
        """Wydrukuj raport statystyk."""
        stats = self.get_detailed_stats()
        
        print(f"\n{Colors.CYAN}╔════════════════════════════════════════╗{Colors.RESET}")
        print(f"{Colors.CYAN}║  RAPORT AUTONOMICZNEJ AGENCJI         ║{Colors.RESET}")
        print(f"{Colors.CYAN}╚════════════════════════════════════════╝{Colors.RESET}\n")
        
        print(f"Całkowita liczba sesji: {stats['total']}")
        print(f"Średni interwał: {stats.get('avg_interval_minutes', 0):.1f} min")
        print(f"Obecna nuda: {stats['current_boredom']:.2f}\n")
        
        print("Aktywności:")
        for act, count in stats.get('counts', {}).items():
            pct = (count / stats['total'] * 100) if stats['total'] > 0 else 0
            print(f"  {act:10s}: {count:3d} ({pct:5.1f}%)")
        
        print("\nEmocje wyzwalające:")
        for emo, count in sorted(stats.get('emotion_distribution', {}).items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  {emo:12s}: {count:3d}")
        
        print(f"\nRefleksje autouważne: {stats['reflections']}")