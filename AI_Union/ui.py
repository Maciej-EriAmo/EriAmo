# -*- coding: utf-8 -*-
"""
ui.py v8.5
Moduł interfejsu użytkownika dla EriAmo Union.
Obsługuje animacje tekstu, loga i efekty wizualne w stylu Retro Terminal.
"""

import sys
import time
import random

# Używamy centralnej konfiguracji (Single Source of Truth)
try:
    from union_config import Colors
except ImportError:
    # Fallback, gdyby brakowało pliku konfiguracyjnego
    class Colors:
        CYAN = "\033[36m"
        MAGENTA = "\033[35m"
        GREEN = "\033[32m"
        YELLOW = "\033[33m"
        RED = "\033[31m"
        BOLD = "\033[1m"
        FAINT = "\033[2m"
        RESET = "\033[0m"
        WHITE = "\033[37m"

class RetroUI:
    """Zarządza warstwą wizualną terminala (Retro Style)."""

    def __init__(self):
        self.typing_speed = 0.02

    def print_logo(self):
        """Wyświetla logo startowe."""
        logo = f"""
    {Colors.CYAN}╔══════════════════════════════════════════════════════════════╗
    ║ {Colors.BOLD}{Colors.MAGENTA}  E R I A M O   U N I O N   {Colors.CYAN}                                 ║
    ║ {Colors.FAINT}  Artificial General Intelligence v8.5                       {Colors.CYAN}║
    ╚══════════════════════════════════════════════════════════════╝{Colors.RESET}
        """
        print(logo)
        time.sleep(0.3)

    def print_animated_text(self, text, color=Colors.WHITE, delay=None):
        """
        Wyświetla tekst znak po znaku (efekt maszyny do pisania).
        """
        if delay is None:
            delay = self.typing_speed

        print(f"{color}", end="")
        for char in text:
            sys.stdout.write(char)
            sys.stdout.flush()
            # Interpunkcja daje dłuższą pauzę (naturalność mowy)
            if char in [".", "!", "?"]:
                time.sleep(delay * 5)
            elif char in [",", ";"]:
                time.sleep(delay * 3)
            else:
                time.sleep(delay)
        print(f"{Colors.RESET}")

    def show_thinking_dots(self, message="Myślę", duration_sec=1.0, color=Colors.FAINT + Colors.CYAN):
        """
        Wyświetla animowane kropki [...]
        """
        sys.stdout.write(f"{color}{message}")
        sys.stdout.flush()
        
        steps = int(duration_sec / 0.3)
        for _ in range(steps):
            sys.stdout.write(".")
            sys.stdout.flush()
            time.sleep(0.3)
            
        sys.stdout.write(f"{Colors.RESET}\n")

    def print_system_message(self, msg, type="INFO"):
        """Formatowane komunikaty systemowe."""
        if type == "INFO":
            col = Colors.GREEN
        elif type == "WARN":
            col = Colors.YELLOW
        elif type == "ERROR":
            col = Colors.RED
        elif type == "UNION":
            col = Colors.MAGENTA
        else:
            col = Colors.CYAN
            
        print(f"{col}[{type}] {msg}{Colors.RESET}")

# Alias dla kompatybilności wstecznej (jeśli jakieś stare moduły tego używają)
FancyUI = RetroUI