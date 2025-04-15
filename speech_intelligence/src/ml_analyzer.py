import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt
import os

def analyze_features(features_df):
    """
    Apply machine learning techniques to analyze speech features
    
    Args:
        features_df: DataFrame with extracted features
        
    Returns:
        Dictionary with analysis results
    """
    # Store original data
    original_df = features_df.copy()
    
    # Select numerical features
    features_to_analyze = [
        'speech_rate', 'pitch_variability', 'pause_count', 
        'avg_pause_duration', 'filler_rate', 'lexical_diversity',
        'words_per_sentence', 'word_repetitions', 'word_finding_difficulties'
    ]
    
    # Ensure all features exist
    for feature in features_to_analyze:
        if feature not in features_df.columns:
            features_df[feature] = 0
    
    X = features_df[features_to_analyze].fillna(0)
    
    # Standardize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Apply PCA for visualization
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_scaled)
    
    # Feature importance from PCA
    feature_importance = pd.DataFrame(
        pca.components_.T, 
        columns=[f'PC{i+1}' for i in range(2)],
        index=features_to_analyze
    ).abs()
    
    # K-means clustering
    kmeans = KMeans(n_clusters=2, random_state=42)
    clusters = kmeans.fit_predict(X_scaled)
    
    # Anomaly detection using Isolation Forest
    isolation_forest = IsolationForest(contamination=0.2, random_state=42)
    anomalies = isolation_forest.fit_predict(X_scaled)
    # Convert predictions to binary (1: normal, -1: anomaly)
    is_anomaly = anomalies == -1
    
    # Calculate feature importance for anomaly detection
    feature_scores = {}
    for i, feature in enumerate(features_to_analyze):
        # Train a model with all features except this one
        X_without = np.delete(X_scaled, i, axis=1)
        iso_without = IsolationForest(contamination=0.2, random_state=42)
        anomalies_without = iso_without.fit_predict(X_without) == -1
        
        # Calculate how much this feature contributes to anomaly detection
        feature_scores[feature] = np.mean(is_anomaly != anomalies_without)
    
    # Visualize results
    plt.figure(figsize=(12, 8))
    
    # Create plots directory
    plots_dir = os.path.join('reports', 'plots')
    os.makedirs(plots_dir, exist_ok=True)
    
    # Plot PCA with clusters and anomalies
    plt.scatter(X_pca[:, 0], X_pca[:, 1], c=clusters, cmap='viridis', alpha=0.7)
    plt.scatter(X_pca[is_anomaly, 0], X_pca[is_anomaly, 1], 
               edgecolors='red', facecolors='none', s=100, label='Potential Cognitive Impairment')
    
    for i, txt in enumerate(original_df['file_name']):
        plt.annotate(txt, (X_pca[i, 0], X_pca[i, 1]))
    
    plt.title('Speech Pattern Analysis')
    plt.xlabel(f'Principal Component 1 ({pca.explained_variance_ratio_[0]:.2%} variance)')
    plt.ylabel(f'Principal Component 2 ({pca.explained_variance_ratio_[1]:.2%} variance)')
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, 'speech_pattern_analysis.png'))
    
    # Add results to original dataframe
    original_df['cluster'] = clusters
    original_df['anomaly_score'] = isolation_forest.score_samples(X_scaled)
    original_df['potential_impairment'] = is_anomaly
    
    # Calculate average values by cluster
    cluster_profiles = original_df.groupby('cluster')[features_to_analyze].mean()
    
    # Calculate correlation between features and anomaly scores
    correlations = {}
    for feature in features_to_analyze:
        correlations[feature] = np.corrcoef(
            original_df[feature], 
            original_df['anomaly_score']
        )[0, 1]
    
    return {
        'original_data': original_df,
        'pca_components': pca.components_,
        'pca_variance': pca.explained_variance_ratio_,
        'feature_importance': feature_importance,
        'feature_importance_anomaly': feature_scores,
        'correlations': correlations,
        'cluster_profiles': cluster_profiles,
        'features_analyzed': features_to_analyze
    }
