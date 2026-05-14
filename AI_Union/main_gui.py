# -*- coding: utf-8 -*-
"""
EriAmo v5.9 - Interfejs Graficzny
- Wizualizacja wygaszania emocji
- Rozróżnienie osi efemerycznych i trwałych
- Bezpieczna obsługa wątków
- Dostosowany do płaskiej struktury katalogów (AI_Union root)
main_gui.py v5.0.6
ZMIANY v5.0.6:
- MIDI zapis przez soul_composer.compose_menuet()
- FIX: import MultimodalAgency, WM_DELETE_WINDOW, /exit, logi

- ✅ Synchronizacja z v9.8.9: Podgląd Vacuum i Coherence w statusie.
- ✅ Naprawione filtrowanie: Fraktale v8.0 zostają w terminalu.
- ✅ Dynamiczna etykieta stanu kwantowego.
"""
import tkinter as tk
from tkinter import scrolledtext, ttk
import sys
import threading
import queue
import os
import re

try:
    from multimodal_agency import MultimodalAgency
except ImportError:
    MultimodalAgency = None

class SelectiveRedirector:
    def __init__(self, gui_queue):
        self.queue = gui_queue
        self.terminal = sys.__stdout__

    def write(self, string):
        self.terminal.write(string)
        # Filtrujemy fraktale i ruminacje, by nie psuły formatowania w małym GUI
        if any(x in string for x in ["FRACTAL", "---", "===", "∠", "Vacuum:", "Koherencja:"]):
            return
        if string.strip():
            stripped = string.strip()
            if stripped.startswith("[") and not string.startswith("\n"):
                string = "\n" + string
            self.queue.put(("TEXT", string))

    def flush(self): self.terminal.flush()

class EriAmoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("EriAmo Union v9.8.9 [Quantum Hybrid]")
        self.root.geometry("1000x850")
        self.root.configure(bg="#0a0a0a")
        self.msg_queue = queue.Queue()
        self.is_closing = False
        
        self.color_map = {'96': '#00f0ff', '92': '#00ff00', '93': '#ffff00', '95': '#ff00ff', '91': '#ff4444', '0': '#ddd'}
        
        self.init_backend()
        self.create_widgets()
        
        sys.stdout = SelectiveRedirector(self.msg_queue)
        self.root.after(100, self.update_loop)

    def init_backend(self):
        try:
            from union_core import EriAmoUnion
            self.union = EriAmoUnion(verbose=True)
            if MultimodalAgency:
                self.agency = MultimodalAgency(self.union, verbose=True)
                self.agency.start()
            else:
                self.agency = None
                print("[GUI] MultimodalAgency niedostępna")
            self.union.start()
        except Exception as e: print(f"Błąd startu: {e}")

    def create_widgets(self):
        # Header z danymi kwantowymi
        self.header = tk.Frame(self.root, bg="#111", height=40)
        self.header.pack(fill=tk.X)
        
        self.q_label = tk.Label(self.header, text="Quantum: Strumień nieaktywny", 
                                bg="#111", fg="#00f0ff", font=("Consolas", 10))
        self.q_label.pack(side=tk.LEFT, padx=20)

        # Chat
        self.console_log = scrolledtext.ScrolledText(self.root, bg="#050505", fg="#bbb", 
                                                    font=("Consolas", 12), borderwidth=0)
        self.console_log.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        for code, hex_color in self.color_map.items():
            self.console_log.tag_config(code, foreground=hex_color)
        self.console_log.tag_config("USER", foreground="#00ffaa", font=("Consolas", 12, "bold"))

        # Input
        self.entry = tk.Entry(self.root, bg="#151515", fg="#fff", font=("Consolas", 13), 
                             borderwidth=0, insertbackground="white")
        self.entry.pack(fill=tk.X, padx=20, pady=20, ipady=12)
        self.entry.bind("<Return>", self.send_command)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def update_loop(self):
        while not self.msg_queue.empty():
            _, data = self.msg_queue.get_nowait()
            self.append_text(data)
        
        # Aktualizacja statusu kwantowego w nagłówku GUI
        if not self.is_closing:
            try:
                q = self.union.aii.quantum
                vac = abs(q.state.amplitudes['vacuum'])**2
                coh = q.get_phase_coherence()
                self.q_label.config(text=f"Vacuum: {vac:.2f} | Koherencja: {coh:.2f} | Status: Stabilny")
            except: pass
        self.root.after(500, self.update_loop)

    def append_text(self, text, tag=None):
        ansi_regexp = re.compile(r'\x1b\[([0-9;]*)m')
        parts = ansi_regexp.split(text)
        current_tag = tag
        for i, part in enumerate(parts):
            if i % 2 == 0:
                if part: self.console_log.insert(tk.END, part, current_tag)
            else:
                code = part.split(';')[-1] # Obsługa złożonych kodów
                if code in self.color_map: current_tag = code
                elif code == "0": current_tag = tag
        self.console_log.see(tk.END)

    def send_command(self, event=None):
        cmd = self.entry.get().strip()
        if not cmd: return
        self.entry.delete(0, tk.END)
        self.append_text(f"\nTy > {cmd}\n", "USER")
        if cmd.strip().lower() == "/exit":
            self.on_closing()
            return
        if cmd.strip().lower() == "/menuet":
            def play_menuet():
                try:
                    import random
                    from soul_composer import SoulComposerV8
                    composer = SoulComposerV8(self.union.aii)
                    emotions = self.union.aii.get_emotions()
                    dominant = max(emotions.items(), key=lambda x: x[1])
                    is_minor = emotions.get("smutek", 0) > 0.4
                    key = random.choice(["C", "G", "D", "F"])
                    result = composer.compose_menuet(key=key, minor=is_minor, use_nn=True)
                    reward = result.get("evaluation", {}).get("reward", 0.0)
                    midi = result.get("midi", "brak")
                    tone = "moll" if is_minor else "dur"
                    self.msg_queue.put(("TEXT",
                        f" [MENUET] Skomponowano w {key} {tone}"
                        f" (dominanta: {dominant[0]}, reward: {reward:.3f})\n"
                        f" [MENUET] Plik: {midi}\n"))
                except Exception as e:
                    self.msg_queue.put(("TEXT", f" [MENUET] Błąd: {e}\n"))
            threading.Thread(target=play_menuet, daemon=True).start()
            return
        if self.agency: self.agency.stimulate(cmd)  # Reset nudy
        def run_and_display():
            resp = self.union.process_input(cmd)
            if resp:
                self.msg_queue.put(("TEXT", f" [EriAmo] {resp}\n"))
        threading.Thread(target=run_and_display, daemon=True).start()

    def on_closing(self):
        self.is_closing = True
        if self.agency: self.agency.stop()
        self.union.stop()
        self.root.destroy()
        sys.exit(0)

if __name__ == "__main__":
    root = tk.Tk()
    app = EriAmoGUI(root)
    root.mainloop()