import sqlite3
import os
import pandas as pd
from datetime import datetime

class AssessmentHistoryViewer:
    def __init__(self, db_path=None):
        if db_path is None:
            self.db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'assessment_history.db')
        else:
            self.db_path = db_path
        self.conn = None
        
    def connect(self):
        """Connect to the assessment history database."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            print(f"Connected to {self.db_path}")
            return True
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")
            return False
            
    def get_tables(self):
        """Get all tables in the database."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        return [table[0] for table in tables]
    
    def get_table_info(self, table_name):
        """Get column information for a table."""
        cursor = self.conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        return cursor.fetchall()
        
    def get_assessment_history(self, limit=100):
        """Get assessment history data."""
        tables = self.get_tables()
        results = {}
        
        for table in tables:
            try:
                query = f"SELECT * FROM {table} LIMIT {limit}"
                df = pd.read_sql_query(query, self.conn)
                results[table] = df
                print(f"\nTable: {table} ({len(df)} records)")
                print("-" * 40)
                print(df.head())
            except Exception as e:
                print(f"Error querying table {table}: {e}")
                
        return results
    
    def search_assessments(self, keyword=None, date_from=None, date_to=None, table=None):
        """Search assessment history with filters."""
        if not self.conn:
            print("Not connected to database")
            return None
            
        if table is None:
            tables = self.get_tables()
        else:
            tables = [table]
            
        results = {}
        
        for table_name in tables:
            try:
                # Get table columns
                columns = [col[1] for col in self.get_table_info(table_name)]
                
                where_clauses = []
                if keyword:
                    text_columns = []
                    for col in columns:
                        cursor = self.conn.cursor()
                        try:
                            # Check column type by running a test query
                            cursor.execute(f"SELECT typeof({col}) FROM {table_name} LIMIT 1")
                            col_type = cursor.fetchone()
                            if col_type and col_type[0].lower() in ('text', 'string', 'varchar'):
                                text_columns.append(col)
                        except:
                            pass
                    
                    if text_columns:
                        text_conditions = [f"{col} LIKE '%{keyword}%'" for col in text_columns]
                        where_clauses.append(f"({' OR '.join(text_conditions)})")
                
                # Add date range filters if date columns exist
                date_columns = []
                for col in columns:
                    if "date" in col.lower() or "time" in col.lower():
                        date_columns.append(col)
                
                if date_columns and (date_from or date_to):
                    for date_col in date_columns:
                        if date_from:
                            where_clauses.append(f"{date_col} >= '{date_from}'")
                        if date_to:
                            where_clauses.append(f"{date_col} <= '{date_to}'")
                
                # Build the query
                query = f"SELECT * FROM {table_name}"
                if where_clauses:
                    query += " WHERE " + " AND ".join(where_clauses)
                
                # Execute the query
                df = pd.read_sql_query(query, self.conn)
                results[table_name] = df
                
            except Exception as e:
                print(f"Error querying table {table_name}: {e}")
                
        return results
    
    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            print("Connection closed.")
