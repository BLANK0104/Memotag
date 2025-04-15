import pandas as pd
import numpy as np
from pathlib import Path
import sys
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os
import json

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parents[2]))
from config import REPORTS_DIR

class ReportGenerator:
    """Generate analysis reports and insights"""
    
    def __init__(self):
        self.report_dir = Path(REPORTS_DIR)
        self.report_dir.mkdir(exist_ok=True)
        self.output_dir = str(self.report_dir)
    
    def generate_summary_statistics(self, results_df):
        """Generate summary statistics for the analysis results."""
        summary = {}
        
        # Get only numeric columns for correlation
        numeric_df = results_df.select_dtypes(include=['number'])
        
        # Skip correlation calculation if 'impairment_numeric' is not in numeric columns
        if 'impairment_numeric' in numeric_df.columns:
            correlations = numeric_df.corr()['impairment_numeric'].abs().sort_values(ascending=False)
            summary['top_correlations'] = correlations.head(5).to_dict()
        else:
            summary['top_correlations'] = {}
        
        # Group statistics by impairment level
        for level in results_df['impairment_level'].unique():
            subset = results_df[results_df['impairment_level'] == level]
            numeric_subset = subset.select_dtypes(include=['number'])
            
            summary[f'{level}_stats'] = {
                'count': len(subset),
                'avg_anomaly_score': numeric_subset['anomaly_score'].mean() if 'anomaly_score' in numeric_subset else 0,
                'features': {}
            }
            
            # Calculate statistics for each feature
            for col in numeric_subset.columns:
                if col not in ['impairment_numeric', 'anomaly_score', 'cluster']:
                    summary[f'{level}_stats']['features'][col] = {
                        'mean': numeric_subset[col].mean(),
                        'std': numeric_subset[col].std()
                    }
        
        return summary
    
    def generate_cluster_analysis(self, results_df):
        """Analyze clusters and their characteristics"""
        # Group by cluster
        if 'cluster' in results_df.columns:
            cluster_stats = []
            
            for cluster in results_df['cluster'].unique():
                cluster_df = results_df[results_df['cluster'] == cluster]
                
                stats = {
                    'cluster': cluster,
                    'sample_count': len(cluster_df),
                    'avg_risk_score': cluster_df['risk_score'].mean(),
                    'anomaly_count': cluster_df['anomaly'].sum()
                }
                
                # Add impairment distribution if available
                if 'impairment_level' in cluster_df.columns:
                    impairment_counts = cluster_df['impairment_level'].value_counts()
                    for level in impairment_counts.index:
                        stats[f'impairment_{level}'] = impairment_counts[level]
                    
                    # Calculate predominant impairment level
                    if not impairment_counts.empty:
                        stats['predominant_impairment'] = impairment_counts.idxmax()
                
                cluster_stats.append(stats)
            
            cluster_analysis = pd.DataFrame(cluster_stats)
            return cluster_analysis
        
        return pd.DataFrame()
    
    def generate_high_risk_samples(self, results_df, threshold=0.7):
        """Identify high-risk samples based on risk score"""
        high_risk = results_df[results_df['risk_score'] >= threshold].sort_values('risk_score', ascending=False)
        return high_risk
    
    def generate_feature_insights(self, feature_importance, top_n=5):
        """Generate insights on top features"""
        # Get top N features
        top_features = dict(sorted(feature_importance.items(), 
                                  key=lambda x: x[1], 
                                  reverse=True)[:top_n])
        
        insights = {
            'top_features': top_features,
            'insights': {
                'hesitation_ratio': "The ratio of hesitations to total words indicates word retrieval difficulties.",
                'pause_rate': "Higher pause rates may indicate cognitive processing delays.",
                'word_finding_difficulty_count': "Direct indicator of word-finding problems common in early impairment.",
                'speech_rate_wpm': "Slowed speech rate often correlates with cognitive decline.",
                'counting_errors': "Errors in sequential tasks can indicate working memory issues."
            }
        }
        
        # Only include insights for top features
        insights['insights'] = {k: v for k, v in insights['insights'].items() 
                               if k in top_features}
        
        return insights
    
    def generate_html_report(self, results_df, feature_importance, summary_stats):
        """Generate an HTML report with all analyses and visualizations."""
        # HTML header and style
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>MemoTag Cognitive Analysis Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }}
                h1, h2, h3 {{ color: #2c3e50; }}
                .container {{ max-width: 1200px; margin: 0 auto; }}
                .summary-box {{ background-color: #f8f9fa; border-left: 4px solid #4285f4; padding: 15px; margin-bottom: 20px; }}
                .risk-high {{ color: #e74c3c; }}
                .risk-medium {{ color: #f39c12; }}
                .risk-low {{ color: #27ae60; }}
                table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
                th, td {{ text-align: left; padding: 12px; }}
                th {{ background-color: #4285f4; color: white; }}
                tr:nth-child(even) {{ background-color: #f2f2f2; }}
                .viz-section {{ margin-top: 30px; }}
                .viz-container {{ text-align: center; margin: 20px 0; }}
                .feature-importance {{ display: flex; }}
                .feature-bar {{ height: 20px; margin: 5px 0; background-color: #3498db; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>MemoTag Cognitive Analysis Report</h1>
                <p>Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
                
                <div class="summary-box">
                    <h2>Analysis Summary</h2>
                    <p><strong>Total samples analyzed:</strong> {len(results_df)}</p>
        """
        
        # Add risk breakdown
        if 'risk_score' in results_df.columns:
            high_risk = len(results_df[results_df['risk_score'] > 0.7])
            med_risk = len(results_df[(results_df['risk_score'] > 0.4) & (results_df['risk_score'] <= 0.7)])
            low_risk = len(results_df[results_df['risk_score'] <= 0.4])
            
            html_content += f"""
                    <p><strong>Risk breakdown:</strong></p>
                    <ul>
                        <li><span class="risk-high">High risk:</span> {high_risk} samples</li>
                        <li><span class="risk-medium">Medium risk:</span> {med_risk} samples</li>
                        <li><span class="risk-low">Low risk:</span> {low_risk} samples</li>
                    </ul>
            """
        
        # Add top features
        html_content += f"""
                    <p><strong>Top predictive features:</strong></p>
                    <ol>
        """
        
        # Add top 5 features from feature importance
        for i, (feature, importance) in enumerate(sorted(feature_importance.items(), 
                                                        key=lambda x: x[1], reverse=True)[:5]):
            html_content += f"""
                        <li>{feature} (importance: {importance:.3f})</li>
            """
        
        html_content += """
                    </ol>
                </div>
        """
        
        # Add tables section with results
        html_content += """
                <h2>Detailed Results</h2>
                <table>
                    <tr>
                        <th>Sample ID</th>
                        <th>Impairment Level</th>
                        <th>Risk Score</th>
                        <th>Anomaly Detected</th>
                        <th>Cluster</th>
                    </tr>
        """
        
        # Add rows for each sample
        for _, row in results_df.sort_values(by='risk_score', ascending=False).iterrows():
            sample_id = row.get('sample_id', row.get('participant_id', 'Unknown'))
            impairment = row.get('impairment_level', 'Unknown')
            risk_score = row.get('risk_score', 0)
            anomaly = 'Yes' if row.get('anomaly', 0) == 1 else 'No'
            cluster = row.get('cluster', 'N/A')
            
            risk_class = 'risk-high' if risk_score > 0.7 else ('risk-medium' if risk_score > 0.4 else 'risk-low')
            
            html_content += f"""
                    <tr>
                        <td>{sample_id}</td>
                        <td>{impairment}</td>
                        <td class="{risk_class}">{risk_score:.3f}</td>
                        <td>{anomaly}</td>
                        <td>{cluster}</td>
                    </tr>
            """
        
        html_content += """
                </table>
        """
        
        # Add visualization references
        html_content += """
                <h2>Visualizations</h2>
                
                <div class="viz-section">
                    <h3>Feature Distributions</h3>
                    <div class="viz-container">
                        <img src="feature_distributions.png" alt="Feature Distributions" style="max-width:100%;">
                    </div>
                </div>
                
                <div class="viz-section">
                    <h3>Clustering Results</h3>
                    <div class="viz-container">
                        <img src="clustering_results.png" alt="Clustering Results" style="max-width:100%;">
                    </div>
                </div>
                
                <div class="viz-section">
                    <h3>Risk Scores</h3>
                    <div class="viz-container">
                        <img src="risk_scores.png" alt="Risk Scores" style="max-width:100%;">
                    </div>
                </div>
                
                <div class="viz-section">
                    <h3>Feature Importance</h3>
                    <div class="viz-container">
                        <img src="feature_importance.png" alt="Feature Importance" style="max-width:100%;">
                    </div>
                </div>
                
                <footer>
                    <p>MemoTag Speech Intelligence Module - Cognitive Analysis Report</p>
                    <p>© 2023 MemoTag Health Analytics</p>
                </footer>
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    def generate_full_report(self, results_df, feature_importance):
        """Generate a full HTML report with all analyses and visualizations."""
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Generate summary statistics
        summary_stats = self.generate_summary_statistics(results_df)
        
        # Set up the report
        report_path = os.path.join(self.output_dir, 'cognitive_analysis_report.html')
        
        # Create HTML content
        html_content = self.generate_html_report(results_df, feature_importance, summary_stats)
        
        # Write the report to file
        with open(report_path, 'w') as f:
            f.write(html_content)
        
        # Export feature importance as CSV for reference
        # Check if feature_importance is a DataFrame or dict
        if hasattr(feature_importance, 'to_csv'):  # It's a DataFrame
            feature_importance.to_csv(os.path.join(self.output_dir, 'feature_importance.csv'))
        else:  # It's a dictionary
            # Convert dict to DataFrame first
            pd.DataFrame(list(feature_importance.items()), 
                         columns=['Feature', 'Importance']).to_csv(
                             os.path.join(self.output_dir, 'feature_importance.csv'), 
                             index=False
                         )
        
        # Create JSON export for potential API use
        json_data = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'sample_count': len(results_df),
            'summary_statistics': summary_stats,
            'feature_importance': feature_importance
        }
        
        with open(os.path.join(self.output_dir, 'analysis_results.json'), 'w') as f:
            json.dump(json_data, f, cls=NumpyEncoder, indent=2)
        
        return report_path

class NumpyEncoder(json.JSONEncoder):
    """Custom encoder for numpy objects"""
    def default(self, obj):
        if isinstance(obj, (np.integer, np.floating, np.bool_)):
            return obj.item()
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)
