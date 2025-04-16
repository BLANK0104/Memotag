from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
import pandas as pd
import json
from datetime import datetime

def get_db_connection():
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'assessment_history.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'assessment_history_viewer_key'

    @app.route('/')
    def index():
        """Show list of tables in the database"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        return render_template('index.html', tables=tables)

    @app.route('/table/<table_name>')
    def view_table(table_name):
        """View contents of a specific table"""
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        offset = (page - 1) * per_page
        
        conn = get_db_connection()
        
        # Get table info (columns)
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Get total count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        total_records = cursor.fetchone()[0]
        total_pages = (total_records + per_page - 1) // per_page
        
        # Get data with pagination
        cursor.execute(f"SELECT * FROM {table_name} LIMIT {per_page} OFFSET {offset}")
        rows = cursor.fetchall()
        
        # Convert rows to list of dicts
        data = []
        for row in rows:
            data.append(dict(row))
        
        conn.close()
        
        return render_template('table.html', 
                              table_name=table_name,
                              columns=columns,
                              data=data,
                              page=page,
                              per_page=per_page,
                              total_pages=total_pages,
                              total_records=total_records)

    @app.route('/search', methods=['GET', 'POST'])
    def search():
        """Search across tables"""
        if request.method == 'POST':
            keyword = request.form.get('keyword', '')
            table = request.form.get('table', 'all')
            date_from = request.form.get('date_from', '')
            date_to = request.form.get('date_to', '')
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Get all tables if not specified
            if table == 'all':
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = [row[0] for row in cursor.fetchall()]
            else:
                tables = [table]
            
            results = {}
            
            for table_name in tables:
                # Get column info
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = [col[1] for col in cursor.fetchall()]
                
                where_clauses = []
                
                # Keyword search on text columns
                if keyword:
                    text_conditions = []
                    for col in columns:
                        try:
                            cursor.execute(f"SELECT typeof({col}) FROM {table_name} LIMIT 1")
                            col_type = cursor.fetchone()
                            if col_type and col_type[0].lower() in ('text', 'string', 'varchar'):
                                text_conditions.append(f"{col} LIKE '%{keyword}%'")
                        except:
                            pass
                    
                    if text_conditions:
                        where_clauses.append(f"({' OR '.join(text_conditions)})")
                
                # Date filtering
                if date_from or date_to:
                    date_columns = [col for col in columns if 'date' in col.lower() or 'time' in col.lower()]
                    
                    for date_col in date_columns:
                        if date_from:
                            where_clauses.append(f"{date_col} >= '{date_from}'")
                        if date_to:
                            where_clauses.append(f"{date_col} <= '{date_to}'")
                
                # Build query
                query = f"SELECT * FROM {table_name}"
                if where_clauses:
                    query += " WHERE " + " AND ".join(where_clauses)
                query += " LIMIT 100"  # Limit results
                
                try:
                    cursor.execute(query)
                    rows = cursor.fetchall()
                    if rows:
                        results[table_name] = [dict(row) for row in rows]
                except Exception as e:
                    print(f"Error querying {table_name}: {e}")
            
            conn.close()
            return render_template('search_results.html', 
                                  results=results, 
                                  keyword=keyword,
                                  table=table,
                                  date_from=date_from, 
                                  date_to=date_to)
        
        # GET request - show search form
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        return render_template('search.html', tables=tables)
    
    # Ensure templates directory exists
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)
            
    return app
