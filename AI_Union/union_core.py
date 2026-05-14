# -*- coding: utf-8 -*-
"""
union_core.py v2.1.1
Serce systemu.
FIX v2.1.1: guard przed AttributeError gdy chunk_lexicon=None w stop()
FIX v2.1.0: Głośne raportowanie zapisu danych przy zamykaniu.
"""

import sys
import os

# Import Rdzenia Językowego
try:
    from aii import AII
except ImportError:
    print("❌ Błąd krytyczny: Nie znaleziono pliku aii.py")
    sys.exit(1)

# Konfiguracja
try:
    from union_config import UnionConfig, Colors
except ImportError:
    class Colors:
        CYAN = ""; RESET = ""; RED = ""; YELLOW = ""; GREEN = ""; MAGENTA = ""

class EriAmoUnion:
    def __init__(self, verbose=True):
        self.verbose = verbose
        if self.verbose:
            print(f"{Colors.CYAN}[UNION] Ładowanie rdzenia AII...{Colors.RESET}")
        
        # Inicjalizacja Mózgu
        self.aii = AII(standalone_mode=False) 
        self.running = False

    def start(self):
        """Uruchamia procesy Unii."""
        self.running = True
        if self.verbose:
            print(f"{Colors.CYAN}[UNION] System połączony.{Colors.RESET}")

    def stop(self):
        """Bezpieczne zamykanie z raportem."""
        self.running = False
        print(f"\n{Colors.MAGENTA}╔══════════════════════════════════════╗{Colors.RESET}")
        print(f"{Colors.MAGENTA}║ [UNION] ROZPOCZYNAM PROCEDURĘ ZAPISU ║{Colors.RESET}")
        
        if self.aii:
            print(f"{Colors.YELLOW}║ 💾 Zapisywanie pamięci (D_Map)...    ║{Colors.RESET}")
            # Wymuszamy zapis
            self.aii.save()
            
            # Raport
            count = len(self.aii.D_Map)
            print(f"{Colors.GREEN}║ ✅ Zapisano {count} wspomnień.           ║{Colors.RESET}")
            
            # FIX v2.1.1: guard — chunk_lexicon może być None przy błędzie init
            chunks = getattr(getattr(self.aii, "chunk_lexicon", None), "total_chunks", None)
            if chunks is not None:
                print(f"{Colors.GREEN}║ ✅ Zapisano {chunks} chunków językowych.   ║{Colors.RESET}")
        
        print(f"{Colors.MAGENTA}╚══════════════════════════════════════╝{Colors.RESET}")
        print(f"{Colors.CYAN}[SYSTEM] Można bezpiecznie zamknąć.{Colors.RESET}")

    def process_input(self, user_input):
        """Przekazuje tekst do rdzenia AII i zwraca odpowiedź."""
        if not self.aii:
            return "Błąd: Rdzeń AII nieaktywny."
        response = self.aii.interact(user_input)
        return response