import sqlite3

DB_PATH = 'subtitles.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS subtitles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id INTEGER,
            path TEXT NOT NULL,
            type TEXT NOT NULL,
            FOREIGN KEY (video_id) REFERENCES videos(id)
        )
    ''')
    conn.commit()
    conn.close()

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
    conn.commit()
    conn.close()

def fetch_all_videos():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, path FROM videos')
    videos = c.fetchall()
    conn.close()
    return videos

def fetch_subtitles_for_video(video_id):
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
    conn.close()
    return subtitles

def delete_video(video_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('DELETE FROM videos WHERE id = ?', (video_id,))
    c.execute('DELETE FROM subtitles WHERE video_id = ?', (video_id,))
    conn.commit()
    conn.close()

def delete_subtitle(subtitle_id):
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
