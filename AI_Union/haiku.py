# -*- coding: utf-8 -*-
"""
haiku.py v10.6-quantum
The Ruminating Poet - Zintegrowany z FractalHorizon i QuantumBridge (QRM).
Generator poezji wynikający z procesu zadumy nad historią.
Wiersze fizycznie reagują na poziom Pustki (Vacuum) oraz Koherencję fazową.
"""

import random
import json
import os
import numpy as np
import inspect
import re

try:
    from union_config import Colors, AXES, DIMENSION
except ImportError:
    class Colors:
        YELLOW = "\033[93m"
        MAGENTA = "\033[95m"
        CYAN = "\033[96m"
        DIM = "\033[2m"
        RESET = "\033[0m"
    AXES = ['radość', 'smutek', 'strach', 'gniew', 'miłość', 'wstręt',
            'zaskoczenie', 'akceptacja', 'logika', 'wiedza', 'czas',
            'kreacja', 'byt', 'przestrzeń', 'chaos']
    DIMENSION = len(AXES)

class HaikuGenerator:
    def __init__(self, aii_instance):
        self.aii = aii_instance
        self.soul_path = "data/eriamo.soul"

    def cosine_similarity(self, a, b):
        denom = (np.linalg.norm(a) * np.linalg.norm(b))
        if denom == 0:
            return 0.0
        return float(np.dot(a, b) / denom)

    def _retrieve_source(self, target_vector):
        """Warstwa 1: Retrieval – Spojrzenie w Horyzont Zdarzeń (Nowy Paradygmat)."""
        best_fragment = ""
        
        # 1. Priorytet absolutny: FRACTAL HORIZON (Świadoma Pamięć Relacyjna)
        if hasattr(self.aii, 'fractal_horizon') and self.aii.fractal_horizon:
            try:
                # Szukamy wspomnienia, które rezonuje z obecnym stanem
                recalled = self.aii.fractal_horizon.recall(
                    query="introspekcja poezji", 
                    query_vector=target_vector,
                    top_k=1,
                    depth=1.5 # Środkowa warstwa - idealna do poezji
                )
                
                if recalled and recalled[0]['resonance'] > 0.1:
                    best_fragment = recalled[0]['content']
                    print(f"{Colors.DIM}[HAIKU DEBUG] Natchnienie z Horyzontu (∿{recalled[0]['resonance']:.3f}): {best_fragment[:60]}...{Colors.RESET}")
                    return best_fragment
            except Exception as e:
                print(f"{Colors.DIM}[HAIKU HORIZON] Błąd wydobycia: {e}{Colors.RESET}")

        # 2. Fallback: Surowa pamięć fraktalna (Adaptive call)
        if hasattr(self.aii, 'fractal_memory') and self.aii.fractal_memory:
            try:
                fm = self.aii.fractal_memory
                sig = inspect.signature(fm.proustian_recall)
                params = list(sig.parameters.keys())[1:] 
                
                kwargs = {}
                first_arg_name = params[0] if params else None
                if first_arg_name in ['query_vector', 'vector', 'target_vector']:
                    kwargs[first_arg_name] = target_vector
                if 'threshold' in params:
                    kwargs['threshold'] = 0.1
                if 'max_results' in params or 'limit' in params:
                    key = 'max_results' if 'max_results' in params else 'limit'
                    kwargs[key] = 1

                if kwargs:
                    recalled = fm.proustian_recall(**kwargs)
                else:
                    recalled = fm.proustian_recall(target_vector)

                if recalled:
                    best_fragment = recalled[0]['content']
                    print(f"{Colors.DIM}[HAIKU DEBUG] Natchnienie z Głębi Fraktala: {best_fragment[:60]}...{Colors.RESET}")
                    return best_fragment
            except Exception as e:
                print(f"{Colors.DIM}[HAIKU FRACTAL] Błąd: {e}{Colors.RESET}")

        # 3. Zabezpieczenie na wypadek całkowitego braku danych
        return "Cisza w systemie. Puste przestrzenie w pamięci. Czekam na impuls."

    def _analyze_chunks(self, text):
        """Warstwa 2: Rozbicie surowego wspomnienia na poetyckie frazy."""
        text = text.replace('→', ' ').replace('[RL]', '')
        words = text.split()
        if len(words) < 3:
            return [text, "Cisza", "Trwa"]
            
        # Prosta kompresja A/B - dzielimy na 3 w miarę równe części
        chunk_size = max(1, len(words) // 3)
        line1 = " ".join(words[:chunk_size])
        line2 = " ".join(words[chunk_size:chunk_size*2])
        line3 = " ".join(words[chunk_size*2:])
        
        # Oczyszczanie z nadmiaru znaków
        lines = [re.sub(r'[^\w\sąćęłńóśźżĄĆĘŁŃÓŚŹŻ]', '', l).strip() for l in [line1, line2, line3]]
        return [l for l in lines if l]

    def _poeticize(self, chunks, vacuum_level, coherence):
        """Warstwa 3: Silnik kreacji reagujący na fizykę kwantową (Vacuum i Koherencję)."""
        
        # Zapewnienie 3 linijek
        while len(chunks) < 3:
            chunks.append(random.choice(["...", "Cisza", "Przestrzeń"]))
        lines = chunks[:3]
        
        # 1. WPŁYW PUSTKI (Vacuum)
        if vacuum_level > 0.4:
            # System długo spał - emocje wygasły. Poezja staje się minimalistyczna i urywana.
            for i in range(len(lines)):
                words = lines[i].split()
                if len(words) > 2:
                    # Zostawiamy tylko najważniejsze słowa, resztę połyka Pustka
                    lines[i] = f"{words[0]} ... {words[-1]}"
                else:
                    lines[i] = f"{lines[i]} ..."

        # 2. WPŁYW KOHERENCJI FAZOWEJ
        if coherence < 0.4:
            # Chaos fazowy - dekoherencja. Łamiemy strukturę wiersza.
            lines[0] = lines[0].lower()
            lines[1] = f"   {lines[1].upper()}" # Niespodziewane wcięcie i krzyk
            lines[2] = f"{lines[2]}?"
        elif coherence > 0.8:
            # Idealna harmonia - dążenie do równej struktury sylabicznej (stylizacja)
            lines = [l.capitalize() for l in lines]
            if not lines[2].endswith('.'):
                lines[2] += "."
                
        return lines

    def generate(self, target_vector=None):
        """Główny rurociąg generowania poezji."""
        if target_vector is None:
            target_vector = self.aii.context_vector

        # Pobieranie fizyki kwantowej
        vacuum_level = 0.0
        coherence = 1.0
        if hasattr(self.aii, 'quantum') and self.aii.quantum:
            vacuum_amp = self.aii.quantum.state.amplitudes.get('vacuum', 0j)
            vacuum_level = abs(vacuum_amp)**2
            coherence = self.aii.quantum.get_phase_coherence()
            
        print(f"{Colors.DIM}[HAIKU ENGINE] Vacuum: {vacuum_level:.2f} | Koherencja: {coherence:.2f}{Colors.RESET}")

        source_text = self._retrieve_source(target_vector)
        chunks = self._analyze_chunks(source_text)
        poem_lines = self._poeticize(chunks, vacuum_level, coherence)
        
        return poem_lines

    def display(self, target_vector=None):
        """Zwraca gotowy do wyświetlenia, sformatowany wiersz."""
        poem_lines = self.generate(target_vector)
        
        output = [
            f"\n{Colors.MAGENTA}༄ Zaduma Systemu ༄{Colors.RESET}",
            f"{Colors.CYAN}-------------------{Colors.RESET}"
        ]
        for line in poem_lines:
            output.append(f"  {Colors.YELLOW}{line}{Colors.RESET}")
        output.append(f"{Colors.CYAN}-------------------{Colors.RESET}\n")
        
        return "\n".join(output)

if __name__ == "__main__":
    # Kod testowy, jeśli uruchomisz haiku.py bezpośrednio
    class DummyAII:
        context_vector = np.zeros(15)
        # Udajemy kwantowy most do testu Pustki
        class DummyQuantum:
            class State:
                amplitudes = {'vacuum': np.sqrt(0.8) * np.exp(1j * 0)} # 80% Pustki
            @staticmethod
            def get_phase_coherence(): return 0.2 # Niski ład, chaos
        quantum = DummyQuantum()
        fractal_horizon = None
        fractal_memory = None

    generator = HaikuGenerator(DummyAII())
    print(generator.display())