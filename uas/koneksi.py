# koneksi.py

import mysql.connector

# Ganti dengan detail database Anda
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root', # Ganti jika user anda bukan 'root'
    'password': '', # Ganti dengan password MySQL Anda
    'database': 'db_prediksi_stok' # Pastikan nama database sudah benar
}

def connect_db():
    """Membuat koneksi ke database."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        print(f"Error: Gagal terhubung ke database: {err}")
        return None

def fetch_data(query, params=None):
    """Mengambil data dari database."""
    conn = connect_db()
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query, params or ())
            result = cursor.fetchall()
            return result
        except mysql.connector.Error as err:
            print(f"Error saat mengambil data: {err}")
            return []
        finally:
            cursor.close()
            conn.close()
    return []

def execute_query(query, params=None):
    """Menjalankan query DML (INSERT, UPDATE, DELETE)."""
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute(query, params or ())
            conn.commit()
            return cursor.rowcount # Mengembalikan jumlah baris yang terpengaruh
        except mysql.connector.Error as err:
            print(f"Error saat menjalankan query: {err}")
            conn.rollback()
            return 0
        finally:
            cursor.close()
            conn.close()
    return 0