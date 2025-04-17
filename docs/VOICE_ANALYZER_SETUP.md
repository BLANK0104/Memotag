# MemoTag Voice Analyzer Setup

This tool enables real-time cognitive assessment through voice recording and analysis.

## Prerequisites

1. Python 3.7 or higher
2. A working microphone
3. The following Python packages:
   - pyaudio
   - SpeechRecognition
   - nltk
   - numpy
   - pandas
   - matplotlib

## Installation

Install the required packages using pip:

```bash
pip install pyaudio SpeechRecognition nltk numpy pandas matplotlib
```

Note: If you encounter issues installing PyAudio on Windows, you may need to install it from a wheel file:

```bash
pip install pipwin
pipwin install pyaudio
```

## Running the Voice Analyzer

Run the analyzer with:

```bash
python voice_analyzer.py
```

## Usage Instructions

1. When prompted, select a cognitive task from the list (1-5)
2. Specify the recording duration (default: 60 seconds)
3. When recording starts, complete the cognitive task by speaking clearly
4. The tool will transcribe your speech and analyze multiple cognitive markers
5. Review the analysis results and visualizations

## Features Analyzed

The tool analyzes the following speech features:

- **transcript_length**: Total number of words spoken
- **hesitation_count**: Number of hesitation markers (um, uh, etc.)
- **hesitation_ratio**: Ratio of hesitations to total words
- **pause_count**: Number of detected pauses
- **pause_rate**: Pauses per sentence
- **speech_rate_wpm**: Speaking rate in words per minute
- **counting_sequence_length**: Length of numeric sequences in speech
- **counting_errors**: Errors in counting sequences
- **animal_count**: Number of unique animals named
- **word_finding_difficulty_count**: Estimated instances of word-finding difficulties

## Interpreting Results

The tool calculates a cognitive risk score from 0-1:
- 0.0-0.3: Low risk - No significant concerns
- 0.3-0.6: Moderate risk - May warrant further assessment
- 0.6-1.0: High risk - Consider professional cognitive assessment

**Note:** This tool is for educational and demonstration purposes only. It is not a medical device or diagnostic tool.
