import numpy as np
import librosa
import re
import pandas as pd
from textblob import TextBlob

def extract_features(audio_dict, transcript_dict):
    """
    Extract features from audio and transcript
    
    Args:
        audio_dict: Dictionary with audio data
        transcript_dict: Dictionary with transcript data
        
    Returns:
        Dictionary of extracted features
    """
    features = {}
    
    # Extract acoustic features
    acoustic_features = extract_acoustic_features(audio_dict)
    features.update(acoustic_features)
    
    # Extract linguistic features
    linguistic_features = extract_linguistic_features(transcript_dict)
    features.update(linguistic_features)
    
    return features

def extract_acoustic_features(audio_dict):
    """Extract features from audio data"""
    y = audio_dict['waveform']
    sr = audio_dict['sample_rate']
    
    # Calculate speech rate (syllables per second)
    # This is a rough approximation
    envelope = np.abs(y)
    envelope = pd.Series(envelope).rolling(int(sr * 0.03)).mean().fillna(0).values
    peaks = librosa.util.peak_pick(envelope, pre_max=int(sr*0.03), 
                                  post_max=int(sr*0.03), 
                                  pre_avg=int(sr*0.1), 
                                  post_avg=int(sr*0.1), 
                                  delta=0.1, 
                                  wait=int(sr*0.1))
    num_syllables = len(peaks)
    speech_rate = num_syllables / audio_dict['duration']
    
    # Calculate pitch (F0) statistics
    f0, voiced_flag, _ = librosa.pyin(y, 
                                     fmin=librosa.note_to_hz('C2'), 
                                     fmax=librosa.note_to_hz('C5'),
                                     sr=sr)
    
    # Remove NaN values
    f0 = f0[~np.isnan(f0)]
    
    if len(f0) > 0:
        pitch_mean = np.mean(f0)
        pitch_std = np.std(f0)
        pitch_range = np.max(f0) - np.min(f0)
    else:
        pitch_mean = pitch_std = pitch_range = 0
    
    # Calculate pauses
    silence_threshold = 0.015
    is_silence = np.abs(y) < silence_threshold
    silence_runs = np.where(np.diff(np.hstack(([False], is_silence, [False]))))[0].reshape(-1, 2)
    
    # Only count pauses longer than 0.3 seconds but shorter than 2 seconds
    pause_min_length = int(0.3 * sr)
    pause_max_length = int(2.0 * sr)
    
    pauses = [run for run in silence_runs if pause_min_length < (run[1] - run[0]) < pause_max_length]
    pause_count = len(pauses)
    
    if pause_count > 0:
        pause_durations = [(p[1] - p[0]) / sr for p in pauses]
        avg_pause_duration = np.mean(pause_durations)
    else:
        avg_pause_duration = 0
    
    return {
        'speech_rate': speech_rate,
        'pitch_mean': pitch_mean,
        'pitch_std': pitch_std,
        'pitch_variability': pitch_std / pitch_mean if pitch_mean > 0 else 0,
        'pitch_range': pitch_range,
        'pause_count': pause_count,
        'avg_pause_duration': avg_pause_duration,
        'total_pause_time': pause_count * avg_pause_duration
    }

def extract_linguistic_features(transcript_dict):
    """Extract features from transcript"""
    full_text = transcript_dict['full_transcript']
    
    # Count filler words/hesitation markers
    filler_words = ['uh', 'um', 'er', 'ah', 'like', 'you know', 'i mean']
    filler_count = sum(len(re.findall(r'\b' + fw + r'\b', full_text.lower())) for fw in filler_words)
    
    # Word count and sentence count
    blob = TextBlob(full_text)
    word_count = len(blob.words)
    sentence_count = len(blob.sentences)
    
    # Calculate lexical diversity (type-token ratio)
    if word_count > 0:
        unique_words = len(set(word.lower() for word in blob.words))
        lexical_diversity = unique_words / word_count
    else:
        lexical_diversity = 0
    
    # Calculate average words per sentence
    words_per_sentence = word_count / sentence_count if sentence_count > 0 else 0
    
    # Check for incomplete sentences
    incomplete_sentence_count = len(re.findall(r'[a-zA-Z]+\s*\.{3}|[a-zA-Z]+\s*$', full_text))
    
    # Detect word repetitions (potential sign of difficulty)
    words = [w.lower() for w in blob.words]
    repetitions = 0
    for i in range(1, len(words)):
        if words[i] == words[i-1]:
            repetitions += 1
    
    # Calculate sentiment (could be relevant for emotional content)
    sentiment = blob.sentiment.polarity
    
    # Find potential word-finding difficulties (long pauses followed by simple words)
    # This is approximated by looking for "..." in text
    word_finding_difficulties = len(re.findall(r'\.{3}\s*[a-zA-Z]{1,4}\b', full_text))
    
    return {
        'filler_count': filler_count,
        'filler_rate': filler_count / word_count if word_count > 0 else 0,
        'word_count': word_count,
        'sentence_count': sentence_count,
        'words_per_sentence': words_per_sentence,
        'lexical_diversity': lexical_diversity,
        'incomplete_sentences': incomplete_sentence_count,
        'word_repetitions': repetitions,
        'sentiment': sentiment,
        'word_finding_difficulties': word_finding_difficulties
    }
