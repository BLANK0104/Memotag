import pandas as pd
import matplotlib.pyplot as plt
import os
import seaborn as sns
import numpy as np

def generate_report(results, output_path):
    """
    Generate a markdown report from analysis results
    
    Args:
        results: Dictionary with analysis results
        output_path: Path to save the report
    """
    # Create directory for plots
    plots_dir = os.path.join(os.path.dirname(output_path), 'plots')
    os.makedirs(plots_dir, exist_ok=True)
    
    # Create correlation heatmap
    corr_data = pd.Series(results['correlations'])
    plt.figure(figsize=(10, 6))
    corr_data.sort_values().plot(kind='barh')
    plt.title('Feature Correlation with Anomaly Score')
    plt.tight_layout()
    corr_path = os.path.join(plots_dir, 'feature_correlations.png')
    plt.savefig(corr_path)
    
    # Create feature importance plot for anomaly detection
    plt.figure(figsize=(10, 6))
    importance_df = pd.DataFrame({
        'Feature': list(results['feature_importance_anomaly'].keys()),
        'Importance': list(results['feature_importance_anomaly'].values())
    })
    importance_df = importance_df.sort_values('Importance', ascending=False)
    sns.barplot(x='Importance', y='Feature', data=importance_df)
    plt.title('Feature Importance for Cognitive Impairment Detection')
    plt.tight_layout()
    importance_path = os.path.join(plots_dir, 'feature_importance.png')
    plt.savefig(importance_path)
    
    # Extract top features
    top_features = importance_df.head(3)['Feature'].tolist()
    
    # Write the report
    with open(output_path, 'w') as f:
        f.write("# MemoTag Speech Intelligence Analysis Report\n\n")
        
        f.write("## Executive Summary\n\n")
        anomaly_count = results['original_data']['potential_impairment'].sum()
        total_samples = len(results['original_data'])
        f.write(f"Analysis of {total_samples} voice samples complete. ")
        f.write(f"**{anomaly_count}** samples ({anomaly_count/total_samples:.0%}) ")
        f.write("showed patterns potentially indicative of cognitive impairment.\n\n")
        
        f.write("## Key Findings\n\n")
        f.write("### Most Insightful Features\n\n")
        f.write("The following features showed the strongest association with cognitive impairment patterns:\n\n")
        for feature in top_features:
            f.write(f"1. **{feature}**: Importance score {results['feature_importance_anomaly'][feature]:.3f}\n")
        f.write("\n![Feature Importance](plots/feature_importance.png)\n\n")
        
        f.write("### Speech Pattern Analysis\n\n")
        f.write("![Speech Pattern Analysis](plots/speech_pattern_analysis.png)\n\n")
        f.write("This visualization shows the clustering of speech patterns, with ")
        f.write("red circles indicating potential cognitive impairment based on anomaly detection.\n\n")
        
        f.write("## ML Methods Used\n\n")
        f.write("### 1. Unsupervised Anomaly Detection\n\n")
        f.write("We used **Isolation Forest** for anomaly detection, which identifies outliers ")
        f.write("based on speech patterns that deviate from the norm. This approach works well for ")
        f.write("detecting unusual speech patterns without requiring labeled training data.\n\n")
        
        f.write("### 2. Clustering Analysis\n\n")
        f.write("**K-means clustering** was applied to identify natural groupings in speech patterns. ")
        f.write("This helps distinguish between different speech profile types and identify ")
        f.write("potential subgroups within the data.\n\n")
        
        f.write("### 3. Dimensionality Reduction\n\n")
        f.write("**Principal Component Analysis (PCA)** was used to reduce the feature space to ")
        f.write("two dimensions while preserving ")
        f.write(f"{(results['pca_variance'][0] + results['pca_variance'][1]):.1%} ")
        f.write("of the original variance. This enables effective visualization and ")
        f.write("interpretation of complex speech patterns.\n\n")
        
        f.write("## Potential Next Steps\n\n")
        f.write("To make this analysis clinically robust, we recommend:\n\n")
        f.write("1. **Validated Dataset**: Collect a larger dataset with clinically-validated ")
        f.write("cognitive impairment diagnoses to enable supervised learning approaches.\n\n")
        
        f.write("2. **Longitudinal Analysis**: Track changes in speech patterns over time for ")
        f.write("each individual to establish personalized baselines and detect deviations.\n\n")
        
        f.write("3. **Multi-modal Integration**: Combine speech analysis with other cognitive ")
        f.write("assessments (e.g., memory tests, daily activity monitoring) for a more ")
        f.write("comprehensive evaluation.\n\n")
        
        f.write("4. **Clinical Validation Study**: Partner with neurologists and geriatricians ")
        f.write("to validate the model against standard cognitive assessment tools ")
        f.write("(e.g., MMSE, MoCA).\n\n")
        
        f.write("5. **Feature Engineering**: Develop additional linguistic markers specific to ")
        f.write("dementia and MCI based on the clinical literature, such as idea density and ")
        f.write("semantic coherence.\n\n")

def create_sample_data():
    """Create sample audio files for testing"""
    # This would generate sample audio files with various speech patterns
    # Implementation would depend on specific requirements
    pass
