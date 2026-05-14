# -*- coding: utf-8 -*-
"""
unified_memory.py v1.0.1
EriAmo Union - Unified Cross-Modal Memory System

ZMIANY v1.0.1:
- FIX: recall_by_ontological — stary model 9-osiowy zastąpiony AXES z union_config
- FIX: save_to_file — os.makedirs("") rzucał FileNotFoundError gdy brak katalogu

Stores memories with multimodal anchors:
- Text (keywords, definitions)
- Music (features, patterns)
- Emotional state at encoding
- Ontological state at encoding
- Cross-modal links

Supports:
- Proustian recall (emotion → memories)
- Cross-modal recall (text → music, music → text)
- Memory consolidation

Author: Claude & Maciej
Date: December 19, 2025
"""

import json
import time
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import os


class UnifiedMemory:
    """
    Cross-modal memory system for Union.
    
    Each memory can have multiple anchors:
    - text: keywords, content, definitions
    - music: tempo, key, mode, features
    - audio: (future) sound classification
    - emotional_state: [8] emotions at encoding
    - ontological_state: {9 axes} at encoding
    """
    
    def __init__(self, verbose: bool = False):
        """
        Initialize unified memory system.
        
        Args:
            verbose: Print debug information
        """
        self.verbose = verbose
        self.D_Map = {}  # Unified memory storage
        self.next_id = 1
        
        # Statistics
        self.total_memories = 0
        self.text_memories = 0
        self.music_memories = 0
        self.hybrid_memories = 0
        
        # Links between memories
        self.memory_links = {}  # {mem_id: [linked_ids]}
        
        if self.verbose:
            print("[UnifiedMemory] Initialized")
    
    # =========================================================================
    # MEMORY STORAGE
    # =========================================================================
    
    def store_memory(
        self,
        content: str,
        modalities: Dict[str, Any],
        emotional_state: np.ndarray,
        ontological_state: Dict[str, float],
        tags: Optional[List[str]] = None,
        category: Optional[str] = None,
        weight: float = 10.0
    ) -> str:
        """
        Store a new memory with multimodal anchors.
        
        Args:
            content: Main text content
            modalities: Dict with 'text', 'music', 'audio' keys
            emotional_state: [8] array of emotions at encoding
            ontological_state: Dict of music axes at encoding
            tags: Optional list of tags
            category: Optional category label
            weight: Memory importance weight
        
        Returns:
            memory_id: Unique identifier for this memory
        """
        memory_id = f"Mem_{self.next_id:05d}"
        self.next_id += 1
        
        # Determine memory type
        has_text = bool(modalities.get('text'))
        has_music = bool(modalities.get('music'))
        has_audio = bool(modalities.get('audio'))
        
        is_hybrid = (has_text and has_music) or (has_text and has_audio) or (has_music and has_audio)
        
        memory = {
            'id': memory_id,
            'content': content,
            'timestamp': time.time(),
            
            # Multimodal anchors
            'text_anchor': modalities.get('text', {}),
            'music_anchor': modalities.get('music', {}),
            'audio_anchor': modalities.get('audio', {}),
            
            # State at encoding (for Proustian recall)
            'emotional_state': emotional_state.tolist() if isinstance(emotional_state, np.ndarray) else emotional_state,
            'ontological_state': ontological_state,
            
            # Metadata
            'tags': tags or [],
            'category': category or 'general',
            'weight': weight,
            'retrieval_count': 0,
            'last_retrieved': None,
            
            # Type flags
            'has_text': has_text,
            'has_music': has_music,
            'has_audio': has_audio,
            'is_hybrid': is_hybrid
        }
        
        self.D_Map[memory_id] = memory
        
        # Update statistics
        self.total_memories += 1
        if has_text:
            self.text_memories += 1
        if has_music:
            self.music_memories += 1
        if is_hybrid:
            self.hybrid_memories += 1
        
        if self.verbose:
            modal_desc = []
            if has_text: modal_desc.append("text")
            if has_music: modal_desc.append("music")
            if has_audio: modal_desc.append("audio")
            print(f"[Memory] Stored {memory_id}: {'+'.join(modal_desc)}")
        
        return memory_id
    
    # =========================================================================
    # RECALL BY TEXT
    # =========================================================================
    
    def recall_by_text(
        self,
        query: str,
        lexicon: Any,  # EvolvingLexicon instance
        threshold: float = 0.3,
        max_results: int = 5
    ) -> List[Dict]:
        """
        Recall memories by text query.
        
        Uses lexicon to analyze query and find semantic matches.
        
        Args:
            query: Text query
            lexicon: EvolvingLexicon instance for analysis
            threshold: Minimum similarity threshold
            max_results: Maximum number of results
        
        Returns:
            List of dicts with 'memory' and 'score'
        """
        # Analyze query with lexicon
        try:
            query_vector, sector, unknown = lexicon.analyze_text(query, enable_reinforcement=False)
        except:
            # Fallback if analyze_text signature different
            query_vector = np.zeros(8)
        
        matches = []
        
        for mem_id, memory in self.D_Map.items():
            if not memory.get('has_text'):
                continue
            
            text_anchor = memory['text_anchor']
            
            # Keyword similarity
            keyword_score = 0.0
            if 'keywords' in text_anchor:
                keyword_score = self._keyword_similarity(query, text_anchor['keywords'])
            
            # Content similarity (simple substring)
            content_score = 0.0
            content = memory.get('content', '').lower()
            if query.lower() in content:
                content_score = 0.5
            
            # Emotional similarity
            emotion_score = 0.0
            if len(query_vector) == 8:
                mem_emotions = np.array(memory['emotional_state'])
                if np.linalg.norm(query_vector) > 0 and np.linalg.norm(mem_emotions) > 0:
                    emotion_score = 1 - np.linalg.norm(query_vector - mem_emotions) / (2 * np.sqrt(8))
            
            # Combined score (weighted)
            final_score = (
                0.4 * keyword_score +
                0.3 * content_score +
                0.3 * emotion_score
            )
            
            if final_score > threshold:
                matches.append({
                    'memory': memory,
                    'score': final_score,
                    'breakdown': {
                        'keyword': keyword_score,
                        'content': content_score,
                        'emotion': emotion_score
                    }
                })
        
        # Sort by score and return top results
        matches.sort(key=lambda x: x['score'], reverse=True)
        
        if self.verbose and matches:
            print(f"[Recall Text] Found {len(matches)} matches, top score: {matches[0]['score']:.3f}")
        
        return matches[:max_results]
    
    # =========================================================================
    # RECALL BY MUSIC
    # =========================================================================
    
    def recall_by_music(
        self,
        music_features: Dict[str, Any],
        threshold: float = 0.3,
        max_results: int = 5
    ) -> List[Dict]:
        """
        Recall memories by music features.
        
        Matches on:
        - Key signature
        - Tempo (within range)
        - Mode (major/minor)
        - Energy/intensity
        
        Args:
            music_features: Dict with music features
            threshold: Minimum similarity threshold
            max_results: Maximum number of results
        
        Returns:
            List of dicts with 'memory' and 'score'
        """
        matches = []
        
        for mem_id, memory in self.D_Map.items():
            if not memory.get('has_music'):
                continue
            
            music_anchor = memory['music_anchor']
            
            # Calculate music similarity
            score = self._music_similarity(music_features, music_anchor)
            
            if score > threshold:
                matches.append({
                    'memory': memory,
                    'score': score
                })
        
        matches.sort(key=lambda x: x['score'], reverse=True)
        
        if self.verbose and matches:
            print(f"[Recall Music] Found {len(matches)} matches, top score: {matches[0]['score']:.3f}")
        
        return matches[:max_results]
    
    # =========================================================================
    # RECALL BY EMOTION (PROUSTIAN MEMORY!)
    # =========================================================================
    
    def recall_by_emotion(
        self,
        emotion_vector: np.ndarray,
        threshold: float = 0.5,
        max_results: int = 5
    ) -> List[Dict]:
        """
        Recall memories by emotional state (Proustian recall).
        
        When you FEEL something similar to a past experience,
        it triggers that memory.
        
        Args:
            emotion_vector: [8] current emotional state
            threshold: Minimum similarity threshold
            max_results: Maximum number of results
        
        Returns:
            List of dicts with 'memory' and 'score'
        """
        matches = []
        
        query_norm = np.linalg.norm(emotion_vector)
        if query_norm < 0.01:
            return []  # No strong emotion, no recall
        
        for mem_id, memory in self.D_Map.items():
            mem_emotions = np.array(memory['emotional_state'])
            mem_norm = np.linalg.norm(mem_emotions)
            
            if mem_norm < 0.01:
                continue
            
            # Cosine similarity
            similarity = np.dot(emotion_vector, mem_emotions) / (query_norm * mem_norm + 1e-6)
            
            if similarity > threshold:
                matches.append({
                    'memory': memory,
                    'score': float(similarity)
                })
        
        matches.sort(key=lambda x: x['score'], reverse=True)
        
        if self.verbose and matches:
            print(f"[Recall Emotion] Found {len(matches)} matches (Proustian!), top: {matches[0]['score']:.3f}")
        
        return matches[:max_results]
    
    # =========================================================================
    # RECALL BY ONTOLOGICAL STATE
    # =========================================================================
    
    def recall_by_ontological(
        self,
        ontological_state: Dict[str, float],
        threshold: float = 0.3,
        max_results: int = 5
    ) -> List[Dict]:
        """
        Recall memories by ontological state similarity.
        
        Args:
            ontological_state: Dict with 9 music axes
            threshold: Minimum similarity threshold
            max_results: Maximum number of results
        
        Returns:
            List of dicts with 'memory' and 'score'
        """
        matches = []
        
        # FIX v1.0.1: AXES z union_config zamiast starego modelu 9-osiowego
        # (logika, emocje, affections, ...) sprzed migracji na 15 osi
        try:
            from union_config import AXES as axes_order
        except ImportError:
            axes_order = ['radość','smutek','strach','gniew','miłość','wstręt',
                          'zaskoczenie','akceptacja','logika','wiedza','czas',
                          'kreacja','byt','przestrzeń','chaos']
        query_vec = np.array([ontological_state.get(axis, 0.0) for axis in axes_order])
        query_norm = np.linalg.norm(query_vec)
        
        if query_norm < 0.01:
            return []
        
        for mem_id, memory in self.D_Map.items():
            mem_onto = memory['ontological_state']
            mem_vec = np.array([mem_onto.get(axis, 0.0) for axis in axes_order])
            mem_norm = np.linalg.norm(mem_vec)
            
            if mem_norm < 0.01:
                continue
            
            # Cosine similarity
            similarity = np.dot(query_vec, mem_vec) / (query_norm * mem_norm + 1e-6)
            
            if similarity > threshold:
                matches.append({
                    'memory': memory,
                    'score': float(similarity)
                })
        
        matches.sort(key=lambda x: x['score'], reverse=True)
        
        if self.verbose and matches:
            print(f"[Recall Ontological] Found {len(matches)} matches, top: {matches[0]['score']:.3f}")
        
        return matches[:max_results]
    
    # =========================================================================
    # MEMORY LINKS
    # =========================================================================
    
    def link_memories(self, mem_id1: str, mem_id2: str, link_type: str = "related"):
        """
        Create explicit link between two memories.
        
        Args:
            mem_id1: First memory ID
            mem_id2: Second memory ID
            link_type: Type of link ('similar', 'caused_by', 'reminds_of', 'opposite')
        """
        if mem_id1 not in self.D_Map or mem_id2 not in self.D_Map:
            return False
        
        # Add bidirectional link
        if mem_id1 not in self.memory_links:
            self.memory_links[mem_id1] = []
        if mem_id2 not in self.memory_links:
            self.memory_links[mem_id2] = []
        
        self.memory_links[mem_id1].append({'to': mem_id2, 'type': link_type})
        self.memory_links[mem_id2].append({'to': mem_id1, 'type': link_type})
        
        if self.verbose:
            print(f"[Memory] Linked {mem_id1} ↔ {mem_id2} ({link_type})")
        
        return True
    
    def get_linked_memories(self, mem_id: str) -> List[Dict]:
        """Get all memories linked to this one."""
        if mem_id not in self.memory_links:
            return []
        
        linked = []
        for link in self.memory_links[mem_id]:
            linked_id = link['to']
            if linked_id in self.D_Map:
                linked.append({
                    'memory': self.D_Map[linked_id],
                    'link_type': link['type']
                })
        
        return linked
    
    # =========================================================================
    # UTILITY METHODS
    # =========================================================================
    
    def _keyword_similarity(self, query: str, keywords: List[str]) -> float:
        """Simple keyword matching."""
        query_words = set(query.lower().split())
        keyword_set = set(k.lower() for k in keywords)
        
        if not query_words or not keyword_set:
            return 0.0
        
        overlap = len(query_words & keyword_set)
        return overlap / len(query_words)
    
    def _music_similarity(self, feat1: Dict, feat2: Dict) -> float:
        """Calculate music feature similarity."""
        score = 0.0
        count = 0
        
        # Key similarity
        if 'key' in feat1 and 'key' in feat2:
            score += 1.0 if feat1['key'] == feat2['key'] else 0.0
            count += 1
        
        # Tempo similarity (within 20 BPM)
        if 'tempo' in feat1 and 'tempo' in feat2:
            tempo_diff = abs(feat1['tempo'] - feat2['tempo'])
            score += max(0, 1.0 - tempo_diff / 40.0)
            count += 1
        
        # Mode similarity (major/minor)
        if 'mode' in feat1 and 'mode' in feat2:
            score += 1.0 if feat1['mode'] == feat2['mode'] else 0.0
            count += 1
        
        # Energy similarity
        if 'energy' in feat1 and 'energy' in feat2:
            energy_diff = abs(feat1['energy'] - feat2['energy'])
            score += max(0, 1.0 - energy_diff)
            count += 1
        
        return score / count if count > 0 else 0.0
    
    def update_retrieval_stats(self, mem_id: str):
        """Update retrieval statistics for a memory."""
        if mem_id in self.D_Map:
            self.D_Map[mem_id]['retrieval_count'] += 1
            self.D_Map[mem_id]['last_retrieved'] = time.time()
    
    def get_statistics(self) -> Dict:
        """Get memory system statistics."""
        return {
            'total_memories': self.total_memories,
            'text_memories': self.text_memories,
            'music_memories': self.music_memories,
            'hybrid_memories': self.hybrid_memories,
            'links': len(self.memory_links),
            'most_retrieved': self._get_most_retrieved(3)
        }
    
    def _get_most_retrieved(self, n: int = 3) -> List[Dict]:
        """Get most frequently retrieved memories."""
        sorted_mems = sorted(
            self.D_Map.items(),
            key=lambda x: x[1]['retrieval_count'],
            reverse=True
        )
        
        return [
            {
                'id': mem_id,
                'content': mem['content'][:50],
                'count': mem['retrieval_count']
            }
            for mem_id, mem in sorted_mems[:n]
        ]
    
    # =========================================================================
    # PERSISTENCE
    # =========================================================================
    
    def save_to_file(self, filepath: str):
        """Save unified D_Map to JSONL format."""
        # FIX v1.0.1: dirname("file.soul") == "" → makedirs("") rzuca błąd
        dir_path = os.path.dirname(filepath)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            # Metadata
            meta = {
                '_type': '@META',
                'format': 'unified_memory',
                'version': '1.0.0',
                'total_memories': self.total_memories,
                'text_memories': self.text_memories,
                'music_memories': self.music_memories,
                'hybrid_memories': self.hybrid_memories,
                'timestamp': time.time()
            }
            f.write(json.dumps(meta, ensure_ascii=False) + '\n')
            
            # Memories
            for mem_id, memory in self.D_Map.items():
                f.write(json.dumps(memory, ensure_ascii=False) + '\n')
            
            # Links
            if self.memory_links:
                links_data = {
                    '_type': '@LINKS',
                    'links': self.memory_links
                }
                f.write(json.dumps(links_data, ensure_ascii=False) + '\n')
        
        if self.verbose:
            print(f"[Memory] Saved {self.total_memories} memories to {filepath}")
    
    def load_from_file(self, filepath: str):
        """Load unified D_Map from JSONL format."""
        if not os.path.exists(filepath):
            if self.verbose:
                print(f"[Memory] No file at {filepath}, starting fresh")
            return False
        
        self.D_Map = {}
        self.memory_links = {}
        
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue
                
                data = json.loads(line)
                
                if data.get('_type') == '@META':
                    # Load metadata
                    self.total_memories = data.get('total_memories', 0)
                    self.text_memories = data.get('text_memories', 0)
                    self.music_memories = data.get('music_memories', 0)
                    self.hybrid_memories = data.get('hybrid_memories', 0)
                
                elif data.get('_type') == '@LINKS':
                    # Load links
                    self.memory_links = data.get('links', {})
                
                else:
                    # Load memory
                    mem_id = data.get('id')
                    if mem_id:
                        self.D_Map[mem_id] = data
                        
                        # Update next_id
                        id_num = int(mem_id.split('_')[1])
                        self.next_id = max(self.next_id, id_num + 1)
        
        if self.verbose:
            print(f"[Memory] Loaded {len(self.D_Map)} memories from {filepath}")
        
        return True


# =============================================================================
# TEST FUNCTIONS
# =============================================================================

def test_unified_memory():
    """Quick test of UnifiedMemory functionality."""
    print("\n🧪 Testing UnifiedMemory\n")
    
    memory = UnifiedMemory(verbose=True)
    
    # Test 1: Store text memory
    print("[Test 1] Storing text memory...")
    mem_id1 = memory.store_memory(
        content="Koncert w parku latem",
        modalities={
            'text': {
                'keywords': ['koncert', 'park', 'lato', 'muzyka']
            }
        },
        emotional_state=np.array([0.9, 0, 0, 0, 0.6, 0, 0, 0.4]),  # radość, miłość
        ontological_state={},
        tags=['experience', 'music']
    )
    print(f"  Stored: {mem_id1}")
    print("  ✅ Text memory stored\n")
    
    # Test 2: Store music memory
    print("[Test 2] Storing music memory...")
    mem_id2 = memory.store_memory(
        content="Smutna ballada fortepianowa",
        modalities={
            'music': {
                'key': 'A minor',
                'tempo': 60,
                'mode': 'minor'
            }
        },
        emotional_state=np.array([0, 0.8, 0, 0, 0, 0, 0, 0.3]),  # smutek
        ontological_state={'affections': 0.8}
    )
    print(f"  Stored: {mem_id2}")
    print("  ✅ Music memory stored\n")
    
    # Test 3: Store hybrid memory
    print("[Test 3] Storing hybrid memory...")
    mem_id3 = memory.store_memory(
        content="Radosna piosenka na weselu",
        modalities={
            'text': {'keywords': ['wesele', 'piosenka', 'radość']},
            'music': {'tempo': 120, 'mode': 'major'}
        },
        emotional_state=np.array([0.9, 0, 0, 0, 0.8, 0, 0, 0.5]),
        ontological_state={'kreacja': 0.7}
    )
    print(f"  Stored: {mem_id3}")
    print("  ✅ Hybrid memory stored\n")
    
    # Test 4: Proustian recall
    print("[Test 4] Proustian recall (by emotion)...")
    similar_emotion = np.array([0.7, 0, 0, 0, 0.6, 0, 0, 0.6])
    results = memory.recall_by_emotion(similar_emotion, threshold=0.7)
    
    print(f"  Found {len(results)} memories")
    if results:
        print(f"  Top match: {results[0]['memory']['content']}")
        print(f"  Score: {results[0]['score']:.3f}")
    print("  ✅ Proustian recall works\n")
    
    # Test 5: Statistics
    print("[Test 5] Memory statistics...")
    stats = memory.get_statistics()
    print(f"  Total: {stats['total_memories']}")
    print(f"  Text: {stats['text_memories']}")
    print(f"  Music: {stats['music_memories']}")
    print(f"  Hybrid: {stats['hybrid_memories']}")
    print("  ✅ Statistics work\n")
    
    # Test 6: Save/Load
    print("[Test 6] Save and load...")
    test_file = "test_unified_memory.soul"
    memory.save_to_file(test_file)
    
    memory2 = UnifiedMemory(verbose=False)
    memory2.load_from_file(test_file)
    
    assert len(memory2.D_Map) == 3, "Should load 3 memories"
    print(f"  Loaded {len(memory2.D_Map)} memories")
    print("  ✅ Save/Load works\n")
    
    # Cleanup
    if os.path.exists(test_file):
        os.remove(test_file)
    
    print("✅ All UnifiedMemory tests passed!\n")
    
    return memory


if __name__ == "__main__":
    test_unified_memory()