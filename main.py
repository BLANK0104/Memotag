import os
import json
import pandas as pd
from pathlib import Path

# Import project modules
from src.utils.simulated_data_generator import SimulatedDataGenerator
from src.data_processing.feature_extractor import FeatureExtractor
from src.models.unsupervised_analyzer import UnsupervisedAnalyzer
from src.visualization.visualizer import Visualizer
from src.reports.report_generator import ReportGenerator
from config import AUDIO_SAMPLES_DIR, PROCESSED_DATA_DIR, REPORTS_DIR

def main():
    """Main workflow for MemoTag speech intelligence module"""
    print("MemoTag Speech Intelligence Module")
    print("---------------------------------")
    
    # Step 1: Generate simulated voice transcript samples
    print("\nStep 1: Generating simulated voice transcript samples...")
    data_generator = SimulatedDataGenerator()
    samples = data_generator.generate_samples(num_samples=10)
    print(f"Generated {len(samples)} simulated samples")
    
    # Step 2: Extract features from samples
    print("\nStep 2: Extracting linguistic and cognitive features...")
    feature_extractor = FeatureExtractor()
    features_df = feature_extractor.process_samples(samples)
    
    # Save processed features
    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
    features_df.to_csv(Path(PROCESSED_DATA_DIR) / 'extracted_features.csv', index=False)
    print(f"Extracted {len(features_df.columns)} features from {len(features_df)} samples")
    
    # Step 3: Apply unsupervised learning
    print("\nStep 3: Applying unsupervised learning techniques...")
    unsupervised_analyzer = UnsupervisedAnalyzer()
    results_df = unsupervised_analyzer.analyze(features_df)
    
    # Get feature importance
    feature_importance = unsupervised_analyzer.generate_feature_importance(features_df)
    
    # Save results
    results_df.to_csv(Path(PROCESSED_DATA_DIR) / 'analysis_results.csv', index=False)
    print(f"Completed unsupervised analysis with {len(results_df)} results")
    
    # Step 4: Generate visualizations
    print("\nStep 4: Generating visualizations...")
    visualizer = Visualizer()
    try:
        visualizer.create_all_visualizations(results_df, feature_importance)
        print("Visualizations saved to reports directory")
    except Exception as e:
        print(f"Warning: Some visualizations could not be generated: {e}")
    
    # Step 5: Generate report
    print("\nStep 5: Generating analysis report...")
    report_generator = ReportGenerator()
    try:
        report_path = report_generator.generate_full_report(results_df, feature_importance)
        print(f"Analysis report generated at: {report_path}")
    except Exception as e:
        print(f"Error generating report: {e}")
        report_path = None
    
    # Summary of key findings
    high_risk = results_df[results_df['risk_score'] > 0.7]
    top_features = list(feature_importance.keys())[:5]
    
    print("\nKey Findings Summary:")
    print(f"- Samples analyzed: {len(results_df)}")
    print(f"- High-risk samples identified: {len(high_risk)}")
    print(f"- Most important features: {', '.join(top_features)}")
    print(f"- Report available at: {report_path}")
    
    print("\nMemoTag Speech Intelligence Module completed successfully.")

if __name__ == "__main__":
    main()
