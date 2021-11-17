import sqlite3

def drop_table(conn):
    # Удаление таблицы
    print('Droping tables...')
    cursor = conn.cursor()
    cursor.execute("""
        DROP TABLE last_request
        """) 


def init_table(conn):
    # инициализация таблиц
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE last_request
        (sender_id text, message text, is_busy boolean)
        """)
    cursor.execute("""
        INSERT INTO last_request
        VALUES ('NULL', 'NULL', False)
        """)
    conn.commit()

def read_data(conn):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT *
        FROM last_request
        """)
    return cursor.fetchone()

def set_data(conn, *args, **kwarg):
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE last_request
        SET sender_id = ?, message = ?, is_busy = ?
        """, args)
    conn.commit()


if __name__ == "__main__":
    print("Connecting to database")
    conn = sqlite3.connect(':memory:')
    init_table(conn)
    conn.close()
    pass