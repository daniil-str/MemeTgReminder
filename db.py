import sqlite3

from config import BASE_DIR


def init_db():
    conn = sqlite3.connect(BASE_DIR / "mydatabase.db")
    cursor = conn.cursor()
    cursor.execute("""
        create table if not exists messages (
            id integer primary key autoincrement,
            chat_id integer,
            user_id integer,
            message_id integer,
            time_of_day TIME);
    """)
    conn.commit()
    cursor.close()
    conn.close()