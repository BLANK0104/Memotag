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
from src.data_processing.acoustic_analyzer import AcousticAnalyzer
from src.models.unsupervised_analyzer import UnsupervisedAnalyzer
from src.visualization.visualizer import Visualizer
from src.tracking.longitudinal_tracker import LongitudinalTracker

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
            "Complete this sentence: The quick brown fox jumps over the lazy dog",
            "What is today's date including the day of the week?",
            "Read this passage with emotion: 'All of us have moments in our lives that test our courage.'"
        ]
        
        # Initialize analyzers
        self.feature_extractor = FeatureExtractor()
        self.acoustic_analyzer = AcousticAnalyzer()
        self.tracker = LongitudinalTracker()  # Initialize the longitudinal tracker
        
        # Hesitation markers
        self.hesitation_markers = ['um', 'uh', 'er', 'ah', 'like', 'you know', 'hmm']
        
        # Current user for longitudinal tracking
        self.current_user_id = None
        self.last_audio_path = None
    
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
        
        # Save the last audio path for tracking
        self.last_audio_path = str(filename)
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
    
    # New methods for longitudinal tracking
    def set_user(self, user_id=None, name=None, age=None, gender=None, notes=None):
        """Set or create a user for longitudinal tracking"""
        if not user_id:
            # Generate a random user ID if none provided
            user_id = f"user_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Register the user in the database
        self.current_user_id = self.tracker.register_user(
            user_id=user_id,
            name=name,
            age=age,
            gender=gender,
            notes=notes
        )
        
        print(f"\nUser set: {user_id}" + (f" ({name})" if name else ""))
        return self.current_user_id
    
    def analyze_with_tracking(self, task_index=0):
        """Run analysis and store results in the longitudinal tracking system"""
        if not self.current_user_id:
            print("\nNo user set. Creating anonymous user for this session.")
            self.set_user()
        
        # Run regular analysis
        features, risk_score, transcript = self.run_analysis(task_index)
        
        if features and risk_score is not None:
            print("\nStoring assessment in longitudinal tracking system...")
            
            # Store the assessment data
            assessment_id = self.tracker.store_assessment(
                user_id=self.current_user_id,
                features=features,
                risk_score=risk_score,
                task_type=task_index,
                audio_path=self.last_audio_path,
                transcript=transcript
            )
            
            # Check for alerts from this assessment
            alerts = self.tracker.get_alerts(
                user_id=self.current_user_id,
                days=1,
                unreviewed_only=True
            )
            
            if not alerts.empty:
                print("\n" + "!"*50)
                print("ALERT: Significant changes detected from baseline:")
                print("!"*50)
                
                for _, alert in alerts.iterrows():
                    severity_text = "HIGH" if alert['severity'] == 3 else "MEDIUM" if alert['severity'] == 2 else "LOW"
                    feature_name = alert['feature_name'].replace('_', ' ').title()
                    change_direction = "increase" if alert['deviation_value'] > 0 else "decrease"
                    print(f"- {severity_text} severity: {feature_name} shows {abs(alert['deviation_value']):.2f} {change_direction} from baseline")
                
                print("\nThese changes may indicate cognitive function changes.")
                print("!"*50)
                
                # Mark alerts as reviewed
                for alert_id in alerts['alert_id']:
                    self.tracker.mark_alert_reviewed(alert_id)
            
            # Generate trend report if we have enough data
            history = self.tracker.get_user_history(self.current_user_id)
            assessments_count = len(history['timestamp'].unique())
            
            if assessments_count > 1:
                print(f"\nGenerating trend report (based on {assessments_count} assessments)...")
                report_path = self.tracker.generate_trend_report(self.current_user_id)
                if report_path:
                    print(f"Trend report saved to: {report_path}")
                    
                    # Show trend visualization
                    try:
                        img = plt.imread(report_path)
                        plt.figure(figsize=(12, 15))
                        plt.imshow(img)
                        plt.axis('off')
                        plt.title("Cognitive Function Trends Over Time")
                        plt.show()
                    except Exception as e:
                        print(f"Could not display trend report: {e}")
            
        return features, risk_score, transcript

    def analyze_features(self, transcript, audio_duration, audio_path=None):
        """Extract cognitive features from transcript and audio"""
        print("\nAnalyzing speech features...")
        
        # Extract linguistic features (from transcript)
        linguistic_features = self._analyze_linguistic_features(transcript, audio_duration)
        
        # Extract acoustic features if audio path is provided
        acoustic_features = {}
        acoustic_indicators = {}
        if audio_path:
            acoustic_features = self.acoustic_analyzer.extract_features(audio_path)
            acoustic_indicators = self.acoustic_analyzer.get_cognitive_indicators()
            
            # Generate acoustic visualizations
            viz_path = self.acoustic_analyzer.generate_visualizations(audio_path)
            print(f"Acoustic analysis visualizations saved to: {viz_path}")
        
        # Combine all features
        features = {**linguistic_features}
        
        # Add key acoustic indicators to the main features
        for key, value in acoustic_indicators.items():
            features[f'acoustic_{key}'] = value
            
        print(f"Extracted {len(features)} features ({len(linguistic_features)} linguistic, {len(acoustic_indicators)} acoustic indicators)")
        
        # Store full acoustic features separately (too many for regular display)
        self.acoustic_features = acoustic_features
            
        return features
    
    def _analyze_linguistic_features(self, transcript, audio_duration):
        """Extract linguistic features from transcript"""
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
        fig, axs = plt.subplots(3, 2, figsize=(15, 14))
        
        # Plot 1: Speech metrics
        metrics = ['transcript_length', 'speech_rate_wpm', 'counting_sequence_length']
        values = [features.get(metric, 0) for metric in metrics]
        axs[0, 0].bar(metrics, values, color='skyblue')
        axs[0, 0].set_title('Speech Production Metrics')
        axs[0, 0].set_ylabel('Value')
        axs[0, 0].tick_params(axis='x', rotation=45)
        
        # Plot 2: Hesitation and pause metrics
        metrics = ['hesitation_count', 'pause_count', 'word_finding_difficulty_count']
        values = [features.get(metric, 0) for metric in metrics]
        axs[0, 1].bar(metrics, values, color='salmon')
        axs[0, 1].set_title('Hesitation and Pause Metrics')
        axs[0, 1].set_ylabel('Count')
        axs[0, 1].tick_params(axis='x', rotation=45)
        
        # Plot 3: Ratio metrics
        metrics = ['hesitation_ratio', 'pause_rate']
        values = [features.get(metric, 0) for metric in metrics]
        axs[1, 0].bar(metrics, values, color='lightgreen')
        axs[1, 0].set_title('Ratio Metrics')
        axs[1, 0].set_ylabel('Ratio')
        
        # Plot 4: Task-specific metrics
        metrics = ['animal_count', 'counting_errors']
        values = [features.get(metric, 0) for metric in metrics]
        axs[1, 1].bar(metrics, values, color='purple')
        axs[1, 1].set_title('Task-specific Metrics')
        axs[1, 1].set_ylabel('Count')
        
        # Plot 5: Acoustic indicators
        acoustic_metrics = [k for k in features.keys() if k.startswith('acoustic_')]
        if acoustic_metrics:
            values = [features.get(metric, 0) for metric in acoustic_metrics]
            labels = [m.replace('acoustic_', '') for m in acoustic_metrics]
            axs[2, 0].bar(labels, values, color='orange')
            axs[2, 0].set_title('Acoustic Indicators')
            axs[2, 0].set_ylabel('Score')
            axs[2, 0].tick_params(axis='x', rotation=45)
            
            # Plot 6: Overall risk score
            if 'risk_score' in features:
                axs[2, 1].bar(['Risk Score'], [features['risk_score']], 
                            color='red' if features['risk_score'] > 0.6 else 
                                 'orange' if features['risk_score'] > 0.3 else 'green')
                axs[2, 1].set_title('Cognitive Risk Assessment')
                axs[2, 1].set_ylabel('Risk Score')
                axs[2, 1].set_ylim(0, 1)
                
                # Add threshold lines
                axs[2, 1].axhline(y=0.3, color='green', linestyle='--', alpha=0.7)
                axs[2, 1].axhline(y=0.6, color='red', linestyle='--', alpha=0.7)
        else:
            fig.delaxes(axs[2, 0])
            fig.delaxes(axs[2, 1])
        
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
            'hesitation_ratio': 0.10,
            'pause_rate': 0.08,
            'speech_rate_wpm': -0.10,  # Lower speed may indicate issues (negative correlation)
            'word_finding_difficulty_count': 0.15,
            'counting_sequence_length': -0.08,  # Longer counting sequence is good
            'counting_errors': 0.15,
            'animal_count': -0.08,  # More animals named is good
            
            # Acoustic features (if available)
            'acoustic_vocal_stability': -0.07,  # Higher stability is good
            'acoustic_articulation_precision': -0.07,  # Higher precision is good
            'acoustic_rhythm_regularity': -0.07,  # Higher regularity is good
            'acoustic_voice_quality': -0.05,  # Higher quality is good
            'acoustic_energy_variability': -0.05   # Lower variability is good (higher score is better)
        }
        
        # Normalize feature values (simplified approach)
        normalized = {}
        
        # Speech rate normalization (typically 120-160 WPM is normal)
        speech_rate = features.get('speech_rate_wpm', 0)
        if speech_rate < 100:
            normalized['speech_rate_wpm'] = 0.8  # Very slow speech
        elif speech_rate < 120:
            normalized['speech_rate_wpm'] = 0.6  # Slow speech
        elif speech_rate <= 160:
            normalized['speech_rate_wpm'] = 0.2  # Normal speech
        else:
            normalized['speech_rate_wpm'] = 0.4  # Fast speech can also indicate issues
        
        # Hesitation ratio normalization (0-0.15 is normal)
        hesitation_ratio = features.get('hesitation_ratio', 0)
        normalized['hesitation_ratio'] = min(1.0, hesitation_ratio * 5)
        
        # Pause rate normalization
        pause_rate = features.get('pause_rate', 0)
        normalized['pause_rate'] = min(1.0, pause_rate * 2)
        
        # Word finding difficulty normalization
        word_finding = features.get('word_finding_difficulty_count', 0)
        transcript_length = max(1, features.get('transcript_length', 1))
        normalized['word_finding_difficulty_count'] = min(1.0, word_finding * 10 / transcript_length)
        
        # Counting sequence normalization (task specific)
        count_length = features.get('counting_sequence_length', 0)
        if count_length > 25:
            normalized['counting_sequence_length'] = 0.1  # Very good counting
        elif count_length > 15:
            normalized['counting_sequence_length'] = 0.3  # Good counting
        elif count_length > 10:
            normalized['counting_sequence_length'] = 0.5  # Average counting
        else:
            normalized['counting_sequence_length'] = 0.8  # Poor counting
        
        # Counting errors normalization
        counting_errors = features.get('counting_errors', 0)
        count_length = max(1, features.get('counting_sequence_length', 1))
        normalized['counting_errors'] = min(1.0, counting_errors * 3 / count_length)
        
        # Animal count normalization (task specific - typically >15 in 60s is good)
        animal_count = features.get('animal_count', 0)
        if animal_count > 15:
            normalized['animal_count'] = 0.1  # Excellent performance
        elif animal_count > 10:
            normalized['animal_count'] = 0.3  # Good performance
        elif animal_count > 5:
            normalized['animal_count'] = 0.5  # Average performance
        else:
            normalized['animal_count'] = 0.8  # Poor performance
        
        # Include acoustic features if available
        for feature in ['acoustic_vocal_stability', 'acoustic_articulation_precision', 
                       'acoustic_rhythm_regularity', 'acoustic_voice_quality', 'acoustic_energy_variability']:
            if feature in features:
                # These are already normalized from the acoustic analyzer
                normalized[feature] = features[feature]
        
        # Calculate weighted risk score
        risk_score = 0
        feature_count = 0
        
        for feature, weight in weights.items():
            if feature in normalized:
                risk_score += normalized[feature] * abs(weight) * (1 if weight > 0 else -1)
                feature_count += 1
        
        # Adjust for number of features available
        if feature_count > 0:
            risk_score = risk_score * (len(weights) / feature_count)
        
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
        
        # Extract features (now including acoustic analysis)
        features = self.analyze_features(transcript, audio_duration, audio_path)
        
        # Calculate risk score
        risk_score = self.calculate_cognitive_risk_score(features)
        features['risk_score'] = risk_score
        
        # Display results
        print("\nSpeech Analysis Results:")
        print("="*50)
        print("\nLinguistic Features:")
        for feature, value in features.items():
            if not feature.startswith('acoustic_') and feature != 'risk_score':
                print(f"{feature.replace('_', ' ').title()}: {value:.2f}" 
                    if isinstance(value, float) else f"{feature.replace('_', ' ').title()}: {value}")
        
        if any(k.startswith('acoustic_') for k in features.keys()):
            print("\nAcoustic Indicators:")
            for feature, value in features.items():
                if feature.startswith('acoustic_'):
                    print(f"{feature.replace('acoustic_', '').replace('_', ' ').title()}: {value:.2f}")
        
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
    print("\nLongitudinal tracking is available to monitor changes over time.")
    
    analyzer = VoiceAnalyzer()
    
    # Ask about longitudinal tracking
    track_response = input("\nWould you like to enable longitudinal tracking? (y/n): ").strip().lower()
    use_tracking = track_response.startswith('y')
    
    if use_tracking:
        print("\nPlease provide user information for tracking:")
        user_id = input("User ID (or press Enter for auto-generated ID): ").strip()
        name = input("Name (optional): ").strip()
        age_input = input("Age (optional): ").strip()
        gender = input("Gender (optional): ").strip()
        notes = input("Notes (optional): ").strip()
        
        try:
            age = int(age_input) if age_input else None
        except ValueError:
            age = None
            print("Invalid age format. Age will be left blank.")
        
        analyzer.set_user(user_id, name, age, gender, notes)
    
    # Show available tasks
    print("\nAvailable Tasks:")
    for i, task in enumerate(analyzer.tasks):
        print(f"{i+1}. {task}")
    
    try:
        task_num = int(input("\nSelect a task number (1-6): ")) - 1
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
    
    # Run the analysis with tracking if enabled
    if use_tracking:
        analyzer.analyze_with_tracking(task_num)
    else:
        analyzer.run_analysis(task_num)
    
    # If tracking was used, provide option to view historical data
    if use_tracking and analyzer.current_user_id:
        view_history = input("\nWould you like to view historical trends? (y/n): ").strip().lower()
        if view_history.startswith('y'):
            report_path = analyzer.tracker.generate_trend_report(analyzer.current_user_id)
            if report_path:
                print(f"Trend report generated at: {report_path}")
                try:
                    img = plt.imread(report_path)
                    plt.figure(figsize=(12, 15))
                    plt.imshow(img)
                    plt.axis('off')
                    plt.title("Cognitive Function Trends Over Time")
                    plt.show()
                except Exception as e:
                    print(f"Could not display trend report: {e}")
            else:
                print("Not enough historical data available for trend analysis.")

if __name__ == "__main__":
    main()
