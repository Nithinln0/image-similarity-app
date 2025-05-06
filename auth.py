import sqlite3
import bcrypt

# Initialize user table
def init_user_db():
    try:
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
        conn.close()
        print("User database initialized successfully.")
    except Exception as e:
        print(f"Error initializing user database: {e}")
        raise e

# Register a new user
def register_user(username, password):
    try:
        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed.decode('utf-8')))
        conn.commit()
        conn.close()
        print(f"User {username} registered successfully with hash: {hashed.decode('utf-8')}")
        return True
    except sqlite3.IntegrityError:
        print(f"Username {username} already exists.")
        return False
    except Exception as e:
        print(f"Error registering user: {e}")
        return False

# Authenticate user
def login_user(username, password):
    try:
        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        print(f"Querying database for username: {username}")
        c.execute("SELECT password FROM users WHERE username = ?", (username,))
        row = c.fetchone()
        conn.close()
        if row:
            stored_hashed_pw = row[0]
            print(f"Found user {username} with stored hash: {stored_hashed_pw}")
            hashed_pw = stored_hashed_pw.encode('utf-8') if isinstance(stored_hashed_pw, str) else stored_hashed_pw
            input_password = password.encode('utf-8')
            print(f"Input password (encoded): {input_password}")
            password_match = bcrypt.checkpw(input_password, hashed_pw)
            print(f"Password match for {username}: {password_match}")
            if password_match:
                print(f"User {username} logged in successfully.")
                return True
            else:
                print(f"Invalid password for user {username}. Input password does not match stored hash.")
                return False
        else:
            print(f"User {username} not found in database.")
            return False
    except Exception as e:
        print(f"Error during login for {username}: {e}")
        return False