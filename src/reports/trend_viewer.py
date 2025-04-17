import os
import sys
import argparse
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parents[2]))
from src.tracking.longitudinal_tracker import LongitudinalTracker

def list_users():
    """List all users in the database"""
    tracker = LongitudinalTracker()
    
    # Connect to the database
    conn = sqlite3.connect(tracker.db_path)
    cursor = conn.cursor()
    
    # Get users with assessment counts
    cursor.execute('''
    SELECT u.user_id, u.name, u.age, u.gender, 
           COUNT(DISTINCT a.assessment_id) as assessments,
           MAX(a.timestamp) as last_assessment
    FROM users u
    LEFT JOIN assessments a ON u.user_id = a.user_id
    GROUP BY u.user_id
    ORDER BY last_assessment DESC
    ''')
    
    users = cursor.fetchall()
    conn.close()
    
    if not users:
        print("No users found in the database.")
        return
    
    # Display users in a table
    print("\n{:<20} {:<20} {:<5} {:<8} {:<12} {:<20}".format(
        "User ID", "Name", "Age", "Gender", "Assessments", "Last Assessment"))
    print("-" * 80)
    
    for user in users:
        user_id, name, age, gender, assessment_count, last_assessment = user
        
        name_str = name if name else "N/A"
        age_str = str(age) if age is not None else "N/A"
        gender_str = gender if gender else "N/A"
        last_date = pd.to_datetime(last_assessment).strftime("%Y-%m-%d %H:%M") if last_assessment else "Never"
        
        print("{:<20} {:<20} {:<5} {:<8} {:<12} {:<20}".format(
            user_id, name_str, age_str, gender_str, assessment_count, last_date))

def manage_baseline(user_id, action, days=30):
    """Manage personalized baseline for a specific user"""
    tracker = LongitudinalTracker()
    
    if action == 'create':
        # Create a new baseline for the user based on the specified days
        print(f"Creating baseline for user {user_id} using the past {days} days of data...")
        success, message = tracker.create_baseline(user_id, days=days)
        if success:
            print(f"Baseline created successfully: {message}")
        else:
            print(f"Failed to create baseline: {message}")
    
    elif action == 'view':
        # View the current baseline for the user
        print(f"Fetching baseline data for user {user_id}...")
        baseline_data = tracker.get_baseline(user_id)
        
        if baseline_data is not None and not baseline_data.empty:
            print("\n--- Current Baseline Values ---")
            print(f"Created on: {baseline_data['created_date'].iloc[0]}")
            print(f"Based on data from: {baseline_data['start_date'].iloc[0]} to {baseline_data['end_date'].iloc[0]}")
            print("\nBaseline metrics:")
            
            for feature, value in baseline_data[['feature_name', 'baseline_value', 'variability']].iterrows():
                feature_name = value['feature_name'].replace('_', ' ').title()
                print(f"- {feature_name}: {value['baseline_value']:.2f} (±{value['variability']:.2f})")
        else:
            print(f"No baseline found for user {user_id}. Use 'create' to establish a baseline.")
    
    elif action == 'update':
        # Update the baseline for the user
        print(f"Updating baseline for user {user_id} using the past {days} days of data...")
        success, message = tracker.update_baseline(user_id, days=days)
        if success:
            print(f"Baseline updated successfully: {message}")
        else:
            print(f"Failed to update baseline: {message}")

def view_user_trends(user_id, days=90, use_baseline=True):
    """View trends for a specific user"""
    tracker = LongitudinalTracker()
    
    print(f"\nGenerating trend report for user {user_id} over the past {days} days...")
    report_path = tracker.generate_trend_report(user_id, days=days, use_baseline=use_baseline)
    
    if report_path:
        print(f"Trend report generated: {report_path}")
        
        # Get alerts for this user
        alerts = tracker.get_alerts(user_id, days=days, use_baseline=use_baseline)
        if not alerts.empty:
            print("\nAlerts detected during this period:")
            for _, alert in alerts.iterrows():
                severity = "HIGH" if alert['severity'] == 3 else "MEDIUM" if alert['severity'] == 2 else "LOW"
                feature = alert['feature_name'].replace('_', ' ').title()
                date = pd.to_datetime(alert['timestamp']).strftime('%Y-%m-%d')
                direction = "increase" if alert['deviation_value'] > 0 else "decrease"
                
                # Include baseline reference if available
                if use_baseline and 'baseline_value' in alert:
                    print(f"- [{date}] {severity}: {feature} showed {abs(alert['deviation_value']):.2f} {direction} " 
                          f"(baseline: {alert['baseline_value']:.2f} ±{alert['baseline_variability']:.2f})")
                else:
                    print(f"- [{date}] {severity}: {feature} showed {abs(alert['deviation_value']):.2f} {direction}")
        
        # Display the trend visualization
        try:
            img = plt.imread(report_path)
            plt.figure(figsize=(12, 15))
            plt.imshow(img)
            plt.axis('off')
            plt.title(f"Cognitive Function Trends - User: {user_id}")
            plt.show()
        except Exception as e:
            print(f"Could not display trend report: {e}")
    else:
        print(f"No data found for user {user_id} in the specified time range.")

def main():
    """Main function to run the trend viewer"""
    parser = argparse.ArgumentParser(description="View longitudinal speech analysis trends")
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # List users command
    subparsers.add_parser('list', help='List all users with assessment data')
    
    # View trends command
    view_parser = subparsers.add_parser('view', help='View trends for a specific user')
    view_parser.add_argument('user_id', help='User ID to view trends for')
    view_parser.add_argument('--days', type=int, default=90, help='Number of days to analyze (default: 90)')
    view_parser.add_argument('--no-baseline', action='store_false', dest='use_baseline',
                          help='Disable personalized baseline comparison')
    view_parser.set_defaults(use_baseline=True)
    
    # Baseline management command
    baseline_parser = subparsers.add_parser('baseline', help='Manage personalized baselines')
    baseline_parser.add_argument('user_id', help='User ID to manage baseline for')
    baseline_parser.add_argument('action', choices=['create', 'view', 'update'], 
                              help='Action to perform on the baseline')
    baseline_parser.add_argument('--days', type=int, default=30, 
                              help='Days of data to use for baseline creation/update (default: 30)')
    
    args = parser.parse_args()
    
    if args.command == 'list':
        list_users()
    elif args.command == 'view' and args.user_id:
        view_user_trends(args.user_id, args.days, args.use_baseline)
    elif args.command == 'baseline' and args.user_id:
        manage_baseline(args.user_id, args.action, args.days)
    else:
        parser.print_help()

if __name__ == "__main__":
    import sqlite3  # Import here to avoid issues with circular imports
    main()
