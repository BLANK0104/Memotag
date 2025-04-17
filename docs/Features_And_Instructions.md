# MemoTag Speech Intelligence Module

This module processes voice clips to extract patterns that might indicate early cognitive impairment.

## Overview

The MemoTag Speech Intelligence Module analyzes speech patterns to detect potential signs of cognitive decline. The system:

1. Processes audio samples and their transcripts
2. Extracts linguistic and acoustic features relevant to cognitive health
3. Uses unsupervised machine learning to identify patterns and anomalies
4. Generates insights and risk assessments

## Project Structure

```
d:\Memotag\
  ├── data\                     # Directory for voice samples and processed data
  │   ├── audio_samples\        # Raw and simulated audio samples
  │   └── processed\            # Processed features and results
  ├── models\                   # Trained ML models
  ├── reports\                  # Generated reports and visualizations
  ├── src\                      # Source code
  │   ├── data_processing\      # Audio and feature processing
  │   ├── models\               # ML/NLP models
  │   ├── visualization\        # Visualization utilities
  │   ├── reports\              # Report generation
  │   ├── utils\                # Helper functions
  │   ├── web\                  # Web interface components
  │   │   └── templates\        # Templates for web interface
  │   └── tracking\             # Longitudinal tracking functionality
  ├── main.py                   # Entry point
  ├── voice_analyzer.py         # Real-time voice analysis tool
  ├── assessment_history_viewer.py  # Assessment history CLI viewer
  ├── web_history_viewer.py     # Web interface for assessment history
  ├── config.py                 # Configuration settings
  ├── assessment_history.db     # Database for assessment history
  └── requirements.txt          # Project dependencies
```

## Features Analyzed

The module extracts and analyzes the following speech features:

- **Hesitation markers**: Frequency of filler words (um, uh, etc.)
- **Pauses**: Frequency and duration of silent pauses
- **Word recall issues**: Signs of word-finding difficulties
- **Speech rate**: Words per minute
- **Task-specific features**: Performance on specific cognitive tasks (counting, naming)
- **Acoustic features**: 
  - Vocal stability and tremor
  - Pitch variation and control
  - Articulatory precision
  - Voice quality measures
  - Rhythm and prosody

## Cognitive Risk Score

The system calculates a comprehensive **Risk Score** (0.0-1.0) that quantifies potential cognitive concerns:

- **Calculation method**: Weighted analysis of linguistic and acoustic features
- **Key indicators**: Hesitations, pauses, speech rate, word recall, task performance, and acoustic qualities
- **Interpretation**:
  - **Low Risk** (0.0-0.3): No significant cognitive concerns detected
  - **Moderate Risk** (0.3-0.6): Some speech patterns may warrant further assessment
  - **High Risk** (0.6-1.0): Consider professional cognitive assessment
- **Visualization**: Risk scores are visually represented in analysis reports
- **Tracking**: Longitudinal monitoring tracks risk score changes over time


## Usage

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the main script:
   ```
   python main.py
   ```

3. View the generated report in the `reports` directory

4. For real-time voice analysis, use one of these methods:
   
   • Windows:
   ```
   run_voice_analyzer.bat
   ```
   
   • Linux/macOS:
   ```
   chmod +x run_voice_analyzer.sh
   ./run_voice_analyzer.sh
   ```
   
   • Direct Python execution:
   ```
   python voice_analyzer.py
   ```

## Longitudinal Tracking

The system now includes comprehensive longitudinal tracking capabilities:

- **User Profiles**: Create and maintain profiles for each user with personal information, assessment history, and personalized thresholds
- **Session History**: Store and access historical assessment data
- **Personalized Baselines**: Automatically calculate baseline values for each speech feature
- **Change Detection**: Identify significant deviations from user's established baseline
- **Trend Visualization**: Generate visual reports showing changes in speech patterns over time
- **Alert System**: Receive alerts when speech markers show concerning changes

To use longitudinal tracking:

1. Enable tracking when prompted in the voice analyzer:
   ```
   python voice_analyzer.py
   ```
   
2. Perform multiple assessments over time for the same user to build a baseline

3. View trend reports and alerts for users:
   ```
   python src/reports/trend_viewer.py list     # List all users
   python src/reports/trend_viewer.py view <user_id>  # View trends for a specific user
   ```

## Assessment History Viewer

The module includes tools to view and analyze assessment history:

1. Command-line interface:
   ```
   python assessment_history_viewer.py
   ```
   This displays tables and recent assessments from the database.

2. Web interface:
   ```
   python web_history_viewer.py
   ```
   Then open your browser to http://127.0.0.1:5000

The history viewer provides:
- Table listing
- Detailed data view with pagination
- Search functionality with filtering by keyword and date
- Historical trend analysis

## Real-Time Voice Analysis

The module now supports real-time voice processing through the `voice_analyzer.py` tool which:

- Records user speech through the microphone
- Transcribes speech using speech recognition
- Analyzes cognitive markers in real-time
- Extracts acoustic features using advanced audio processing
- Provides immediate feedback with risk assessment
- Generates visualizations of speech patterns and acoustic properties

Available cognitive tasks include:
- Counting backwards
- Animal naming
- Narrative description
- Sentence completion
- Orientation questions
- Emotional expression reading

## Troubleshooting

If you encounter errors during execution:

- **Visualization errors**: The system automatically detects data types and applies appropriate visualization techniques
- **Data warnings**: Common Pandas warnings are handled with best practices
- **Missing dependencies**: Ensure all requirements are installed with `pip install -r requirements.txt`

## Analysis Methods

The module uses several unsupervised learning techniques:

- **Clustering**: Groups samples with similar speech patterns
- **Anomaly Detection**: Identifies unusual speech patterns that may indicate cognitive issues
- **Dimensionality Reduction**: Visualizes complex feature relationships

## Next Steps

Future improvements planned:

1. ✅ Real-time audio processing - **IMPLEMENTED**
2. ✅ Expanded feature set with acoustic analysis - **IMPLEMENTED**
3. ✅ Longitudinal tracking capabilities - **IMPLEMENTED**
   - Tracking speech patterns over multiple sessions
   - Detecting subtle changes in cognitive markers over time
   - Establishing personalized baselines for each user
   - Generating trend reports to visualize cognitive changes
   - Alert system for significant pattern deviations
4. ✅ Assessment history viewer - **IMPLEMENTED**
   - Command-line interface for quick assessment review
   - Web interface for comprehensive history analysis
   - Search and filter functionality
   - Data visualization for historical trends
5. Personalized baseline development
6. Clinical validation studies

