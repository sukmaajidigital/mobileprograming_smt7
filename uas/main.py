# main.py (FINAL FIX - STRING ICONS & COLORS)

import flet as ft
from ui_login import build_login_view
from ui_inventory import build_inventory_view

# --- 1. Fungsi CRUD ---

def get_list_barang():
    """Mengambil semua data barang."""
    return fetch_data("SELECT id_barang, nama_barang, stok_saat_ini, harga_jual, stok_minimum FROM barang")

def delete_barang(id_barang):
    """Menghapus barang berdasarkan ID."""
    query = "DELETE FROM barang WHERE id_barang = %s"
    return execute_query(query, (id_barang,))

def tambah_barang(nama, kode, kategori, beli, jual, stok, min_stok, satuan):
    """Menambahkan barang baru."""
    query = """
    INSERT INTO barang (nama_barang, kode_sku, kategori, harga_beli, harga_jual, stok_saat_ini, stok_minimum, satuan_barang) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    params = (nama, kode, kategori, beli, jual, stok, min_stok, satuan)
    return execute_query(query, params)

# --- 2. Fungsi Utama Aplikasi Flet ---

def main(page: ft.Page):
    page.title = "Smart Inventory Flet - Prediksi Stok"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.ADAPTIVE
    page.theme_mode = ft.ThemeMode.LIGHT

    def on_login_success(user_row):
        page.clean()
        widgets, overlays = build_inventory_view(user_row)
        for w in widgets:
            page.add(w)
        for o in overlays:
            page.overlay.append(o)
        page.update()

    login_view = build_login_view(on_login_success)
    page.add(ft.Container(content=login_view, padding=20, width=600))


if __name__ == "__main__":
    ft.app(target=main)