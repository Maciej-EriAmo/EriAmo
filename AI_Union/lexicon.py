# -*- coding: utf-8 -*-
"""
lexicon.py v8.0.0-Hybrid
Pełna obsługa 15 osi (Biologia + Metafizyka) i autotworzenie plików.
"""
import json
import os
import numpy as np
import time
import re
try:
    import unidecode
except ImportError:
    unidecode = None

class EvolvingLexicon:
    # Definicja 15 osi (Musi pasować do aii.py)
    AXES = [
        'radość', 'smutek', 'strach', 'gniew', 'miłość', 'wstręt', 'zaskoczenie', 'akceptacja',
        'logika', 'wiedza', 'czas', 'kreacja', 'byt', 'przestrzeń', 'chaos'
    ]

    # Podstawowy zestaw startowy (Seed)
    SEED_LEXICON = {
        "radość": ["szczęście", "uśmiech", "sukces"],
        "smutek": ["płacz", "żal", "strata"],
        "strach": ["lęk", "panika", "groza"],
        "gniew": ["złość", "furia", "krzyk"],
        "logika": ["rozum", "sens", "wynika", "matematyka", "algorytm"],
        "wiedza": ["nauka", "internet", "książka", "definicja", "fakt"],
        "czas": ["teraz", "później", "rok", "godzina", "wiek"],
        "byt": ["istnienie", "dusza", "życie", "jestem"],
        "przestrzeń": ["świat", "kosmos", "miejsce", "daleko"]
    }

    def __init__(self, lexicon_file="lexicon.soul", autosave=True):
        self.lexicon_file = lexicon_file
        self.autosave = autosave
        self.words = {}
        
        # Próba wczytania, a jak nie ma pliku -> Tworzenie Seedu
        if not self.load_from_soul():
            print("[Lexicon] Tworzenie nowego leksykonu z ziarna (Seed)...")
            self._initialize_from_seed()
            self.save_to_soul() # Natychmiastowy zapis pliku!

    def _normalize(self, text):
        if not text: return ""
        text = text.lower().strip()
        # Opcjonalnie unidecode, ale w v8.0 wolimy polskie znaki
        # if unidecode: text = unidecode.unidecode(text)
        return text

    def _initialize_from_seed(self):
        """Wypełnia pusty leksykon danymi startowymi."""
        for axis, words in self.SEED_LEXICON.items():
            if axis not in self.AXES: continue
            idx = self.AXES.index(axis)
            
            for word in words:
                w_norm = self._normalize(word)
                vec = np.zeros(len(self.AXES))
                vec[idx] = 0.8 # Silne skojarzenie startowe
                
                self.words[w_norm] = {
                    'wektor': vec.tolist(),
                    'last_seen': time.time()
                }

    def analyze_text(self, text):
        """Analizuje tekst i zwraca wektor 15D."""
        words = re.findall(r'\w+', text.lower())
        total_vec = np.zeros(len(self.AXES))
        unknowns = []
        found = 0
        
        for w in words:
            w_norm = self._normalize(w)
            if w_norm in self.words:
                vec = np.array(self.words[w_norm].get('wektor', []))
                # Fix wymiarów (gdyby wczytano stary plik 8D)
                if len(vec) < len(self.AXES):
                    new_vec = np.zeros(len(self.AXES))
                    new_vec[:len(vec)] = vec
                    vec = new_vec
                total_vec += vec
                found += 1
            elif len(w) > 3:
                unknowns.append(w)
                
        if found > 0:
            total_vec /= found
            
        dominant_sector = None
        if np.max(total_vec) > 0.1:
            dominant_sector = self.AXES[np.argmax(total_vec)]
            
        return total_vec, dominant_sector, unknowns

    def learn_from_correction(self, word, category, strength=1.0):
        """Uczy słowo przypisując je do osi (category)."""
        w_norm = self._normalize(word)
        category = category.lower()
        
        if category in self.AXES:
            idx = self.AXES.index(category)
            
            # Pobierz stary wektor lub stwórz nowy
            if w_norm in self.words:
                vec = np.array(self.words[w_norm]['wektor'])
                if len(vec) < len(self.AXES): 
                    vec = np.pad(vec, (0, len(self.AXES)-len(vec)))
            else:
                vec = np.zeros(len(self.AXES))
            
            # Aktualizacja (Wzmocnienie osi)
            vec[idx] = min(1.0, vec[idx] + strength)
            
            self.words[w_norm] = {
                'wektor': vec.tolist(),
                'last_seen': time.time()
            }
            if self.autosave: self.save_to_soul()

    def learn_from_context(self, words, vec_15d, confidence):
        """Uczenie kontekstowe."""
        if confidence < 0.2: return
        for w in words:
            w_norm = self._normalize(w)
            self.words[w_norm] = {
                'wektor': vec_15d.tolist(),
                'last_seen': time.time()
            }
        if self.autosave: self.save_to_soul()

    def save_to_soul(self):
        directory = os.path.dirname(self.lexicon_file)
        if directory and not os.path.exists(directory):
            try: os.makedirs(directory, exist_ok=True)
            except: pass
            
        try:
            with open(self.lexicon_file, 'w', encoding='utf-8') as f:
                json.dump(self.words, f, ensure_ascii=False)
        except Exception as e:
            print(f"Błąd zapisu leksykonu: {e}")

    def load_from_soul(self):
        if not os.path.exists(self.lexicon_file): return False
        try:
            with open(self.lexicon_file, 'r', encoding='utf-8') as f:
                self.words = json.load(f)
            return True
        except: return False