import os
from pathlib import Path

# Project structure
PROJECT_ROOT = Path(r'd:\Memotag')
DATA_DIR = PROJECT_ROOT / 'data'
AUDIO_SAMPLES_DIR = DATA_DIR / 'audio_samples'
PROCESSED_DATA_DIR = DATA_DIR / 'processed'
MODELS_DIR = PROJECT_ROOT / 'models'
REPORTS_DIR = PROJECT_ROOT / 'reports'

# Create directories if they don't exist
for directory in [DATA_DIR, AUDIO_SAMPLES_DIR, PROCESSED_DATA_DIR, MODELS_DIR, REPORTS_DIR]:
    os.makedirs(directory, exist_ok=True)

# Audio processing parameters
SAMPLE_RATE = 16000
FRAME_SIZE = 512
HOP_LENGTH = 256

# Feature extraction parameters
MIN_PAUSE_LENGTH = 0.3  # seconds
HESITATION_MARKERS = ['um', 'uh', 'er', 'ah', 'like', 'you know']

# Simulated data parameters
NUM_SAMPLES = 10
IMPAIRMENT_LEVELS = ['none', 'mild', 'moderate', 'severe']
