-- ==========================================
-- 1. STRUKTUR TABEL
-- ==========================================

-- Tabel 1: User (Wajib)
-- Perbaikan: Menghapus koma setelah akses_terakhir agar tidak error
CREATE TABLE user (
    id_user INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL,
    hak_akses ENUM('admin', 'kasir', 'pemilik') NOT NULL,
    akses_terakhir DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Tabel 2: Master Supplier (Minimal 7 Kolom)
-- Kolom: id, nama, alamat, kota, telp, email, kontak, lead_time
CREATE TABLE supplier (
    id_supplier INT PRIMARY KEY AUTO_INCREMENT,
    nama_supplier VARCHAR(100) NOT NULL,
    alamat_kantor TEXT NOT NULL,
    kota_asal VARCHAR(50) NOT NULL,
    no_telepon VARCHAR(20) NOT NULL,
    email_perusahaan VARCHAR(100),
    kontak_person VARCHAR(50) NOT NULL,
    estimasi_pengiriman_hari INT DEFAULT 1 -- Data untuk analisis logistik
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Tabel 3: Master Barang (Minimal 7 Kolom)
-- Kolom: id, nama, kode, kategori, beli, jual, stok, min_stok, satuan
CREATE TABLE barang (
    id_barang INT PRIMARY KEY AUTO_INCREMENT,
    nama_barang VARCHAR(150) NOT NULL,
    kode_sku VARCHAR(50) NOT NULL UNIQUE,
    kategori VARCHAR(50) NOT NULL,
    harga_beli DECIMAL(10, 2) NOT NULL,
    harga_jual DECIMAL(10, 2) NOT NULL,
    stok_saat_ini INT NOT NULL DEFAULT 0,
    stok_minimum INT NOT NULL DEFAULT 5, -- Trigger untuk prediksi restock
    satuan_barang VARCHAR(20) NOT NULL DEFAULT 'Pcs'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Tabel 4: Transaksi (Minimal 10 Kolom & Relasional)
-- Tabel ini mencatat masuk/keluar barang untuk bahan prediksi AI
CREATE TABLE transaksi (
    id_transaksi INT PRIMARY KEY AUTO_INCREMENT,
    no_faktur VARCHAR(50) NOT NULL,
    tanggal_transaksi DATE NOT NULL,
    
    -- Relasi ke tabel lain
    id_user INT NOT NULL,
    id_barang INT NOT NULL,
    id_supplier INT, -- Boleh NULL jika ini transaksi penjualan ke customer
    
    jenis_transaksi ENUM('masuk', 'keluar') NOT NULL, -- Masuk (Beli), Keluar (Jual)
    jumlah_barang INT NOT NULL,
    harga_satuan_saat_itu DECIMAL(10, 2) NOT NULL,
    total_harga DECIMAL(12, 2) NOT NULL,
    metode_pembayaran VARCHAR(50) DEFAULT 'Tunai',
    keterangan_tambahan TEXT,
    
    FOREIGN KEY (id_user) REFERENCES user(id_user) ON UPDATE CASCADE,
    FOREIGN KEY (id_barang) REFERENCES barang(id_barang) ON UPDATE CASCADE,
    FOREIGN KEY (id_supplier) REFERENCES supplier(id_supplier) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ==========================================
-- 2. DUMMY DATA (INSERT)
-- ==========================================

-- Isi Data User
INSERT INTO user (username, password, hak_akses) VALUES 
('admin_gudang', 'admin123', 'admin'),
('kasir_depan', 'kasir123', 'kasir'),
('pak_bos', 'bos123', 'pemilik');

-- Isi Data Supplier
INSERT INTO supplier (nama_supplier, alamat_kantor, kota_asal, no_telepon, email_perusahaan, kontak_person, estimasi_pengiriman_hari) VALUES 
('CV. Benang Nusantara', 'Jl. Industri No. 45', 'Pekalongan', '081234567890', 'sales@benangnusantara.com', 'Budi Santoso', 2),
('PT. Tekstil Jaya Abadi', 'Kawasan Industri Terboyo', 'Semarang', '024-7654321', 'info@tekstiljaya.co.id', 'Siti Aminah', 3),
('UD. Pewarna Alami', 'Jl. Kaliurang Km 5', 'Yogyakarta', '081987654321', 'order@pewarnaalami.com', 'Andi Hidayat', 4);

-- Isi Data Barang
INSERT INTO barang (nama_barang, kode_sku, kategori, harga_beli, harga_jual, stok_saat_ini, stok_minimum, satuan_barang) VALUES 
('Kain Mori Primissima', 'KAIN-001', 'Bahan Baku', 25000.00, 35000.00, 150, 20, 'Meter'),
('Canting Tulis Tembaga', 'ALAT-001', 'Peralatan', 15000.00, 25000.00, 50, 10, 'Pcs'),
('Malam/Lilin Batik Klowong', 'BAHAN-001', 'Bahan Baku', 30000.00, 45000.00, 80, 15, 'Kg'),
('Kemeja Batik Tulis Pola', 'BAJU-001', 'Pakaian Jadi', 250000.00, 450000.00, 12, 5, 'Pcs'),
('Pewarna Naptol Merah', 'WARNA-001', 'Bahan Kimia', 40000.00, 60000.00, 25, 5, 'Kaleng');

-- Isi Data Transaksi (Gabungan Masuk & Keluar untuk Data Latih AI)
-- Skenario: 
-- Barang Masuk = Restock dari Supplier
-- Barang Keluar = Penjualan (Supplier NULL)

INSERT INTO transaksi (no_faktur, tanggal_transaksi, id_user, id_barang, id_supplier, jenis_transaksi, jumlah_barang, harga_satuan_saat_itu, total_harga, metode_pembayaran, keterangan_tambahan) VALUES 
-- Transaksi 1: Pembelian Stok Awal (Masuk)
('INV-IN-001', '2025-10-01', 1, 1, 1, 'masuk', 100, 25000.00, 2500000.00, 'Transfer Bank', 'Stok awal bulan Oktober'),
('INV-IN-002', '2025-10-01', 1, 4, 2, 'masuk', 20, 250000.00, 5000000.00, 'Tempo', 'Stok kemeja baru'),

-- Transaksi 2: Penjualan Harian (Keluar) - Data ini yang akan diprediksi trennya
('INV-OUT-001', '2025-10-02', 2, 1, NULL, 'keluar', 10, 35000.00, 350000.00, 'Tunai', 'Pembelian eceran'),
('INV-OUT-002', '2025-10-03', 2, 1, NULL, 'keluar', 5, 35000.00, 175000.00, 'Tunai', 'Pembelian eceran'),
('INV-OUT-003', '2025-10-05', 2, 4, NULL, 'keluar', 2, 450000.00, 900000.00, 'QRIS', 'Pelanggan VIP'),
('INV-OUT-004', '2025-10-06', 2, 1, NULL, 'keluar', 15, 35000.00, 525000.00, 'Tunai', 'Pesanan seragam kecil'),
('INV-OUT-005', '2025-10-10', 2, 1, NULL, 'keluar', 20, 35000.00, 700000.00, 'Transfer', 'Kirim ke Surabaya'),
('INV-OUT-006', '2025-10-12', 2, 3, NULL, 'keluar', 5, 45000.00, 225000.00, 'Tunai', 'Untuk praktek sekolah'),

-- Transaksi 3: Restock Ulang (Masuk)
('INV-IN-003', '2025-10-15', 1, 1, 1, 'masuk', 50, 25000.00, 1250000.00, 'Tunai', 'Restock tengah bulan');