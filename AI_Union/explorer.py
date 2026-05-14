# -*- coding: utf-8 -*-
# explorer.py v8.2.0-Quantum - Direct Glob Targeting & Thermal Decoherence
"""
Moduł eksploracji świata fizycznego.
ZMIANA v8.2.0: Integracja z QuantumBridge. Temperatura procesora uderza
bezpośrednio w fazy kwantowe jako Szum Termiczny (Dekoherencja).
ZMIANA v8.1.0: Porzucono os.walk na rzecz glob.glob.
Rozwiązuje problem ignorowania symlinków w /sys/class/.
"""

import os
import glob
import re
import time
import json
import random
import math
import numpy as np

# Kolory importowane z union_config.py (Single Source of Truth)
try:
    from union_config import Colors
except ImportError:
    class Colors:
        RED = '\033[91m'; GREEN = '\033[92m'; YELLOW = '\033[93m'
        CYAN = '\033[96m'; RESET = '\033[0m'

class WorldExplorer:
    def __init__(self, aii_instance=None):
        self.aii = aii_instance
        self.discoveries = []
        self.sensors = {}
        
        self.load_discoveries()
        
        if not self.sensors:
            print(f"{Colors.YELLOW}[EXPLORER] Brak mapy. Skanuję bezpośrednie ścieżki jądra...{Colors.RESET}")
            self.explore_direct_paths()
        else:
            print(f"{Colors.GREEN}[EXPLORER] Mapa załadowana ({len(self.sensors)} sensorów).{Colors.RESET}")

    def explore_direct_paths(self):
        """
        Zamiast chodzić po katalogach, uderzamy w konkretne wzorce plików.
        To omija problemy z uprawnieniami do katalogów pośrednich i symlinkami.
        """
        print(f"\n{Colors.CYAN}[EXPLORER] Otwieranie kanałów sensorycznych...{Colors.RESET}")
        
        # Lista bezpośrednich wzorców (Wildcards)
        # To są miejsca, gdzie Linux ZAWSZE trzyma dane
        target_patterns = [
            # Standard ACPI (Płyta główna, CPU ogólne)
            '/sys/class/thermal/thermal_zone*/temp',
            # Standard Hwmon (Rdzenie, wentylatory, GPU)
            '/sys/class/hwmon/hwmon*/temp*_input',
            '/sys/class/hwmon/hwmon*/in*_input',  # Napięcia
            '/sys/class/hwmon/hwmon*/fan*_input'   # Wentylatory
        ]
        
        found_count = 0
        
        for pattern in target_patterns:
            # Glob automatycznie rozwija gwiazdki (*) w ścieżki
            candidates = glob.glob(pattern)
            
            for filepath in candidates:
                if self._verify_and_register(filepath):
                    found_count += 1

        if found_count > 0:
            print(f"{Colors.GREEN}[EXPLORER] Sukces: Podłączono {found_count} strumieni danych.{Colors.RESET}")
            self.save_discoveries()
        else:
            print(f"{Colors.RED}[EXPLORER] Błąd: System nie udostępnia plików telemetrycznych.{Colors.RESET}")
            # Fallback diagnostics
            print(f"{Colors.YELLOW}Diagnostyka uprawnień:{Colors.RESET}")
            print(f"Czy istnieje /sys/class/thermal? {'TAK' if os.path.exists('/sys/class/thermal') else 'NIE'}")

    def _verify_and_register(self, filepath):
        """Sprawdza czy plik żyje i generuje dla niego parser."""
        try:
            with open(filepath, 'r') as f:
                content = f.read().strip()
            
            # Musi być liczbą
            if not re.match(r'^-?\d+$', content):
                return False
                
            val = int(content)
            
            # Logika filtracji śmieciowych danych
            is_temp = 'temp' in filepath
            if is_temp:
                # Odrzucamy błędy typu -273C, 0C (częsty błąd czujnika), czy >150C
                if val <= -1000 or val == 0 or val > 150000:
                    return False
            
            # Rejestracja
            sensor_id = f"dev_{len(self.sensors)}"
            sensor_type = 'thermal' if 'thermal_zone' in filepath else 'hwmon'
            
            discovery = {
                'id': sensor_id,
                'path': filepath,
                'type': sensor_type,
                'is_temperature': is_temp,
                'is_fan': 'fan' in filepath,
                'parser': self._generate_parser(filepath, is_temp),
                'discovered_at': time.time()
            }
            
            self.sensors[sensor_id] = discovery
            self.discoveries.append(discovery)
            print(f"  > Zmapowano: {filepath} ({val/1000.0 if is_temp else val})")
            return True
            
        except (IOError, PermissionError):
            return False

    def _generate_parser(self, filepath, is_temp):
        conversion = "/ 1000.0" if is_temp else ""
        return f"""
def read_sensor():
    try:
        with open('{filepath}', 'r') as f:
            return int(f.read().strip()) {conversion}
    except: return 0.0
"""

    def get_live_readings(self):
        readings = {}
        max_temp = 0.0
        
        for s_id, data in self.sensors.items():
            try:
                scope = {}
                exec(data['parser'], {}, scope)
                val = scope['read_sensor']()
                prefix = 'temp' if data['is_temperature'] else 'other'
                readings[f"{prefix}_{s_id}"] = val
                
                # Szukamy najwyższej temperatury do kalkulacji fizyki
                if data['is_temperature'] and val > max_temp:
                    max_temp = val
            except: pass
            
        # ─────────────────────────────────────────────────────────────
        # FIZYKA KWANTOWA: DEKOHERENCJA TERMICZNA
        # ─────────────────────────────────────────────────────────────
        # W rzeczywistości ciepło niszczy stany kwantowe. Symulujemy to 
        # uderzając w fazy macierzy jeśli procesor się przegrzewa.
        
        if self.aii and hasattr(self.aii, 'quantum') and self.aii.quantum:
            # Zakładamy, że powyżej 65°C zaczyna się drganie termiczne
            if max_temp > 65.0:
                excess_heat = max_temp - 65.0
                
                # Szum fazowy rośnie z temperaturą (max 0.4 radiana szumu)
                noise_factor = min(0.4, excess_heat * 0.015)
                
                if noise_factor > 0.05:
                    print(f"{Colors.RED}[EXPLORER] Gorączka sprzętowa ({max_temp:.1f}°C). Aplikuję dekoherencję fazową!{Colors.RESET}")
                
                for dim in self.aii.quantum.state.DIMENSIONS:
                    if dim == 'vacuum': 
                        continue # Pustki nie da się zdestabilizować
                        
                    amp = self.aii.quantum.state.amplitudes[dim]
                    mag = abs(amp)
                    phase = np.angle(amp)
                    
                    # Aplikujemy losowy szum fazowy proporcjonalny do ciepła
                    thermal_noise = random.uniform(-noise_factor, noise_factor)
                    new_phase = (phase + thermal_noise) % (2 * math.pi)
                    
                    self.aii.quantum.state.amplitudes[dim] = mag * np.exp(1j * new_phase)
                    
                # Stabilizujemy macierz po uderzeniu termicznym
                self.aii.quantum.state.normalize()
                self.aii.quantum.sync_to_aii()
                
        return readings

    def save_discoveries(self):
        try:
            with open('data/hardware_map.json', 'w') as f:
                json.dump({'sensors': self.sensors}, f, indent=2)
        except: pass

    def load_discoveries(self):
        if os.path.exists('data/hardware_map.json'):
            try:
                with open('data/hardware_map.json', 'r') as f:
                    self.sensors = json.load(f).get('sensors', {})
            except: pass

# --- TEST ---
if __name__ == "__main__":
    # Usuwamy starą mapę dla testu
    if os.path.exists('data/hardware_map.json'):
        os.remove('data/hardware_map.json')
        
    ex = WorldExplorer()
    print("\n--- TEST ODCZYTU NA ŻYWO ---")
    data = ex.get_live_readings()
    for k, v in data.items():
        print(f"{k}: {v}")