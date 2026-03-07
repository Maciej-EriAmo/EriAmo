# soul_composer.py v8.3.0 - Quantum Hybrid (15 Axes + Physics)
# -*- coding: utf-8 -*-
"""
Kompozytor Duszowy EriAmo v8.2.0 [QUANTUM HYBRID]
Pełna integracja z architekturą 15-osiową oraz fizyką kwantową (QRM).

Zmiany v8.3.0:
- DODANO: compose_menuet() — pełny pipeline z zapisem MIDI
  (music21 primary, midiutil fallback, txt zawsze)
- DODANO: _evaluate_menuet() — ewaluacja RL
- DODANO: _save_with_midiutil() — fallback MIDI bez music21

Zmiany v8.2.0 względem v8.1:
- Wprowadzono odczyt Pustki (Vacuum) i Dekoherencji Fazowej.
- Pustka -> Rozciąga czas i zamienia nuty na pauzy (Rests).
- Dekoherencja -> Rozbija skale, łamie rytm (Atonalność).
- FIX: Obsługa music21.note.Rest() dla wygenerowanej Pustki.
"""
import random
import datetime
import os
import numpy as np

# Importy systemowe
try:
    from union_config import UnionConfig
    from genre_definitions import GENRE_DEFINITIONS
except ImportError:
    print("[COMPOSER] Błąd krytyczny: Brak konfiguracji!")
    UnionConfig = None

# Obsługa Music21
try:
    import music21
    MUSIC21_AVAIL = True
except ImportError:
    MUSIC21_AVAIL = False
    print("[COMPOSER] Music21 niedostępne - tylko eksport tekstowy")

# Obsługa Audio
try:
    from midi2audio import FluidSynth
    from pydub import AudioSegment
    AUDIO_AVAIL = True
except ImportError:
    AUDIO_AVAIL = False

# Fallback MIDI bez music21
try:
    from midiutil import MIDIFile
    MIDIUTIL_AVAIL = True
except ImportError:
    MIDIUTIL_AVAIL = False


class SoulComposerV8:
    OUTPUT_DIR = "compositions"
    SOUNDFONT_PATH = "/usr/share/sounds/sf2/FluidR3_GM.sf2"

    CHORD_MAP = {
        'maj': [0, 4, 7], 'min': [0, 3, 7], '7': [0, 4, 7, 10],
        'dim': [0, 3, 6], 'power': [0, 7, 12], 'sus4': [0, 5, 7],
        'maj7': [0, 4, 7, 11], 'min7': [0, 3, 7, 10]
    }

    INSTRUMENT_MAP = {
        'piano': 0, 'bright_piano': 1, 'organ': 19, 'guitar': 29,
        'distortion': 30, 'bass': 33, 'strings': 48, 'slow_strings': 49,
        'choir': 52, 'voice': 53, 'trumpet': 56, 'brass': 61, 'sax': 65,
        'oboe': 68, 'flute': 73, 'pad': 89, 'scifi': 96, 'sitar': 104
    }
    
    MENUET_MASTERS = {
        'MOZART_DICE': {'name': 'Mozart Würfelspiel', 'style': 'galant'},
        'BACH': {'name': 'Johann Sebastian Bach', 'style': 'polyphonic'},
        'MOZART': {'name': 'Wolfgang Amadeus Mozart', 'style': 'classical'},
        'HANDEL': {'name': 'Georg Friedrich Händel', 'style': 'royal'},
        'HAYDN': {'name': 'Joseph Haydn', 'style': 'witty'},
        'RIEPEL': {'name': 'Joseph Riepel', 'style': 'textbook'}
    }

    def __init__(self, aii_instance, logger=None):
        self.aii = aii_instance
        self.logger = logger
        self._slur_start = None
        os.makedirs(self.OUTPUT_DIR, exist_ok=True)
        
        if UnionConfig:
            self.AXES_MAP = {axis: i for i, axis in enumerate(UnionConfig.AXES)}
        else:
            self.AXES_MAP = {}

    # --- 1. INTELIGENTNE POBIERANIE STANU DUSZY ---

    def _get_soul_metrics(self) -> dict:
        if not self.aii:
            return {ax: 0.1 for ax in UnionConfig.AXES} if UnionConfig else {}
            
        emotions = self.aii.get_emotions() if hasattr(self.aii, 'get_emotions') else {}
        metrics = emotions.copy()
        metrics['improwizacja'] = (metrics.get('kreacja', 0) * 0.7 + metrics.get('chaos', 0) * 0.3) * 100
        return metrics

    def _get_quantum_state(self) -> dict:
        """Pobiera twardą fizykę (Pustka i Koherencja)."""
        quantum_state = {'vacuum': 0.0, 'coherence': 1.0}
        if hasattr(self.aii, 'quantum') and self.aii.quantum:
            vacuum_amp = self.aii.quantum.state.amplitudes.get('vacuum', 0j)
            quantum_state['vacuum'] = abs(vacuum_amp)**2
            quantum_state['coherence'] = self.aii.quantum.get_phase_coherence()
        return quantum_state

    # --- 2. LOGIKA RYTMU (OPARTA NA CZASIE, LOGICE I FIZYCE KWANTOWEJ) ---

    def _get_rhythm_duration(self, metrics: dict, quantum_state: dict, base_tempo_mod: float = 0.0) -> float:
        vacuum = quantum_state.get('vacuum', 0.0)
        coherence = quantum_state.get('coherence', 1.0)
        
        # WPŁYW FIZYKI KWANTOWEJ NA CZAS
        if vacuum > 0.6:
            # Pustka zamraża czas - gigantyczne, rozwlekłe nuty
            return random.choice([2.0, 4.0, 8.0])
            
        if coherence < 0.4:
            # Dekoherencja (np. termiczna) łamie rytm, wprowadza polirytmię
            return random.choice([0.25, 0.75, 1.25, 0.33, 1.5])
            
        # Klasyczna logika wektorowa
        time_val = metrics.get('czas', 0.5) * 10.0 + base_tempo_mod 
        
        opts_fast = [0.25, 0.5, 0.5, 1.0]
        opts_med = [0.5, 1.0, 1.0, 2.0]
        opts_slow = [1.0, 2.0, 4.0]
        
        if time_val > 7.0: pool = opts_fast
        elif time_val < 2.0: pool = opts_slow
        else: pool = opts_med
            
        duration = random.choice(pool)
        
        if metrics.get('chaos', 0) > 0.6 and random.random() < 0.3:
            duration *= 1.5 
            
        return duration

    # --- 3. GENEROWANIE NUT (HARMONIA) ---

    def _build_chord_notes(self, root: int, chord_type: str) -> list:
        intervals = self.CHORD_MAP.get(chord_type, [0, 4, 7])
        return [root + i for i in intervals]

    def _apply_intention_vector(self, genre_name: str) -> np.ndarray:
        if genre_name not in GENRE_DEFINITIONS:
            return np.zeros(UnionConfig.DIMENSION if UnionConfig else 15)
            
        f_def = GENRE_DEFINITIONS[genre_name]["f_intencja_wektor"]
        F_int = np.zeros(UnionConfig.DIMENSION if UnionConfig else 15)
        
        for axis, val in f_def.items():
            if axis in self.AXES_MAP:
                norm_val = val * 0.1 
                F_int[self.AXES_MAP[axis]] = norm_val
                
        if hasattr(self.aii, 'context_vector'):
            self.aii.context_vector += F_int
            if np.max(self.aii.context_vector) > 1.0:
                 self.aii.context_vector /= np.max(self.aii.context_vector)
                 
        return F_int

    def _render_audio(self, midi_path: str) -> dict:
        if not AUDIO_AVAIL or not os.path.exists(self.SOUNDFONT_PATH): return {}
        base_path = os.path.splitext(midi_path)[0]
        wav_path = f"{base_path}.wav"
        ogg_path = f"{base_path}.ogg"
        paths = {}
        try:
            fs = FluidSynth(self.SOUNDFONT_PATH)
            fs.midi_to_audio(midi_path, wav_path)
            if os.path.exists(wav_path):
                audio = AudioSegment.from_wav(wav_path)
                audio.export(ogg_path, format="ogg")
                paths['ogg'] = ogg_path
                os.remove(wav_path)
        except Exception as e:
            print(f"[AUDIO ERROR] {e}")
        return paths

    # ============= GENERATORY NATYWNE (15 OSI + QUANTUM) =============

    def _emotion_dice_roll(self, metrics: dict) -> int:
        logika = metrics.get('logika', 0)
        chaos = metrics.get('chaos', 0)
        radość = metrics.get('radość', 0)
        
        base_roll = random.randint(1, 6) + random.randint(1, 6)
        
        modifier = 0
        if radość > 0.6: modifier += 1
        if metrics.get('smutek', 0) > 0.6: modifier -= 1
        
        result = base_roll + modifier
        
        if chaos > 0.7 and random.random() < 0.4:
            result = random.choice([2, 3, 11, 12])
            
        if logika > 0.8:
            if result < 5: result += 2
            if result > 9: result -= 2
            
        return max(2, min(12, result))

    def _generate_polyphonic_generic(self, genre_name: str, quantum_state: dict) -> dict:
        """Kwantowo-wrażliwy generator dowolnych struktur muzycznych."""
        metrics = self._get_soul_metrics()
        vacuum = quantum_state.get('vacuum', 0.0)
        coherence = quantum_state.get('coherence', 1.0)
        
        is_minor = metrics.get('smutek', 0) > metrics.get('radość', 0)
        base_root = 57 if is_minor else 60 
        
        if is_minor:
            progression = [(base_root, 'min'), (base_root-4, 'maj'), (base_root+3, 'maj'), (base_root-2, 'maj')]
        else:
            progression = [(base_root, 'maj'), (base_root+7, 'maj'), (base_root+9, 'min'), (base_root+5, 'maj')]
            
        melody, harmony = [], []
        
        scale = [base_root, base_root+2, base_root+4, base_root+5, base_root+7, base_root+9, base_root+11, base_root+12]
        if is_minor: 
             scale = [base_root, base_root+2, base_root+3, base_root+5, base_root+7, base_root+8, base_root+10, base_root+12]

        for root, ctype in progression * 2: 
            # 1. HARMONIA (Zależna od Pustki)
            spacing = 0 if metrics.get('przestrzeń', 0) < 0.5 else 12
            cn = self._build_chord_notes(root, ctype)
            chord_notes = [cn[0]-12, cn[1], cn[2]+spacing]
            
            # Pustka zżera akordy bazy
            if vacuum > 0.5 and random.random() < vacuum:
                harmony.append([{'type': 'rest', 'duration': 4.0}])
            else:
                harmony.append([{'type': 'chord', 'pitch': chord_notes, 'duration': 4.0, 'dynamic': 'mf'}])
            
            # 2. MELODIA (Zależna od Dekoherencji i Pustki)
            rh_measure = []
            beat = 0.0
            while beat < 4.0:
                dur = self._get_rhythm_duration(metrics, quantum_state)
                if beat + dur > 4.0: dur = 4.0 - beat
                
                # Niska koherencja = trytony i wypadanie ze skali (atonalność)
                if coherence < 0.5 and random.random() > coherence:
                    note = random.choice(scale) + random.choice([-1, 1, 6]) 
                elif metrics.get('chaos', 0) > 0.7 and random.random() < 0.2:
                    note = random.randint(base_root, base_root+12) 
                else:
                    note = random.choice(scale)
                
                if metrics.get('przestrzeń', 0) > 0.7:
                    note += 12
                    
                # Pustka połyka dźwięk (Rest)
                if vacuum > 0.4 and random.random() < vacuum:
                    rh_measure.append({'type': 'rest', 'duration': dur})
                else:
                    rh_measure.append({'type': 'note', 'pitch': note, 'duration': dur, 'dynamic': 'mf'})
                    
                beat += dur
            melody.append(rh_measure)
            
        return {'melody': melody, 'harmony': harmony}

    # ============= MUSIC21 SCORE =============

    def _create_music21_score(self, data: dict, genre_name: str, instrument_override: str = None, quantum_state: dict = None):
        if not MUSIC21_AVAIL: return None
        score = music21.stream.Score()
        
        # Metadane
        md = music21.metadata.Metadata()
        logika_val = self.aii.context_vector[8] if hasattr(self.aii, 'context_vector') else 0.5
        md.title = f"{genre_name} [Logic:{logika_val:.1f}]"
        md.composer = "EriAmo v8.2 Quantum"
        score.insert(0, md)
        
        # Instrument
        midi_prog = 0
        if instrument_override:
            midi_prog = self.INSTRUMENT_MAP.get(instrument_override.lower(), 0)
        elif genre_name == "MENUET": midi_prog = 6 
        elif genre_name == "ROCK_AND_ROLL": midi_prog = 29 
        elif genre_name == "AMBIENT": midi_prog = 96 
        
        # Tempo + Pustka = bardzo wolno
        metrics = self._get_soul_metrics()
        base_bpm = 120
        if quantum_state and quantum_state.get('vacuum', 0) > 0.5:
            base_bpm = 40 # Totalne zwolnienie w Pustce
        elif metrics.get('czas', 0) > 0.7: base_bpm = 160
        elif metrics.get('czas', 0) < 0.3: base_bpm = 70
        
        # PART 1: RH
        p1 = music21.stream.Part()
        p1.insert(0, music21.tempo.MetronomeMark(number=base_bpm))
        inst = music21.instrument.Instrument()
        inst.midiProgram = midi_prog
        p1.insert(0, inst)
        
        # ZABEZPIECZENIE: FIX dla pauz (Rests)
        for m_data in data['melody']:
            m = music21.stream.Measure()
            for ev in m_data:
                if ev.get('type') == 'rest':
                    n = music21.note.Rest()
                else:
                    n = music21.note.Note(ev['pitch'])
                n.quarterLength = ev['duration']
                m.append(n)
            p1.append(m)
            
        # PART 2: LH
        p2 = music21.stream.Part()
        inst2 = music21.instrument.Instrument()
        inst2.midiProgram = midi_prog if genre_name != "ROCK_AND_ROLL" else 33 
        p2.insert(0, inst2)
        
        for m_data in data['harmony']:
            m = music21.stream.Measure()
            for ev in m_data:
                if ev.get('type') == 'rest':
                    c = music21.note.Rest()
                    c.quarterLength = ev['duration']
                    m.append(c)
                elif ev.get('type') == 'chord':
                    c = music21.chord.Chord(ev['pitch'])
                    c.quarterLength = ev['duration']
                    m.append(c)
            p2.append(m)
            
        score.insert(0, p1)
        score.insert(0, p2)
        return score

    # ============= GŁÓWNA METODA KOMPOZYCJI =============

    def compose_new_work(self, genre_name: str, instrument_override: str = None, tonic: str = None) -> dict:
        
        self._apply_intention_vector(genre_name)
        quantum_state = self._get_quantum_state()
        
        # System sam rozpozna że to menuet i przekaże kontrolę do zewnętrznego skryptu
        # Zwykłe gatunki idą przez generację natywną
        data = self._generate_polyphonic_generic(genre_name, quantum_state)
            
        score = self._create_music21_score(data, genre_name, instrument_override, quantum_state)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        base = f"{self.OUTPUT_DIR}/{genre_name}_{timestamp}"
        paths = {'txt': f"{base}.txt"}
        
        if score:
            paths['midi'] = f"{base}.mid"
            score.write('midi', fp=paths['midi'])
            if AUDIO_AVAIL:
                audio = self._render_audio(paths['midi'])
                paths.update(audio)
                
        with open(paths['txt'], "w", encoding="utf-8") as f:
            f.write(f"Gatunek: {genre_name}\n")
            f.write(f"Quantum State: Vacuum {quantum_state['vacuum']:.2f}, Coherence {quantum_state['coherence']:.2f}\n")
            f.write(f"Stan Umysłu (15 osi):\n")
            metrics = self._get_soul_metrics()
            for k, v in metrics.items():
                f.write(f"  {k}: {v:.2f}\n")
                
        return paths


    # ============= MENUET — ZAPIS DO MIDI =============

    def compose_menuet(self, key: str = 'C', minor: bool = False, use_nn: bool = True) -> dict:
        """
        Komponuje menuet i zapisuje do MIDI.
        Używa MenuetGeneratorEnhanced jeśli dostępny, inaczej _generate_polyphonic_generic.
        """
        import datetime
        quantum_state = self._get_quantum_state()
        metrics = self._get_soul_metrics()

        print(f"\n{'='*70}")
        print(f"KOMPONOWANIE MENUETU ({key} {'moll' if minor else 'dur'})")
        print(f"{'='*70}")
        print(f"[EMOCJE] Dominanta: {max(metrics.items(), key=lambda x: x[1])[0].upper()} "
              f"({max(metrics.values()):.2f})")
        print(f"[QUANTUM] Vacuum: {quantum_state['vacuum']:.2f} | "
              f"Coherence: {quantum_state['coherence']:.2f}")

        # Spróbuj użyć MenuetGeneratorEnhanced
        try:
            from menuet_generator_enhanced import MenuetGeneratorEnhanced
            try:
                from soul_composer_tiny_nn import SoulComposerTinyNN
                nn = SoulComposerTinyNN()
            except Exception:
                nn = None
            gen = MenuetGeneratorEnhanced(self, nn)
            data = gen.generate_full_menuet(metrics, quantum_state, use_nn, key, minor)
        except Exception as e:
            print(f"[MENUET] Fallback do generatora natywnego: {e}")
            data = self._generate_polyphonic_generic('MENUET', quantum_state)

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        base = f"{self.OUTPUT_DIR}/menuet_{key}{'m' if minor else ''}_{timestamp}"
        paths = {}

        # Zapis MIDI przez music21
        if MUSIC21_AVAIL:
            try:
                score = self._create_music21_score(data, 'MENUET', 'piano', quantum_state)
                if score:
                    midi_path = f"{base}.mid"
                    score.write('midi', fp=midi_path)
                    paths['midi'] = midi_path
                    print(f"[MENUET] MIDI zapisany: {midi_path}")
                    if AUDIO_AVAIL:
                        audio = self._render_audio(midi_path)
                        paths.update(audio)
            except Exception as e:
                print(f"[MENUET] music21 błąd: {e}")

        # Fallback: midiutil
        if 'midi' not in paths and MIDIUTIL_AVAIL:
            try:
                midi_path = self._save_with_midiutil(data, base, minor)
                paths['midi'] = midi_path
                print(f"[MENUET] MIDI (midiutil) zapisany: {midi_path}")
            except Exception as e:
                print(f"[MENUET] midiutil błąd: {e}")

        # Zawsze zapisz txt
        txt_path = f"{base}.txt"
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(f"Menuet {key} {'minor' if minor else 'major'}\n")
            f.write(f"Wygenerowano: {datetime.datetime.now().isoformat()}\n")
            f.write(f"Quantum: Vacuum {quantum_state['vacuum']:.3f}, "
                    f"Coherence {quantum_state['coherence']:.3f}\n")
            f.write(f"Stan emocjonalny:\n")
            for k, v in sorted(metrics.items(), key=lambda x: -x[1])[:8]:
                f.write(f"  {k}: {v:.3f}\n")
            meta = data.get('metadata', {})
            f.write(f"\nForma: {meta.get('form', 'Menuet')}\n")
            f.write(f"Takty: {meta.get('measures', len(data['melody']))}\n")
        paths['txt'] = txt_path

        # Ewaluacja RL
        print("[RL] Ocena kompozycji...")
        reward = self._evaluate_menuet(data, metrics, quantum_state)
        print(f"[RL] Reward: {reward:.3f} | ", end="")
        if reward > 0.8: print("Doskonała kompozycja", end="")
        elif reward > 0.6: print("Dobra kompozycja", end="")
        elif reward > 0.4: print("Przeciętna kompozycja", end="")
        else: print("Eksperymentalna kompozycja", end="")
        print(f" (reward: {reward:.3f}).")

        paths['evaluation'] = {'reward': reward}
        return paths

    def _save_with_midiutil(self, data: dict, base_path: str, minor: bool) -> str:
        """Zapis MIDI używając midiutil (fallback gdy brak music21)."""
        midi = MIDIFile(2)  # 2 tracki: melodia + harmonia
        tempo = 120
        midi.addTempo(0, 0, tempo)
        midi.addTempo(1, 0, tempo)

        # Track 0: melodia
        time = 0.0
        for measure in data['melody']:
            for ev in measure:
                dur = ev.get('duration', 1.0)
                if ev.get('type') == 'note':
                    pitch = int(ev['pitch'])
                    midi.addNote(0, 0, pitch, time, dur, 80)
                time += dur

        # Track 1: harmonia
        time = 0.0
        for measure in data['harmony']:
            for ev in measure:
                dur = ev.get('duration', 3.0)
                if ev.get('type') == 'chord':
                    pitches = ev['pitch'] if isinstance(ev['pitch'], list) else [ev['pitch']]
                    for p in pitches:
                        midi.addNote(1, 0, int(p), time, dur, 60)
                time += dur

        midi_path = f"{base_path}.mid"
        with open(midi_path, 'wb') as f:
            midi.writeFile(f)
        return midi_path

    def _evaluate_menuet(self, data: dict, metrics: dict, quantum_state: dict) -> float:
        """Prosta ewaluacja RL menuetu."""
        score = 0.5  # Bazowy

        # Różnorodność melodyczna
        pitches = [ev['pitch'] for m in data['melody'] for ev in m if ev.get('type') == 'note']
        if pitches:
            unique_ratio = len(set(pitches)) / len(pitches)
            score += unique_ratio * 0.2

        # Proporcja pauz (Pustka) — nie za dużo
        rests = sum(1 for m in data['melody'] for ev in m if ev.get('type') == 'rest')
        notes = len(pitches)
        if notes + rests > 0:
            rest_ratio = rests / (notes + rests)
            score += (0.1 - abs(rest_ratio - 0.1)) * 0.3

        # Koherencja kwantowa = lepsza ocena
        score += quantum_state.get('coherence', 1.0) * 0.1

        # Emocje pozytywne = bonus
        score += metrics.get('radość', 0) * 0.05
        score += metrics.get('kreacja', 0) * 0.05

        return min(1.0, max(0.0, score))


if __name__ == "__main__":
    print("=" * 70)
    print("TEST: Soul Composer v8.2 + Quantum Physics")
    print("=" * 70)
    
    class DummyAII:
        context_vector = np.array([0.5]*15)
        def get_emotions(self): return {'logika': 0.8, 'chaos': 0.2, 'czas': 0.5, 'przestrzeń': 0.8}
        class DummyQuantum:
            class State: amplitudes = {'vacuum': np.sqrt(0.9) * np.exp(1j * 0)} # Silna pustka
            def get_phase_coherence(self): return 0.2 # Dekoherencja
        quantum = DummyQuantum()

    composer = SoulComposerV8(DummyAII())
    
    # Test kompozycji (zwróci dane ścieżek, jeśli masz music21 zapisze też plik mid)
    print("\nGeneruję utwór z symulacją 90% Pustki i silnej Dekoherencji...")
    res = composer.compose_new_work("ambient")
    print(f"Utwór zapisany pomyślnie. Pliki wyjściowe: {res}")
    print("Dzięki zintegrowaniu 'music21.note.Rest()' system nie crashuje przy wygaszonych dźwiękach.")