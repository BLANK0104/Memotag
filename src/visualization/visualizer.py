import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parents[2]))
from config import REPORTS_DIR

class Visualizer:
    """Generate visualizations for analysis results"""
    
    def __init__(self):
        self.report_dir = Path(REPORTS_DIR)
        self.report_dir.mkdir(exist_ok=True)
    
    def plot_feature_distributions(self, results_df):
        """
        Plot distribution of features by impairment level.
        """
        features = [col for col in results_df.columns if col not in ['participant_id', 'impairment_level', 'cluster', 'anomaly_score']]
        
        # Create grid of subplots
        n_features = len(features)
        n_cols = 2
        n_rows = (n_features + 1) // 2
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 4 * n_rows))
        axes = axes.flatten()
        
        for i, feature in enumerate(features):
            if i >= len(axes):  # Safeguard against array index out of bounds
                break
                
            ax = axes[i]
            
            # Check the data type of the feature and use appropriate plot
            if pd.api.types.is_numeric_dtype(results_df[feature]):
                # For numeric features, check variance before using KDE
                plot_success = False
                for level in results_df['impairment_level'].unique():
                    subset = results_df[results_df['impairment_level'] == level]
                    
                    # Check if subset has data and variance
                    if len(subset) > 0 and subset[feature].var() > 0:
                        sns.kdeplot(subset[feature], ax=ax, label=level, warn_singular=False)
                        plot_success = True
                        
                # If KDE failed for all groups, fall back to boxplot
                if not plot_success:
                    sns.boxplot(x='impairment_level', y=feature, data=results_df, ax=ax)
            else:
                # For categorical features, use count plot
                sns.countplot(x=feature, hue='impairment_level', data=results_df, ax=ax)
                
            ax.set_title(f'Distribution of {feature}')
            ax.set_xlabel(feature)
            
            # Only set legend if there are labeled artists
            handles, labels = ax.get_legend_handles_labels()
            if handles:
                ax.legend()
        
        plt.tight_layout()
        plt.savefig(self.report_dir / 'feature_distributions.png', dpi=300)
        plt.close()
    
    def plot_clustering_results(self, results_df):
        """Plot clustering results with PCA reduction"""
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Color by cluster
        scatter = ax.scatter(results_df['pca1'], results_df['pca2'], 
                  c=results_df['cluster'], cmap='viridis', 
                  s=80, alpha=0.8)
        
        # Mark anomalies with a different symbol
        anomalies = results_df[results_df['anomaly'] == 1]
        if not anomalies.empty:
            ax.scatter(anomalies['pca1'], anomalies['pca2'], 
                      s=120, facecolors='none', edgecolors='red', 
                      linewidth=2, label='Anomaly')
        
        # Add legend for clusters
        legend1 = ax.legend(*scatter.legend_elements(),
                            loc="upper right", title="Clusters")
        ax.add_artist(legend1)
        
        # If ground truth is available, add labels
        if 'impairment_level' in results_df.columns:
            # Add text labels for impairment level
            for i, row in results_df.iterrows():
                ax.annotate(row['impairment_level'], 
                           (row['pca1'], row['pca2']),
                           fontsize=8, alpha=0.7,
                           xytext=(5, 5), textcoords='offset points')
        
        ax.set_title('Clustering Results with PCA Dimensionality Reduction')
        ax.set_xlabel('Principal Component 1')
        ax.set_ylabel('Principal Component 2')
        
        plt.tight_layout()
        plt.savefig(self.report_dir / 'clustering_results.png', dpi=300)
        plt.close()
    
    def plot_risk_scores(self, results_df):
        """Plot risk scores with sample identification"""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Sort by risk score
        sorted_df = results_df.sort_values('risk_score', ascending=False)
        
        # Determine identifier column (use 'participant_id' or index if 'sample_id' doesn't exist)
        id_column = 'sample_id'
        if id_column not in sorted_df.columns:
            if 'participant_id' in sorted_df.columns:
                id_column = 'participant_id'
            else:
                # Create a temporary sample ID if none exists
                sorted_df = sorted_df.copy()
                sorted_df['temp_id'] = [f"Sample_{i+1}" for i in range(len(sorted_df))]
                id_column = 'temp_id'
        
        # Bar chart of risk scores
        bars = ax.bar(sorted_df[id_column], sorted_df['risk_score'], 
                     color=sorted_df['risk_score'].apply(lambda x: plt.cm.RdYlGn_r(x)))
        
        # Highlight anomalies if anomaly column exists
        if 'anomaly' in sorted_df.columns:
            for i, is_anomaly in enumerate(sorted_df['anomaly']):
                if is_anomaly:
                    bars[i].set_edgecolor('red')
                    bars[i].set_linewidth(2)
        
        # Annotate with impairment level if available
        if 'impairment_level' in sorted_df.columns:
            for i, (_, row) in enumerate(sorted_df.iterrows()):
                ax.annotate(row['impairment_level'],
                           xy=(i, row['risk_score']),
                           xytext=(0, 5),
                           textcoords='offset points',
                           ha='center', va='bottom',
                           fontsize=8)
        
        ax.set_title('Cognitive Impairment Risk Scores')
        ax.set_xlabel('Sample ID')
        ax.set_ylabel('Risk Score (higher = more at risk)')
        ax.set_ylim(0, 1.1)
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        plt.savefig(self.report_dir / 'risk_scores.png', dpi=300)
        plt.close()
    
    def plot_feature_importance(self, feature_importance):
        """Plot feature importance"""
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Convert to DataFrame for plotting
        imp_df = pd.DataFrame({'Feature': list(feature_importance.keys()),
                              'Importance': list(feature_importance.values())})
        
        # Sort by importance
        imp_df = imp_df.sort_values('Importance', ascending=True)
        
        # Horizontal bar chart
        ax.barh(imp_df['Feature'], imp_df['Importance'], color='teal')
        
        ax.set_title('Feature Importance for Cognitive Impairment Detection')
        ax.set_xlabel('Relative Importance')
        
        plt.tight_layout()
        plt.savefig(self.report_dir / 'feature_importance.png', dpi=300)
        plt.close()
    
    def create_all_visualizations(self, results_df, feature_importance):
        """Create all visualizations at once"""
        self.plot_feature_distributions(results_df)
        self.plot_clustering_results(results_df)
        self.plot_risk_scores(results_df)
        self.plot_feature_importance(feature_importance)
