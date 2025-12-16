from koneksi import fetch_data, execute_query


def catat_transaksi(no_faktur, tanggal, id_user, id_barang, id_supplier, jenis, jumlah, harga_satuan, metode, ket):
    total = float(harga_satuan) * int(jumlah)
    query = (
        """
        INSERT INTO transaksi (no_faktur, tanggal_transaksi, id_user, id_barang, id_supplier, jenis_transaksi, jumlah_barang,
                               harga_satuan_saat_itu, total_harga, metode_pembayaran, keterangan_tambahan)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
    )
    params = (no_faktur, tanggal, id_user, id_barang, id_supplier, jenis, jumlah, harga_satuan, total, metode, ket)
    return execute_query(query, params)


def list_transaksi_barang(id_barang):
    return fetch_data(
        "SELECT * FROM transaksi WHERE id_barang = %s ORDER BY tanggal_transaksi DESC",
        (id_barang,),
    )
