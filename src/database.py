import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '../data/chatbot.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            user_query TEXT,
            bot_response TEXT,
            match_score REAL,
            feedback INTEGER,
            session_id TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS escalations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            user_query TEXT,
            suggested_answer TEXT
        )
    ''')
    conn.commit()
    conn.close()

def log_interaction(session_id, query, response, score):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO interactions (session_id, user_query, bot_response, match_score) VALUES (?, ?, ?, ?)",
              (session_id, query, response, score))
    conn.commit()
    interaction_id = c.lastrowid
    conn.close()
    return interaction_id

def log_feedback(interaction_id, feedback):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE interactions SET feedback = ? WHERE id = ?", (feedback, interaction_id))
    conn.commit()
    conn.close()

def log_escalation(query, suggestion=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO escalations (user_query, suggested_answer) VALUES (?, ?)", (query, suggestion))
    conn.commit()
    conn.close()
