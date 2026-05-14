# -*- coding: utf-8 -*-
"""
fractal.py v8.1.0-Quantum
Generator fraktali ASCII kompatybilny z architekturą wektorową (15 osi) 
oraz zintegrowany z QuantumBridge (fizyka Pustki i Koherencji Fazowej).
"""
import random
import math
import numpy as np
import time

try:
    from union_config import Colors
except ImportError:
    class Colors:
        CYAN = '\033[96m'; RED = '\033[91m'; GREEN = '\033[92m'; YELLOW = '\033[93m'
        BLUE = '\033[94m'; MAGENTA = '\033[95m'; WHITE = '\033[97m'; RESET = '\033[0m'
        FAINT = '\033[2m'  # Dodane dla faint/dim

class FractalGenerator:
    def __init__(self, aii_instance):
        self.aii = aii_instance
        self.width = 120  # Rozdzielczość
        self.height = 50  # Rozdzielczość
        
        # Mapa kolorów dla osi (Biologia + Metafizyka)
        self.COLOR_MAP = {
            'radość': Colors.YELLOW,
            'smutek': Colors.BLUE,
            'strach': Colors.MAGENTA,
            'gniew': Colors.RED,
            'miłość': Colors.MAGENTA, 
            'wstręt': Colors.GREEN,
            'zaskoczenie': Colors.CYAN,
            'akceptacja': Colors.WHITE,
            'logika': Colors.CYAN,
            'wiedza': Colors.BLUE,
            'czas': Colors.WHITE,
            'kreacja': Colors.YELLOW,
            'byt': Colors.GREEN,
            'przestrzeń': Colors.MAGENTA,
            'chaos': Colors.RED,
            'vacuum': Colors.FAINT # Kolor Pustki
        }

    def _get_dominant_emotion(self):
        """Pobiera dominującą emocję z wektora klasycznego."""
        if hasattr(self.aii, 'context_vector') and hasattr(self.aii, 'AXES_ORDER'):
            vec = self.aii.context_vector
            axes = self.aii.AXES_ORDER
            
            if len(vec) > 0 and np.max(vec) > 0:
                idx = np.argmax(vec)
                if idx < len(axes):
                    return axes[idx]
        
        if hasattr(self.aii, 'emocja'):
            return self.aii.emocja
            
        return "neutralna"

    def _get_quantum_physics(self):
        """Pobiera parametry z Mostu Kwantowego (Pustka i Koherencja)."""
        vacuum_level = 0.0
        coherence = 1.0
        
        if hasattr(self.aii, 'quantum') and self.aii.quantum:
            vacuum_amp = self.aii.quantum.state.amplitudes.get('vacuum', 0j)
            vacuum_level = abs(vacuum_amp)**2
            coherence = self.aii.quantum.get_phase_coherence()
            
        return vacuum_level, coherence

    def _apply_quantum_decay(self, buffer, vacuum_level, color):
        """Aplikuje zjawisko rozpadu do Pustki (Vacuum) na gotowy bufor fraktala."""
        if vacuum_level <= 0.1:
            return buffer # Pustka jest znikoma, fraktal nienaruszony
            
        decayed_buffer = []
        # Im większa pustka, tym więcej znaków "wyparowuje"
        erase_probability = min(0.9, vacuum_level * 1.5) 
        
        for line in buffer:
            # Rozbij linię na znaki (omijając kody ANSI, co w ASCII-arcie bywa trudne, 
            # więc upraszczamy: działamy na surowym ciągu przed dodaniem koloru dla bezpieczeństwa)
            pass 
            
        # Bezpieczniejsza metoda: Modyfikujemy ciąg PRZED nałożeniem ANSI w głównej pętli
        return buffer

    def generate(self, pattern_type=None):
        """Generuje klatkę fraktala w oparciu o stan systemu i fizykę kwantową."""
        emotion = self._get_dominant_emotion()
        vacuum_level, coherence = self._get_quantum_physics()
        
        # Jeśli Pustka dominuje całkowicie, kolor staje się szary/wyblakły
        if vacuum_level > 0.6:
            color = self.COLOR_MAP.get('vacuum')
            emotion_label = f"PUSTKA ({emotion} zanika)"
        else:
            color = self.COLOR_MAP.get(emotion, Colors.WHITE)
            emotion_label = emotion
            
        # Szum fazowy (niska koherencja) zniekształca fraktal
        phase_noise = 1.0 - coherence
        
        # Wybór algorytmu
        if pattern_type:
            algo = pattern_type
        elif emotion in ['logika', 'wiedza', 'akceptacja'] and vacuum_level < 0.5:
            algo = 'mandelbrot' # Porządek
        elif emotion in ['chaos', 'gniew', 'strach', 'zaskoczenie']:
            algo = 'julia'      # Chaos
        elif emotion in ['kreacja', 'miłość', 'radość']:
            algo = 'sierpinski' # Symetria
        else:
            algo = 'noise'      # Rozmycie / Pustka

        buffer = []
        chars = " .:-=+*#%@"
        
        # Parametry dynamiczne
        t = time.time()
        zoom = 1.0 + 0.5 * math.sin(t * 0.5)
        
        # Obliczanie prawdopodobieństwa wyparowania (Vacuum)
        erase_prob = min(0.95, vacuum_level * 1.2)
        
        if algo == 'mandelbrot':
            for y in range(self.height):
                row = ""
                for x in range(self.width):
                    if random.random() < erase_prob:
                        row += " " # Pustka pochłania piksel
                        continue
                        
                    cx = (x - self.width/2) / (self.width/3) / zoom - 0.5
                    cy = (y - self.height/2) / (self.height/2) / zoom
                    
                    # Aplikacja szumu fazowego do współrzędnych
                    if phase_noise > 0.3:
                        cx += random.uniform(-0.05, 0.05) * phase_noise
                        cy += random.uniform(-0.05, 0.05) * phase_noise
                        
                    c = complex(cx, cy)
                    z = 0
                    iter_val = 0
                    max_iter = 40 
                    while abs(z) < 2 and iter_val < max_iter:
                        z = z*z + c
                        iter_val += 1
                    row += chars[int(iter_val / max_iter * (len(chars)-1))]
                buffer.append(color + row + Colors.RESET)
                
        elif algo == 'julia':
            c = complex(-0.8, 0.156)
            for y in range(self.height):
                row = ""
                for x in range(self.width):
                    if random.random() < erase_prob:
                        row += " "
                        continue
                        
                    zx = 1.5 * (x - self.width / 2) / (0.5 * self.width)
                    zy = (y - self.height / 2) / (0.5 * self.height)
                    
                    if phase_noise > 0.3:
                        zx += random.uniform(-0.1, 0.1) * phase_noise
                        zy += random.uniform(-0.1, 0.1) * phase_noise
                        
                    z = complex(zx, zy)
                    iter_val = 0
                    max_iter = 40 
                    while abs(z) < 2 and iter_val < max_iter:
                        z = z*z + c
                        iter_val += 1
                    row += chars[int(iter_val / max_iter * (len(chars)-1))]
                buffer.append(color + row + Colors.RESET)
        
        elif algo == 'sierpinski':
            for y in range(self.height):
                row_raw = ' ' * (self.height - y - 1) * 2 
                for x in range(y + 1):
                    if bin(x & y).count('1') % 2 == 0:
                        # Jeśli wysoka Pustka lub niska Koherencja, niszczymy strukturę trójkąta
                        if random.random() < erase_prob or (phase_noise > 0.5 and random.random() < 0.2):
                            row_raw += '  '
                        else:
                            row_raw += '▲ ' 
                    else:
                        row_raw += '  '
                buffer.append(color + row_raw.rstrip() + Colors.RESET) 
        
        else:  # Noise (Idealne dla wysokiej Pustki)
            for y in range(self.height):
                row = ""
                for x in range(self.width):
                    if random.random() < erase_prob:
                        row += " "
                    elif (x & y): 
                        row += " "
                    else: 
                        # Szum fazowy zmienia gęstość znaku
                        char_idx = min(len(chars)-1, int(4 + random.uniform(-3, 3) * phase_noise))
                        row += chars[max(0, char_idx)]
                buffer.append(color + row + Colors.RESET)

        self.last_emotion_label = emotion_label
        self.last_vacuum = vacuum_level
        self.last_coherence = coherence
        return "\n".join(buffer)

    def display(self, pattern_type=None):
        """Metoda wywoływana przez Agency."""
        art = self.generate(pattern_type)
        print(f"\n{Colors.CYAN}[FRACTAL PROJECTION]{Colors.RESET}")
        print(art)
        
        # Wyświetlanie statystyk kwantowych pod fraktalem
        if hasattr(self, 'last_vacuum'):
            print(f"{Colors.FAINT}(Dominanta: {self.last_emotion_label} | "
                  f"Pustka: {self.last_vacuum:.0%} | "
                  f"Koherencja: {self.last_coherence:.2f}){Colors.RESET}\n")
        else:
            print(f"{Colors.FAINT}(Dominanta: {self._get_dominant_emotion()}){Colors.RESET}\n")

if __name__ == "__main__":
    # Test
    class MockAII:
        context_vector = np.array([0,0,0,1.0,0,0,0,0,0,0,0,0,0,0,0]) 
        AXES_ORDER = ['radość', 'smutek', 'strach', 'gniew', 'miłość', 'wstręt', 'zaskoczenie', 'akceptacja',
                      'logika', 'wiedza', 'czas', 'kreacja', 'byt', 'przestrzeń', 'chaos']
        
        class DummyQuantum:
            class State:
                amplitudes = {'vacuum': np.sqrt(0.7) * np.exp(1j * 0)} # 70% Pustki
            @staticmethod
            def get_phase_coherence(): return 0.3 # Niski ład, duży szum
        quantum = DummyQuantum()
    
    gen = FractalGenerator(MockAII())
    gen.display()