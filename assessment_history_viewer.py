import sqlite3
import os
import pandas as pd
from datetime import datetime
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from tracking.history_viewer import AssessmentHistoryViewer

def main():
    viewer = AssessmentHistoryViewer()
    if viewer.connect():
        print("\n=== ASSESSMENT HISTORY DATABASE VIEWER ===\n")
        
        # List available tables
        tables = viewer.get_tables()
        print(f"Available tables: {', '.join(tables)}")
        
        # Show all assessment history
        print("\n=== SHOWING RECENT ASSESSMENT HISTORY ===")
        viewer.get_assessment_history(limit=10)
        
        # Example of searching
        print("\n=== SEARCH EXAMPLE ===")
        print("Searching for assessments with keyword 'important'")
        search_results = viewer.search_assessments(keyword="important")
        for table, df in search_results.items():
            if not df.empty:
                print(f"\nResults from {table} ({len(df)} matches):")
                print(df)
        
        viewer.close()

if __name__ == "__main__":
    main()
