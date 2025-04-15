import os
import sys
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import pyaudio
import wave
import speech_recognition as sr
from datetime import datetime
import nltk
import re
from nltk.tokenize import word_tokenize, sent_tokenize

# Download required NLTK data if not already present
nltk.download('punkt', quiet=True)
nltk.download('wordnet', quiet=True)

# Add project root to path to access existing modules
sys.path.append(str(Path(__file__).resolve().parent))

# Import project modules
from src.data_processing.feature_extractor import FeatureExtractor
from src.models.unsupervised_analyzer import UnsupervisedAnalyzer
from src.visualization.visualizer import Visualizer

class VoiceAnalyzer:
    """Records and analyzes speech in real time for cognitive markers"""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.audio_format = pyaudio.paInt16
        self.channels = 1
        self.sample_rate = 44100
        self.chunk_size = 1024
        self.record_seconds = 60  # Default recording time
        self.output_dir = Path('data/audio_samples')
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
        # Define cognitive tasks
        self.tasks = [
            "Count backwards from 100 to 70",
            "Name as many animals as you can think of in 30 seconds",
            "Describe what you did yesterday in detail",
            "Complete this sentence: The quick brown fox jumps over the...",
            "What is today's date including the day of the week?"
        ]
        
        # Initialize feature extractor
        self.feature_extractor = FeatureExtractor()
        
        # Hesitation markers
        self.hesitation_markers = ['um', 'uh', 'er', 'ah', 'like', 'you know', 'hmm']
        
    def record_audio(self, task_index=0, filename=None):
        """Record audio from microphone"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = self.output_dir / f"task_{task_index+1}_{timestamp}.wav"
        
        # Display task instructions
        print("\n" + "="*50)
        print(f"TASK {task_index+1}: {self.tasks[task_index]}")
        print("="*50)
        print("Recording will start in 3 seconds...")
        
        for i in range(3, 0, -1):
            print(f"{i}...")
            time.sleep(1)
        
        print("Recording... (speak clearly)")
        
        # Initialize PyAudio
        audio = pyaudio.PyAudio()
        
        # Open stream
        stream = audio.open(
            format=self.audio_format,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size
        )
        
        frames = []
        start_time = time.time()
        
        # Record audio
        for _ in range(0, int(self.sample_rate / self.chunk_size * self.record_seconds)):
            try:
                data = stream.read(self.chunk_size)
                frames.append(data)
                
                # Show recording progress
                elapsed = time.time() - start_time
                if elapsed > self.record_seconds:
                    break
                    
                # Update progress bar every second
                if len(frames) % int(self.sample_rate / self.chunk_size) == 0:
                    progress = int(elapsed) + 1
                    remaining = max(0, self.record_seconds - progress)
                    progress_bar = "▓" * progress + "░" * remaining
                    print(f"\r{progress_bar} {progress}/{self.record_seconds}s", end="")
                    
            except KeyboardInterrupt:
                print("\nRecording stopped by user")
                break
        
        print("\nRecording complete!")
        
        # Stop and close the stream
        stream.stop_stream()
        stream.close()
        audio.terminate()
        
        # Save the audio file
        wf = wave.open(str(filename), 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(audio.get_sample_size(self.audio_format))
        wf.setframerate(self.sample_rate)
        wf.writeframes(b''.join(frames))
        wf.close()
        
        print(f"Audio saved to: {filename}")
        return str(filename)
        
    def transcribe_audio(self, audio_path):
        """Convert audio to text using speech recognition"""
        print("Transcribing audio...")
        
        with sr.AudioFile(audio_path) as source:
            audio_data = self.recognizer.record(source)
            
            try:
                # Use Google's speech recognition (requires internet)
                transcript = self.recognizer.recognize_google(audio_data)
                print("Transcript: " + transcript)
                return transcript
            except sr.UnknownValueError:
                print("Speech recognition could not understand audio")
                return ""
            except sr.RequestError as e:
                print(f"Could not request results from speech recognition service; {e}")
                return ""
    
    def analyze_features(self, transcript, audio_duration):
        """Extract cognitive features from transcript"""
        print("\nAnalyzing speech features...")
        
        # Basic transcript metrics
        word_tokens = word_tokenize(transcript.lower())
        sentence_tokens = sent_tokenize(transcript)
        
        # 1. Count transcript length
        transcript_length = len(word_tokens)
        
        # 2. Count hesitations
        hesitation_count = sum(word.lower() in self.hesitation_markers for word in word_tokens)
        
        # 3. Calculate hesitation ratio
        hesitation_ratio = hesitation_count / transcript_length if transcript_length > 0 else 0
        
        # 4. Detect pauses (simplistic approach - based on punctuation)
        pause_count = transcript.count(',') + transcript.count('...') + transcript.count('.')
        
        # 5. Calculate pause rate
        pause_rate = pause_count / len(sentence_tokens) if len(sentence_tokens) > 0 else 0
        
        # 6. Speech rate in words per minute
        speech_rate_wpm = (transcript_length / audio_duration) * 60
        
        # 7. Find counting sequence (for counting backward task)
        counting_pattern = re.findall(r'\b\d+\b', transcript)
        counting_sequence_length = len(counting_pattern)
        
        # 8. Check for counting errors
        counting_errors = 0
        if counting_sequence_length >= 2:
            for i in range(len(counting_pattern) - 1):
                try:
                    # For counting backwards, check if current > next and the difference is 1
                    current = int(counting_pattern[i])
                    next_num = int(counting_pattern[i + 1])
                    if not (current > next_num and current - next_num == 1):
                        counting_errors += 1
                except ValueError:
                    continue
        
        # 9. Count animal names (for animal naming task)
        animal_list = ['dog', 'cat', 'bird', 'fish', 'cow', 'horse', 'sheep', 'goat', 
                       'pig', 'chicken', 'duck', 'rabbit', 'mouse', 'rat', 'tiger', 
                       'lion', 'elephant', 'bear', 'wolf', 'fox', 'deer', 'monkey', 
                       'frog', 'snake', 'turtle', 'dolphin', 'whale', 'shark', 'octopus']
        
        animal_count = sum(animal in word_tokens for animal in animal_list)
        
        # 10. Word finding difficulty (simplistic detection based on pauses and hesitations)
        # This is just an estimate - in reality would need more complex analysis
        word_finding_difficulty_count = hesitation_count + transcript.count('...') * 2
        
        # Compile features into a dictionary
        features = {
            'transcript_length': transcript_length,
            'hesitation_count': hesitation_count,
            'hesitation_ratio': hesitation_ratio,
            'pause_count': pause_count,
            'pause_rate': pause_rate,
            'speech_rate_wpm': speech_rate_wpm,
            'counting_sequence_length': counting_sequence_length,
            'counting_errors': counting_errors,
            'animal_count': animal_count,
            'word_finding_difficulty_count': word_finding_difficulty_count
        }
        
        return features
    
    def visualize_results(self, features):
        """Visualize the analyzed speech features"""
        # Create a figure with subplots
        fig, axs = plt.subplots(2, 2, figsize=(12, 10))
        
        # Plot 1: Speech metrics
        metrics = ['transcript_length', 'speech_rate_wpm', 'counting_sequence_length']
        values = [features[metric] for metric in metrics]
        axs[0, 0].bar(metrics, values, color='skyblue')
        axs[0, 0].set_title('Speech Production Metrics')
        axs[0, 0].set_ylabel('Value')
        axs[0, 0].tick_params(axis='x', rotation=45)
        
        # Plot 2: Hesitation and pause metrics
        metrics = ['hesitation_count', 'pause_count', 'word_finding_difficulty_count']
        values = [features[metric] for metric in metrics]
        axs[0, 1].bar(metrics, values, color='salmon')
        axs[0, 1].set_title('Hesitation and Pause Metrics')
        axs[0, 1].set_ylabel('Count')
        axs[0, 1].tick_params(axis='x', rotation=45)
        
        # Plot 3: Ratio metrics
        metrics = ['hesitation_ratio', 'pause_rate']
        values = [features[metric] for metric in metrics]
        axs[1, 0].bar(metrics, values, color='lightgreen')
        axs[1, 0].set_title('Ratio Metrics')
        axs[1, 0].set_ylabel('Ratio')
        
        # Plot 4: Task-specific metrics
        metrics = ['animal_count', 'counting_errors']
        values = [features[metric] for metric in metrics]
        axs[1, 1].bar(metrics, values, color='purple')
        axs[1, 1].set_title('Task-specific Metrics')
        axs[1, 1].set_ylabel('Count')
        
        plt.tight_layout()
        
        # Save and show plot
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        plt.savefig(f"speech_analysis_{timestamp}.png")
        plt.show()
    
    def calculate_cognitive_risk_score(self, features):
        """Calculate an estimated cognitive risk score based on features
        This is a simple heuristic for demonstration purposes"""
        # Define weights for each feature (would be determined by clinical research)
        weights = {
            'hesitation_ratio': 0.15,
            'pause_rate': 0.1,
            'speech_rate_wpm': -0.15,  # Lower speed may indicate issues (negative correlation)
            'word_finding_difficulty_count': 0.2,
            'counting_sequence_length': -0.1,  # Longer counting sequence is good
            'counting_errors': 0.2,
            'animal_count': -0.1  # More animals named is good
        }
        
        # Normalize feature values (simplified approach)
        normalized = {}
        
        # Speech rate normalization (typically 120-160 WPM is normal)
        speech_rate = features['speech_rate_wpm']
        if speech_rate < 100:
            normalized['speech_rate_wpm'] = 0.8  # Very slow speech
        elif speech_rate < 120:
            normalized['speech_rate_wpm'] = 0.6  # Slow speech
        elif speech_rate <= 160:
            normalized['speech_rate_wpm'] = 0.2  # Normal speech
        else:
            normalized['speech_rate_wpm'] = 0.4  # Fast speech can also indicate issues
        
        # Hesitation ratio normalization (0-0.15 is normal)
        hesitation_ratio = features['hesitation_ratio']
        normalized['hesitation_ratio'] = min(1.0, hesitation_ratio * 5)
        
        # Pause rate normalization
        pause_rate = features['pause_rate']
        normalized['pause_rate'] = min(1.0, pause_rate * 2)
        
        # Word finding difficulty normalization
        word_finding = features['word_finding_difficulty_count'] / max(1, features['transcript_length'])
        normalized['word_finding_difficulty_count'] = min(1.0, word_finding * 10)
        
        # Counting sequence normalization (task specific)
        count_length = features['counting_sequence_length']
        if count_length > 25:
            normalized['counting_sequence_length'] = 0.1  # Very good counting
        elif count_length > 15:
            normalized['counting_sequence_length'] = 0.3  # Good counting
        elif count_length > 10:
            normalized['counting_sequence_length'] = 0.5  # Average counting
        else:
            normalized['counting_sequence_length'] = 0.8  # Poor counting
        
        # Counting errors normalization
        error_ratio = features['counting_errors'] / max(1, features['counting_sequence_length'])
        normalized['counting_errors'] = min(1.0, error_ratio * 3)
        
        # Animal count normalization (task specific - typically >15 in 60s is good)
        animal_count = features['animal_count']
        if animal_count > 15:
            normalized['animal_count'] = 0.1  # Excellent performance
        elif animal_count > 10:
            normalized['animal_count'] = 0.3  # Good performance
        elif animal_count > 5:
            normalized['animal_count'] = 0.5  # Average performance
        else:
            normalized['animal_count'] = 0.8  # Poor performance
        
        # Calculate weighted risk score
        risk_score = 0
        for feature, weight in weights.items():
            if feature in normalized:
                risk_score += normalized[feature] * abs(weight) * (1 if weight > 0 else -1)
        
        # Normalize final score between 0 and 1
        risk_score = max(0, min(1, (risk_score + 0.5) / 2))
        
        return risk_score
    
    def run_analysis(self, task_index=0):
        """Run a complete analysis cycle for a task"""
        # Record audio
        audio_path = self.record_audio(task_index)
        
        # Get audio duration
        with wave.open(audio_path, 'rb') as wf:
            audio_duration = wf.getnframes() / float(wf.getframerate())
        
        # Transcribe audio
        transcript = self.transcribe_audio(audio_path)
        if not transcript:
            print("No transcript available for analysis.")
            return
        
        # Extract features
        features = self.analyze_features(transcript, audio_duration)
        
        # Calculate risk score
        risk_score = self.calculate_cognitive_risk_score(features)
        
        # Display results
        print("\nSpeech Analysis Results:")
        print("="*50)
        for feature, value in features.items():
            print(f"{feature.replace('_', ' ').title()}: {value:.2f}" 
                  if isinstance(value, float) else f"{feature.replace('_', ' ').title()}: {value}")
        
        print("\nCognitive Risk Assessment:")
        print("="*50)
        print(f"Risk Score: {risk_score:.2f}")
        
        if risk_score < 0.3:
            print("Risk Level: Low - No significant cognitive concerns detected")
        elif risk_score < 0.6:
            print("Risk Level: Moderate - Some speech patterns may warrant further assessment")
        else:
            print("Risk Level: High - Consider professional cognitive assessment")
        
        # Visualize the results
        self.visualize_results(features)
        
        return features, risk_score, transcript

def main():
    """Main function to run the voice analyzer"""
    print("MemoTag Voice Analysis Tool")
    print("="*50)
    print("This tool will record your voice and analyze speech patterns")
    print("that might indicate cognitive function.")
    
    analyzer = VoiceAnalyzer()
    
    # Show available tasks
    print("\nAvailable Tasks:")
    for i, task in enumerate(analyzer.tasks):
        print(f"{i+1}. {task}")
    
    try:
        task_num = int(input("\nSelect a task number (1-5): ")) - 1
        if task_num < 0 or task_num >= len(analyzer.tasks):
            print("Invalid selection. Using task 1.")
            task_num = 0
    except ValueError:
        print("Invalid input. Using task 1.")
        task_num = 0
    
    try:
        record_time = int(input("Recording time in seconds (default: 60): "))
        analyzer.record_seconds = record_time
    except ValueError:
        print("Using default recording time of 60 seconds.")
    
    # Run the analysis
    analyzer.run_analysis(task_num)

if __name__ == "__main__":
    main()
