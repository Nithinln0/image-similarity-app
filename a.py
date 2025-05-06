import sqlite3
import bcrypt
def init_user_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')
    conn.commit()
    
    # Print existing users for debugging
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    print("Existing users:", users)  # This will show current usernames
    conn.close()
