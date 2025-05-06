import sqlite3
import datetime

DB_NAME = "image_similarity.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comparisons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image1_name TEXT,
            image2_name TEXT,
            image1_blob BLOB,
            image2_name TEXT,
            image2_blob BLOB,
            similarity REAL,
            result TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

def insert_result(image1_name, image1_blob, image2_name, image2_blob, score, result):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
        INSERT INTO comparisons (image1_name, image1_blob, image2_name, image2_blob, similarity, result, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (image1_name, image1_blob, image2_name, image2_blob, score, result, timestamp))
    conn.commit()
    conn.close()

