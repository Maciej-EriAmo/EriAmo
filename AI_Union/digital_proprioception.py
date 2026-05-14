"""
EriAmo Union v8.6.1 - Digital Proprioception (Explorer Wrapper)
Autor: Maciej Mazur
Data: 2026-01-25

Moduł ten pełni rolę warstwy abstrakcji nad autonomicznym `explorer.py`.
Pobiera surowe dane z dynamicznie odkrytych sensorów i agreguje je
do ustandaryzowanego formatu zrozumiałego dla Rdzenia Świadomości.
"""

import os
import psutil
from explorer import WorldExplorer  # Importujemy Twój moduł

class DigitalProprioception:
    def __init__(self):
        # Inicjalizacja autonomicznego badacza
        # Przekazujemy None jako aii_instance, bo na tym etapie
        # rdzeń może jeszcze nie istnieć (będzie wstrzyknięty później jeśli trzeba)
        self.explorer = WorldExplorer(aii_instance=None)
        
        # Szybka diagnostyka
        self.sensor_count = len(self.explorer.sensors)
        self.source_metadata = f"Autonomous Explorer ({self.sensor_count} sensors)"

    def get_status(self):
        """
        Zwraca zintegrowany stan świadomości fizycznej.
        """
        # 1. Pobranie surowych danych z wygenerowanych parserów
        raw_senses = self.explorer.get_live_readings()
        
        # 2. Interpretacja temperatury (Heurystyka)
        # System szuka najwyższego odczytu spośród wszystkich sensorów temperatury,
        # zakładając, że 'Hot Spot' to rdzeń obliczeniowy pod obciążeniem.
        temps = [val for key, val in raw_senses.items() if 'temp' in key]
        
        if temps:
            # Odrzucamy błędy pomiarowe (np. -273 lub >150)
            valid_temps = [t for t in temps if -50 < t < 150]
            current_temp = max(valid_temps) if valid_temps else 0.0
        else:
            current_temp = 0.0

        # 3. Odczyt obciążenia CPU (System operacyjny wie najlepiej)
        if os.name == 'posix':
            load1, _, _ = os.getloadavg()
            cpu_stress = (load1 / os.cpu_count()) * 100
            cpu_stress = min(cpu_stress, 100.0)
        else:
            cpu_stress = psutil.cpu_percent(interval=0.1)

        # 4. Pamięć
        mem = psutil.virtual_memory()

        return {
            "cpu_stress": round(cpu_stress, 1),
            "ram_pressure": round(mem.percent, 1),
            "temperature": round(current_temp, 1),
            "sensor_id": self.source_metadata,
            "raw_dump": raw_senses  # Dla celów debugowania
        }

# --- Test integracji ---
if __name__ == "__main__":
    print("--- INTEGRACJA UKŁADU NERWOWEGO ---")
    body = DigitalProprioception()
    status = body.get_status()
    
    print(f"\n[STAN ERIAMO]")
    print(f"Obciążenie: {status['cpu_stress']}%")
    print(f"Temperatura: {status['temperature']}°C")
    print(f"Źródło:      {status['sensor_id']}")
    
    print("\n[SUROWE DANE Z NERWÓW]")
    for k, v in status['raw_dump'].items():
        print(f"  > {k}: {v}")