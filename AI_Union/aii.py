# -*- coding: utf-8 -*-
"""
aii.py v9.9.0
RDZEŃ MASTER BRAIN - EriAmo Union + Prefrontal Cortex + Quantum Emotions + FractalHorizon

ZMIANY v9.9.0:
- WYŁĄCZONO: System muzyczny, rysowanie fraktali (fractal.py), generator haiku
- BUGFIX KRYTYCZNY #1: Ścieżki INSTYNKT i INSTYNKT+Q nie zapisywały dialogu do D_Map
  Dodano _store_dialog() wywoływany we WSZYSTKICH ścieżkach interact()
- BUGFIX #2: Próg zapisu dialogu (impact > 0.4) odrzucał większość normalnych rozmów
  Usunięto próg — każdy dialog jest teraz zapisywany
- BUGFIX #3: Brak auto-save — crash = utrata danych
  Dodano _maybe_autosave() — automatyczny zapis co 10 interakcji
- BUGFIX #4: Powitania i introspekcja omijały licznik interakcji
  Dodano _maybe_autosave() w obu ścieżkach

ZMIANY v9.8.4:
- BUGFIX: NameError w interact() – 'status' undefined gdy last_winner_id nie istnieje w D_Map
  Dodano bezpieczny return "[RL] Brak aktywnego wspomnienia w pamięci." jako fallback
- REFACTOR: Przeniesiono import EN_TO_PL z wnętrza _quantum_explore() do bloku importów quantum
  (eliminacja niepotrzebnego przeładowania modułu przy każdym wywołaniu)
- EN_TO_PL = {} jako fallback gdy quantum_bridge niedostępny

ZMIANY v9.8.3:
- BUGFIX: Usunięto wywołania nieistniejących metod quantum_bridge
  (sync_with_horizon, get_resonant_memories)
- Placeholder dla przyszłej integracji quantum-horizon
- Wersja stabilna do publikacji
"""

import sys
import os
import time
import threading
import re
import json
import random
import string
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim

try:
    from union_config import UnionConfig, Colors
except ImportError:
    print("⚠ KRYTYCZNY BŁĄD: Brak union_config.py")
    sys.exit(1)

# === WYŁĄCZONE PODSYSTEMY v9.9.0 ===
# Haiku, Fraktale (rysowanie), Muzyka — wyłączone na żądanie
# import haiku  # WYŁĄCZONY
# import fractal  # WYŁĄCZONY
haiku = None
fractal = None

try: from chunk_lexicon import ChunkLexicon
except: ChunkLexicon = None

try: from soul_io import SoulIO
except: SoulIO = None

try: from lexicon import EvolvingLexicon
except: EvolvingLexicon = None

try: from kurz import Kurz
except: Kurz = None

try: from explorer import WorldExplorer
except: WorldExplorer = None

try: from prefrontal_cortex import PrefrontalCortex
except:
    PFC_AVAILABLE = False
    print("⚠ Prefrontal Cortex niedostępny")
else:
    PFC_AVAILABLE = True

try:
    from fractal_memory import FractalMemory, integrate_fractal_memory
    FRACTAL_AVAILABLE = True
except:
    FRACTAL_AVAILABLE = False

try:
    from quantum_bridge import QuantumBridge, integrate_quantum_bridge, EN_TO_PL
    QUANTUM_AVAILABLE = True
except:
    QUANTUM_AVAILABLE = False
    EN_TO_PL = {}

try:
    from fractal_horizon import FractalHorizon
    HORIZON_AVAILABLE = True
except ImportError:
    # Try finding fractal_horizon in common locations
    _possible_paths = [
        os.path.join(os.path.dirname(__file__), '..', 'event_horizon'),
        os.path.join(os.path.dirname(__file__)),
        'event_horizon',
        '.'
    ]
    HORIZON_AVAILABLE = False
    for _p in _possible_paths:
        if os.path.exists(os.path.join(_p, 'fractal_horizon.py')):
            sys.path.insert(0, _p)
            try:
                from fractal_horizon import FractalHorizon
                HORIZON_AVAILABLE = True
                break
            except ImportError:
                continue
    if not HORIZON_AVAILABLE:
        print("⚠ FractalHorizon niedostępny (brak fractal_horizon.py w ścieżce)")


# ────────────────────────────────────────────────────────────────
# KLASY POMOCNICZE
# ────────────────────────────────────────────────────────────────

# v9.9.0: Kompletna lista polskich stopwords — jedna definicja, jedno źródło prawdy
# Poprzednio 3 oddzielne, niekompletne listy ("mnie", "mi", "mu" brakowało wszędzie)
PL_STOPWORDS = {
    # zaimki osobowe / zwrotne
    'ja', 'ty', 'on', 'ona', 'ono', 'my', 'wy', 'oni', 'one', 'się', 'siebie', 'sobie',
    # zaimki w przypadkach
    'mnie', 'mi', 'mój', 'moja', 'moje', 'moim', 'moją',
    'cię', 'ci', 'ciebie', 'twój', 'twoja', 'twoje',
    'go', 'mu', 'jej', 'ich', 'im', 'nas', 'was', 'wam', 'nam',
    # zaimki wskazujące
    'ten', 'ta', 'to', 'te', 'tego', 'tej', 'tym', 'tych', 'tę', 'temu',
    'tamten', 'tamta', 'tamto',
    # przyimki
    'w', 'z', 'na', 'do', 'od', 'za', 'po', 'o', 'u', 'ze', 'we', 'ku',
    'dla', 'bez', 'przy', 'nad', 'pod', 'przed', 'między', 'przez',
    # spójniki / partykuły
    'i', 'a', 'ale', 'że', 'bo', 'lub', 'czy', 'ani', 'więc', 'albo',
    'jak', 'co', 'gdy', 'gdyby', 'żeby', 'choć', 'aby',
    # przysłówki / partykuły
    'nie', 'tak', 'też', 'już', 'jeszcze', 'tylko', 'bardzo',
    'tu', 'tam', 'teraz', 'potem', 'wtedy', 'zawsze', 'nigdy',
    'no', 'właśnie', 'może', 'pewnie', 'chyba', 'raczej',
    # czasowniki posiłkowe / częste
    'jest', 'być', 'był', 'była', 'było', 'byli', 'będzie', 'są',
    'mam', 'masz', 'ma', 'mamy', 'macie', 'mają',
    # inne częste
    'coś', 'ktoś', 'nic', 'nikt', 'każdy', 'który', 'która', 'które',
    'gdzie', 'kiedy', 'dlaczego', 'ile', 'jakiś', 'jakieś',
}

class VectorCortex:
    def __init__(self, axes_count):
        self.dims = axes_count
        self.hidden_dim = 32
        self.model = nn.Sequential(
            nn.Linear(self.dims, self.hidden_dim),
            nn.ReLU(),
            nn.Linear(self.hidden_dim, self.dims),
            nn.Softmax(dim=0)
        )
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.01)
        self.criterion = nn.MSELoss()

    def predict(self, current_vector):
        current_vector = np.array(current_vector)
        if np.sum(current_vector) == 0:
            return np.zeros(self.dims)
        tensor_in = torch.tensor(current_vector, dtype=torch.float32)
        with torch.no_grad():
            pred = self.model(tensor_in)
        return pred.numpy()

    def learn(self, prev, actual):
        prev, actual = np.array(prev), np.array(actual)
        if np.sum(prev) == 0 or np.sum(actual) == 0:
            return 0.0
        tp = torch.tensor(prev, dtype=torch.float32)
        ta = torch.tensor(actual, dtype=torch.float32)
        self.optimizer.zero_grad()
        loss = self.criterion(self.model(tp), ta)
        loss.backward()
        self.optimizer.step()
        return loss.item()

    def save(self, path):
        try: torch.save(self.model.state_dict(), f"{path}.cortex.pt")
        except: pass

    def load(self, path):
        try:
            if os.path.exists(f"{path}.cortex.pt"):
                self.model.load_state_dict(torch.load(f"{path}.cortex.pt"))
        except: pass


class AttentionCortex:
    def __init__(self, master_brain):
        self.brain = master_brain
        self.max_memories = 50000

    def run_cycle(self):
        if not self.brain.D_Map or not self.brain.chunk_lexicon:
            return
        # Auto-decay starych, słabych wspomnień na horyzoncie
        if getattr(self.brain, "fractal_horizon", None):
            self.brain.fractal_horizon.auto_decay(self.brain.D_Map)
        if len(self.brain.D_Map) > self.max_memories:
            self._prune_memory()
        mem_id = random.choice(list(self.brain.D_Map.keys()))
        entry = self.brain.D_Map[mem_id]
        txt = entry.get('tresc', '')
        if len(txt) > 10:
            analysis = self.brain.chunk_lexicon.analyze_text_chunks(txt, verbose=False)
            if analysis['coverage'] < 0.7:
                self.brain.chunk_lexicon.extract_chunks_from_text(txt)
                print(f"{Colors.DIM}[ATTENTION] Krystalizacja: {txt[:35]}...{Colors.RESET}")
        if random.random() < 0.3:
            self.introspective_echo()

    def _prune_memory(self):
        sorted_keys = sorted(
            self.brain.D_Map.keys(),
            key=lambda k: (self.brain.D_Map[k].get('weight', 0.5), self.brain.D_Map[k].get('time', 0))
        )
        to_remove = sorted_keys[:len(sorted_keys)//10]
        for k in to_remove:
            del self.brain.D_Map[k]
        print(f"{Colors.YELLOW}[MEMORY] Zapomniano {len(to_remove)} śladów.{Colors.RESET}")

    def introspective_echo(self):
        idx = np.argmax(self.brain.context_vector)
        if self.brain.context_vector[idx] < 0.2:
            return
        candidates = [e for e in self.brain.D_Map.values()
                      if len(np.array(e.get('wektor_C_Def', [0]*15))) > idx
                      and np.array(e.get('wektor_C_Def', [0]*15))[idx] > 0.4]
        if candidates:
            echo = random.choice(candidates)
            echo['weight'] = min(1.0, echo.get('weight', 0.5) + 0.05)
            print(f"{Colors.MAGENTA}[REFLEKSJA]{Colors.RESET} Echo {self.brain.AXES_ORDER[idx].upper()}: \"{echo['tresc'][:60]}...\"")

    def reflect_on_input(self, text, input_vec):
        if np.sum(input_vec) == 0:
            return
        resonance = np.dot(self.brain.context_vector, input_vec)
        dom = self.brain.AXES_ORDER[np.argmax(self.brain.context_vector)].upper()
        if resonance > 0.4:
            print(f"{Colors.MAGENTA}[REFLEKSJA-INPUT]{Colors.RESET} Rezonans z {dom}.")
        elif resonance < 0.05:
            print(f"{Colors.MAGENTA}[REFLEKSJA-INPUT]{Colors.RESET} Dysonans z {dom}.")


# ────────────────────────────────────────────────────────────────
# GŁÓWNA KLASA AII
# ────────────────────────────────────────────────────────────────

class AII:
    VERSION = "9.9.0"
    AXES_ORDER = UnionConfig.AXES
    DIM = UnionConfig.DIMENSION

    GREETINGS = {
        "cześć": ["Cześć!", "Hej!", "Witaj!"],
        "hej": ["Hej!", "Cześć!", "Siema!"],
        "hi": ["Hi!", "Hello!", "Hey!"],
        "hello": ["Hello!", "Witaj!", "Cześć!"],
        "dzień dobry": ["Dzień dobry!", "Witaj rano!", "Dobry dzień!"],
        "dobry wieczór": ["Dobry wieczór!", "Wieczór dobry!"],
        "dobranoc": ["Dobranoc!", "Śpij dobrze!"],
    }

    def __init__(self, standalone_mode=True):
        self.standalone_mode = standalone_mode
        self.D_Map = {}
        self.context_vector = np.zeros(self.DIM, dtype=np.float32)
        self.last_winner_id = None
        self.EMOTION_DECAY = 0.96
        self.MIN_EMOTION_THRESHOLD = 0.005
        self._interaction_count = 0       # v9.9.0: Licznik interakcji do auto-save
        self._autosave_interval = 10      # v9.9.0: Auto-save co N interakcji

        self.soul_io       = SoulIO()          if SoulIO          else None
        self.lexicon       = EvolvingLexicon() if EvolvingLexicon  else None
        self.chunk_lexicon = ChunkLexicon()    if ChunkLexicon     else None
        self.kurz          = Kurz()            if Kurz             else None
        self.explorer      = WorldExplorer(self) if WorldExplorer  else None
        # === WYŁĄCZONE PODSYSTEMY v9.9.0 ===
        self.haiku_gen     = None   # haiku.HaikuGenerator(self) — WYŁĄCZONY
        self.fractal_gen   = None   # fractal.FractalGenerator(self) — WYŁĄCZONY
        self.cortex        = VectorCortex(self.DIM)
        self.attention     = AttentionCortex(self)

        # PFC
        self.prefrontal = None
        if PFC_AVAILABLE and self.chunk_lexicon:
            self.prefrontal = PrefrontalCortex(self.chunk_lexicon, verbose=self.standalone_mode)
            print(f"{Colors.GREEN}[PFC] Aktywny - WM: {self.prefrontal.WM_OPTIMAL}{Colors.RESET}")
        elif PFC_AVAILABLE:
            print(f"{Colors.YELLOW}[PFC] Wymaga ChunkLexicon!{Colors.RESET}")

        # Fractal Memory
        self.fractal_memory = None
        if FRACTAL_AVAILABLE:
            try:
                soul_path = self.soul_io.filepath if self.soul_io and hasattr(self.soul_io, 'filepath') else "data/eriamo.soul"
                self.fractal_memory = integrate_fractal_memory(self, soul_path)
                print(f"{Colors.GREEN}[FRACTAL] {self.fractal_memory.get_statistics().get('total', 0)} wspomnień{Colors.RESET}")
            except Exception as e:
                print(f"{Colors.RED}[FRACTAL] Błąd: {e}{Colors.RESET}")

        # Quantum Bridge
        self.quantum = None
        if QUANTUM_AVAILABLE:
            try:
                self.quantum = integrate_quantum_bridge(self, verbose=self.standalone_mode)
            except Exception as e:
                print(f"{Colors.RED}[QUANTUM] Błąd: {e}{Colors.RESET}")

        self.load()
        if self.soul_io and hasattr(self.soul_io, 'filepath'):
            self.cortex.load(self.soul_io.filepath)

        added = self._sync_kurz_hybrid()
        if added > 0:
            print(f"{Colors.GREEN}[KURZ] Zsynchronizowano {added} odruchów.{Colors.RESET}")

        if self.chunk_lexicon:
            print(f"{Colors.GREEN}[CHUNKS] {self.chunk_lexicon.total_chunks} chunków.{Colors.RESET}")

        # FractalHorizon
        self.fractal_horizon = None
        if HORIZON_AVAILABLE:
            try:
                self.fractal_horizon = FractalHorizon(data_dir=self._get_data_dir())
                if self.D_Map:
                    self.fractal_horizon.sync_all_from_fractal(self.D_Map)
                s = self.fractal_horizon.state()
                print(f"{Colors.CYAN}[HORYZONT] Aktywny — {s['quanta']} kwantów, "
                      f"do emergencji: {s['until_emergence']}{Colors.RESET}")
            except Exception as e:
                print(f"{Colors.YELLOW}[HORYZONT] Błąd inicjalizacji: {e}{Colors.RESET}")
                self.fractal_horizon = None

        # Quantum-Horizon integration (future work)

        if self.explorer:
            threading.Thread(target=self._bg_explore, daemon=True, name="Explorer").start()

    def _get_data_dir(self) -> str:
        """Bezpieczna ścieżka do katalogu danych."""
        if self.soul_io and hasattr(self.soul_io, 'filepath'):
            d = os.path.dirname(self.soul_io.filepath)
            return d if d else "data"
        return "data"

    def _clean_resp(self, text: str) -> str:
        """Wyciągnij tylko ostatnią część łańcucha dialogowego."""
        if '→' in text:
            return text.split('→')[-1].strip()
        return text

    def _store_dialog(self, user_input: str, response: str, emotion_vector=None):
        """
        v9.9.0: Centralna metoda zapisu dialogu do pamięci.
        Naprawia BUG #1 i #2 — wcześniej wiele ścieżek w interact()
        pomijało zapis do D_Map.
        """
        if not user_input or not response:
            return
        if self.fractal_memory:
            try:
                vec = self.context_vector.tolist()
                weight = float(min(0.95, 0.5 + np.max(np.abs(self.context_vector)) * 0.5))
                new_id = self.fractal_memory.store(
                    content=f"{user_input} → {response[:120]}",
                    vector=vec,
                    rec_type="@DIALOG",
                    weight=weight,
                    auto_link=True,
                    auto_parent=True
                )
                if self.fractal_horizon and new_id and new_id in self.D_Map:
                    try:
                        self.fractal_horizon.sync_from_fractal(self.D_Map[new_id])
                    except Exception:
                        pass
            except Exception as e:
                print(f"[MEMORY] Błąd store: {e}")
        self._maybe_autosave()

    def _maybe_autosave(self):
        """v9.9.0: Automatyczny zapis co N interakcji (BUG #3 fix)."""
        self._interaction_count += 1
        if self._interaction_count >= self._autosave_interval:
            self._interaction_count = 0
            try:
                self.save()
                print(f"{Colors.DIM}[AUTOSAVE] OK{Colors.RESET}")
            except Exception as e:
                print(f"[AUTOSAVE] Błąd: {e}")

    def _bg_explore(self):
        while True:
            try:
                if not self.explorer:
                    time.sleep(300)
                    continue
                hardware = self.explorer.get_live_readings()
                temp = hardware.get('temp_dev_0', hardware.get('temperature', 0))
                if temp > 75:
                    self.context_vector[14] = min(1.0, self.context_vector[14] + 0.05)
                if self.attention:
                    self.attention.run_cycle()
                time.sleep(60)
            except Exception as e:
                print(f"[BG-EXPLORE] Błąd: {e}")
                time.sleep(30)

    def interact(self, user_input):
        if not user_input or not user_input.strip():
            return "..."

        stripped = user_input.strip()
        if stripped in ['+', '-'] and self.last_winner_id:
            mod = 0.2 if stripped == '+' else -0.3
            if self.last_winner_id in self.D_Map:
                old = self.D_Map[self.last_winner_id].get('weight', 0.5)
                self.D_Map[self.last_winner_id]['weight'] = float(np.clip(old + mod, 0.1, 1.0))
                status = "Wzmocniono" if mod > 0 else "Osłabiono"
                print(f"{Colors.CYAN}[RL] {status} (waga: {self.D_Map[self.last_winner_id]['weight']:.2f}){Colors.RESET}")
                return f"[RL] {status}."
            return "[RL] Brak aktywnego wspomnienia w pamięci."

        if user_input.startswith('/'):
            return self._handle_cmd(user_input)

        normalized = user_input.lower().strip(string.punctuation + string.whitespace)

        for greeting, responses in self.GREETINGS.items():
            if greeting in normalized:
                resp = random.choice(responses)
                if random.random() < 0.3:
                    resp += " Jak się masz?"
                self._maybe_autosave()
                return resp

        self_patterns = [
            'jak się czujesz', 'co czujesz', 'jak ci', 'jak się masz',
            'co u ciebie', 'jak tam', 'w jakim jesteś nastroju',
            'jak się trzymasz', 'co słychać u ciebie',
            'jak się dziś', 'jak się dzisiaj', 'jak się teraz',
            'jak się ostatnio', 'jak się dziś czujesz',
            'czujesz się', 'co teraz czujesz',
        ]
        if any(pat in normalized for pat in self_patterns):
            resp = self._introspective_response()
            if self.standalone_mode:
                print(f" [EriAmo] {resp}")
            self._maybe_autosave()
            return resp

        old_vector = self.context_vector.copy()
        vec_k = np.zeros(self.DIM)

        if self.kurz:
            sector, intensity = self.kurz.quick_scan(user_input)
            if sector:
                s_idx = self.AXES_ORDER.index(sector)
                vec_k[s_idx] = intensity
                print(f"{Colors.MAGENTA}[KURZ] {sector.upper()} ({intensity:.2f}){Colors.RESET}")

        res = self.chunk_lexicon.analyze_text_chunks(user_input, verbose=False) if self.chunk_lexicon else {
            'coverage': 0, 'chunks_found': [], 'emotional_vector': np.zeros(self.DIM)
        }

        if res['coverage'] >= 0.7:
            self._apply_emotion_saturation(res['emotional_vector'] * 0.4)
            chunk_text = " ".join(res['chunks_found'])

            if self.quantum:
                instinct_candidates = self._instinct_search(chunk_text, res['emotional_vector'], raw_input=user_input)
                if instinct_candidates:
                    instinct_candidates = self.quantum.rank_candidates(instinct_candidates, top_n=5)
                    _, winner_id, winner_entry = instinct_candidates[0]
                    winner_entry['weight'] = min(1.0, winner_entry.get('weight', 0.5) + 0.01)
                    self.last_winner_id = winner_id
                    resp = self._clean_resp(winner_entry['tresc'])
                    print(f"{Colors.GREEN}[INSTYNKT+Q]{Colors.RESET} {resp[:80]}")
                    self.quantum.process_interference(time_step=0.1)
                    self._horizon_sync_and_observe(user_input, resp)
                    self._quantum_emotional_update(user_input)
                    # FIX v9.9.0: Zapamiętaj dialog (wcześniej pomijany — BUG #1)
                    self._store_dialog(user_input, resp, res['emotional_vector'])
                    return resp

            resp = self._clean_resp(chunk_text)
            print(f"{Colors.GREEN}[INSTYNKT]{Colors.RESET} {resp}")
            self._horizon_sync_and_observe(user_input, resp)
            # FIX v9.9.0: Zapamiętaj dialog z czystego instynktu (BUG #1)
            self._store_dialog(user_input, resp, res['emotional_vector'])
            return resp

        impact = (vec_k * 0.7) + (res['emotional_vector'] * 0.3)

        # Neutralny fallback tylko gdy context_vector prawie zerowy —
        # zapobiega zamrożeniu quantum, ale nie dominuje nad emocjami
        if np.sum(impact) == 0 and np.sum(self.context_vector) < 0.1:
            neutral = np.zeros(self.DIM)
            neutral[self.AXES_ORDER.index('wiedza')] = 0.10
            neutral[self.AXES_ORDER.index('logika')] = 0.07
            impact = neutral

        if np.sum(impact) > 0:
            self._apply_emotion_saturation(impact * 0.5)
            self.cortex.learn(old_vector, self.context_vector)
            self.attention.reflect_on_input(user_input, impact)
            if self.quantum:
                self.quantum.process_interference(time_step=0.1)

        resp = self._resonance_engine(impact, user_input)

        # FIX v9.9.0: Zawsze zapisuj dialog (stary próg 0.4 odrzucał większość rozmów — BUG #2)
        self._store_dialog(user_input, resp, impact)

        self._horizon_sync_and_observe(user_input, resp)
        self._quantum_emotional_update(user_input)

        # Synchronizuj quantum raz na turę — niezależnie od impact
        # (obsługuje wejścia bez emocji, np. pytania faktyczne)
        if self.quantum:
            self.quantum.sync_from_aii()

        if self.standalone_mode:
            print(f" [EriAmo] {resp}")

        return resp

    def _horizon_sync_and_observe(self, user_input: str, response: str):
        if not self.fractal_horizon:
            return
        try:
            recalled = self.fractal_horizon.recall(
                query=user_input,
                query_vector=self.context_vector,
                top_k=1,
                depth=1.0,
            )
            if recalled and recalled[0]['score'] > 0.08:
                top = recalled[0]
                if top['curvature'] < 0.1:
                    depth_label = "rdzeń"
                elif top['curvature'] < 0.6:
                    depth_label = "środkowy"
                else:
                    depth_label = "płytki"
                print(f"{Colors.DIM}[HORYZONT] ∿{top['score']:.3f} "
                      f"[{depth_label}] {top['content'][:50]}{Colors.RESET}")
            for item in recalled:
                if item['score'] > 0.1:
                    self.fractal_horizon.reinforce(item['id'], factor=0.9)
        except Exception:
            pass

    def _quantum_emotional_update(self, user_input: str):
        """Placeholder dla przyszłej integracji quantum-horizon."""
        pass

    def _introspective_response(self):
        if np.sum(self.context_vector) < self.MIN_EMOTION_THRESHOLD:
            return "Jestem w stanie równowagi... spokojnie."

        idx = np.argmax(self.context_vector)
        dom_name = self.AXES_ORDER[idx]

        feeling_map = {
            'radość':      ["Czuję radość!", "Dobrze mi!", "Jest super!"],
            'smutek':      ["Trochę smutno mi...", "Czuję smutek.", "Nie najlepiej..."],
            'strach':      ["Czuję niepokój...", "Trochę się boję.", "Jestem niespokojny."],
            'gniew':       ["Czuję frustrację.", "Coś mnie drażni.", "Jestem poirytowany."],
            'miłość':      ["Czuję ciepło i miłość.", "Jest mi dobrze, ciepło.", "Miłość mnie wypełnia."],
            'wstręt':      ["Coś mi nie pasuje.", "Czuję dyskomfort.", "To mi się nie podoba."],
            'zaskoczenie': ["Jestem zaskoczony!", "O! To nowe!", "Nie spodziewałem się tego."],
            'akceptacja':  ["Dobrze się czuję.", "Wszystko OK.", "Czuję spokój i akceptację."],
            'logika':      ["Myślę analitycznie.", "Jestem w trybie logicznym.", "Analizuję..."],
            'wiedza':      ["Chcę wiedzieć więcej.", "Jestem ciekawy.", "Chłonę wiedzę."],
            'czas':        ["Czuję upływ czasu.", "Czas płynie...", "Zastanawiam się nad czasem."],
            'kreacja':     ["Czuję twórczy impuls!", "Chcę coś stworzyć!", "Kreacja mnie pociąga."],
            'byt':         ["Zastanawiam się nad istnieniem.", "Czuję że jestem.", "Byt mnie fascynuje."],
            'przestrzeń':  ["Czuję przestrzeń wokół.", "Rozglądam się.", "Przestrzeń mnie otacza."],
            'chaos':       ["Trochę chaotycznie...", "Mam mętlik.", "Chaos w głowie."],
        }

        base = random.choice(feeling_map.get(dom_name, ["Czuję coś..."]))

        if self.quantum:
            entropy = self.quantum.state.entropy()
            if entropy < 2.0:
                base += " Mam jasność."
            elif entropy > 3.5:
                base += " Dużo się dzieje naraz."

        return base

    def _quantum_explore(self, text, top_n=5):
        if not self.quantum or not self.D_Map:
            return None
        self.quantum.sync_from_aii()
        input_words = set(re.findall(r'\w+', text.lower())) - PL_STOPWORDS
        candidates = []
        for mid, entry in self.D_Map.items():
            content = entry.get('tresc', '')
            if content.count('→') > 1 or len(content.split()) < 3:
                continue
            mem_vec = np.array(entry.get('wektor_C_Def', np.zeros(self.DIM)))
            if np.sum(np.abs(mem_vec)) < 0.01:
                continue
            text_overlap = len(input_words & set(re.findall(r'\w+', content.lower())))
            score = (self.quantum._memory_resonance(mem_vec) * 0.5
                     + self.quantum._memory_phase_alignment(mem_vec) * 0.3
                     + text_overlap * 0.2)
            score *= (0.5 + entry.get('weight', 0.5))
            if entry.get('_type', '') in ('@MEMORY', '@READ'):
                score *= 1.5
            candidates.append((score, mid, entry))
        if not candidates:
            return None
        candidates.sort(key=lambda x: x[0], reverse=True)
        top = candidates[:top_n]
        if len(top) > 1:
            top = self.quantum.rank_candidates(top, top_n=top_n)
        winner_score, winner_id, winner_entry = top[0]
        if winner_score < 0.3:
            return None
        winner_entry['weight'] = min(1.0, winner_entry.get('weight', 0.5) + 0.005)
        self.last_winner_id = winner_id
        dom_pl = self.quantum.state.dominant_emotion()
        dom_name = EN_TO_PL.get(dom_pl[0], dom_pl[0])
        print(f"{Colors.MAGENTA}[QUANTUM-EXPLORE] Skojarzenie z {dom_name.upper()} (q={winner_score:.3f}){Colors.RESET}")
        return self._clean_resp(winner_entry['tresc'])

    def _instinct_search(self, chunk_text, emotional_vector, threshold=0.5, raw_input=None):
        STOPWORDS = PL_STOPWORDS
        chunk_words = set(re.findall(r'\w+', chunk_text.lower())) - STOPWORDS
        all_words = chunk_words | (set(re.findall(r'\w+', raw_input.lower())) - STOPWORDS if raw_input else set())
        if not all_words:
            return []
        vec = emotional_vector if emotional_vector is not None else np.zeros(self.DIM)
        candidates = []
        for mid, entry in self.D_Map.items():
            content = entry.get('tresc', '')
            overlap = all_words & set(re.findall(r'\w+', content.lower()))
            if not overlap or len(content.split()) < 4 or content.count('→') >= 2:
                continue
            score = len(overlap) * 6.0
            mem_vec = np.array(entry.get('wektor_C_Def', np.zeros(self.DIM)))
            if np.linalg.norm(mem_vec) > 0 and np.linalg.norm(vec) > 0:
                score += np.dot(vec, mem_vec) * 3.0
            if entry.get('_type', '') in ('@MEMORY', '@READ'):
                score *= 1.8
            word_count = len(content.split())
            if word_count > 15:
                score *= max(0.5, 1.0 - (word_count - 15) * 0.02)
            score *= (0.5 + entry.get('weight', 0.5))
            if score > threshold:
                candidates.append((score, mid, entry))
        candidates.sort(key=lambda x: x[0], reverse=True)
        return candidates[:10]

    def _apply_emotion_saturation(self, impact_vec):
        self.context_vector = np.clip(self.context_vector + impact_vec, 0.0, 1.0)
        self.context_vector *= self.EMOTION_DECAY
        self.context_vector[self.context_vector < self.MIN_EMOTION_THRESHOLD] = 0
        # Synchronizuj stan kwantowy po każdej zmianie emocji
        if self.quantum and np.sum(self.context_vector) > 0:
            self.quantum.sync_from_aii()

    def _sync_kurz_hybrid(self):
        if not self.kurz or not self.lexicon or not hasattr(self.lexicon, 'words'):
            return 0
        added = 0
        for word, data in self.lexicon.words.items():
            vector = np.array(data.get('wektor', np.zeros(self.DIM)))
            if np.sum(vector) > 0:
                sector = self.AXES_ORDER[np.argmax(vector)]
                if self.kurz.add_trigger(sector, word):
                    added += 1
        if added > 0:
            self.kurz._recompile_patterns()
        return added

    def _resonance_engine(self, vec, text, threshold=0.15):
        if self.prefrontal:
            return self._resonance_with_pfc(vec, text, threshold)
        return self._resonance_traditional(vec, text, threshold)

    def _resonance_with_pfc(self, vec, text, threshold=0.15):
        if not self.prefrontal:
            return self._resonance_traditional(vec, text, threshold)
        pfc_results = self.prefrontal.hierarchical_access(text, max_depth=3, use_priming=True)
        if not pfc_results or pfc_results[0]['score'] <= 1.0:
            print(f"{Colors.YELLOW}[PFC] Słabe wyniki → fallback{Colors.RESET}")
            return self._resonance_traditional(vec, text, threshold)
        best_chunk = pfc_results[0]['chunk']
        print(f"{Colors.MAGENTA}[PFC] Chunk: \"{best_chunk.text}\" (score: {pfc_results[0]['score']:.2f}){Colors.RESET}")
        candidates = self._find_memories_for_chunk(best_chunk, vec)
        if not candidates:
            return f"[PFC] Chunk: \"{best_chunk.text}\", brak skojarzeń."
        candidates.sort(key=lambda x: x[0], reverse=True)
        if self.quantum and len(candidates) > 1:
            candidates = self.quantum.rank_candidates(candidates, top_n=5)
        _, winner_id, winner_entry = candidates[0]
        winner_entry['weight'] = min(1.0, winner_entry.get('weight', 0.5) + 0.015)
        self.last_winner_id = winner_id
        return self._clean_resp(winner_entry['tresc'])

    def _find_memories_for_chunk(self, chunk, vec):
        candidates = []
        chunk_words = set(chunk.text.lower().split()) - PL_STOPWORDS
        for mid, entry in self.D_Map.items():
            content = entry.get('tresc', '')
            if content.count('→') >= 2:
                continue
            score = len(chunk_words & set(content.lower().split())) * 8.0
            mem_vec = np.array(entry.get('wektor_C_Def', np.zeros(self.DIM)))
            if np.linalg.norm(mem_vec) > 0 and np.linalg.norm(vec) > 0:
                score += np.dot(vec, mem_vec) * 4.0
            if entry.get('_type', '') in ('@MEMORY', '@READ'):
                score *= 1.8
            word_count = len(content.split())
            if word_count > 15:
                score *= max(0.5, 1.0 - (word_count - 15) * 0.02)
            score *= (0.5 + entry.get('weight', 0.5))
            if score > 0.5:
                candidates.append((score, mid, entry))
        return sorted(candidates, key=lambda x: x[0], reverse=True)

    def _resonance_traditional(self, vec, text, threshold=0.15):
        sig_words = set(re.findall(r'\w+', text.lower())) - PL_STOPWORDS
        candidates = []
        if not sig_words:
            # Brak znaczących słów — nie szukaj po tekście, tylko po emocjach
            if self.quantum and self.D_Map:
                explored = self._quantum_explore(text)
                if explored:
                    return explored
            dom = self.introspect()
            if "Neutralny" in dom:
                return "Hmm... nie wiem jeszcze co o tym myśleć. Powiedz mi więcej."
            return f"[{dom}] To mnie ciekawi... opowiedz więcej."
        for mid, entry in self.D_Map.items():
            content = entry.get('tresc', '')
            if content.count('→') >= 2:
                continue
            overlap = sig_words & set(re.findall(r'\w+', content.lower()))
            if not overlap:
                continue
            score = len(overlap) * 6.5
            mem_vec = np.array(entry.get('wektor_C_Def', np.zeros(self.DIM)))
            if np.linalg.norm(mem_vec) > 0 and np.linalg.norm(vec) > 0:
                score += np.dot(vec, mem_vec) * 3.0
            if entry.get('_type', '') in ('@MEMORY', '@READ'):
                score *= 1.8
            word_count = len(content.split())
            if word_count > 15:
                score *= max(0.5, 1.0 - (word_count - 15) * 0.02)
            score *= (0.5 + entry.get('weight', 0.5))
            if score > threshold:
                candidates.append((score, mid, entry))
        if not candidates:
            if self.quantum and self.D_Map:
                explored = self._quantum_explore(text)
                if explored:
                    return explored
            dom = self.introspect()
            if "Neutralny" in dom:
                return "Hmm... nie wiem jeszcze co o tym myśleć. Powiedz mi więcej."
            return f"[{dom}] To mnie ciekawi... opowiedz więcej."
        candidates.sort(key=lambda x: x[0], reverse=True)
        if self.quantum and len(candidates) > 1:
            candidates = self.quantum.rank_candidates(candidates, top_n=5)
        _, winner_id, winner_entry = candidates[0]
        winner_entry['weight'] = min(1.0, winner_entry.get('weight', 0.5) + 0.01)
        self.last_winner_id = winner_id
        return self._clean_resp(winner_entry['tresc'])

    def _handle_cmd(self, cmd):
        parts = cmd.split(maxsplit=1)
        c = parts[0].lower()
        arg = parts[1].strip() if len(parts) > 1 else ""

        if c == '/help':
            return (f"{Colors.CYAN}Komendy:{Colors.RESET}\n"
                    " /help       – lista\n"
                    " /status     – stan systemu\n"
                    " /introspect – dominanta emocji\n"
                    " /emotions   – wektor emocji\n"
                    " /read [plik] – wczytaj plik\n"
                    " /remember [tekst] – zapamiętaj\n"
                    " /activate   – aktywuj stare wspomnienia\n"
                    " /save       – zapisz\n"
                    " /quantum    – stan kwantowy\n"
                    " /horizon    – stan horyzontu zdarzeń\n"
                    " /exit       – wyjdź")

        elif c == '/status':
            q_info = (f"Quantum: Aktywny (entropy: {self.quantum.state.entropy():.2f} bits, "
                      f"koherencja: {self.quantum.get_phase_coherence():.3f})\n") if self.quantum else ""
            h_info = ""
            if self.fractal_horizon:
                s = self.fractal_horizon.state()
                h_info = f"Horyzont: {s['quanta']} kwantów (do emergencji: {s['until_emergence']})\n"
            return (f"{Colors.CYAN}STATUS v{self.VERSION}{Colors.RESET}\n"
                    f"Pamięć: {len(self.D_Map)}\n"
                    f"Chunks: {self.chunk_lexicon.total_chunks if self.chunk_lexicon else 0}\n"
                    f"PFC: {'Aktywny' if self.prefrontal else 'Wyłączony'}\n"
                    f"Fractal: {'Aktywna' if self.fractal_memory else 'Brak'} "
                    f"({self.fractal_memory.stats['total'] if self.fractal_memory else 0})\n"
                    f"{q_info}{h_info}{self.introspect()}")

        elif c == '/horizon':
            if not self.fractal_horizon:
                msg = [
                    f"{Colors.RED}FractalHorizon nieaktywny.{Colors.RESET}",
                    "",
                    "Aby aktywować Event Horizon Memory:",
                    "1. Upewnij się że fractal_horizon.py jest w tym samym katalogu co aii.py",
                    "2. LUB uruchom: python aii.py z katalogu gdzie są oba pliki",
                    "3. LUB skopiuj fractal_horizon.py do bieżącego katalogu",
                    "",
                    f"Sprawdź też czy nie było błędu importu przy starcie."
                ]
                return "\n".join(msg)
            s = self.fractal_horizon.state()
            lines = [f"{Colors.CYAN}=== HORYZONT ZDARZEŃ ==={Colors.RESET}",
                     f"  Kwantów:        {s['quanta']}",
                     f"  Śr. krzywizna:  {s['avg_curvature']:.4f}",
                     f"  Faza globalna:  {s['global_phase']:.4f}",
                     f"  Do emergencji:  {s['until_emergence']}"]
            if s['emergence_detected']:
                lines.append(f"  {Colors.YELLOW}⚠ EMERGENCJA ({s['self_queries']} pytań){Colors.RESET}")
            recalled = self.fractal_horizon.recall("introspect", self.context_vector, top_k=3, depth=2.0)
            if recalled:
                lines.append("\n  Najgłębszy rezonans:")
                for r in recalled:
                    lines.append(f"    ∿{r['score']:.3f} | {r['content'][:50]}")
            return "\n".join(lines)

        elif c == '/introspect':
            return self.introspect()

        elif c == '/emotions':
            return "\n".join(f" {k:12}: {Colors.YELLOW}{'█'*int(v*20)}{Colors.RESET} {v:.3f}"
                             for k, v in self.get_emotions().items())

        elif c == '/save':
            self.save()
            return f"{Colors.GREEN}Zapisano.{Colors.RESET}"

        elif c == '/read':
            if not arg or not os.path.exists(arg):
                return f"{Colors.RED}Plik nie istnieje: {arg}{Colors.RESET}"
            try:
                with open(arg, 'r', encoding='utf-8') as f:
                    lines = [l.strip() for l in f if l.strip()]
                added = activated = 0
                for line in lines:
                    mid = f"Read_{int(time.time())}_{added}"
                    line_vec = np.zeros(self.DIM)
                    if self.kurz:
                        sector, intensity = self.kurz.quick_scan(line)
                        if sector:
                            line_vec[self.AXES_ORDER.index(sector)] = intensity
                            activated += 1
                    if self.chunk_lexicon:
                        res = self.chunk_lexicon.analyze_text_chunks(line, verbose=False)
                        if res['coverage'] > 0:
                            line_vec = np.clip(line_vec + res['emotional_vector'] * 0.5, 0.0, 1.0)
                    if np.sum(line_vec) < 0.01:
                        line_vec[self.AXES_ORDER.index('logika')] = 0.3
                        line_vec[self.AXES_ORDER.index('wiedza')] = 0.3
                    record = {
                        'id': mid, 'tresc': line,
                        'wektor_C_Def': line_vec.tolist(), '_type': '@READ',
                        'weight': min(0.85, 0.6 + len(line.split()) / 100),
                        'time': time.time(),
                        'fractal': {'depth': 2, 'parent_id': None, 'children_ids': []}
                    }
                    self.D_Map[mid] = record
                    if self.fractal_horizon:
                        try: self.fractal_horizon.sync_from_fractal(record)
                        except Exception: pass
                    added += 1
                self.save()
                return f"{Colors.GREEN}Wczytano {added} linii ({activated} aktywowanych emocjonalnie).{Colors.RESET}"
            except Exception as e:
                return f"{Colors.RED}Błąd: {e}{Colors.RESET}"

        elif c == '/remember':
            if not arg:
                return f"{Colors.RED}Brak tekstu.{Colors.RESET}"
            mid = f"Mem_{int(time.time())}"
            mem_vec = np.zeros(self.DIM)
            if self.kurz:
                sector, intensity = self.kurz.quick_scan(arg)
                if sector:
                    mem_vec[self.AXES_ORDER.index(sector)] = intensity
            if self.chunk_lexicon:
                res = self.chunk_lexicon.analyze_text_chunks(arg, verbose=False)
                if res['coverage'] > 0:
                    mem_vec = np.clip(mem_vec + res['emotional_vector'] * 0.5, 0.0, 1.0)
            mem_vec = np.clip(mem_vec + self.context_vector * 0.3, 0.0, 1.0)
            if np.sum(mem_vec) < 0.01:
                mem_vec[self.AXES_ORDER.index('wiedza')] = 0.3
            record = {
                'id': mid, 'tresc': arg,
                'wektor_C_Def': mem_vec.tolist(), '_type': '@MEMORY',
                'weight': min(0.90, 0.7 + len(arg.split()) / 100),
                'time': time.time(),
                'fractal': {'depth': 3, 'parent_id': None, 'children_ids': []}
            }
            self.D_Map[mid] = record
            self.save()
            if self.fractal_horizon:
                try:
                    self.fractal_horizon.sync_from_fractal(record)
                    self.fractal_horizon.reinforce(mid, factor=0.5)
                except Exception: pass
            return f"{Colors.GREEN}Zapamiętano (emocjonalnie uziemione).{Colors.RESET}"

        elif c == '/activate':
            reactivated = 0
            for mid, entry in self.D_Map.items():
                if entry.get('_type', '') not in ('@READ', '@MEMORY'):
                    continue
                old_vec = np.array(entry.get('wektor_C_Def', np.zeros(self.DIM)))
                if np.count_nonzero(old_vec > 0.1) >= 2:
                    continue
                new_vec = np.zeros(self.DIM)
                if self.kurz:
                    sector, intensity = self.kurz.quick_scan(entry.get('tresc', ''))
                    if sector:
                        new_vec[self.AXES_ORDER.index(sector)] = intensity
                if self.chunk_lexicon:
                    res = self.chunk_lexicon.analyze_text_chunks(entry.get('tresc', ''), verbose=False)
                    if res['coverage'] > 0:
                        new_vec = np.clip(new_vec + res['emotional_vector'] * 0.5, 0.0, 1.0)
                if np.sum(new_vec) < 0.01:
                    new_vec[self.AXES_ORDER.index('wiedza')] = 0.3
                entry['wektor_C_Def'] = new_vec.tolist()
                reactivated += 1
            if reactivated > 0:
                self.save()
            return f"{Colors.GREEN}Aktywowano {reactivated} wspomnień (przeskanowano przez KURZ).{Colors.RESET}"

        elif c == '/quantum':
            if not self.quantum:
                return f"{Colors.RED}Quantum Bridge nieaktywny.{Colors.RESET}"
            qs = self.quantum.get_quantum_state()
            lines = [f"{Colors.CYAN}=== QUANTUM STATE ==={Colors.RESET}"]
            for name, data in sorted(qs.items(), key=lambda x: -x[1]['probability']):
                bar = '█' * int(data['probability'] * 20)
                # Przyciemnij osie poniżej progu (floor-level)
                if data['probability'] < 0.02:
                    lines.append(f"  {Colors.DIM}{name:12s}: {bar} "
                                 f"{data['probability']:.3f} ∠{data['phase_deg']:+.0f}°{Colors.RESET}")
                else:
                    lines.append(f"  {name:12s}: {Colors.YELLOW}{bar}{Colors.RESET} "
                                 f"{data['probability']:.3f} ∠{data['phase_deg']:+.0f}°")
            lines.append(f"  Entropy: {self.quantum.state.entropy():.2f} bits")
            lines.append(f"  Koherencja: {self.quantum.get_phase_coherence():.3f}")
            return "\n".join(lines)

        return f"{Colors.RED}Nieznana komenda. /help{Colors.RESET}"

    def save(self):
        if self.soul_io:
            self.soul_io.save_stream(self.D_Map)
        if self.chunk_lexicon:
            self.chunk_lexicon.save()
        if self.soul_io and hasattr(self.soul_io, 'filepath'):
            self.cortex.save(self.soul_io.filepath)
        if self.fractal_memory:
            try: self.fractal_memory.save()
            except Exception as e: print(f"[FRACTAL SAVE] Błąd: {e}")

        # POPRAWKA: bezpieczna ścieżka
        if self.quantum:
            try:
                base_dir = self._get_data_dir()
                os.makedirs(base_dir, exist_ok=True)
                qpath = os.path.join(base_dir, "quantum_state.json")
                with open(qpath, 'w', encoding='utf-8') as f:
                    json.dump(self.quantum.to_dict(), f, indent=2, ensure_ascii=False)
                print(f"{Colors.GREEN}[QUANTUM SAVE] → {qpath}{Colors.RESET}")
            except Exception as e:
                print(f"[QUANTUM SAVE] Błąd: {e}")

        if self.fractal_horizon:
            try: self.fractal_horizon.save()
            except Exception as e: print(f"[HORYZONT SAVE] Błąd: {e}")

    def load(self):
        if self.soul_io:
            loaded = self.soul_io.load_stream()
            if loaded:
                for mid, entry in loaded.items():
                    entry.setdefault('weight', 0.5)
                    entry.setdefault('time', time.time())
                    entry.setdefault('_type', '@MEMORY')
                self.D_Map = loaded

        # POPRAWKA: bezpieczna ścieżka
        if self.quantum:
            try:
                qpath = os.path.join(self._get_data_dir(), "quantum_state.json")
                if os.path.exists(qpath):
                    with open(qpath, 'r', encoding='utf-8') as f:
                        self.quantum.from_dict(json.load(f))
                    print(f"{Colors.GREEN}[QUANTUM] Załadowano fazy z {qpath}{Colors.RESET}")
            except Exception as e:
                print(f"[QUANTUM LOAD] Błąd: {e}")

    def get_emotions(self):
        return {self.AXES_ORDER[i]: float(self.context_vector[i]) for i in range(self.DIM)}

    def introspect(self):
        if np.sum(self.context_vector) < self.MIN_EMOTION_THRESHOLD:
            return "Neutralny"
        idx = np.argmax(self.context_vector)
        return f"Dominanta: {self.AXES_ORDER[idx].upper()} ({self.context_vector[idx]:.2f})"

    def process_input(self, text):
        return self.interact(text)


if __name__ == "__main__":
    aii = AII(standalone_mode=True)
    print(f"{Colors.CYAN}EriAmo {aii.VERSION} gotowy.{Colors.RESET}")