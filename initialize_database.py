import sqlite3
import os
import datetime
import random
import numpy as np

def initialize_database():
    """Initialize assessment history database with tables and sample data"""
    db_path = os.path.join(os.path.dirname(__file__), 'assessment_history.db')
    
    print(f"Initializing database at {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        age INTEGER,
        gender TEXT,
        profile_created_date TEXT
    )
    ''')
    
    # Create assessments table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS assessments (
        assessment_id INTEGER PRIMARY KEY,
        user_id INTEGER,
        assessment_date TEXT,
        task_type TEXT,
        duration_seconds REAL,
        completion_status TEXT,
        notes TEXT,
        FOREIGN KEY (user_id) REFERENCES users (user_id)
    )
    ''')
    
    # Create speech_features table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS speech_features (
        feature_id INTEGER PRIMARY KEY,
        assessment_id INTEGER,
        hesitation_count INTEGER,
        pause_count INTEGER,
        pause_duration_avg REAL,
        speech_rate REAL,
        word_recall_issues INTEGER,
        vocal_tremor REAL,
        pitch_variation REAL,
        articulation_precision REAL,
        FOREIGN KEY (assessment_id) REFERENCES assessments (assessment_id)
    )
    ''')
    
    # Create risk_scores table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS risk_scores (
        score_id INTEGER PRIMARY KEY,
        assessment_id INTEGER,
        risk_score REAL,
        linguistic_risk REAL,
        acoustic_risk REAL,
        overall_assessment TEXT,
        recommendations TEXT,
        FOREIGN KEY (assessment_id) REFERENCES assessments (assessment_id)
    )
    ''')
    
    # Check if tables are empty before inserting sample data
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    
    if user_count == 0:
        print("Adding sample data...")
        # Insert sample users
        sample_users = [
            (1, "John Smith", 72, "Male", "2023-01-15"),
            (2, "Mary Johnson", 68, "Female", "2023-02-03"),
            (3, "Robert Williams", 75, "Male", "2023-01-22"),
            (4, "Patricia Brown", 70, "Female", "2023-03-05"),
            (5, "James Davis", 65, "Male", "2023-02-18")
        ]
        cursor.executemany("INSERT INTO users VALUES (?, ?, ?, ?, ?)", sample_users)
        
        # Generate sample assessments
        assessments = []
        task_types = ["Counting Backwards", "Animal Naming", "Narrative Description", 
                      "Sentence Completion", "Orientation Questions"]
        completion_statuses = ["Completed", "Partially Completed", "Interrupted", "Completed"]
        
        assessment_id = 1
        for user_id in range(1, 6):
            # Generate 3-5 assessments per user
            for _ in range(random.randint(3, 5)):
                assessment_date = datetime.datetime(2023, random.randint(1, 12), 
                                                 random.randint(1, 28)).strftime("%Y-%m-%d")
                task_type = random.choice(task_types)
                duration = round(random.uniform(30.0, 180.0), 1)
                status = random.choice(completion_statuses)
                notes = f"Regular assessment for {task_type} task" if status == "Completed" else "Some issues encountered"
                
                assessments.append((assessment_id, user_id, assessment_date, task_type, 
                                   duration, status, notes))
                assessment_id += 1
        
        cursor.executemany("INSERT INTO assessments VALUES (?, ?, ?, ?, ?, ?, ?)", assessments)
        
        # Generate sample speech features
        speech_features = []
        for feature_id in range(1, assessment_id):
            hesitation = random.randint(0, 15)
            pause_count = random.randint(3, 20)
            pause_duration = round(random.uniform(0.2, 2.0), 2)
            speech_rate = round(random.uniform(80.0, 180.0), 1)
            recall_issues = random.randint(0, 8)
            tremor = round(random.uniform(0.0, 0.5), 2)
            pitch = round(random.uniform(0.1, 0.9), 2)
            articulation = round(random.uniform(0.3, 1.0), 2)
            
            speech_features.append((feature_id, feature_id, hesitation, pause_count, 
                                  pause_duration, speech_rate, recall_issues, 
                                  tremor, pitch, articulation))
        
        cursor.executemany("INSERT INTO speech_features VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                          speech_features)
        
        # Generate sample risk scores
        risk_scores = []
        assessment_texts = ["No significant cognitive concerns detected", 
                         "Some speech patterns may warrant further assessment", 
                         "Consider professional cognitive assessment"]
        
        for score_id in range(1, assessment_id):
            linguistic_risk = round(random.uniform(0.0, 1.0), 2)
            acoustic_risk = round(random.uniform(0.0, 1.0), 2)
            risk_score = round((linguistic_risk + acoustic_risk) / 2, 2)
            
            if risk_score < 0.3:
                assessment = assessment_texts[0]
            elif risk_score < 0.6:
                assessment = assessment_texts[1]
            else:
                assessment = assessment_texts[2]
                
            recommendations = "Continue regular monitoring" if risk_score < 0.3 else \
                            "Schedule follow-up assessment in 1 month" if risk_score < 0.6 else \
                            "Consult with healthcare professional"
            
            risk_scores.append((score_id, score_id, risk_score, linguistic_risk, 
                              acoustic_risk, assessment, recommendations))
        
        cursor.executemany("INSERT INTO risk_scores VALUES (?, ?, ?, ?, ?, ?, ?)", risk_scores)
    
    conn.commit()
    conn.close()
    
    print("Database initialization completed. Tables created:")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    for table in tables:
        print(f" - {table[0]}")
        cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
        count = cursor.fetchone()[0]
        print(f"   ({count} records)")
    conn.close()
    
    return True

if __name__ == "__main__":
    initialize_database()
