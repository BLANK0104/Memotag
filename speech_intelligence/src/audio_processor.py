import librosa
import numpy as np
import soundfile as sf
import os

def preprocess_audio(audio_path, target_sr=16000):
    """
    Preprocess audio file: load, normalize, remove noise, and resample
    
    Args:
        audio_path: Path to the audio file
        target_sr: Target sampling rate
        
    Returns:
        Dictionary with processed audio data and metadata
    """
    print(f"Preprocessing audio: {audio_path}")
    
    # Load audio file
    y, sr = librosa.load(audio_path, sr=None)
    
    # Resample if needed
    if sr != target_sr:
        y = librosa.resample(y, orig_sr=sr, target_sr=target_sr)
        sr = target_sr
    
    # Normalize audio
    y = librosa.util.normalize(y)
    
    # Simple noise reduction (remove low amplitude noise)
    noise_threshold = 0.015
    y = librosa.effects.preemphasis(y)
    y = np.where(np.abs(y) < noise_threshold, 0, y)
    
    # Trim silence at beginning and end
    y, _ = librosa.effects.trim(y, top_db=30)
    
    # Save processed audio
    processed_dir = os.path.join('data', 'processed_data', 'audio')
    os.makedirs(processed_dir, exist_ok=True)
    output_path = os.path.join(processed_dir, os.path.basename(audio_path))
    sf.write(output_path, y, sr)
    
    return {
        'waveform': y,
        'sample_rate': sr,
        'duration': librosa.get_duration(y=y, sr=sr),
        'processed_path': output_path,
        'original_path': audio_path
    }

def segment_audio(audio_dict):
    """
    Segment audio into sentences based on silence
    
    Args:
        audio_dict: Dictionary containing audio data
        
    Returns:
        List of segments with timestamps
    """
    y = audio_dict['waveform']
    sr = audio_dict['sample_rate']
    
    # Find silence regions (potential sentence boundaries)
    intervals = librosa.effects.split(y, top_db=30)
    
    segments = []
    for i, (start, end) in enumerate(intervals):
        start_time = start / sr
        end_time = end / sr
        segment = {
            'id': i,
            'start_time': start_time,
            'end_time': end_time,
            'duration': end_time - start_time,
            'waveform': y[start:end]
        }
        segments.append(segment)
    
    return segments
