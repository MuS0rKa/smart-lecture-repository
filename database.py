import sqlite3

def get_connection():
    return sqlite3.connect("study_buddy.db")

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Таблица для хранения учебных материалов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lectures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL
        )
    ''')
    
    # Таблица для хранения истории вопросов и ответов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lecture_id INTEGER,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (lecture_id) REFERENCES lectures (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def add_lecture(title, content):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO lectures (title, content) VALUES (?, ?)", (title, content))
    conn.commit()
    conn.close()

def get_lectures():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title FROM lectures")
    lectures = cursor.fetchall()
    conn.close()
    return lectures

def save_interaction(lecture_id, question, answer):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO history (lecture_id, question, answer) VALUES (?, ?, ?)",
        (lecture_id, question, answer)
    )
    conn.commit()
    conn.close()

def get_history(lecture_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT question, answer FROM history WHERE lecture_id = ?", (lecture_id,))
    history = cursor.fetchall()
    conn.close()
    return history

if __name__ == "__main__":
    init_db()
    print("База данных успешно инициализирована!")