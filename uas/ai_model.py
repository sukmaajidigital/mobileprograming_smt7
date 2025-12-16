# ai_model.py

import pandas as pd
from sklearn.linear_model import LinearRegression
from koneksi import fetch_data
import numpy as np

def prepare_data_for_ai(id_barang):
    """
    Ambil transaksi 'keluar' untuk id_barang dan olah menjadi
    time-series mingguan termasuk Moving Average.
    """
    # 1. Ambil data transaksi keluar untuk barang tertentu
    query = """
    SELECT tanggal_transaksi, SUM(jumlah_barang) as jumlah_terjual
    FROM transaksi
    WHERE id_barang = %s AND jenis_transaksi = 'keluar'
    GROUP BY tanggal_transaksi
    ORDER BY tanggal_transaksi
    """
    data_raw = fetch_data(query, (id_barang,))
    
    if not data_raw:
        return None

    # Konversi ke DataFrame Pandas
    df = pd.DataFrame(data_raw)
    df['tanggal_transaksi'] = pd.to_datetime(df['tanggal_transaksi'])
    df = df.set_index('tanggal_transaksi')
    
    # Resample ke penjualan mingguan
    df_weekly = df['jumlah_terjual'].resample('W').sum().fillna(0)
    df_weekly = df_weekly.reset_index()
    # Waktu
    df_weekly['Minggu_ke'] = np.arange(len(df_weekly)) + 1
    # Moving average 4 minggu, digeser agar tidak kebocoran data
    df_weekly['Avg_4_Minggu'] = df_weekly['jumlah_terjual'].rolling(window=4).mean().shift(1)
    return df_weekly.dropna()

def predict_sales(id_barang):
    """
    Prediksi penjualan mingguan berikutnya dan agregasi bulanan
    menggunakan LinearRegression atas fitur waktu.
    """
    df_model = prepare_data_for_ai(id_barang)
    
    if df_model is None or len(df_model) < 5:
        return "Data penjualan kurang memadai (min 5 minggu data)."

    # Pisahkan fitur (X) dan target (y)
    # Fitur X: Minggu_ke (Time step)
    # Target y: jumlah_terjual (Sales)
    X = df_model[['Minggu_ke']].values
    y = df_model['jumlah_terjual'].values
    
    # Integrasi AI: Latih model Linear Regression
    model = LinearRegression()
    model.fit(X, y)
    
    # Prediksi untuk Minggu selanjutnya
    minggu_terakhir = df_model['Minggu_ke'].max()
    minggu_berikutnya = minggu_terakhir + 1
    
    X_pred = np.array([[minggu_berikutnya]])
    y_pred = model.predict(X_pred)[0]
    
    # Membulatkan hasil prediksi
    prediksi_qty_mingguan = max(0, int(round(y_pred)))
    # Estimasi bulanan sederhana: rata-rata 4-5 minggu/bulan
    prediksi_qty_bulanan = max(0, int(round(y_pred * 4)))
    
    # Ambil data stok saat ini
    stok_saat_ini = fetch_data("SELECT stok_saat_ini, stok_minimum FROM barang WHERE id_barang = %s", (id_barang,))[0]
    stok_qty = stok_saat_ini['stok_saat_ini']
    min_stok = stok_saat_ini['stok_minimum']

    # Analisis dan Klasifikasi Sederhana:
    analisis = {
        "Prediksi_Mingguan": prediksi_qty_mingguan,
        "Prediksi_Bulanan": prediksi_qty_bulanan,
        "Stok_Saat_Ini": stok_qty,
        "Sisa_Stok_Setelah_Prediksi": stok_qty - prediksi_qty_mingguan,
        "Status": "Cukup"
    }
    
    # Klasifikasi / Analisis:
    if stok_qty <= min_stok:
        analisis["Status"] = "Wajib Restock Segera (Stok Kritis)"
    elif (stok_qty - prediksi_qty_mingguan) < min_stok:
        analisis["Status"] = "Perlu Restock Dalam Waktu Dekat (Stok Diprediksi Habis)"
    
    return analisis