import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.ensemble import IsolationForest
from sklearn.metrics import silhouette_score
import sys
from pathlib import Path
import joblib
import matplotlib.pyplot as plt

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parents[2]))
from config import MODELS_DIR, REPORTS_DIR

class UnsupervisedAnalyzer:
    """Apply unsupervised ML techniques to detect patterns in speech features"""
    
    def __init__(self, feature_columns=None):
        self.feature_columns = feature_columns
        self.scaler = StandardScaler()
        self.anomaly_model = None
        self.cluster_model = None
        self.pca = None
    
    def preprocess_data(self, features_df):
        """Preprocess features for analysis"""
        # Choose features to use if not specified
        if self.feature_columns is None:
            # Exclude metadata columns
            self.feature_columns = [col for col in features_df.columns 
                                    if col not in ['sample_id', 'impairment_level']]
        
        # Extract feature matrix
        X = features_df[self.feature_columns].copy()
        
        # Fill missing values
        X = X.fillna(0)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        return X_scaled, X
    
    def apply_clustering(self, X_scaled, n_clusters=3):
        """Apply clustering to identify potential groups"""
        self.cluster_model = KMeans(n_clusters=n_clusters, random_state=42)
        clusters = self.cluster_model.fit_predict(X_scaled)
        
        # Evaluate clustering
        silhouette = silhouette_score(X_scaled, clusters) if len(np.unique(clusters)) > 1 else 0
        
        return clusters, silhouette
    
    def detect_anomalies(self, X_scaled):
        """Apply anomaly detection to identify unusual patterns"""
        self.anomaly_model = IsolationForest(contamination=0.1, random_state=42)
        anomaly_scores = self.anomaly_model.fit_predict(X_scaled)
        
        # Convert to binary anomaly indicator (1=normal, -1=anomaly)
        is_anomaly = anomaly_scores == -1
        
        return is_anomaly, self.anomaly_model.decision_function(X_scaled)
    
    def dimension_reduction(self, X_scaled, n_components=2):
        """Apply dimensionality reduction for visualization"""
        self.pca = PCA(n_components=n_components)
        X_reduced = self.pca.fit_transform(X_scaled)
        
        # Calculate explained variance
        explained_variance = self.pca.explained_variance_ratio_.sum()
        
        return X_reduced, explained_variance
    
    def analyze(self, features_df):
        """Run the full analysis pipeline"""
        # Preprocess data
        X_scaled, X_original = self.preprocess_data(features_df)
        
        # Apply clustering
        clusters, silhouette = self.apply_clustering(X_scaled)
        
        # Apply anomaly detection
        anomalies, anomaly_scores = self.detect_anomalies(X_scaled)
        
        # Apply dimensionality reduction
        X_reduced, explained_variance = self.dimension_reduction(X_scaled)
        
        # Combine results
        results = features_df.copy()
        results['cluster'] = clusters
        results['anomaly'] = anomalies.astype(int)
        results['anomaly_score'] = anomaly_scores
        results['pca1'] = X_reduced[:, 0]
        results['pca2'] = X_reduced[:, 1]
        
        # Calculate risk score (combines clustering and anomaly detection)
        # Higher score indicates higher risk of cognitive impairment
        
        # 1. Use anomaly score as base
        # 2. Adjust based on cluster association
        cluster_risk = np.zeros(len(results))
        
        # Analyze which clusters have more impaired samples (if ground truth available)
        if 'impairment_level' in results.columns:
            cluster_impairment = {}
            for cluster in np.unique(clusters):
                cluster_samples = results[results['cluster'] == cluster]
                # Map impairment levels to numerical values
                impairment_map = {'none': 0, 'mild': 1, 'moderate': 2, 'severe': 3}
                
                if 'impairment_level' in cluster_samples.columns:
                    cluster_samples.loc[:, 'impairment_numeric'] = cluster_samples['impairment_level'].map(impairment_map)
                    avg_impairment = cluster_samples['impairment_numeric'].mean()
                    cluster_impairment[cluster] = avg_impairment
            
            # Normalize to 0-1 range
            max_impairment = max(cluster_impairment.values()) if cluster_impairment else 1
            for cluster, impairment in cluster_impairment.items():
                normalized_risk = impairment / max_impairment if max_impairment > 0 else 0
                cluster_risk[results['cluster'] == cluster] = normalized_risk
        
        # Combine anomaly score and cluster risk
        # Convert anomaly score to 0-1 scale (lower is more anomalous, so we invert)
        normalized_anomaly = (anomaly_scores - np.min(anomaly_scores))
        if np.max(normalized_anomaly) > 0:
            normalized_anomaly = normalized_anomaly / np.max(normalized_anomaly)
        normalized_anomaly = 1 - normalized_anomaly  # Invert so higher is more anomalous
        
        # Combine (weight anomaly detection higher)
        results['risk_score'] = 0.7 * normalized_anomaly + 0.3 * cluster_risk
        
        # Save models
        self.save_models()
        
        return results
    
    def save_models(self):
        """Save trained models"""
        models_dict = {
            'scaler': self.scaler,
            'anomaly_model': self.anomaly_model,
            'cluster_model': self.cluster_model,
            'pca': self.pca,
            'feature_columns': self.feature_columns
        }
        
        joblib.dump(models_dict, Path(MODELS_DIR) / 'unsupervised_models.pkl')
        
    def generate_feature_importance(self, features_df):
        """Generate feature importance based on models"""
        importance = {}
        
        # 1. Feature importance from PCA
        if self.pca is not None:
            # Use the absolute loading values
            for i, feature in enumerate(self.feature_columns):
                # Sum of absolute loadings across components
                importance[feature] = np.sum(np.abs(self.pca.components_[:, i]))
        
        # 2. Feature importance from clustering (based on cluster centers)
        if self.cluster_model is not None:
            cluster_centers = self.cluster_model.cluster_centers_
            # Calculate the variance of each feature across cluster centers
            for i, feature in enumerate(self.feature_columns):
                feature_variance = np.var(cluster_centers[:, i])
                if feature in importance:
                    importance[feature] += feature_variance
                else:
                    importance[feature] = feature_variance
        
        # Normalize to 0-1
        max_importance = max(importance.values()) if importance else 1
        normalized_importance = {feature: value/max_importance for feature, value in importance.items()}
        
        # Sort by importance
        sorted_importance = {k: v for k, v in sorted(normalized_importance.items(), 
                                                      key=lambda item: item[1], 
                                                      reverse=True)}
        
        return sorted_importance
