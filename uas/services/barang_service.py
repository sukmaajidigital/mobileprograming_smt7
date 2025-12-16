from koneksi import fetch_data, execute_query


def get_list_barang():
    return fetch_data("SELECT id_barang, nama_barang, stok_saat_ini, harga_jual, stok_minimum, satuan_barang FROM barang")


def get_satuan_dict():
    barang_list = fetch_data("SELECT id_barang, satuan_barang FROM barang")
    return {item['id_barang']: item for item in barang_list}


def tambah_barang(nama, kode, kategori, beli, jual, stok, min_stok, satuan):
    query = (
        """
        INSERT INTO barang (nama_barang, kode_sku, kategori, harga_beli, harga_jual, stok_saat_ini, stok_minimum, satuan_barang)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
    )
    params = (nama, kode, kategori, beli, jual, stok, min_stok, satuan)
    return execute_query(query, params)


def delete_barang(id_barang):
    return execute_query("DELETE FROM barang WHERE id_barang = %s", (id_barang,))


def update_stok(id_barang, delta):
    # delta positif untuk masuk, negatif untuk keluar
    query = "UPDATE barang SET stok_saat_ini = stok_saat_ini + %s WHERE id_barang = %s"
    return execute_query(query, (delta, id_barang))
