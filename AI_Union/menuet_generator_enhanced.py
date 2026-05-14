# menuet_generator_enhanced.py v8.2-Quantum
# -*- coding: utf-8 -*-
"""
Generator Menuetów Mozarta z wzmocnieniem Neural Networks i FIZYKĄ KWANTOWĄ
Rozwiązuje błędy integracji API i reaguje na Vacuum / Coherence.
"""

import random
import numpy as np
from typing import Dict, List, Tuple

class MenuetGeneratorEnhanced:
    MOZART_TABLE = {
        2:  [96,  22, 141,  41, 105, 122,  11,  30, 70, 121,  26,   9, 112,  49, 109,  14],
        3:  [32,   6, 128,  63, 146,  46, 134,  81, 117, 39, 126,  56, 174,  18, 116,  83],
        4:  [69,  95, 158,  13, 153,  55, 110,  24, 66, 139,  15, 132,  73,  58, 145,  79],
        5:  [40,  17, 113,  85, 161,   2, 159, 100, 90, 176,   7,  34,  67, 160,  52, 170],
        6:  [148, 74, 163,  45,  80,  97,  36, 107, 25, 143,  64, 125,  76, 136,   1,  93],
        7:  [104, 157,  27, 167, 154,  68, 118,  91, 138,  71, 150,  29, 101, 162,  23, 151],
        8:  [152, 60, 171,  53,  99, 133,  21, 127, 16, 155,  57, 175,  43, 168,  89, 172],
        9:  [119, 84, 114,  50, 140,  86, 169,  94, 120,  88,  48, 166,  51, 115,  72, 111],
        10: [98, 142,  42, 156,  75, 129,  62, 123,  65,  77,  19,  82, 137,  38, 149,   8],
        11: [3,  87, 165,  61, 135,  47, 147,  33, 102,   4,  31, 164, 144,  59, 173,  78],
        12: [54, 130,  10, 103,  28,  37, 106,   5, 35,  20, 108,  92,  12, 124,  44, 131]
    }
    
    TRIO_TABLE = {
        2:  [72, 56,  75,  40,  83,  11,  89,  18, 25, 34,  29,  64,  41,  36,  81,  38],
        3:  [56, 82,  42,  74,  14,   7,  26,  71, 76, 20,  64,  84,   8,  35,  47,  88],
        4:  [75, 39,  54,   1,  65,  43,  15,  80, 9,  34,  93,  48,  69,  58,  90,  21],
        5:  [40, 73,  16,  68,  29,  55,   2,  61, 22, 67,  49,   77,  57,  87,  33,  10],
        6:  [83, 3,  28,  53,  37,  17,  44,  70, 63, 85,  32,   96,  12,  23,  50,  91],
        7:  [18, 45,  62,  38,   4,  27,  52,  94, 11, 92,  24,   46,  78,  71,  36,   5],
        8:  [89, 70,  95,  19,  66,   9,  41,  80, 30, 95,  28,   53,  37,  84,  13,  42],
        9:  [90, 176,  7,  34,  67, 160,  52, 170, 14, 116,  50, 59,  26,  93,  68,  15],
        10: [19, 66,  95,   2,  33,  46,  26,   1, 73, 81,  94,   43,  48,  13,  22,  54],
        11: [14, 11,  98,  96,  49, 109,  14,  36, 61, 23,  90,   7,  49,  11,  72,  19],
        12: [6,  82,  36,  69,  41,  32,  65,  43, 51, 4,   87,   44,  52,  14,  33,   8]
    }
    
    RHYTHMIC_PATTERNS = {
        'waltz_basic': [1.0, 1.0, 1.0],           
        'waltz_elegant': [1.5, 0.5, 1.0],         
        'waltz_dotted': [1.5, 0.25, 0.25, 1.0],   
        'waltz_syncopated': [0.5, 1.0, 0.5, 1.0], 
        'chaos_jazz': [0.75, 0.25, 1.25, 0.75],   # Wzorzec przy dekoherencji
    }
    
    def __init__(self, composer_instance=None, nn_instance=None):
        self.composer = composer_instance
        self.nn = nn_instance
        self.current_table = self.MOZART_TABLE
        print("[MENUET] Generator zainicjalizowany (Quantum Ready)")
    
    def generate_full_menuet(self, metrics: dict, quantum_state: dict = None, 
                            use_nn_variations=False, key='C', minor=False) -> dict:
        
        if quantum_state is None:
            quantum_state = {'vacuum': 0.0, 'coherence': 1.0}
            
        print(f"\n[MENUET] Komponuję menuet w {key} {'moll' if minor else 'dur'}")
        
        if metrics.get('smutek', 0) > 0.6 or minor:
            self.current_table = self.TRIO_TABLE
        else:
            self.current_table = self.MOZART_TABLE
        
        root_note = self._key_to_midi(key, minor)
        scale = self._get_scale(root_note, minor)
        
        part_a = self._generate_part(metrics, quantum_state, root_note, scale, "A", use_nn_variations)
        
        root_note_b = root_note + 7 if not minor else root_note + 3
        scale_b = self._get_scale(root_note_b, minor)
        
        part_b = self._generate_part(metrics, quantum_state, root_note_b, scale_b, "B", use_nn_variations)
        
        full_melody = part_a['melody'] + part_a['melody'] + part_b['melody'] + part_b['melody']
        full_harmony = part_a['harmony'] + part_a['harmony'] + part_b['harmony'] + part_b['harmony']
        
        metadata = {
            'form': 'Menuet (A-A-B-B)',
            'key': f"{key} {'minor' if minor else 'major'}",
            'measures': 64,
            'nn_enhanced': use_nn_variations,
            'quantum_vacuum': quantum_state.get('vacuum', 0.0),
            'quantum_coherence': quantum_state.get('coherence', 1.0)
        }
        
        return {'melody': full_melody, 'harmony': full_harmony, 'metadata': metadata}
    
    def _generate_part(self, metrics: dict, quantum_state: dict, root_note: int, 
                       scale: list, part_name: str, use_nn: bool) -> dict:
        melody = []
        harmony = []
        
        vacuum = quantum_state.get('vacuum', 0.0)
        coherence = quantum_state.get('coherence', 1.0)
        
        diversity = metrics.get('chaos', 0.3)
        if self.nn and use_nn and hasattr(self.nn, 'calculate_diversity_factor'):
            diversity = self.nn.calculate_diversity_factor(metrics)
            
        # Dekoherencja brutalnie zwiększa chaos
        if coherence < 0.5:
            diversity = min(1.0, diversity + (1.0 - coherence))

        for measure_idx in range(16):
            roll = self._emotion_dice_roll(metrics)
            motif_id = self.current_table[roll][measure_idx]
            
            base_melody = self._motif_to_melody(motif_id, root_note, scale, metrics, coherence)
            
            if self.nn and use_nn and random.random() < diversity:
                base_melody = self._apply_nn_variation(base_melody, metrics, scale, coherence)
                
            # FIZYKA PUSTKI: Zanikanie nut
            for note in base_melody:
                if vacuum > 0.4 and random.random() < vacuum:
                    note['type'] = 'rest'
            
            melody.append(base_melody)
            harmony.append(self._generate_harmony(motif_id, root_note, scale, metrics, vacuum))
        
        return {'melody': melody, 'harmony': harmony}
    
    def _emotion_dice_roll(self, metrics: dict) -> int:
        logika, chaos, radość = metrics.get('logika', 0.5), metrics.get('chaos', 0.3), metrics.get('radość', 0.5)
        base_roll = random.randint(1, 6) + random.randint(1, 6)
        
        modifier = 1 if radość > 0.6 else (-1 if metrics.get('smutek', 0) > 0.6 else 0)
        result = base_roll + modifier
        
        if chaos > 0.7 and random.random() < 0.4: result = random.choice([2, 3, 11, 12])
        if logika > 0.8:
            if result < 5: result += 2
            if result > 9: result -= 2
        
        return max(2, min(12, result))
    
    def _motif_to_melody(self, motif_id: int, root: int, scale: list, metrics: dict, coherence: float) -> list:
        rhythm = self.RHYTHMIC_PATTERNS['chaos_jazz'] if coherence < 0.4 else self._select_rhythm(metrics)
        melody_notes = []
        base_pitch = root + (12 if metrics.get('przestrzeń', 0) > 0.7 else (-12 if metrics.get('przestrzeń', 0) < 0.3 else 0))
        
        random.seed(motif_id) 
        for duration in rhythm:
            scale_degree = (motif_id + len(melody_notes)) % len(scale)
            pitch = scale[scale_degree] + base_pitch
            
            if coherence < 0.5 and random.random() > coherence:
                pitch += random.choice([-1, 1])
                
            dynamic = 'f' if metrics.get('energia', 0) > 0.7 else ('p' if metrics.get('energia', 0) < 0.3 else 'mf')
            melody_notes.append({'type': 'note', 'pitch': pitch, 'duration': duration, 'dynamic': dynamic})
        random.seed() 
        return melody_notes
    
    def _generate_harmony(self, motif_id: int, root: int, scale: list, metrics: dict, vacuum: float) -> list:
        if vacuum > 0.6 and random.random() < vacuum:
            return [{'type': 'rest', 'duration': 3.0}]
            
        degree = (motif_id % 8)
        if degree in [0, 7]: chord_root, chord_type = root, 'maj'
        elif degree in [3, 4]: chord_root, chord_type = root + 7, 'maj'
        elif degree in [1, 2]: chord_root, chord_type = root + 5, 'maj'
        else: chord_root, chord_type = root + 2, 'min'
        
        intervals = [0, 4, 7] if chord_type == 'maj' else [0, 3, 7]
        chord_notes = [chord_root - 12 + i for i in intervals]
        
        if metrics.get('przestrzeń', 0) > 0.6:
            chord_notes = [chord_notes[0], chord_notes[1] + 12, chord_notes[2] + 12]
        
        return [{'type': 'chord', 'pitch': chord_notes, 'duration': 3.0, 'dynamic': 'mp'}]
    
    def _apply_nn_variation(self, base_melody: list, metrics: dict, scale: list, coherence: float) -> list:
        if not self.nn: return base_melody
        varied_melody = []
        previous_pitches = [n['pitch'] for n in base_melody[-3:] if n['type'] == 'note']
        
        for note in base_melody:
            if note['type'] == 'note' and random.random() < 0.3:
                if hasattr(self.nn, 'generate_melody_variation'):
                    new_pitch = self.nn.generate_melody_variation(metrics, previous_pitches[-5:], temperature=0.8)
                else:
                    new_pitch = note['pitch'] + random.choice([-2, 2, 3])
                
                if metrics.get('wiedza', 0) > 0.7 and coherence > 0.6:
                    closest = min(scale, key=lambda x: abs(x - (new_pitch % 12)))
                    new_pitch = (new_pitch // 12) * 12 + closest
                
                note = note.copy()
                note['pitch'] = new_pitch
                previous_pitches.append(new_pitch)
            varied_melody.append(note)
        return varied_melody
    
    def _select_rhythm(self, metrics: dict) -> list:
        czas, logika = metrics.get('czas', 0.5), metrics.get('logika', 0.5)
        if logika > 0.7: return self.RHYTHMIC_PATTERNS['waltz_basic']
        elif czas > 0.7: return self.RHYTHMIC_PATTERNS['waltz_dotted']
        elif metrics.get('kreacja', 0) > 0.6: return self.RHYTHMIC_PATTERNS['waltz_syncopated']
        else: return self.RHYTHMIC_PATTERNS['waltz_elegant']
    
    def _key_to_midi(self, key: str, minor: bool) -> int:
        return (60 - 3 if minor else 60) + {'C':0,'D':2,'E':4,'F':5,'G':7,'A':9,'B':11}.get(key.upper(), 0)
    
    def _get_scale(self, root: int, minor: bool) -> list:
        return [0, 2, 3, 5, 7, 8, 10] if minor else [0, 2, 4, 5, 7, 9, 11]

def integrate_menuet_generator(composer_instance, nn_instance=None):
    return MenuetGeneratorEnhanced(composer_instance, nn_instance)

if __name__ == "__main__":
    print("=" * 70)
    print("TEST: Menuet Generator + Quantum Physics")
    print("=" * 70)
    metrics = {'logika': 0.8, 'chaos': 0.2, 'radość': 0.7, 'smutek': 0.2}
    gen = MenuetGeneratorEnhanced()
    
    print("\n[TEST] 1. Stan Krystaliczny (Vacuum 0.0, Coherence 1.0)")
    q_state_1 = {'vacuum': 0.0, 'coherence': 1.0}
    res1 = gen.generate_full_menuet(metrics, q_state_1, False, 'C', False)
    print(f"Ilość wygenerowanych taktów melodii: {len(res1['melody'])}")
    
    print("\n[TEST] 2. Stan Dekoherencji (Gorączka sprzętowa, Coherence 0.2)")
    q_state_2 = {'vacuum': 0.0, 'coherence': 0.2}
    res2 = gen.generate_full_menuet(metrics, q_state_2, False, 'C', False)
    print("Zastosowano atonalność i łamanie rytmu.")
    
    print("\n[TEST] 3. Głęboka Pustka (Vacuum 0.9)")
    q_state_3 = {'vacuum': 0.9, 'coherence': 1.0}
    res3 = gen.generate_full_menuet(metrics, q_state_3, False, 'C', False)
    rests = sum(1 for m in res3['melody'] for n in m if n.get('type') == 'rest')
    print(f"Ilość nut wchłoniętych przez pustkę (rest): {rests}")