import os
import random
import json
import numpy as np
from pathlib import Path
import sys
import nltk

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parents[2]))
from config import AUDIO_SAMPLES_DIR, IMPAIRMENT_LEVELS

# Download required NLTK data
nltk.download('punkt')
nltk.download('brown')
nltk.download('wordnet')

class SimulatedDataGenerator:
    """Generate simulated audio transcripts with cognitive impairment markers"""
    
    def __init__(self):
        self.prompts = [
            "Please describe what you did yesterday from morning till evening.",
            "Can you name as many animals as you can in 30 seconds?",
            "What's your favorite holiday memory from your childhood?",
            "Please count backward from 100 by 7.",
            "Can you explain how to make a sandwich?",
        ]
        
        # Load word corpus
        self.words = nltk.corpus.brown.words()[:5000]
        
    def _generate_hesitations(self, level):
        """Generate hesitation markers based on impairment level"""
        hesitation_counts = {
            'none': (0, 1),
            'mild': (1, 3),
            'moderate': (3, 6),
            'severe': (5, 10)
        }
        count_range = hesitation_counts[level]
        count = random.randint(*count_range)
        
        hesitations = []
        for _ in range(count):
            marker = random.choice(['um', 'uh', 'er', 'hmm', 'ah'])
            hesitations.append(marker)
        
        return hesitations
    
    def _generate_pauses(self, level, text_length):
        """Generate pauses based on impairment level"""
        pause_counts = {
            'none': (1, 3),
            'mild': (3, 6),
            'moderate': (6, 10),
            'severe': (10, 15)
        }
        count_range = pause_counts[level]
        count = random.randint(*count_range)
        
        # Generate pause positions
        positions = sorted(random.sample(range(1, text_length), min(count, text_length-1)))
        return positions
    
    def _word_substitution(self, text, level):
        """Simulate word recall issues by substituting words"""
        substitution_rates = {
            'none': 0.00,
            'mild': 0.05,
            'moderate': 0.10,
            'severe': 0.20
        }
        
        words = text.split()
        for i in range(len(words)):
            if random.random() < substitution_rates[level]:
                if random.random() < 0.3:  # 30% chance for semantically related word
                    words[i] = random.choice(self.words)  # Simple substitution for now
                else:
                    # Word finding difficulty (e.g., "the thing")
                    words[i] = random.choice(["thing", "that thing", "what's it called", "you know"])
                    
        return ' '.join(words)
    
    def _alter_speech_rate(self, level):
        """Generate speech rate metadata based on impairment level"""
        # Words per minute ranges
        wpm_ranges = {
            'none': (130, 160),
            'mild': (110, 140),
            'moderate': (90, 120),
            'severe': (70, 100)
        }
        return random.uniform(*wpm_ranges[level])
    
    def _generate_transcript(self, level):
        """Generate a simulated transcript with characteristics of the given impairment level"""
        prompt = random.choice(self.prompts)
        
        # Base responses for different prompts
        base_responses = {
            "Please describe what you did yesterday from morning till evening.": 
                "I woke up around seven and had breakfast. Then I went for a walk in the park. "
                "For lunch I had a sandwich. In the afternoon I read a book and watched TV. "
                "I had dinner with my family and went to bed early.",
                
            "Can you name as many animals as you can in 30 seconds?":
                "Dog cat horse cow sheep pig chicken duck goose elephant lion tiger bear wolf "
                "fox deer rabbit squirrel mouse rat zebra giraffe monkey gorilla",
                
            "What's your favorite holiday memory from your childhood?":
                "My favorite holiday memory is when we went to the beach house for Christmas. "
                "We opened presents in the morning and then spent the day swimming and building "
                "sandcastles. My grandmother made her special cookies and we watched the sunset.",
                
            "Please count backward from 100 by 7.":
                "100, 93, 86, 79, 72, 65, 58, 51, 44, 37, 30, 23, 16, 9, 2",
                
            "Can you explain how to make a sandwich?":
                "First you take two slices of bread. Then you spread butter or mayonnaise. "
                "Add some cheese and ham or whatever filling you like. "
                "You can add lettuce and tomatoes too. Then put the second slice on top."
        }
        
        response = base_responses[prompt]
        
        # Apply cognitive impairment characteristics
        
        # 1. Word recall and substitution issues
        response = self._word_substitution(response, level)
        
        # 2. Insert hesitations
        hesitations = self._generate_hesitations(level)
        words = response.split()
        for hesitation in hesitations:
            position = random.randint(0, len(words))
            words.insert(position, hesitation)
        response = ' '.join(words)
        
        # 3. Calculate pause positions
        pause_positions = self._generate_pauses(level, len(words))
        
        # 4. Speech rate
        speech_rate = self._alter_speech_rate(level)
        
        # Create metadata
        metadata = {
            "prompt": prompt,
            "impairment_level": level,
            "speech_rate_wpm": speech_rate,
            "hesitation_count": len(hesitations),
            "pause_positions": pause_positions,
            "pause_count": len(pause_positions)
        }
        
        return response, metadata
    
    def generate_samples(self, num_samples=10, output_dir=None):
        """Generate simulated transcript samples"""
        if output_dir is None:
            output_dir = AUDIO_SAMPLES_DIR
        
        os.makedirs(output_dir, exist_ok=True)
        samples = []
        
        for i in range(num_samples):
            # Choose impairment level with weighting toward milder cases
            weights = [0.4, 0.3, 0.2, 0.1]  # none, mild, moderate, severe
            level = random.choices(IMPAIRMENT_LEVELS, weights=weights, k=1)[0]
            
            transcript, metadata = self._generate_transcript(level)
            
            sample_id = f"sample_{i+1:02d}"
            metadata["sample_id"] = sample_id
            
            # Save transcript and metadata
            sample_data = {
                "transcript": transcript,
                "metadata": metadata
            }
            
            samples.append(sample_data)
            
            # Save individual sample
            with open(os.path.join(output_dir, f"{sample_id}.json"), 'w') as f:
                json.dump(sample_data, f, indent=2)
        
        # Save all samples to a single file
        with open(os.path.join(output_dir, "all_samples.json"), 'w') as f:
            json.dump(samples, f, indent=2)
            
        return samples

if __name__ == "__main__":
    generator = SimulatedDataGenerator()
    samples = generator.generate_samples()
    print(f"Generated {len(samples)} simulated transcript samples")
