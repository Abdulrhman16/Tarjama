import sqlite3

def initialize_db():
    conn = sqlite3.connect('tarjama.db')
    cursor = conn.cursor()

    # Create videos table
    cursor.execute('''
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

    conn.commit()
    conn.close()

def fetch_all_videos():
    conn = sqlite3.connect('tarjama.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM videos")
    videos = cursor.fetchall()
    conn.close()
    return videos

def fetch_subtitles_for_video(video_id):
    conn = sqlite3.connect('tarjama.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, file_path FROM subtitles WHERE video_id=?", (video_id,))
    subtitles = cursor.fetchall()
    conn.close()
    return subtitles

def delete_video(video_id):
    conn = sqlite3.connect('tarjama.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM videos WHERE id=?", (video_id,))
    cursor.execute("DELETE FROM subtitles WHERE video_id=?", (video_id,))
    conn.commit()
    conn.close()

def delete_subtitle(subtitle_id):
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
