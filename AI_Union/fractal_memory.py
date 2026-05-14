# -*- coding: utf-8 -*-
"""
fractal_memory.py v1.1.2
POPRAWKI v1.1.2:
- BUGFIX: KeyError 'resonance' w store() przy auto_link na starych rekordach
  Dodano migrację w load(): setdefault('resonance') i setdefault('fractal')
  dla wszystkich rekordów wczytywanych z .soul (kompatybilność wsteczna)
- KRYTYCZNY BUGFIX: new_save() w integrate_fractal_memory() nie zapisywała
  quantum_state.json ani fractal_horizon — oba pliki były zawsze puste po restarcie
  Dodano: zapis quantum (→ quantum_state.json) i horizon (→ fractal_horizon.save())
- BUGFIX: new_load() nie wczytywała quantum state po restarcie
  Dodano: load quantum_state.json jeśli plik istnieje i jest niepusty
- Zabezpieczenie: os.path.getsize() > 0 przed json.load() (chroni przed pustym plikiem)
- BUGFIX: usunięto ręczne inkrementowanie stats['by_depth'] w store()
  get_statistics() zawsze liczy z indeksu — jedno źródło prawdy
- BUGFIX: get_statistics() liczy WSZYSTKIE głębokości z _depth_index (nie tylko 1–3)
- BUGFIX: walidacja długości wektora w store() — ValueError jeśli len != DIMENSION
- FEATURE: auto_parent — store() szuka najbardziej rezonującego rodzica i tworzy relację
- FEATURE: auto_link — store() linkuje do podobnych wspomnień (cosine > 0.7)
- OPTYMALIZACJA: proustian_recall() cache'uje znormalizowane wektory (_norm_cache)
- BUGFIX: integrate_fractal_memory() aktualizuje stats po migracji
- ARCHITEKTURA: _guard_dmap() — ochrona referencji D_Map (wykrywa nadpisanie)

POPRAWKI v1.0.4:
- Domyślna ścieżka: data/eriamo.soul (nie eriamo.soul)
- integrate_fractal_memory: nie wywołuje original_load() (łamało referencję)
- Migracja wspomnień z AII do Fractal przy integracji
"""

import numpy as np
import json
import time
import hashlib
import os
import threading
import shutil
from typing import Dict, List, Optional
from collections import defaultdict
from dataclasses import dataclass, field, asdict

try:
    from union_config import UnionConfig, Colors, AXES, DIMENSION
except ImportError:
    AXES = ['radość', 'smutek', 'strach', 'gniew', 'miłość', 'wstręt',
            'zaskoczenie', 'akceptacja', 'logika', 'wiedza', 'czas',
            'kreacja', 'byt', 'przestrzeń', 'chaos']
    DIMENSION = 15
    class Colors:
        CYAN = "\033[36m"
        RESET = "\033[0m"
        YELLOW = "\033[33m"
        MAGENTA = "\033[35m"
        GREEN = "\033[32m"
        RED = "\033[31m"


# ═══════════════════════════════════════════════════════════════════════════════
# STRUKTURY DANYCH
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class FractalMetadata:
    depth: int = 1
    parent_id: Optional[str] = None
    children_ids: List[str] = field(default_factory=list)
    abstraction_hash: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'FractalMetadata':
        return cls(**data) if data else cls()


@dataclass
class ResonanceMetadata:
    linked_ids: List[str] = field(default_factory=list)
    activation_count: int = 0
    last_resonance: float = 0.0

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'ResonanceMetadata':
        return cls(**data) if data else cls()


# ═══════════════════════════════════════════════════════════════════════════════
# GŁÓWNA KLASA
# ═══════════════════════════════════════════════════════════════════════════════

class FractalMemory:
    VERSION = "1.1.2"

    # POPRAWKA: Domyślna ścieżka to data/eriamo.soul
    def __init__(self, soul_file: str = "data/eriamo.soul", verbose: bool = False):
        self.soul_file = soul_file
        self.verbose = verbose

        self.D_Map: Dict[str, dict] = {}
        self._parent_index: Dict[str, str] = {}
        self._children_index: Dict[str, List[str]] = defaultdict(list)
        self._depth_index: Dict[int, set] = {1: set(), 2: set(), 3: set()}
        self._type_index: Dict[str, set] = defaultdict(set)

        self.stats = {
            'total': 0,
            'by_depth': {},
            'version': self.VERSION
        }

        self._lock = threading.RLock()
        self._norm_cache: Dict[str, float] = {}  # cache norm dla proustian_recall
        self._aii_instance = None  # ustawiany przez integrate_fractal_memory

        self.load()

        if self.verbose:
            stats = self.get_statistics()
            print(f"{Colors.CYAN}[FRACTAL] v{self.VERSION} zainicjalizowana – {stats['total']} wspomnień (plik: {self.soul_file}){Colors.RESET}")

    def _clear_indices(self):
        """Resetuje wszystkie indeksy."""
        with self._lock:
            self._parent_index.clear()
            self._children_index.clear()
            self._depth_index = {}
            self._type_index.clear()
            self._norm_cache.clear()
            if self.verbose:
                print(f"{Colors.YELLOW}[FRACTAL] Indeksy wyczyszczone{Colors.RESET}")

    def _index_record(self, mem_id: str, record: dict):
        """Dodaje rekord do indeksów."""
        fractal = record.get('fractal', {})
        depth = fractal.get('depth', 1)
        parent = fractal.get('parent_id')
        rec_type = record.get('_type', '@MEMORY')

        # Upewnij się że depth istnieje w indeksie
        if depth not in self._depth_index:
            self._depth_index[depth] = set()

        self._depth_index[depth].add(mem_id)
        self._type_index[rec_type].add(mem_id)

        if parent:
            self._parent_index[mem_id] = parent
            if mem_id not in self._children_index[parent]:
                self._children_index[parent].append(mem_id)

    def get_statistics(self) -> dict:
        """Zwraca aktualne statystyki. Zawsze liczy z indeksu — jedno źródło prawdy."""
        with self._lock:
            self.stats['total'] = len(self.D_Map)
            # Liczy WSZYSTKIE głębokości z _depth_index, nie tylko 1–3
            self.stats['by_depth'] = {
                depth: len(ids)
                for depth, ids in self._depth_index.items()
            }
            return self.stats.copy()

    def load(self) -> bool:
        if not os.path.exists(self.soul_file):
            if self.verbose:
                print(f"{Colors.YELLOW}[FRACTAL] Brak pliku {self.soul_file} – tabula rasa{Colors.RESET}")
            return False

        with self._lock:
            self.D_Map.clear()
            self._clear_indices()

            try:
                with open(self.soul_file, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            record = json.loads(line)
                            if record.get('_type') == '@META':
                                continue
                            mem_id = record.get('id', f"Mem_{line_num:05d}")
                            record['id'] = mem_id
                            # Migracja starych rekordów (przed v1.1.0) bez kluczy resonance/fractal
                            record.setdefault('resonance', {
                                'linked_ids': [], 'activation_count': 0, 'last_resonance': 0.0
                            })
                            record.setdefault('fractal', {
                                'depth': 1, 'parent_id': None, 'children_ids': []
                            })
                            self.D_Map[mem_id] = record
                            self._index_record(mem_id, record)
                        except json.JSONDecodeError:
                            continue

                stats = self.get_statistics()
                if self.verbose:
                    print(f"{Colors.GREEN}[FRACTAL] Wczytano {stats['total']} wspomnień z {self.soul_file}{Colors.RESET}")
                return True
            except Exception as e:
                print(f"{Colors.RED}[FRACTAL] Błąd ładowania: {e}{Colors.RESET}")
                return False

    def save(self) -> bool:
        with self._lock:
            try:
                # Upewnij się że katalog istnieje
                directory = os.path.dirname(self.soul_file)
                if directory and not os.path.exists(directory):
                    os.makedirs(directory, exist_ok=True)

                if os.path.exists(self.soul_file):
                    shutil.copy2(self.soul_file, self.soul_file + ".bak")

                temp_path = self.soul_file + ".tmp"
                with open(temp_path, 'w', encoding='utf-8') as f:
                    meta = {"_type": "@META", "version": self.VERSION, "stats": self.get_statistics()}
                    f.write(json.dumps(meta, ensure_ascii=False) + "\n")

                    for rec in self.D_Map.values():
                        f.write(json.dumps(rec, ensure_ascii=False) + "\n")

                os.replace(temp_path, self.soul_file)
                if self.verbose:
                    print(f"{Colors.GREEN}[FRACTAL] Zapisano {len(self.D_Map)} wspomnień do {self.soul_file}{Colors.RESET}")
                return True
            except Exception as e:
                print(f"{Colors.RED}[FRACTAL] Błąd zapisu: {e}{Colors.RESET}")
                return False

    def store(
        self,
        content: str,
        vector: np.ndarray | list,
        rec_type: str = "@DIALOG",
        weight: float = 0.5,
        auto_link: bool = True,
        auto_parent: bool = True
    ) -> str:
        """
        Zapisuje nowe wspomnienie.
        - auto_parent: szuka najbardziej rezonującego rodzica depth+1 i tworzy relację
        - auto_link: linkuje do podobnych wspomnień (cosine >= 0.7)
        - Nie inkrementuje stats ręcznie — get_statistics() liczy z indeksu
        """
        if isinstance(vector, np.ndarray):
            vector = vector.tolist()

        # WALIDACJA długości wektora
        if len(vector) != DIMENSION:
            raise ValueError(
                f"[FRACTAL] Wektor musi mieć długość {DIMENSION}, "
                f"otrzymano {len(vector)}"
            )

        mem_id = f"Mem_{int(time.time())}_{len(self.D_Map):04d}"

        depth = 1
        if weight >= 0.90:
            depth = 3
        elif weight >= 0.60:
            depth = 2

        record = {
            "id": mem_id,
            "tresc": content,
            "wektor_C_Def": vector,
            "_type": rec_type,
            "weight": weight,
            "time": time.time(),
            "fractal": {
                "depth": depth,
                "parent_id": None,
                "children_ids": []
            },
            "resonance": {
                "linked_ids": [],
                "activation_count": 0,
                "last_resonance": time.time()
            }
        }

        with self._lock:
            vec_np = np.array(vector, dtype=np.float32)
            vec_norm = float(np.linalg.norm(vec_np))

            # AUTO_PARENT: znajdź rodzica z depth > aktualnej (bardziej abstrakcyjny)
            if auto_parent and vec_norm > 0.01:
                best_parent_id = None
                best_sim = 0.0
                target_depth = depth + 1
                parent_candidates = self._depth_index.get(target_depth, set())
                for pid in parent_candidates:
                    parent_rec = self.D_Map.get(pid)
                    if not parent_rec:
                        continue
                    p_vec = np.array(parent_rec.get('wektor_C_Def', [0] * DIMENSION),
                                     dtype=np.float32)
                    p_norm = self._norm_cache.get(pid) or float(np.linalg.norm(p_vec))
                    self._norm_cache[pid] = p_norm
                    if p_norm < 0.01:
                        continue
                    sim = float(np.dot(vec_np, p_vec) / (vec_norm * p_norm))
                    if sim > best_sim:
                        best_sim = sim
                        best_parent_id = pid

                if best_parent_id and best_sim >= 0.5:
                    record['fractal']['parent_id'] = best_parent_id
                    parent_entry = self.D_Map[best_parent_id]
                    if mem_id not in parent_entry['fractal']['children_ids']:
                        parent_entry['fractal']['children_ids'].append(mem_id)

            # AUTO_LINK: linkuj do podobnych wspomnień tej samej głębokości
            if auto_link and vec_norm > 0.01:
                linked = []
                same_depth = self._depth_index.get(depth, set())
                for lid in same_depth:
                    if lid == mem_id:
                        continue
                    link_rec = self.D_Map.get(lid)
                    if not link_rec:
                        continue
                    l_vec = np.array(link_rec.get('wektor_C_Def', [0] * DIMENSION),
                                     dtype=np.float32)
                    l_norm = self._norm_cache.get(lid) or float(np.linalg.norm(l_vec))
                    self._norm_cache[lid] = l_norm
                    if l_norm < 0.01:
                        continue
                    sim = float(np.dot(vec_np, l_vec) / (vec_norm * l_norm))
                    if sim >= 0.7:
                        linked.append(lid)
                        # Dodaj wzajemne połączenie
                        if mem_id not in link_rec['resonance']['linked_ids']:
                            link_rec['resonance']['linked_ids'].append(mem_id)
                    if len(linked) >= 5:  # max 5 linków
                        break
                record['resonance']['linked_ids'] = linked

            # Zapisz norm do cache
            self._norm_cache[mem_id] = vec_norm

            self.D_Map[mem_id] = record
            self._index_record(mem_id, record)
            # BRAK ręcznego inkrementowania stats — get_statistics() liczy z indeksu

        if self.verbose:
            parent_info = f" parent={record['fractal']['parent_id']}" if record['fractal']['parent_id'] else ""
            links_info = f" links={len(record['resonance']['linked_ids'])}" if record['resonance']['linked_ids'] else ""
            print(f"[FRACTAL] Zapisano {mem_id} (depth={depth}{parent_info}{links_info})")

        return mem_id

    def proustian_recall(self, emotion_vector: np.ndarray, threshold: float = 0.6) -> List[dict]:
        """
        Proustowski recall – rozszerza wektor 8D do 15D.
        Używa _norm_cache dla eliminacji powtórnych obliczeń normy.
        """
        emotion_vector = np.array(emotion_vector, dtype=np.float32)
        if len(emotion_vector) == 8:
            full_vec = np.zeros(DIMENSION, dtype=np.float32)
            full_vec[:8] = emotion_vector
            emotion_vector = full_vec

        emo_norm = float(np.linalg.norm(emotion_vector))
        if emo_norm < 0.01:
            return []

        matches = []
        with self._lock:
            for mid, rec in self.D_Map.items():
                vec = np.array(rec.get('wektor_C_Def', [0] * DIMENSION), dtype=np.float32)

                # Cache normy — unikamy sqrt przy każdym recall
                vec_norm = self._norm_cache.get(mid)
                if vec_norm is None:
                    vec_norm = float(np.linalg.norm(vec))
                    self._norm_cache[mid] = vec_norm

                if vec_norm < 0.01:
                    continue

                sim = float(np.dot(emotion_vector, vec)) / (emo_norm * vec_norm)
                if sim >= threshold:
                    matches.append(rec)

        matches.sort(key=lambda r: r.get('weight', 0.5), reverse=True)
        return matches[:5]


# ═══════════════════════════════════════════════════════════════════════════════
# INTEGRACJA Z AII - POPRAWIONA WERSJA
# ═══════════════════════════════════════════════════════════════════════════════

def integrate_fractal_memory(aii_instance, soul_file: str = "data/eriamo.soul"):
    """
    Integruje FractalMemory z instancją AII.

    v1.1.0:
    - Aktualizuje stats po migracji
    - Przechowuje referencję _aii_instance dla guard
    - new_load() ponownie ustawia D_Map po każdym load()

    v1.0.4:
    - Migracja istniejących wspomnień z AII do Fractal
    - NIE wywołuje original_load() (to łamało referencję D_Map)
    - Tylko Fractal zapisuje do .soul (unika podwójnego zapisu)
    """
    print(f"{Colors.CYAN}[FRACTAL] Integracja z plikiem: {soul_file}{Colors.RESET}")

    fractal = FractalMemory(soul_file, verbose=True)
    fractal._aii_instance = aii_instance

    # Migruj istniejące wspomnienia z AII do Fractal (jeśli AII ma więcej)
    if aii_instance.D_Map:
        migrated = 0
        for mid, record in aii_instance.D_Map.items():
            if mid not in fractal.D_Map:
                fractal.D_Map[mid] = record
                fractal._index_record(mid, record)
                migrated += 1
        if migrated > 0:
            # BUGFIX: aktualizuj stats po migracji
            fractal.get_statistics()
            print(f"{Colors.YELLOW}[FRACTAL] Zmigrowano {migrated} wspomnień z AII{Colors.RESET}")

    # KRYTYCZNE: Wspólna referencja — AII używa tego samego D_Map co Fractal
    aii_instance.D_Map = fractal.D_Map
    aii_instance.fractal_memory = fractal

    def new_save():
        """
        Zapisuje WSZYSTKIE komponenty systemu:
        - FractalMemory → .soul
        - ChunkLexicon
        - VectorCortex
        - QuantumBridge → quantum_state.json
        - FractalHorizon → horizon.json
        """
        # GUARD: sprawdź czy D_Map nie został nadpisany nowym obiektem
        if aii_instance.D_Map is not fractal.D_Map:
            print(f"{Colors.RED}[FRACTAL] ⚠ UWAGA: D_Map rozłączony! Naprawiam referencję.{Colors.RESET}")
            for mid, rec in aii_instance.D_Map.items():
                if mid not in fractal.D_Map:
                    fractal.D_Map[mid] = rec
                    fractal._index_record(mid, rec)
            aii_instance.D_Map = fractal.D_Map

        # 1. Główna pamięć
        fractal.save()

        # 2. Leksykon chunków
        if aii_instance.chunk_lexicon:
            aii_instance.chunk_lexicon.save()

        # 3. VectorCortex
        if hasattr(aii_instance, 'cortex') and aii_instance.soul_io and hasattr(aii_instance.soul_io, 'filepath'):
            aii_instance.cortex.save(aii_instance.soul_io.filepath)

        # 4. Quantum state → quantum_state.json
        if getattr(aii_instance, 'quantum', None):
            try:
                import json as _json
                import os as _os
                base_dir = aii_instance._get_data_dir() if hasattr(aii_instance, '_get_data_dir') else "data"
                _os.makedirs(base_dir, exist_ok=True)
                qpath = _os.path.join(base_dir, "quantum_state.json")
                with open(qpath, 'w', encoding='utf-8') as f:
                    _json.dump(aii_instance.quantum.to_dict(), f, indent=2, ensure_ascii=False)
                print(f"{Colors.GREEN}[QUANTUM SAVE] → {qpath}{Colors.RESET}")
            except Exception as e:
                print(f"{Colors.RED}[QUANTUM SAVE] Błąd: {e}{Colors.RESET}")

        # 5. FractalHorizon → horizon.json
        if getattr(aii_instance, 'fractal_horizon', None):
            try:
                aii_instance.fractal_horizon.save()
            except Exception as e:
                print(f"{Colors.RED}[HORYZONT SAVE] Błąd: {e}{Colors.RESET}")

        print(f"{Colors.GREEN}[SAVE] Zapisano {len(fractal.D_Map)} wspomnień{Colors.RESET}")

    def new_load():
        """
        Ładuje pamięć + quantum state.
        Ponawia wspólną referencję D_Map po każdym load().
        """
        fractal.load()
        aii_instance.D_Map = fractal.D_Map  # KRYTYCZNE: odśwież referencję po load()

        # Quantum state → wczytaj jeśli istnieje
        if getattr(aii_instance, 'quantum', None):
            try:
                import json as _json
                import os as _os
                base_dir = aii_instance._get_data_dir() if hasattr(aii_instance, '_get_data_dir') else "data"
                qpath = _os.path.join(base_dir, "quantum_state.json")
                if _os.path.exists(qpath) and _os.path.getsize(qpath) > 0:
                    with open(qpath, 'r', encoding='utf-8') as f:
                        aii_instance.quantum.from_dict(_json.load(f))
                    # Zastosuj FLOOR natychmiast po wczytaniu —
                    # zapobiega startowi z kolapsem do jednej osi
                    aii_instance.quantum.sync_from_aii()
                    print(f"{Colors.GREEN}[QUANTUM] Załadowano fazy z {qpath}{Colors.RESET}")
            except Exception as e:
                print(f"{Colors.RED}[QUANTUM LOAD] Błąd: {e}{Colors.RESET}")

        print(f"{Colors.GREEN}[LOAD] Wczytano {len(fractal.D_Map)} wspomnień{Colors.RESET}")

    aii_instance.save = new_save
    aii_instance.load = new_load

    stats = fractal.get_statistics()
    print(f"{Colors.GREEN}[FRACTAL] Zintegrowano — {stats['total']} wspomnień aktywnych{Colors.RESET}")
    return fractal


# ═══════════════════════════════════════════════════════════════════════════════
# TEST
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print(f"\n{Colors.CYAN}TEST FractalMemory v1.1.0{Colors.RESET}")

    mem = FractalMemory("test_fractal.soul", verbose=True)

    # Test walidacji wektora
    try:
        mem.store(content="Zły wektor", vector=np.zeros(5), weight=0.5)
        print(f"{Colors.RED}BŁĄD: brak ValueError!{Colors.RESET}")
    except ValueError as e:
        print(f"{Colors.GREEN}✓ Walidacja wektora: {e}{Colors.RESET}")

    # Depth 3 (rodzic)
    id_parent = mem.store(
        content="Abstrakcja: miłość i smutek",
        vector=np.array([0, 0.5, 0, 0, 0.8, 0, 0, 0.5, 0, 0, 0, 0, 0, 0, 0]),
        weight=0.95
    )

    # Depth 2 (powinno auto-linkować do rodzica depth=3)
    id_child = mem.store(
        content="Czuję miłość",
        vector=np.array([0, 0, 0, 0, 1.0, 0, 0, 0.5, 0, 0, 0, 0, 0, 0, 0]),
        weight=0.7
    )

    # Depth 1 (powinno auto-linkować do depth=2)
    id_leaf = mem.store(
        content="Kocham kogoś",
        vector=np.array([0, 0, 0, 0, 0.9, 0, 0, 0.3, 0, 0, 0, 0, 0, 0, 0]),
        weight=0.4
    )

    print("\nStatystyki:")
    s = mem.get_statistics()
    print(f"  total={s['total']} by_depth={s['by_depth']}")

    # Sprawdź relacje
    leaf_rec = mem.D_Map.get(id_leaf, {})
    print(f"\nRelacje liścia ({id_leaf}):")
    print(f"  parent_id = {leaf_rec.get('fractal', {}).get('parent_id')}")
    print(f"  linked_ids = {leaf_rec.get('resonance', {}).get('linked_ids')}")

    print("\nProustian recall (miłość):")
    recalled = mem.proustian_recall(np.array([0, 0, 0, 0, 0.9, 0, 0, 0]))
    for r in recalled:
        print(f"  - {r.get('tresc')} (waga: {r.get('weight')})")

    # Test stats spójności po zapisie i wczytaniu
    mem.save()
    mem2 = FractalMemory("test_fractal.soul", verbose=False)
    s2 = mem2.get_statistics()
    print(f"\nPo reload: total={s2['total']} by_depth={s2['by_depth']}")
    assert s2['total'] == s['total'], "BŁĄD: stats['total'] niezgodne!"
    print(f"{Colors.GREEN}✓ stats spójne po reload{Colors.RESET}")

    # Cleanup
    for f in ["test_fractal.soul", "test_fractal.soul.bak"]:
        if os.path.exists(f):
            os.remove(f)

    print(f"\n{Colors.GREEN}Test zakończony.{Colors.RESET}")