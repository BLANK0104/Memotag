import os
import numpy as np
import librosa
import librosa.display
import matplotlib.pyplot as plt
from pathlib import Path
import pandas as pd
import warnings

# Suppress warnings from librosa
warnings.filterwarnings('ignore')

class AcousticAnalyzer:
    """Extracts acoustic features from voice recordings"""
    
    def __init__(self):
        """Initialize the acoustic analyzer"""
        self.features = {}
        
    def load_audio(self, audio_path):
        """Load audio file and convert to mono"""
        try:
            # Load audio file with librosa (automatically resamples)
            y, sr = librosa.load(audio_path, sr=None, mono=True)
            return y, sr
        except Exception as e:
            print(f"Error loading audio file: {e}")
            return None, None
    
    def extract_features(self, audio_path):
        """Extract comprehensive acoustic features from audio file"""
        print("Extracting acoustic features...")
        
        # Load audio
        y, sr = self.load_audio(audio_path)
        if y is None:
            return {}
        
        # Dictionary to store features
        features = {}
        
        # Basic audio properties
        features['duration'] = librosa.get_duration(y=y, sr=sr)
        
        # 1. Pitch/Fundamental Frequency features
        try:
            # Extract pitch
            pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
            
            # Get pitches with highest magnitude
            pitches_filtered = []
            for i in range(magnitudes.shape[1]):
                index = magnitudes[:, i].argmax()
                pitch = pitches[index, i]
                if pitch > 0:  # Filter out zero pitches
                    pitches_filtered.append(pitch)
            
            if pitches_filtered:
                features['pitch_mean'] = np.mean(pitches_filtered)
                features['pitch_std'] = np.std(pitches_filtered)
                features['pitch_range'] = np.max(pitches_filtered) - np.min(pitches_filtered)
                
                # Pitch variability
                if len(pitches_filtered) > 1:
                    pitch_changes = np.diff(pitches_filtered)
                    features['pitch_variability'] = np.std(pitch_changes)
                else:
                    features['pitch_variability'] = 0
            else:
                features['pitch_mean'] = 0
                features['pitch_std'] = 0
                features['pitch_range'] = 0
                features['pitch_variability'] = 0
        except:
            features['pitch_mean'] = 0
            features['pitch_std'] = 0
            features['pitch_range'] = 0
            features['pitch_variability'] = 0
        
        # 2. Voice tremor analysis
        try:
            # Amplitude envelope
            amplitude_envelope = librosa.onset.onset_strength(y=y, sr=sr)
            # Measure tremor as variability in amplitude envelope
            if len(amplitude_envelope) > 0:
                features['tremor_index'] = np.std(amplitude_envelope) / np.mean(amplitude_envelope)
            else:
                features['tremor_index'] = 0
        except:
            features['tremor_index'] = 0
        
        # 3. Spectral features
        try:
            # Spectral centroid
            cent = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            features['spectral_centroid_mean'] = np.mean(cent)
            features['spectral_centroid_std'] = np.std(cent)
            
            # Spectral bandwidth
            spec_bw = librosa.feature.spectral_bandwidth(y=y, sr=sr)[0]
            features['spectral_bandwidth_mean'] = np.mean(spec_bw)
            
            # Spectral contrast
            contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
            features['spectral_contrast_mean'] = np.mean(contrast)
            
            # Spectral flatness
            flatness = librosa.feature.spectral_flatness(y=y)[0]
            features['spectral_flatness_mean'] = np.mean(flatness)
            
            # Spectral rolloff
            rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
            features['rolloff_mean'] = np.mean(rolloff)
        except:
            features['spectral_centroid_mean'] = 0
            features['spectral_centroid_std'] = 0
            features['spectral_bandwidth_mean'] = 0
            features['spectral_contrast_mean'] = 0
            features['spectral_flatness_mean'] = 0
            features['rolloff_mean'] = 0
        
        # 4. MFCCs (Mel-frequency cepstral coefficients)
        try:
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            for i in range(13):
                features[f'mfcc{i+1}_mean'] = np.mean(mfccs[i])
                features[f'mfcc{i+1}_std'] = np.std(mfccs[i])
        except:
            for i in range(13):
                features[f'mfcc{i+1}_mean'] = 0
                features[f'mfcc{i+1}_std'] = 0
        
        # 5. Speech rhythm features
        try:
            # Tempo estimation
            onset_env = librosa.onset.onset_strength(y=y, sr=sr)
            tempo = librosa.beat.tempo(onset_envelope=onset_env, sr=sr)[0]
            features['tempo'] = tempo
            
            # Rhythm regularity
            # Use autocorrelation of onset strength
            ac = librosa.autocorrelate(onset_env, max_size=len(onset_env))
            # Normalize
            ac = librosa.util.normalize(ac, norm=np.inf)
            # Take second peak (first is at lag 0)
            peaks = librosa.util.peak_pick(ac, pre_max=10, post_max=10, pre_avg=10, post_avg=10, delta=0.5, wait=1)
            if len(peaks) > 0:
                features['rhythm_strength'] = ac[peaks[0]]
            else:
                features['rhythm_strength'] = 0
        except:
            features['tempo'] = 0
            features['rhythm_strength'] = 0
        
        # 6. Voice quality measures
        try:
            # Zero crossing rate (related to voice hoarseness)
            zcr = librosa.feature.zero_crossing_rate(y)[0]
            features['zero_crossing_rate_mean'] = np.mean(zcr)
            features['zero_crossing_rate_std'] = np.std(zcr)
            
            # RMS energy (related to loudness)
            rms = librosa.feature.rms(y=y)[0]
            features['rms_mean'] = np.mean(rms)
            features['rms_std'] = np.std(rms)
            
            # Harmonics-to-noise ratio (estimate via spectral flatness)
            features['harmonic_ratio'] = 1.0 - features['spectral_flatness_mean']
        except:
            features['zero_crossing_rate_mean'] = 0
            features['zero_crossing_rate_std'] = 0
            features['rms_mean'] = 0
            features['rms_std'] = 0
            features['harmonic_ratio'] = 0
            
        # Store features for later use
        self.features = features
        
        print(f"Extracted {len(features)} acoustic features from audio")
        return features
    
    def generate_visualizations(self, audio_path, output_dir=None):
        """Generate visualizations of acoustic features"""
        y, sr = self.load_audio(audio_path)
        if y is None:
            return
            
        if output_dir is None:
            output_dir = Path("reports/acoustic_analysis")
            output_dir.mkdir(exist_ok=True, parents=True)
        
        # Create figure with multiple plots
        fig, axes = plt.subplots(3, 2, figsize=(15, 12))
        
        # 1. Waveform
        librosa.display.waveshow(y, sr=sr, ax=axes[0, 0])
        axes[0, 0].set_title('Waveform')
        
        # 2. Spectrogram
        D = librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max)
        img = librosa.display.specshow(D, y_axis='log', x_axis='time', ax=axes[0, 1])
        axes[0, 1].set_title('Spectrogram')
        fig.colorbar(img, ax=axes[0, 1], format='%+2.0f dB')
        
        # 3. Mel Spectrogram
        S = librosa.feature.melspectrogram(y=y, sr=sr)
        S_dB = librosa.power_to_db(S, ref=np.max)
        img = librosa.display.specshow(S_dB, x_axis='time', y_axis='mel', ax=axes[1, 0])
        axes[1, 0].set_title('Mel Spectrogram')
        fig.colorbar(img, ax=axes[1, 0], format='%+2.0f dB')
        
        # 4. Chroma Features
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        img = librosa.display.specshow(chroma, y_axis='chroma', x_axis='time', ax=axes[1, 1])
        axes[1, 1].set_title('Chromagram')
        fig.colorbar(img, ax=axes[1, 1])
        
        # 5. MFCCs
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        img = librosa.display.specshow(mfccs, x_axis='time', ax=axes[2, 0])
        axes[2, 0].set_title('MFCCs')
        fig.colorbar(img, ax=axes[2, 0])
        
        # 6. Onset Strength
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        times = librosa.times_like(onset_env, sr=sr)
        axes[2, 1].plot(times, onset_env, label='Onset Strength')
        axes[2, 1].set_title('Onset Strength')
        axes[2, 1].set_xlabel('Time (s)')
        axes[2, 1].set_ylabel('Strength')
        
        plt.tight_layout()
        timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
        plt.savefig(os.path.join(output_dir, f'acoustic_analysis_{timestamp}.png'))
        
        return os.path.join(output_dir, f'acoustic_analysis_{timestamp}.png')
    
    def get_cognitive_indicators(self):
        """Extract cognitive health indicators from acoustic features"""
        if not self.features:
            return {}
            
        indicators = {}
        
        # 1. Vocal stability
        if 'pitch_std' in self.features and 'tremor_index' in self.features:
            # Combine pitch variability and tremor
            indicators['vocal_stability'] = 1.0 - (
                (self.features['pitch_std'] / max(1, self.features['pitch_mean'])) * 0.5 + 
                self.features['tremor_index'] * 0.5
            )
            
        # 2. Articulatory precision
        if 'zero_crossing_rate_mean' in self.features and 'spectral_centroid_mean' in self.features:
            # Higher values generally indicate more precise articulation
            indicators['articulation_precision'] = (
                self.features['zero_crossing_rate_mean'] * 10000 + 
                self.features['spectral_centroid_mean'] / 1000
            ) / 2
            
        # 3. Speech rhythm regularity
        if 'rhythm_strength' in self.features:
            indicators['rhythm_regularity'] = self.features['rhythm_strength']
            
        # 4. Voice quality
        if 'harmonic_ratio' in self.features:
            indicators['voice_quality'] = self.features['harmonic_ratio']
            
        # 5. Speech energy variability
        if 'rms_std' in self.features and 'rms_mean' in self.features:
            # Coefficient of variation of energy
            indicators['energy_variability'] = self.features['rms_std'] / max(0.001, self.features['rms_mean'])
        
        # Normalize indicators to 0-1 range (simplified approach)
        normalized = {}
        for key, value in indicators.items():
            if key == 'vocal_stability' or key == 'rhythm_regularity' or key == 'voice_quality':
                # These are already in 0-1 range
                normalized[key] = max(0, min(1, value))
            elif key == 'articulation_precision':
                # Normalize to 0-1 (assuming typical range)
                normalized[key] = max(0, min(1, value / 5))
            elif key == 'energy_variability':
                # Higher variability is mapped to lower score (0-1)
                normalized[key] = max(0, min(1, 1 - (value / 2)))
                
        return normalized
