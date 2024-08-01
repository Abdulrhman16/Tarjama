import sqlite3

<<<<<<< HEAD
DB_PATH = 'subtitles.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
=======
def initialize_db():
    conn = sqlite3.connect('tarjama.db')
    cursor = conn.cursor()

    # Create videos table
    cursor.execute('''
>>>>>>> parent of 3a8aca8 (version 2.2)
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path TEXT NOT NULL,
            description TEXT
        )
    ''')

    # Create subtitles table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subtitles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id INTEGER,
            file_path TEXT NOT NULL,
            type TEXT,
            FOREIGN KEY(video_id) REFERENCES videos(id)
        )
    ''')

<<<<<<< HEAD
def insert_video(path):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO videos (path) VALUES (?)', (path,))
    conn.commit()
    conn.close()

def insert_subtitle(video_id, path, type):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO subtitles (video_id, path, type) VALUES (?, ?, ?)', (video_id, path, type))
=======
>>>>>>> parent of 3a8aca8 (version 2.2)
    conn.commit()
    conn.close()

def fetch_all_videos():
<<<<<<< HEAD
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, path FROM videos')
    videos = c.fetchall()
=======
    conn = sqlite3.connect('tarjama.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM videos")
    videos = cursor.fetchall()
>>>>>>> parent of 3a8aca8 (version 2.2)
    conn.close()
    return videos

def fetch_subtitles_for_video(video_id):
<<<<<<< HEAD
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, path FROM subtitles WHERE video_id = ?', (video_id,))
    subtitles = c.fetchall()
    conn.close()
    return subtitles

def fetch_all_subtitles():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, path, type FROM subtitles')
    subtitles = c.fetchall()
=======
    conn = sqlite3.connect('tarjama.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, file_path FROM subtitles WHERE video_id=?", (video_id,))
    subtitles = cursor.fetchall()
>>>>>>> parent of 3a8aca8 (version 2.2)
    conn.close()
    return subtitles

def delete_video(video_id):
<<<<<<< HEAD
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('DELETE FROM videos WHERE id = ?', (video_id,))
    c.execute('DELETE FROM subtitles WHERE video_id = ?', (video_id,))
=======
    conn = sqlite3.connect('tarjama.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM videos WHERE id=?", (video_id,))
    cursor.execute("DELETE FROM subtitles WHERE video_id=?", (video_id,))
>>>>>>> parent of 3a8aca8 (version 2.2)
    conn.commit()
    conn.close()

def delete_subtitle(subtitle_id):
<<<<<<< HEAD
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('DELETE FROM subtitles WHERE id = ?', (subtitle_id,))
    conn.commit()
    conn.close()

def fetch_video_path(video_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT path FROM videos WHERE id = ?', (video_id,))
    result = c.fetchone()
    conn.close()
    if result:
        return result[0]
    return None

def fetch_subtitle_path(subtitle_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT path FROM subtitles WHERE id = ?', (subtitle_id,))
    result = c.fetchone()
    conn.close()
    if result:
        return result[0]
    return None

init_db()
=======
    conn = sqlite3.connect('tarjama.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM subtitles WHERE id=?", (subtitle_id,))
    conn.commit()
    conn.close()

def insert_subtitle(video_id, file_path, subtitle_type):
    conn = sqlite3.connect('tarjama.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO subtitles (video_id, file_path, type) VALUES (?, ?, ?)",
                   (video_id, file_path, subtitle_type))
    conn.commit()
    conn.close()
>>>>>>> parent of 3a8aca8 (version 2.2)
