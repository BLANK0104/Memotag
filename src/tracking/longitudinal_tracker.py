import os
import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from pathlib import Path
import json
import sys

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parents[2]))

class LongitudinalTracker:
    """
    Tracks user speech patterns across multiple sessions to detect changes over time
    """
    
    def __init__(self, db_path=None):
        """Initialize the tracker with database connection"""
        if db_path is None:
            # Default database location
            db_path = Path("data/tracking/assessment_history.db")
            
        # Ensure directory exists
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize the database schema if it doesn't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            name TEXT,
            age INTEGER,
            gender TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create assessments table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS assessments (
            assessment_id TEXT PRIMARY KEY,
            user_id TEXT,
            task_type INTEGER,
            timestamp TIMESTAMP,
            audio_path TEXT,
            transcript TEXT,
            risk_score REAL,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
        ''')
        
        # Create features table for storing all extracted features
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS assessment_features (
            feature_id INTEGER PRIMARY KEY AUTOINCREMENT,
            assessment_id TEXT,
            feature_name TEXT,
            feature_value REAL,
            FOREIGN KEY (assessment_id) REFERENCES assessments(assessment_id)
        )
        ''')
        
        # Create baseline table for storing user-specific baselines
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_baselines (
            baseline_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            feature_name TEXT,
            baseline_value REAL,
            upper_threshold REAL,
            lower_threshold REAL,
            last_updated TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
        ''')
        
        # Create alerts table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            alert_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            assessment_id TEXT,
            feature_name TEXT,
            deviation_value REAL,
            severity INTEGER,  -- 1: low, 2: medium, 3: high
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_reviewed BOOLEAN DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (assessment_id) REFERENCES assessments(assessment_id)
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def register_user(self, user_id, name=None, age=None, gender=None, notes=None):
        """Register a new user or update existing user details"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,))
        user_exists = cursor.fetchone() is not None
        
        if user_exists:
            # Update user
            cursor.execute('''
            UPDATE users 
            SET name = COALESCE(?, name),
                age = COALESCE(?, age),
                gender = COALESCE(?, gender),
                notes = COALESCE(?, notes)
            WHERE user_id = ?
            ''', (name, age, gender, notes, user_id))
        else:
            # Create new user
            cursor.execute('''
            INSERT INTO users (user_id, name, age, gender, notes)
            VALUES (?, ?, ?, ?, ?)
            ''', (user_id, name, age, gender, notes))
        
        conn.commit()
        conn.close()
        return user_id
    
    def store_assessment(self, user_id, features, risk_score, task_type=0, 
                        audio_path=None, transcript=None, assessment_id=None):
        """Store a new assessment for a user"""
        if assessment_id is None:
            assessment_id = f"{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Store assessment
        cursor.execute('''
        INSERT INTO assessments
            (assessment_id, user_id, task_type, timestamp, audio_path, transcript, risk_score)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (assessment_id, user_id, task_type, datetime.now().isoformat(), 
              audio_path, transcript, risk_score))
        
        # Store all features
        feature_values = []
        for feature_name, feature_value in features.items():
            if isinstance(feature_value, (int, float)):  # Store only numeric features
                feature_values.append((assessment_id, feature_name, feature_value))
        
        cursor.executemany('''
        INSERT INTO assessment_features
            (assessment_id, feature_name, feature_value)
        VALUES (?, ?, ?)
        ''', feature_values)
        
        conn.commit()
        
        # Calculate baseline if enough data is available
        self._update_user_baseline(cursor, user_id)
        
        # Check for significant deviations
        self._check_for_deviations(cursor, user_id, assessment_id, features)
        
        conn.commit()
        conn.close()
        
        return assessment_id
    
    def _update_user_baseline(self, cursor, user_id):
        """Update user baseline if enough assessments are available"""
        # Get count of assessments for this user
        cursor.execute('''
        SELECT COUNT(*) FROM assessments WHERE user_id = ?
        ''', (user_id,))
        
        assessment_count = cursor.fetchone()[0]
        
        # Only calculate baseline if we have at least 3 assessments
        if assessment_count < 3:
            return
        
        # Get all features with at least 3 measurements
        cursor.execute('''
        SELECT feature_name, COUNT(*) as count
        FROM assessment_features af
        JOIN assessments a ON af.assessment_id = a.assessment_id
        WHERE a.user_id = ?
        GROUP BY feature_name
        HAVING count >= 3
        ''', (user_id,))
        
        features_to_update = cursor.fetchall()
        
        for feature_name, _ in features_to_update:
            # Get feature values for this user
            cursor.execute('''
            SELECT feature_value
            FROM assessment_features af
            JOIN assessments a ON af.assessment_id = a.assessment_id
            WHERE a.user_id = ? AND feature_name = ?
            ORDER BY a.timestamp DESC
            LIMIT 5
            ''', (user_id, feature_name))
            
            values = [row[0] for row in cursor.fetchall()]
            
            if len(values) >= 3:
                # Calculate baseline (median) and thresholds
                baseline_value = np.median(values)
                std_dev = np.std(values)
                
                # Set thresholds based on 2 standard deviations
                upper_threshold = baseline_value + (2 * std_dev)
                lower_threshold = baseline_value - (2 * std_dev)
                
                # Update or insert baseline
                cursor.execute('''
                INSERT OR REPLACE INTO user_baselines
                    (user_id, feature_name, baseline_value, upper_threshold, 
                     lower_threshold, last_updated)
                VALUES (?, ?, ?, ?, ?, ?)
                ''', (user_id, feature_name, baseline_value, upper_threshold, 
                      lower_threshold, datetime.now().isoformat()))
    
    def _check_for_deviations(self, cursor, user_id, assessment_id, features):
        """Check for significant deviations from baseline"""
        # Only check if we have baselines
        cursor.execute('''
        SELECT COUNT(*) FROM user_baselines WHERE user_id = ?
        ''', (user_id,))
        
        if cursor.fetchone()[0] == 0:
            return
        
        # Get all baselines for this user
        cursor.execute('''
        SELECT feature_name, baseline_value, upper_threshold, lower_threshold
        FROM user_baselines
        WHERE user_id = ?
        ''', (user_id,))
        
        baselines = {row[0]: {"baseline": row[1], "upper": row[2], "lower": row[3]} 
                   for row in cursor.fetchall()}
        
        # Check each feature for deviations
        alerts = []
        for feature_name, feature_value in features.items():
            if feature_name in baselines and isinstance(feature_value, (int, float)):
                baseline = baselines[feature_name]
                
                # Calculate z-score
                std_range = (baseline["upper"] - baseline["lower"]) / 4  # Approx 2 std devs
                if std_range > 0:
                    z_score = abs((feature_value - baseline["baseline"]) / std_range)
                    
                    # Determine severity
                    severity = 0
                    if z_score > 3:  # Very significant deviation (>3 std devs)
                        severity = 3
                    elif z_score > 2:  # Significant deviation (>2 std devs)
                        severity = 2
                    elif z_score > 1.5:  # Minor deviation (>1.5 std devs)
                        severity = 1
                    
                    if severity > 0:
                        deviation = feature_value - baseline["baseline"]
                        alerts.append((user_id, assessment_id, feature_name, 
                                      deviation, severity))
        
        # Store alerts
        if alerts:
            cursor.executemany('''
            INSERT INTO alerts
                (user_id, assessment_id, feature_name, deviation_value, severity)
            VALUES (?, ?, ?, ?, ?)
            ''', alerts)
    
    def get_user_history(self, user_id, feature_names=None, days=90):
        """Get historical assessment data for a user"""
        conn = sqlite3.connect(self.db_path)
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Build query for selected features or all features
        if feature_names:
            feature_filter = f"AND af.feature_name IN ({','.join(['?']*len(feature_names))})"
            params = [user_id, start_date.isoformat(), end_date.isoformat()] + feature_names
        else:
            feature_filter = ""
            params = [user_id, start_date.isoformat(), end_date.isoformat()]
            
        query = f'''
        SELECT a.timestamp, a.task_type, a.risk_score, af.feature_name, af.feature_value
        FROM assessments a
        JOIN assessment_features af ON a.assessment_id = af.assessment_id
        WHERE a.user_id = ? AND a.timestamp BETWEEN ? AND ? {feature_filter}
        ORDER BY a.timestamp
        '''
        
        # Execute query
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        
        # Convert timestamp to datetime
        if not df.empty:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
        return df
    
    def get_user_baselines(self, user_id):
        """Get current baseline values for a user"""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
        SELECT feature_name, baseline_value, upper_threshold, lower_threshold, last_updated
        FROM user_baselines
        WHERE user_id = ?
        '''
        
        df = pd.read_sql_query(query, conn, params=[user_id])
        conn.close()
        
        return df
    
    def get_alerts(self, user_id=None, days=30, severity=None, unreviewed_only=False):
        """Get alerts for a user or all users"""
        conn = sqlite3.connect(self.db_path)
        
        # Build query conditions
        conditions = []
        params = []
        
        if user_id:
            conditions.append("al.user_id = ?")
            params.append(user_id)
            
        if days:
            conditions.append("al.timestamp >= ?")
            params.append((datetime.now() - timedelta(days=days)).isoformat())
            
        if severity:
            conditions.append("al.severity >= ?")
            params.append(severity)
            
        if unreviewed_only:
            conditions.append("al.is_reviewed = 0")
            
        # Combine conditions
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        query = f'''
        SELECT al.alert_id, al.user_id, u.name, al.assessment_id, al.feature_name, 
               al.deviation_value, al.severity, al.timestamp, al.is_reviewed
        FROM alerts al
        JOIN users u ON al.user_id = u.user_id
        WHERE {where_clause}
        ORDER BY al.severity DESC, al.timestamp DESC
        '''
        
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        
        return df
        
    def mark_alert_reviewed(self, alert_id):
        """Mark an alert as reviewed"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("UPDATE alerts SET is_reviewed = 1 WHERE alert_id = ?", (alert_id,))
        
        conn.commit()
        conn.close()
        
    def generate_trend_report(self, user_id, output_path=None, days=90):
        """Generate a visual report showing trends over time"""
        if output_path is None:
            output_path = Path("reports/trends")
            output_path.mkdir(exist_ok=True, parents=True)
            
        # Get historical data
        history_df = self.get_user_history(user_id, days=days)
        baselines_df = self.get_user_baselines(user_id)
        alerts_df = self.get_alerts(user_id, days=days)
        
        if history_df.empty:
            return None
            
        # Get user information
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name, age, gender FROM users WHERE user_id = ?", (user_id,))
        user_info = cursor.fetchone()
        conn.close()
        
        user_name = user_info[0] if user_info and user_info[0] else user_id
            
        # Create pivot table for key features over time
        key_features = ['hesitation_ratio', 'speech_rate_wpm', 'word_finding_difficulty_count',
                       'acoustic_vocal_stability', 'risk_score']
        
        timestamps = history_df['timestamp'].unique()
        
        # Prepare for visualization
        trends = {}
        for feature in key_features:
            feature_data = history_df[history_df['feature_name'] == feature]
            if not feature_data.empty:
                trends[feature] = feature_data[['timestamp', 'feature_value']].set_index('timestamp')
        
        # Also include risk score
        risk_scores = history_df[['timestamp', 'risk_score']].drop_duplicates().set_index('timestamp')
        
        # Create trend plots
        plt.figure(figsize=(12, 15))
        plt.subplots_adjust(hspace=0.4)
        
        # Plot risk score trend
        plt.subplot(len(trends) + 1, 1, 1)
        plt.title(f"Cognitive Risk Score Trend - {user_name}")
        plt.plot(risk_scores.index, risk_scores['risk_score'], 'r-o')
        plt.axhline(y=0.3, color='g', linestyle='--', alpha=0.5)
        plt.axhline(y=0.6, color='r', linestyle='--', alpha=0.5)
        plt.ylabel('Risk Score')
        plt.ylim(0, 1)
        
        # Plot feature trends
        for i, (feature, data) in enumerate(trends.items(), 2):
            plt.subplot(len(trends) + 1, 1, i)
            
            # Get baseline for this feature if available
            baseline_row = baselines_df[baselines_df['feature_name'] == feature]
            
            plt.plot(data.index, data['feature_value'], 'b-o')
            plt.title(f"{feature.replace('_', ' ').title()}")
            
            # Add baseline and thresholds if available
            if not baseline_row.empty:
                baseline = baseline_row.iloc[0]
                plt.axhline(y=baseline['baseline_value'], color='g', linestyle='-', alpha=0.5)
                plt.axhline(y=baseline['upper_threshold'], color='r', linestyle='--', alpha=0.5)
                plt.axhline(y=baseline['lower_threshold'], color='r', linestyle='--', alpha=0.5)
                
            plt.ylabel('Value')
            
        # Save the plot
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = os.path.join(output_path, f"trend_report_{user_id}_{timestamp}.png")
        plt.tight_layout()
        plt.savefig(report_path)
        plt.close()
        
        return report_path
