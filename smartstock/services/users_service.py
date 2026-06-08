from smartstock.database.connection import get_connection
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO Users (username, password_hash)
            VALUES (?, ?)
        """, (username, hash_password(password)))
        conn.commit()
        success = True
    except:
        success = False

    conn.close()
    return success

def authenticate_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT password_hash FROM Users WHERE username = ?
    """, (username,))
    result = cursor.fetchone()

    conn.close()

    if result is None:
        return False

    return result[0] == hash_password(password)
