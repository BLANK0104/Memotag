import os
import pandas as pd
from src.audio_processor import preprocess_audio
from src.transcriber import transcribe_audio
from src.feature_extractor import extract_features
from src.ml_analyzer import analyze_features
from src.report_generator import generate_report

def main():
    # Define paths
    raw_data_dir = os.path.join('data', 'raw_samples')
    processed_data_dir = os.path.join('data', 'processed_data')
    report_path = os.path.join('reports', 'findings.md')
    
    # Ensure directories exist
    os.makedirs(raw_data_dir, exist_ok=True)
    os.makedirs(processed_data_dir, exist_ok=True)
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    
    # Process each audio file
    audio_files = [os.path.join(raw_data_dir, f) for f in os.listdir(raw_data_dir) 
                  if f.endswith(('.wav', '.mp3'))]
    
    all_features = []
    
    for audio_file in audio_files:
        print(f"Processing {audio_file}...")
        
        # Step 1: Preprocess audio
        processed_audio = preprocess_audio(audio_file)
        
        # Step 2: Transcribe audio
        transcript = transcribe_audio(processed_audio)
        
        # Step 3: Extract features
        features = extract_features(processed_audio, transcript)
        features['file_name'] = os.path.basename(audio_file)
        all_features.append(features)
    
    # Combine all features into a dataframe
    features_df = pd.DataFrame(all_features)
    features_df.to_csv(os.path.join(processed_data_dir, 'all_features.csv'), index=False)
    
    # Step 4: Analyze features with ML
    results = analyze_features(features_df)
    
    # Step 5: Generate report
    generate_report(results, report_path)
    
    print(f"Analysis complete! Report saved to {report_path}")

if __name__ == "__main__":
    main()
