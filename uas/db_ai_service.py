import mysql.connector
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from datetime import datetime, timedelta

# --- 1. KONFIGURASI DATABASE ---
DB_CONFIG = {
    'user': 'root',       # Ganti dengan username DB Anda
    'password': '', # Ganti dengan password DB Anda
    'host': 'localhost',
    'database': 'db_prediksi_stok' # Pastikan nama DB sesuai
}

def connect_db():
    """Membuat dan mengembalikan objek koneksi database."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        print(f"Error Koneksi Database: {err}")
        return None

# --- 2. OPERASI CRUD DASAR (Contoh untuk Barang) ---
def get_all_barang():
    """Mengambil semua data barang."""
    conn = connect_db()
    if not conn: return []
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM barang")
    result = cursor.fetchall()
    conn.close()
    return result

def update_stok(id_barang, qty_perubahan, jenis_transaksi):
    """Mengupdate stok barang setelah transaksi."""
    conn = connect_db()
    if not conn: return False
    cursor = conn.cursor()
    
    # Logic penambahan/pengurangan stok
    if jenis_transaksi == 'masuk':
        sql = "UPDATE barang SET stok_saat_ini = stok_saat_ini + %s WHERE id_barang = %s"
    elif jenis_transaksi == 'keluar':
        sql = "UPDATE barang SET stok_saat_ini = stok_saat_ini - %s WHERE id_barang = %s"
    else:
        return False # Tipe transaksi tidak valid

    try:
        cursor.execute(sql, (qty_perubahan, id_barang))
        conn.commit()
        return True
    except mysql.connector.Error as err:
        print(f"Error Update Stok: {err}")
        conn.rollback()
        return False
    finally:
        conn.close()

# --- 3. ALGORITMA PENGOLAHAN DATA (Moving Average) ---
def calculate_moving_average_sales(df_sales, window=7):
    """Menghitung rata-rata penjualan bergerak (Moving Average)."""
    if df_sales.empty:
        return 0
    # Pastikan data terurut berdasarkan tanggal
    df_sales = df_sales.sort_values(by='tanggal_transaksi')
    # Hitung MA dari kolom jumlah_barang
    df_sales['MA'] = df_sales['jumlah_barang'].rolling(window=window).mean()
    # Mengembalikan rata-rata terbaru (dari window terakhir)
    return df_sales['MA'].iloc[-1] if not df_sales['MA'].empty else 0

# --- 4. INTEGRASI AI (Prediksi Stok Habis - Linear Regression) ---
def predict_stok_habis(id_barang):
    """
    Mengambil data penjualan barang, melatih model Regresi Linear,
    dan memprediksi tanggal stok akan mencapai 0.
    """
    conn = connect_db()
    if not conn: 
        return "Gagal Koneksi DB", None, 0

    # 4.1 Mengambil Data Penjualan Historis
    sql = """
    SELECT 
        tanggal_transaksi, 
        jumlah_barang 
    FROM transaksi 
    WHERE id_barang = %s AND jenis_transaksi = 'keluar'
    ORDER BY tanggal_transaksi
    """
    df = pd.read_sql(sql, conn, params=(id_barang,))
    conn.close()
    
    if len(df) < 5: # Minimal 5 data point untuk training sederhana
        return "Data Penjualan Kurang", None, 0

    # Ambil stok saat ini
    stok_saat_ini = get_barang_stok(id_barang)
    if stok_saat_ini is None:
        return "Barang Tidak Ditemukan", None, 0

    # 4.2 Data Preprocessing (Mengubah Tanggal menjadi Hari ke-N)
    # Jadikan tanggal pertama sebagai titik awal (Hari ke-0)
    df['tanggal_transaksi'] = pd.to_datetime(df['tanggal_transaksi'])
    start_date = df['tanggal_transaksi'].min()
    df['hari_ke'] = (df['tanggal_transaksi'] - start_date).dt.days

    X = df[['hari_ke']] # Input: Hari ke-N
    y = df['jumlah_barang'] # Output: Jumlah penjualan

    # 4.3 Training Model Regresi Linear
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    # 4.4 Prediksi Penjualan Rata-rata
    # Prediksi penjualan untuk hari terakhir yang ada di data (untuk menghitung rata-rata)
    latest_day = df['hari_ke'].max()
    predicted_sales = model.predict([[latest_day]])[0] # Rata-rata prediksi penjualan harian saat ini

    # 4.5 Menghitung Stok Habis
    # Days to zero = Current Stock / (Predicted Sales per day)
    # Tambahkan pencegahan bagi nol
    if predicted_sales <= 0.5: # Jika prediksi penjualan mendekati nol, anggap penjualan stabil 0.5 unit/hari
        days_to_zero = stok_saat_ini / 0.5 
    else:
        days_to_zero = stok_saat_ini / predicted_sales
    
    days_to_zero = max(1, days_to_zero) # Minimal 1 hari

    # 4.6 Menentukan Tanggal Prediksi
    predicted_date = datetime.now() + timedelta(days=days_to_zero)

    ma_sales = calculate_moving_average_sales(df)

    return "Prediksi Sukses", predicted_date.strftime('%d %B %Y'), round(ma_sales, 2), round(predicted_sales, 2)

# Helper untuk mengambil stok saat ini
def get_barang_stok(id_barang):
    conn = connect_db()
    if not conn: return None
    cursor = conn.cursor()
    cursor.execute("SELECT stok_saat_ini FROM barang WHERE id_barang = %s", (id_barang,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None