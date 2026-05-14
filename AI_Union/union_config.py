"""
EriAmo Union - Centralna Konfiguracja
======================================
SINGLE SOURCE OF TRUTH dla wszystkich definicji osi i konfiguracji systemu.

Wszystkie moduły MUSZĄ importować definicje stąd:
    from union_config import UnionConfig, AXES, DIMENSION, Colors
"""

import os
from typing import List, Dict, Set
from pathlib import Path


# ═══════════════════════════════════════════════════════════════════════════════
# DEFINICJE OSI - SINGLE SOURCE OF TRUTH
# ═══════════════════════════════════════════════════════════════════════════════

# Główna lista 15 osi (8 biologicznych + 7 metafizycznych)
AXES: List[str] = [
    # Biologiczne (Plutchik) - indeksy 0-7
    'radość', 'smutek', 'strach', 'gniew',
    'miłość', 'wstręt', 'zaskoczenie', 'akceptacja',
    # Metafizyczne - indeksy 8-14
    'logika', 'wiedza', 'czas', 'kreacja',
    'byt', 'przestrzeń', 'chaos'
]

# Wymiarowość
DIMENSION: int = len(AXES)  # Automatycznie z AXES – bezpieczniej
BIO_DIM: int = 8    # Wymiary biologiczne (emocje Plutchika)
META_DIM: int = DIMENSION - BIO_DIM   # Automatycznie

# Podział funkcjonalny
BIO_AXES: List[str] = AXES[:BIO_DIM]   # Emocje biologiczne
META_AXES: List[str] = AXES[BIO_DIM:]  # Wymiary metafizyczne

# ═══════════════════════════════════════════════════════════════════════════════
# KLASYFIKACJA OSI DLA SYSTEMU MUZYCZNEGO
# ═══════════════════════════════════════════════════════════════════════════════

# Osie efemeryczne - szybko wygasające stany emocjonalne
EPHEMERAL_AXES: List[str] = [
    'radość', 'smutek', 'strach', 'gniew', 'zaskoczenie'
]

# Osie trwałe - stabilne cechy i preferencje
PERSISTENT_AXES: List[str] = [
    'miłość', 'wstręt', 'akceptacja',
    'logika', 'wiedza', 'kreacja', 'byt', 'przestrzeń'
]

# Osie dynamiczne - zmienne w czasie
DYNAMIC_AXES: List[str] = ['czas', 'chaos']

# Walidacja: Upewnij się, że wszystkie osie są pokryte
all_classified = set(EPHEMERAL_AXES + PERSISTENT_AXES + DYNAMIC_AXES)
assert all_classified == set(AXES), f"Błąd: Nie wszystkie osie sklasyfikowane! Brakujące: {set(AXES) - all_classified}"

# ═══════════════════════════════════════════════════════════════════════════════
# KOLORY TERMINALA
# ═══════════════════════════════════════════════════════════════════════════════

class Colors:
    """Kolory ANSI dla terminala."""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    MAGENTA = '\033[35m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'  # Alias dla kompatybilności (usunąłem duplikat END)
    FAINT = DIM  # Alias kompatybilności — niektóre moduły używają FAINT zamiast DIM
    END = RESET  # Alias kompatybilności
    
    # Aliasy dla emocji – mapa na wszystkie osie
    AXIS_COLORS = {
        'radość': GREEN,
        'smutek': BLUE,
        'strach': MAGENTA,
        'gniew': RED,
        'miłość': '\033[38;5;213m',  # Różowy
        'wstręt': '\033[38;5;58m',   # Oliwkowy
        'zaskoczenie': YELLOW,
        'akceptacja': CYAN,
        'logika': WHITE,
        'wiedza': '\033[38;5;214m',  # Pomarańczowy
        'czas': DIM,
        'kreacja': '\033[38;5;27m',  # Niebieski kreatywny
        'byt': '\033[38;5;136m',     # Brązowy
        'przestrzeń': '\033[38;5;69m',  # Niebiesko-zielony
        'chaos': '\033[38;5;196m'    # Ciemny czerwony
    }
    
    @classmethod
    def get_for_axis(cls, axis: str) -> str:
        """Zwraca kolor dla danej osi (fallback na WHITE)."""
        return cls.AXIS_COLORS.get(axis, cls.WHITE)


# ═══════════════════════════════════════════════════════════════════════════════
# GŁÓWNA KLASA KONFIGURACJI
# ═══════════════════════════════════════════════════════════════════════════════

class UnionConfig:
    """
    Centralna konfiguracja systemu EriAmo Union.
    
    Użycie:
        from union_config import UnionConfig
        
        print(UnionConfig.AXES)      # Atrybut klasowy
        print(UnionConfig.DIMENSION) # Atrybut klasowy
    """
    
    # === OSIE (atrybuty KLASOWE - dostępne bez instancji) ===
    AXES = AXES
    DIMENSION = DIMENSION
    BIO_DIM = BIO_DIM
    META_DIM = META_DIM
    
    BIO_AXES = BIO_AXES
    META_AXES = META_AXES
    
    EPHEMERAL_AXES = EPHEMERAL_AXES
    PERSISTENT_AXES = PERSISTENT_AXES
    DYNAMIC_AXES = DYNAMIC_AXES
    
    # Alias dla kompatybilności wstecznej
    AXES_LIST = AXES
    
    # === ŚCIEŻKI ===
    BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
    SOUL_DIR = BASE_DIR / "souls"
    MUSIC_DIR = BASE_DIR / "music"
    LOGS_DIR = BASE_DIR / "logs"
    
    # === PAMIĘĆ ===
    MEMORY_DECAY = 0.95
    EMOTION_DECAY = 0.85
    MAX_MEMORY_SIZE = 10000
    
    # === MUZYKA ===
    DEFAULT_BPM = 120
    DEFAULT_SOUNDFONT = "FluidR3_GM.sf2"
    
    # === SYSTEM ===
    VERSION = "8.7.1-beta"  # Zaktualizowana
    DEBUG = bool(os.getenv('DEBUG', False))  # Z env var
    
    @classmethod
    def init_dirs(cls):
        """Tworzy katalogi jeśli nie istnieją – z obsługą błędów."""
        for dir_path in [cls.SOUL_DIR, cls.MUSIC_DIR, cls.LOGS_DIR]:
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
            except OSError as e:
                print(f"{Colors.RED}[CONFIG] Błąd tworzenia {dir_path}: {e}{Colors.RESET}")
    
    @classmethod
    def get_axis_index(cls, axis_name: str) -> int:
        """Zwraca indeks osi po nazwie – raise jeśli brak."""
        idx = {axis: i for i, axis in enumerate(cls.AXES)}.get(axis_name, -1)
        if idx == -1:
            raise ValueError(f"Oś '{axis_name}' nie istnieje w AXES.")
        return idx
    
    @classmethod
    def is_ephemeral(cls, axis_name: str) -> bool:
        """Sprawdza czy oś jest efemeryczna."""
        return axis_name in set(cls.EPHEMERAL_AXES)
    
    @classmethod
    def is_persistent(cls, axis_name: str) -> bool:
        """Sprawdza czy oś jest trwała."""
        return axis_name in set(cls.PERSISTENT_AXES)
    
    @classmethod
    def is_biological(cls, axis_name: str) -> bool:
        """Sprawdza czy oś jest biologiczna (emocja Plutchika)."""
        return axis_name in cls.BIO_AXES
    
    @classmethod
    def is_metaphysical(cls, axis_name: str) -> bool:
        """Sprawdza czy oś jest metafizyczna."""
        return axis_name in cls.META_AXES

    @classmethod
    def validate_axes(cls):
        """Waliduje konfigurację osi – wywołać na starcie."""
        assert len(cls.AXES) == cls.DIMENSION, "Błąd: len(AXES) != DIMENSION"
        assert len(set(cls.AXES)) == cls.DIMENSION, "Błąd: Duplikaty w AXES"
        assert len(cls.BIO_AXES) == cls.BIO_DIM, "Błąd: BIO_AXES len"
        assert len(cls.META_AXES) == cls.META_DIM, "Błąd: META_AXES len"
        print(f"{Colors.GREEN}[CONFIG] Walidacja osi OK.{Colors.RESET}")


# ═══════════════════════════════════════════════════════════════════════════════
# ALIASY DLA KOMPATYBILNOŚCI WSTECZNEJ
# ═══════════════════════════════════════════════════════════════════════════════

# Alias klasy Config -> UnionConfig
Config = UnionConfig


# ═══════════════════════════════════════════════════════════════════════════════
# EKSPORTY MODUŁU
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Główne definicje osi
    'AXES',
    'DIMENSION',
    'BIO_DIM',
    'META_DIM',
    'BIO_AXES',
    'META_AXES',
    
    # Klasyfikacja osi
    'EPHEMERAL_AXES',
    'PERSISTENT_AXES',
    'DYNAMIC_AXES',
    
    # Aliasy kompatybilności
    'AXES_LIST',
    
    # Klasy
    'UnionConfig',
    'Config',  # Alias dla kompatybilności
    'Colors',
]


# ═══════════════════════════════════════════════════════════════════════════════
# TEST
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    UnionConfig.validate_axes()  # Walidacja na starcie testu
    UnionConfig.init_dirs()      # Test tworzenia dir
    
    print(f"{Colors.CYAN}=== EriAmo Union Config ==={Colors.RESET}")
    print(f"\n{Colors.GREEN}AXES ({DIMENSION}):{Colors.RESET}")
    
    for i, axis in enumerate(AXES):
        category = "BIO" if i < BIO_DIM else "META"
        ephemeral = "⚡" if UnionConfig.is_ephemeral(axis) else ""
        persistent = "🔒" if UnionConfig.is_persistent(axis) else ""
        dynamic = "🔄" if axis in DYNAMIC_AXES else ""
        color = Colors.get_for_axis(axis)
        print(f"  [{i:2d}] {color}{axis:12s}{Colors.RESET} ({category}) {ephemeral}{persistent}{dynamic}")
    
    print(f"\n{Colors.YELLOW}Klasyfikacja:{Colors.RESET}")
    print(f"  Efemeryczne: {EPHEMERAL_AXES}")
    print(f"  Trwałe:      {PERSISTENT_AXES}")
    print(f"  Dynamiczne:  {DYNAMIC_AXES}")