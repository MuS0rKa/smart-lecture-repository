import sqlite3

def get_connection():
    return sqlite3.connect("study_buddy.db")

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Добавили user_id для привязки лекции к человеку
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lectures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL
        )
    ''')
    
    # Добавили user_id для привязки истории
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            lecture_id INTEGER,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (lecture_id) REFERENCES lectures (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def add_lecture(user_id, title, content):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO lectures (user_id, title, content) VALUES (?, ?, ?)", (user_id, title, content))
    conn.commit()
    conn.close()

def get_lectures(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title FROM lectures WHERE user_id = ?", (user_id,))
    lectures = cursor.fetchall()
    conn.close()
    return lectures

def save_interaction(user_id, lecture_id, question, answer):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO history (user_id, lecture_id, question, answer) VALUES (?, ?, ?, ?)",
        (user_id, lecture_id, question, answer)
    )
    conn.commit()
    conn.close()

def get_history(user_id, lecture_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT question, answer FROM history WHERE user_id = ? AND lecture_id = ?", (user_id, lecture_id))
    history = cursor.fetchall()
    conn.close()
    return history

def get_lecture_content(user_id, lecture_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT content FROM lectures WHERE user_id = ? AND id = ?", (user_id, lecture_id))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None