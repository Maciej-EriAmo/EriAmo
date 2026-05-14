# -*- coding: utf-8 -*-
"""
soul_io.py v8.1.0-Safe
FIX: Dodano automatyczny backup przed zapisem i walidację.
"""
import json
import os
import time
import shutil  # Dodano do obsługi kopii zapasowych
from union_config import UnionConfig as Config, Colors

class SoulIO:
    def __init__(self):
        # Spróbuj różnych lokalizacji
        default_path = getattr(Config, 'SOUL_FILE', 'data/eriamo.soul')
        possible_paths = [
            'eriamo.soul',           # Główny katalog (NAJPIERW!)
            './eriamo.soul',
            default_path,            # Z config
            'data/eriamo.soul',
            '../eriamo.soul'
        ]
        
        # Znajdź pierwszy istniejący plik
        self.filepath = default_path
        for path in possible_paths:
            if os.path.exists(path):
                self.filepath = path
                print(f"{Colors.CYAN}[SoulIO] Użycie pliku: {path}{Colors.RESET}")
                break

    def _ensure_directory(self):
        directory = os.path.dirname(self.filepath)
        if directory and not os.path.exists(directory):
            try:
                os.makedirs(directory, exist_ok=True)
            except Exception as e:
                print(f"{Colors.RED}[SoulIO] Błąd tworzenia katalogu: {e}{Colors.RESET}")

    def load_stream(self):
        loaded_data = {}
        if not os.path.exists(self.filepath):
            print(f"{Colors.YELLOW}[SoulIO] Brak pliku pamięci. Tabula Rasa.{Colors.RESET}")
            return loaded_data
            
        count = 0
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line: continue
                    try:
                        data = json.loads(line)
                        # ✅ FIX: Pomiń TYLKO linie META
                        if data.get('_type') == '@META':
                            continue
                        
                        # Generuj ID jeśli nie ma
                        rec_id = data.get('id', f"Mem_{count}_{int(time.time())}")
                        loaded_data[rec_id] = data
                        count += 1
                    except json.JSONDecodeError:
                        # Ignorujemy uszkodzone linie, by nie wywalić całego ładowania
                        continue
            print(f"{Colors.GREEN}[SoulIO] Wczytano {count} wspomnień.{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.RED}[SoulIO] Krytyczny błąd odczytu: {e}{Colors.RESET}")
            
        return loaded_data

    def save_stream(self, data_to_save):
        self._ensure_directory()
        
        # --- FIX: BACKUP DANYCH ---
        if os.path.exists(self.filepath):
            try:
                backup_path = self.filepath + ".bak"
                shutil.copy2(self.filepath, backup_path)
            except Exception as e:
                print(f"{Colors.YELLOW}[SoulIO] Ostrzeżenie: Nie udało się zrobić backupu ({e}){Colors.RESET}")

        try:
            # Zapisz najpierw do pliku tymczasowego, żeby nie uszkodzić głównego przy crashu
            temp_path = self.filepath + ".tmp"
            with open(temp_path, 'w', encoding='utf-8') as f:
                meta = {"_type": "@META", "timestamp": time.time(), "count": len(data_to_save)}
                f.write(json.dumps(meta, ensure_ascii=False) + "\n")
                
                for key, val in data_to_save.items():
                    f.write(json.dumps(val, ensure_ascii=False) + "\n")
            
            # Jeśli zapis się udał, podmień pliki
            os.replace(temp_path, self.filepath)
            
        except Exception as e:
            print(f"{Colors.RED}[SoulIO] Błąd zapisu: {e}{Colors.RESET}")