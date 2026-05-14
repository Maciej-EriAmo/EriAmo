#core.py

import json
from pathlib import Path
from datetime import datetime

class EriAmoCore:
    """
    Main EriAmo system - integrates all components
    """
    
    def __init__(self, soul_file: str = "eriamo.soul"):
        # Core components
        self.emotional_state = QuantumEmotionalState()
        self.interference = EmotionalInterference()
        self.predictor = TemporalEmotionalPredictor()
        self.decider = QuantumDecisionMaker(
            self.emotional_state,
            self.interference
        )
        
        # Persistence
        self.soul_file = Path(soul_file)
        self.load_soul()
    
    def process_stimulus(self, stimulus: dict) -> dict:
        """
        Main processing loop
        
        1. Update emotional state
        2. Apply interference
        3. Record history
        4. Make decision (if needed)
        """
        # 1. Emotional update based on stimulus
        self._update_from_stimulus(stimulus)
        
        # 2. Interference evolution
        self.emotional_state = self.interference.apply_interference(
            self.emotional_state,
            time_step=0.1
        )
        
        # 3. Record
        self.predictor.record(self.emotional_state)
        
        # 4. Decision (if needed)
        response = None
        if stimulus.get('requires_response'):
            response = self.decider.decide(stimulus)
        
        # 5. Save state
        self.save_soul()
        
        return {
            'emotional_state': self.emotional_state.get_probabilities(),
            'dominant_emotion': self.emotional_state.dominant_emotion(),
            'entropy': self.emotional_state.entropy(),
            'response': response,
        }
    
    def _update_from_stimulus(self, stimulus: dict):
        """Update emotional state based on external stimulus"""
        # Example: map stimulus to emotional changes
        
        if stimulus.get('type') == 'praise':
            self.emotional_state.set_emotion('joy', 0.8, phase=0.0)
            self.emotional_state.set_emotion('trust', 0.6, phase=0.2)
        
        elif stimulus.get('type') == 'criticism':
            self.emotional_state.set_emotion('sadness', 0.5, phase=1.0)
            self.emotional_state.set_emotion('logic', 0.7, phase=0.0)
        
        elif stimulus.get('type') == 'threat':
            self.emotional_state.set_emotion('fear', 0.9, phase=0.5)
            self.emotional_state.set_emotion('anger', 0.4, phase=np.pi)
        
        # TODO: More sophisticated mapping in real system
    
    def predict_my_state(self, seconds_ahead: float = 60.0) -> QuantumEmotionalState:
        """Przewidź mój stan za N sekund"""
        steps = int(seconds_ahead / 10)  # Assuming 10s per step
        return self.predictor.predict_future(self.emotional_state, steps)
    
    def save_soul(self):
        """Persist state to .soul file"""
        state_data = {
            'timestamp': datetime.now().isoformat(),
            'emotional_state': {
                dim: {
                    'magnitude': abs(amp),
                    'phase': float(np.angle(amp))
                }
                for dim, amp in self.emotional_state.amplitudes.items()
            },
            'entropy': self.emotional_state.entropy(),
            'dominant': self.emotional_state.dominant_emotion()[0],
        }
        
        # Append to JSONL
        with open(self.soul_file, 'a') as f:
            f.write(json.dumps(state_data) + '\n')
    
    def load_soul(self):
        """Load last state from .soul file"""
        if not self.soul_file.exists():
            return
        
        # Read last line
        with open(self.soul_file, 'r') as f:
            lines = f.readlines()
        
        if not lines:
            return
        
        last_state = json.loads(lines[-1])
        
        # Restore emotional state
        for dim, data in last_state['emotional_state'].items():
            magnitude = data['magnitude']
            phase = data['phase']
            self.emotional_state.amplitudes[dim] = magnitude * np.exp(1j * phase)
        
        print(f"Loaded soul from {self.soul_file}")
        print(f"  Last emotion: {last_state['dominant']}")
        print(f"  Entropy: {last_state['entropy']:.2f}")


def demo():
    """Full system demo"""
    
    eriamo = EriAmoCore(soul_file="eriamo_demo.soul")
    
    # Scenario: series of events
    events = [
        {'type': 'praise', 'requires_response': True},
        {'type': 'criticism', 'requires_response': True},
        {'type': 'threat', 'requires_response': True},
    ]
    
    for i, event in enumerate(events):
        print(f"\n{'='*50}")
        print(f"Event {i+1}: {event['type']}")
        print('='*50)
        
        result = eriamo.process_stimulus(event)
        
        print(f"Emotional state: {result['dominant_emotion']}")
        print(f"Entropy: {result['entropy']:.2f} bits")
        
        if result['response']:
            print(f"Decision: {result['response']['action']} "
                  f"({result['response']['confidence']:.0%})")
        
        # Predict future
        future = eriamo.predict_my_state(seconds_ahead=30)
        print(f"Predicted (30s): {future.dominant_emotion()}")
    
    print(f"\n\nSoul saved to: {eriamo.soul_file}")

if __name__ == "__main__":
    demo()