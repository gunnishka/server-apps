import sqlite3

DATABASE = "todos.db"


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def create_tables():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS todos (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT    NOT NULL,
            description TEXT    NOT NULL,
            completed   INTEGER NOT NULL DEFAULT 0   -- 0=False, 1=True
        )
    """)
    conn.commit()
    conn.close()
    print("Таблица todos создана")


if __name__ == "__main__":
    create_tables()