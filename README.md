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
  │   └── utils\                # Helper functions
  ├── main.py                   # Entry point
  ├── config.py                 # Configuration settings
  └── requirements.txt          # Project dependencies
```

## Features Analyzed

The module extracts and analyzes the following speech features:

- **Hesitation markers**: Frequency of filler words (um, uh, etc.)
- **Pauses**: Frequency and duration of silent pauses
- **Word recall issues**: Signs of word-finding difficulties
- **Speech rate**: Words per minute
- **Task-specific features**: Performance on specific cognitive tasks (counting, naming)

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

1. Integration with real audio processing
2. Expanded feature set with acoustic analysis
3. Longitudinal tracking capabilities
4. Personalized baseline development
5. Clinical validation studies
