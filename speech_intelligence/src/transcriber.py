import speech_recognition as sr
import os
import json

def transcribe_audio(audio_dict):
    """
    Transcribe audio to text
    
    Args:
        audio_dict: Dictionary with audio data
        
    Returns:
        Dictionary with transcript and metadata
    """
    recognizer = sr.Recognizer()
    
    # If we have segments, transcribe each segment
    if 'segments' in audio_dict:
        segments = audio_dict['segments']
        for segment in segments:
            segment['transcript'] = _transcribe_segment(segment['waveform'], 
                                                       audio_dict['sample_rate'],
                                                       recognizer)
        
        full_transcript = " ".join([s['transcript'] for s in segments])
    else:
        # Transcribe full audio
        full_transcript = _transcribe_segment(audio_dict['waveform'], 
                                             audio_dict['sample_rate'],
                                             recognizer)
    
    # Save transcript
    transcripts_dir = os.path.join('data', 'processed_data', 'transcripts')
    os.makedirs(transcripts_dir, exist_ok=True)
    
    base_name = os.path.splitext(os.path.basename(audio_dict['original_path']))[0]
    transcript_path = os.path.join(transcripts_dir, f"{base_name}_transcript.json")
    
    transcript_data = {
        'full_transcript': full_transcript,
        'segments': audio_dict.get('segments', [])
    }
    
    with open(transcript_path, 'w') as f:
        json.dump(transcript_data, f, indent=2)
    
    return transcript_data

def _transcribe_segment(audio_data, sample_rate, recognizer):
    """Helper function to transcribe an audio segment"""
    try:
        # Convert numpy array to AudioData
        audio = sr.AudioData(audio_data.tobytes(), 
                            sample_rate=sample_rate, 
                            sample_width=2)  # 16-bit audio
        
        # Use Google's speech recognition service
        transcript = recognizer.recognize_google(audio)
        return transcript
    except Exception as e:
        print(f"Error transcribing segment: {str(e)}")
        return ""
