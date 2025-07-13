# db.py

import sqlite3
import os
import json # For handling JSON data like tags and theme_analysis

# Assuming Config is accessible or passed
# For now, we'll hardcode paths, but will make it dynamic with app context later
DATABASE_DIR = os.path.join(os.getcwd(), 'data')
if not os.path.exists(DATABASE_DIR):
    os.makedirs(DATABASE_DIR)
SQLITE_DB_PATH = os.path.join(DATABASE_DIR, 'datanest.db')
# CHROMADB_PATH is handled by analysis.py or will be initialized separately

def get_db_connection():
    conn = sqlite3.connect(SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row # This allows access to columns by name
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            link TEXT NOT NULL,
            title TEXT NOT NULL,
            tags TEXT, -- Stored as JSON string
            type TEXT NOT NULL, -- 'article', 'pdf', 'video', 'manual'
            date_added TEXT NOT NULL,
            raw_content TEXT, -- The extracted text content for analysis
            summary TEXT, -- LLM-generated summary
            ai_analysis TEXT, -- Full LLM analysis based on your prompt
            novelty_score REAL, -- Will be set after analysis if useful
            theme_analysis TEXT, -- JSON string of categorized insights per theme
            status TEXT NOT NULL, -- 'new', 'pending_analysis', 'analyzed_for_brief', 'archived', 'master_knowledge'
            thumbnail_url TEXT,
            feedback_notes TEXT -- For your manual feedback
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bedrock_knowledge (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            last_updated TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def add_source_to_db(link, title, tags, source_type, raw_content, thumbnail_url, summary="", ai_analysis="", novelty_score=None, theme_analysis="", status='new', feedback_notes=""):
    conn = get_db_connection()
    cursor = conn.cursor()
    date_added = sqlite3.Date.today().isoformat() # YYYY-MM-DD format

    cursor.execute('''
        INSERT INTO sources (link, title, tags, type, date_added, raw_content, summary, ai_analysis, novelty_score, theme_analysis, status, thumbnail_url, feedback_notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (link, title, json.dumps(tags), source_type, date_added, raw_content, summary, ai_analysis, novelty_score, json.dumps(theme_analysis), status, thumbnail_url, feedback_notes))
    conn.commit()
    source_id = cursor.lastrowid
    conn.close()
    return source_id

def get_sources_from_db(source_type_filter='All', status_filter=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM sources"
    params = []
    conditions = []

    if source_type_filter != 'All':
        conditions.append("type = ?")
        params.append(source_type_filter)

    if status_filter:
        conditions.append("status = ?")
        params.append(status_filter)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY date_added DESC, id DESC" # Order by newest first

    cursor.execute(query, params)
    sources_raw = cursor.fetchall()
    conn.close()

    sources = []
    for s_raw in sources_raw:
        s = dict(s_raw)
        # Convert JSON strings back to Python objects
        if s['tags']:
            s['tags'] = json.loads(s['tags'])
        else:
            s['tags'] = []
        if s['theme_analysis']:
            s['theme_analysis'] = json.loads(s['theme_analysis'])
        else:
            s['theme_analysis'] = {} # Default to empty dict if no analysis

        sources.append(s)
    return sources

def get_bedrock_content_from_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT content FROM bedrock_knowledge ORDER BY last_updated DESC LIMIT 1")
    result = cursor.fetchone()
    conn.close()
    return result['content'] if result else ""

def update_bedrock_content_in_db(content):
    conn = get_db_connection()
    cursor = conn.cursor()
    # Delete existing bedrock content (or manage versions, for now, simple overwrite)
    cursor.execute("DELETE FROM bedrock_knowledge")
    cursor.execute("INSERT INTO bedrock_knowledge (content, last_updated) VALUES (?, ?)",
                   (content, sqlite3.Date.today().isoformat()))
    conn.commit()
    conn.close()

def update_source_status(source_id, new_status):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE sources SET status = ? WHERE id = ?", (new_status, source_id))
    conn.commit()
    conn.close()

def update_source_analysis(source_id, summary, ai_analysis, novelty_score, theme_analysis, status):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE sources
        SET summary = ?, ai_analysis = ?, novelty_score = ?, theme_analysis = ?, status = ?
        WHERE id = ?
    ''', (summary, ai_analysis, novelty_score, json.dumps(theme_analysis), status, source_id))
    conn.commit()
    conn.close()
