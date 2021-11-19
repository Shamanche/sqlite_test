import sqlite3

global conn 
conn = sqlite3.connect(':memory:')

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

def read_data():
    cursor = conn.cursor()
    cursor.execute("""
        SELECT *
        FROM last_request
        """)
    data = cursor.fetchone()
    return {'sender_id': data[0], 'message': data[0], 'is_busy':bool(data[2]) }

def set_data(conn, *args, **kwarg):
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE last_request
        SET sender_id = ?, message = ?, is_busy = ?
        """, args)
    conn.commit()


if __name__ == "__main__":
    print("Connecting to database")
    
    init_table(conn)
    x = read_data(conn)
    conn.close()
    pass