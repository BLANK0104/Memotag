import re
import numpy as np
import pandas as pd
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parents[2]))
from config import HESITATION_MARKERS

class FeatureExtractor:
    """Extract linguistic and cognitive features from transcripts"""
    
    def __init__(self):
        self.hesitation_markers = HESITATION_MARKERS
        self.hesitation_pattern = re.compile(r'\b(' + '|'.join(self.hesitation_markers) + r')\b', re.IGNORECASE)
        
    def extract_hesitations(self, text):
        """Extract hesitation markers from text"""
        matches = self.hesitation_pattern.findall(text.lower())
        return matches
    
    def count_hesitations(self, text):
        """Count hesitation markers in text"""
        return len(self.extract_hesitations(text))
    
    def hesitation_ratio(self, text):
        """Calculate the ratio of hesitation markers to total words"""
        total_words = len(text.split())
        if total_words == 0:
            return 0
        return self.count_hesitations(text) / total_words
    
    def extract_pauses(self, metadata):
        """Extract pause information from metadata"""
        return metadata.get('pause_positions', []), metadata.get('pause_count', 0)
    
    def pause_rate(self, metadata, text):
        """Calculate pauses per 100 words"""
        _, pause_count = self.extract_pauses(metadata)
        word_count = len(text.split())
        if word_count == 0:
            return 0
        return (pause_count / word_count) * 100
    
    def word_finding_difficulties(self, text):
        """Detect potential word finding difficulties"""
        indicators = ["thing", "that thing", "what's it called", "you know", "whatchamacallit"]
        pattern = re.compile(r'\b(' + '|'.join(indicators) + r')\b', re.IGNORECASE)
        matches = pattern.findall(text.lower())
        return matches, len(matches)
    
    def task_specific_features(self, text, prompt):
        """Extract task-specific features based on the prompt type"""
        features = {}
        
        # Animal naming task features
        if "name as many animals" in prompt.lower():
            animal_count = len(text.split())
            # Typical animals named in semantic clusters
            features["animal_count"] = animal_count
        
        # Counting task features
        elif "count backward" in prompt.lower():
            # Extract numbers and check for errors
            numbers = [int(n.strip(',. ')) for n in re.findall(r'\b\d+\b', text)]
            if len(numbers) >= 2:
                diffs = [numbers[i] - numbers[i+1] for i in range(len(numbers)-1)]
                features["counting_errors"] = sum(1 for diff in diffs if diff != 7)
                features["counting_sequence_length"] = len(numbers)
            else:
                features["counting_errors"] = 0
                features["counting_sequence_length"] = 0
        
        return features
    
    def extract_features(self, sample):
        """Extract all features from a sample"""
        transcript = sample["transcript"]
        metadata = sample["metadata"]
        
        features = {
            "sample_id": metadata["sample_id"],
            "impairment_level": metadata["impairment_level"],  # Ground truth
            "speech_rate_wpm": metadata["speech_rate_wpm"],
            "hesitation_count": self.count_hesitations(transcript),
            "hesitation_ratio": self.hesitation_ratio(transcript),
            "pause_count": metadata.get("pause_count", 0),
            "pause_rate": self.pause_rate(metadata, transcript),
            "transcript_length": len(transcript.split()),
        }
        
        # Word finding difficulties
        _, word_finding_count = self.word_finding_difficulties(transcript)
        features["word_finding_difficulty_count"] = word_finding_count
        
        # Task-specific features
        task_features = self.task_specific_features(transcript, metadata["prompt"])
        features.update(task_features)
        
        return features
    
    def process_samples(self, samples):
        """Process multiple samples and return features dataframe"""
        all_features = []
        
        for sample in samples:
            features = self.extract_features(sample)
            all_features.append(features)
            
        return pd.DataFrame(all_features)
