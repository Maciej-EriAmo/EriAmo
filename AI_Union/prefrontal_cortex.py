# -*- coding: utf-8 -*-
"""
prefrontal_cortex.py v1.0.0
Płat przedczołowy EriAmo - Working Memory + Hierarchical Chunk Access

FUNKCJE:
- Fraktalny dostęp do chunków (od kontekstu → słowa)
- Working Memory (max 7±2 elementy)
- Priming boost (ostatnio używane łatwiej się aktivują)
- Executive filtering (wybór tego co ważne)

Autor: Maciej Mazur + Claude
"""

import numpy as np
from typing import List, Dict, Optional, Tuple
from collections import deque
import time

try:
    from union_config import Colors
except ImportError:
    class Colors:
        CYAN = "\033[36m"; RESET = "\033[0m"; YELLOW = "\033[33m"
        MAGENTA = "\033[35m"; GREEN = "\033[32m"


class PrefrontalCortex:
    """
    Płat przedczołowy - Working Memory + Hierarchiczny dostęp do chunków.
    
    Implementuje:
    - Fraktalny dostęp (długie chunki → krótkie → słowa)
    - Working Memory (FIFO, max 7±2)
    - Priming (boost dla niedawno używanych)
    - Executive control (filtrowanie szumu)
    """
    
    # Miller's Law - pojemność pamięci roboczej
    WM_MIN = 5
    WM_MAX = 9
    WM_OPTIMAL = 7
    
    # Progi znaczącej długości chunków
    CONTEXT_LEVEL = 5    # 5-6 słów = szeroki kontekst
    PHRASE_LEVEL = 3     # 3-4 słowa = frazy
    BIGRAM_LEVEL = 2     # 2 słowa = bigramy
    
    def __init__(self, chunk_lexicon, verbose: bool = False):
        """
        Args:
            chunk_lexicon: Instancja ChunkLexicon
            verbose: Debug output
        """
        self.chunks = chunk_lexicon
        self.verbose = verbose
        
        # Working Memory - FIFO queue
        self.working_memory: deque = deque(maxlen=self.WM_OPTIMAL)
        
        # Historia aktywacji (dla priming)
        self.activation_history = {}  # {chunk_text: last_access_time}
        
        # Statystyki
        self.access_count = 0
        self.cache_hits = 0
        
        if self.verbose:
            print(f"{Colors.CYAN}[PREFRONTAL] Inicjalizacja - WM capacity: {self.WM_OPTIMAL}{Colors.RESET}")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # HIERARCHICAL ACCESS (FRAKTAL)
    # ═══════════════════════════════════════════════════════════════════════════
    
    def hierarchical_access(
        self, 
        query: str, 
        max_depth: int = 3,
        use_priming: bool = True
    ) -> List[Dict]:
        """
        Fraktalny dostęp do chunków - od szerokiego kontekstu do atomów.
        
        POZIOMY (top-down):
        1. CONTEXT (5-6 słów)  - szeroki kontekst
        2. PHRASE  (3-4 słowa) - frazy znaczeniowe
        3. BIGRAM  (2 słowa)   - podstawowe bloki
        
        Args:
            query: Zapytanie tekstowe
            max_depth: Maksymalna głębokość hierarchii
            use_priming: Czy uwzględnić priming boost
            
        Returns:
            Lista chunków posortowanych według relevance (hierarchicznie)
        """
        self.access_count += 1
        query_lower = query.lower()
        results = []
        
        # Sprawdź Working Memory (cache) - najszybszy dostęp
        wm_hits = self._check_working_memory(query_lower)
        if wm_hits:
            self.cache_hits += 1
            if self.verbose:
                print(f"{Colors.GREEN}[WM HIT] {len(wm_hits)} chunków z pamięci roboczej{Colors.RESET}")
            results.extend(wm_hits)
        
        # Hierarchiczne przeszukiwanie (od góry w dół)
        levels = [
            (self.CONTEXT_LEVEL, "CONTEXT"),
            (self.PHRASE_LEVEL, "PHRASE"),
            (self.BIGRAM_LEVEL, "BIGRAM")
        ]
        
        for min_length, level_name in levels[:max_depth]:
            level_matches = self._search_level(
                query_lower, 
                min_length,
                use_priming
            )
            
            if level_matches:
                if self.verbose:
                    print(f"{Colors.YELLOW}[{level_name}] {len(level_matches)} matches{Colors.RESET}")
                results.extend(level_matches)
        
        # Deduplikacja (chunk może pasować do wielu poziomów)
        seen = set()
        unique_results = []
        for chunk_data in results:
            chunk_id = chunk_data['chunk'].text
            if chunk_id not in seen:
                seen.add(chunk_id)
                unique_results.append(chunk_data)
        
        # Sortuj według score (priming + frequency)
        unique_results.sort(key=lambda x: x['score'], reverse=True)
        
        # Dodaj TOP matches do Working Memory
        for match in unique_results[:3]:
            self._add_to_working_memory(match['chunk'])
        
        return unique_results
    
    def _search_level(
        self, 
        query: str, 
        min_length: int,
        use_priming: bool
    ) -> List[Dict]:
        """
        Przeszukuje chunks o danej długości.
        
        Returns:
            Lista dict z keys: 'chunk', 'score', 'level'
        """
        matches = []
        
        for chunk_text, chunk_obj in self.chunks.chunks.items():
            # Filtr długości (fraktalny poziom)
            if chunk_obj.length < min_length:
                continue
            
            # Filtr zawierania (prosty substring)
            if query not in chunk_text:
                continue
            
            # Oblicz score
            score = self._calculate_relevance_score(
                chunk_obj,
                query,
                use_priming
            )
            
            matches.append({
                'chunk': chunk_obj,
                'score': score,
                'level': min_length
            })
        
        return matches
    
    def _calculate_relevance_score(
        self,
        chunk,
        query: str,
        use_priming: bool
    ) -> float:
        """
        Oblicza score relevance dla chunka.
        
        Składowe:
        - Frequency (jak często używany)
        - Priming (kiedy ostatnio)
        - Length match (czy długość pasuje do kontekstu)
        """
        score = 0.0
        
        # 1. Frequency (jak często chunk był używany)
        score += chunk.frequency * 0.4
        
        # 2. Priming boost (niedawno używane łatwiej się aktivują)
        if use_priming:
            priming_boost = chunk.get_boost()  # 1.0 + priming_strength
            score *= priming_boost
        
        # 3. Length bonus (dłuższe chunki = bardziej specific context)
        length_bonus = chunk.length * 0.1
        score += length_bonus
        
        return score
    
    # ═══════════════════════════════════════════════════════════════════════════
    # WORKING MEMORY (CACHE)
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _check_working_memory(self, query: str) -> List[Dict]:
        """
        Sprawdza czy query pasuje do chunków w Working Memory.
        
        Returns:
            Lista matches z WM
        """
        hits = []
        
        for chunk in self.working_memory:
            if query in chunk.text:
                score = self._calculate_relevance_score(
                    chunk,
                    query,
                    use_priming=True
                )
                
                # WM bonus - chunki w WM mają boost (szybszy dostęp)
                score *= 1.5
                
                hits.append({
                    'chunk': chunk,
                    'score': score,
                    'level': chunk.length,
                    'from_wm': True
                })
        
        return hits
    
    def _add_to_working_memory(self, chunk):
        """
        Dodaje chunk do Working Memory (FIFO).
        
        Jeśli WM pełna, najstarszy element jest usuwany.
        """
        # Update priming
        chunk.update_priming()
        
        # Dodaj do WM (deque automatycznie usuwa najstarszy jeśli full)
        self.working_memory.append(chunk)
        
        # Zapisz timestamp dla priming
        self.activation_history[chunk.text] = time.time()
    
    def get_working_memory_contents(self) -> List[str]:
        """Zwraca teksty chunków w WM (dla debugowania)."""
        return [chunk.text for chunk in self.working_memory]
    
    def clear_working_memory(self):
        """Czyści Working Memory (np. przy zmianie kontekstu)."""
        self.working_memory.clear()
        if self.verbose:
            print(f"{Colors.MAGENTA}[WM] Cleared{Colors.RESET}")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # EXECUTIVE CONTROL (FILTROWANIE)
    # ═══════════════════════════════════════════════════════════════════════════
    
    def executive_filter(
        self,
        candidates: List[Dict],
        top_k: int = 3,
        min_score: float = 0.5
    ) -> List[Dict]:
        """
        Executive Control - wybiera najważniejsze chunki.
        
        Filtruje szum i wybiera top-k najbardziej relevantnych.
        
        Args:
            candidates: Lista dict z chunkami i scores
            top_k: Ile najlepszych wybrać
            min_score: Minimalny próg score
            
        Returns:
            Przefiltrowana lista
        """
        # Filtr minimalnego score
        filtered = [c for c in candidates if c['score'] >= min_score]
        
        # Sortuj i weź top-k
        filtered.sort(key=lambda x: x['score'], reverse=True)
        
        return filtered[:top_k]
    
    # ═══════════════════════════════════════════════════════════════════════════
    # STATYSTYKI & MONITORING
    # ═══════════════════════════════════════════════════════════════════════════
    
    def get_statistics(self) -> Dict:
        """Zwraca statystyki działania PFC."""
        cache_hit_rate = (self.cache_hits / self.access_count * 100) if self.access_count > 0 else 0
        
        return {
            'wm_size': len(self.working_memory),
            'wm_capacity': self.WM_OPTIMAL,
            'total_accesses': self.access_count,
            'cache_hits': self.cache_hits,
            'cache_hit_rate': cache_hit_rate,
            'activation_history_size': len(self.activation_history)
        }
    
    def print_status(self):
        """Wyświetla status PFC."""
        stats = self.get_statistics()
        
        print(f"\n{Colors.CYAN}{'='*60}")
        print("PREFRONTAL CORTEX STATUS")
        print(f"{'='*60}{Colors.RESET}")
        
        print(f"Working Memory: {stats['wm_size']}/{stats['wm_capacity']}")
        print(f"Cache Hit Rate: {stats['cache_hit_rate']:.1f}%")
        print(f"Total Accesses: {stats['total_accesses']}")
        
        if self.working_memory:
            print(f"\n{Colors.YELLOW}Current WM Contents:{Colors.RESET}")
            for i, chunk in enumerate(self.working_memory, 1):
                print(f"  [{i}] {chunk.text[:40]}...")
        
        print(f"{Colors.CYAN}{'='*60}{Colors.RESET}\n")


# ═══════════════════════════════════════════════════════════════════════════════
# INTEGRACJA Z AII
# ═══════════════════════════════════════════════════════════════════════════════

def integrate_prefrontal_cortex(aii_instance):
    """
    Dodaje PFC do instancji AII.
    
    Usage:
        pfc = integrate_prefrontal_cortex(aii)
        results = pfc.hierarchical_access("jak się masz", max_depth=3)
    """
    if not aii_instance.chunk_lexicon:
        print(f"{Colors.YELLOW}[WARN] ChunkLexicon nie aktywny - PFC potrzebuje chunków!{Colors.RESET}")
        return None
    
    pfc = PrefrontalCortex(aii_instance.chunk_lexicon, verbose=True)
    
    # Dodaj jako atrybut AII
    aii_instance.prefrontal = pfc
    
    print(f"{Colors.GREEN}[PFC] Płat przedczołowy zintegrowany z AII!{Colors.RESET}")
    
    return pfc


# ═══════════════════════════════════════════════════════════════════════════════
# TEST
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print(f"\n{Colors.CYAN}{'='*60}")
    print("TEST: Prefrontal Cortex v1.0.0")
    print(f"{'='*60}{Colors.RESET}\n")
    
    # Mock ChunkLexicon dla testów
    class MockChunk:
        def __init__(self, text, length, freq):
            self.text = text
            self.length = length
            self.frequency = freq
            self.priming_strength = 0.0
            self.last_seen = time.time()
        
        def update_priming(self):
            self.priming_strength = min(1.0, self.priming_strength + 0.3)
        
        def get_boost(self):
            return 1.0 + self.priming_strength
    
    class MockLexicon:
        def __init__(self):
            self.chunks = {
                "jak się masz": MockChunk("jak się masz", 3, 10),
                "co słychać": MockChunk("co słychać", 2, 8),
                "wszystko w porządku": MockChunk("wszystko w porządku", 3, 5),
                "jak": MockChunk("jak", 1, 15),
                "się": MockChunk("się", 1, 20),
                "masz": MockChunk("masz", 1, 12),
            }
    
    # Stwórz PFC
    lexicon = MockLexicon()
    pfc = PrefrontalCortex(lexicon, verbose=True)
    
    # Test 1: Hierarchical Access
    print(f"\n{Colors.YELLOW}[Test 1] Hierarchical Access{Colors.RESET}")
    results = pfc.hierarchical_access("jak się masz", max_depth=3)
    
    print(f"\nZnaleziono {len(results)} chunków:")
    for i, r in enumerate(results[:5], 1):
        print(f"  [{i}] {r['chunk'].text} (score: {r['score']:.2f}, level: {r['level']})")
    
    # Test 2: Working Memory
    print(f"\n{Colors.YELLOW}[Test 2] Working Memory{Colors.RESET}")
    pfc.print_status()
    
    # Test 3: Executive Filter
    print(f"\n{Colors.YELLOW}[Test 3] Executive Filter{Colors.RESET}")
    filtered = pfc.executive_filter(results, top_k=2, min_score=1.0)
    print(f"Po filtrze: {len(filtered)} chunków")
    
    # Test 4: Cache Hit
    print(f"\n{Colors.YELLOW}[Test 4] Cache Hit (2nd access){Colors.RESET}")
    results2 = pfc.hierarchical_access("jak się", max_depth=2)
    
    pfc.print_status()
    
    print(f"\n{Colors.GREEN}✅ Testy zakończone!{Colors.RESET}\n")
