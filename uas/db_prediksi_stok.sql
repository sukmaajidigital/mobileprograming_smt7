-- Database: Sistem Informasi Kasir Batik
-- Created: 2025-12-16

-- Hapus database jika sudah ada (opsional)
-- DROP DATABASE IF EXISTS db_kasir_batik;

-- Buat database
CREATE DATABASE IF NOT EXISTS db_prediksi_stok;
USE db_prediksi_stok;

-- Pastikan import bersih dan urutan ID konsisten
SET FOREIGN_KEY_CHECKS = 0;
-- Hapus tabel jika sudah ada (hindari error TRUNCATE sebelum tabel dibuat)
DROP TABLE IF EXISTS transaksi;
DROP TABLE IF EXISTS barang;
DROP TABLE IF EXISTS supplier;
DROP TABLE IF EXISTS user;
SET FOREIGN_KEY_CHECKS = 1;


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
('UD. Pewarna Alami', 'Jl. Kaliurang Km 5', 'Yogyakarta', '081987654321', 'order@pewarnaalami.com', 'Andi Hidayat', 4),
('PT. Batik Nusantara Sejahtera', 'Jl. Raya Solo Km 12', 'Solo', '081345678901', 'marketing@batiknusantara.co.id', 'Dewi Lestari', 2),
('CV. Lilin Berkah', 'Jl. Gatot Subroto No. 88', 'Bandung', '022-8765432', 'order@lilinberkah.com', 'Ahmad Fauzi', 3),
('UD. Kain Tradisional', 'Jl. Malioboro No. 123', 'Yogyakarta', '0274-456789', 'info@kaintradisional.com', 'Sri Mulyani', 2),
('PT. Pewarna Indonesia', 'Kawasan Industri Cikupa', 'Tangerang', '021-5551234', 'sales@pewarnaindonesia.co.id', 'Bambang Wijaya', 5),
('CV. Canting Mas', 'Jl. Diponegoro No. 67', 'Pekalongan', '081556789012', 'cantingmas@gmail.com', 'Ratna Sari', 2),
('UD. Tekstil Maju Jaya', 'Jl. Sudirman No. 234', 'Surabaya', '031-7890123', 'tekstilmaju@yahoo.com', 'Hendra Kusuma', 4),
('PT. Batik Modern', 'Jl. HR Rasuna Said', 'Jakarta', '021-5289000', 'cs@batikmodern.co.id', 'Linda Anggraini', 6);

-- ==========================================
-- Isi Data Barang: 100 Bahan Baku + 100 Produk Jadi
-- ==========================================

-- === BAGIAN 1: 100 DATA BAHAN BAKU ===
INSERT INTO barang (nama_barang, kode_sku, kategori, harga_beli, harga_jual, stok_saat_ini, stok_minimum, satuan_barang) VALUES 
-- Kain-kain dasar (20 jenis)
('Kain Mori Primissima', 'KAIN-001', 'Bahan Baku', 25000.00, 35000.00, 150, 20, 'Meter'),
('Kain Mori Primis', 'KAIN-002', 'Bahan Baku', 22000.00, 32000.00, 200, 25, 'Meter'),
('Kain Mori Biru', 'KAIN-003', 'Bahan Baku', 23000.00, 33000.00, 180, 20, 'Meter'),
('Kain Sutera Putih', 'KAIN-004', 'Bahan Baku', 150000.00, 200000.00, 50, 10, 'Meter'),
('Kain Katun Prima', 'KAIN-005', 'Bahan Baku', 28000.00, 38000.00, 175, 20, 'Meter'),
('Kain Rayon Polos', 'KAIN-006', 'Bahan Baku', 20000.00, 30000.00, 160, 25, 'Meter'),
('Kain Satin Putih', 'KAIN-007', 'Bahan Baku', 45000.00, 60000.00, 100, 15, 'Meter'),
('Kain Dobi Premium', 'KAIN-008', 'Bahan Baku', 35000.00, 48000.00, 120, 18, 'Meter'),
('Kain Paris Halus', 'KAIN-009', 'Bahan Baku', 32000.00, 45000.00, 140, 20, 'Meter'),
('Kain Voal Premium', 'KAIN-010', 'Bahan Baku', 30000.00, 42000.00, 150, 22, 'Meter'),
('Kain Santung Premium', 'KAIN-011', 'Bahan Baku', 38000.00, 52000.00, 95, 15, 'Meter'),
('Kain Organdi Halus', 'KAIN-012', 'Bahan Baku', 42000.00, 58000.00, 80, 12, 'Meter'),
('Kain Brokat Putih', 'KAIN-013', 'Bahan Baku', 65000.00, 85000.00, 60, 10, 'Meter'),
('Kain Jumputan Polos', 'KAIN-014', 'Bahan Baku', 27000.00, 38000.00, 110, 18, 'Meter'),
('Kain Tenun Polos', 'KAIN-015', 'Bahan Baku', 48000.00, 65000.00, 75, 12, 'Meter'),
('Kain Batik Tulis Putihan', 'KAIN-016', 'Bahan Baku', 55000.00, 75000.00, 85, 15, 'Meter'),
('Kain Poplin Premium', 'KAIN-017', 'Bahan Baku', 26000.00, 37000.00, 130, 20, 'Meter'),
('Kain Viscose Lembut', 'KAIN-018', 'Bahan Baku', 33000.00, 46000.00, 105, 16, 'Meter'),
('Kain Sutera Thailand', 'KAIN-019', 'Bahan Baku', 180000.00, 250000.00, 40, 8, 'Meter'),
('Kain Linen Putih', 'KAIN-020', 'Bahan Baku', 52000.00, 70000.00, 70, 12, 'Meter'),

-- Lilin/Malam Batik (15 jenis)
('Malam/Lilin Batik Klowong', 'BAHAN-001', 'Bahan Baku', 30000.00, 45000.00, 80, 15, 'Kg'),
('Malam Carikan Premium', 'BAHAN-002', 'Bahan Baku', 35000.00, 50000.00, 65, 12, 'Kg'),
('Malam Tembokan Khusus', 'BAHAN-003', 'Bahan Baku', 32000.00, 47000.00, 70, 13, 'Kg'),
('Malam Lorodan', 'BAHAN-004', 'Bahan Baku', 28000.00, 42000.00, 75, 14, 'Kg'),
('Malam Parafin Murni', 'BAHAN-005', 'Bahan Baku', 25000.00, 38000.00, 90, 16, 'Kg'),
('Malam Gondorukem', 'BAHAN-006', 'Bahan Baku', 40000.00, 58000.00, 55, 10, 'Kg'),
('Malam Microwax', 'BAHAN-007', 'Bahan Baku', 38000.00, 55000.00, 60, 11, 'Kg'),
('Malam Batik Cap', 'BAHAN-008', 'Bahan Baku', 33000.00, 48000.00, 68, 12, 'Kg'),
('Malam Putih Premium', 'BAHAN-009', 'Bahan Baku', 36000.00, 52000.00, 63, 11, 'Kg'),
('Malam Kuning Halus', 'BAHAN-010', 'Bahan Baku', 34000.00, 49000.00, 72, 13, 'Kg'),
('Malam Batik Campuran', 'BAHAN-011', 'Bahan Baku', 29000.00, 43000.00, 78, 14, 'Kg'),
('Malam Kendal Prima', 'BAHAN-012', 'Bahan Baku', 37000.00, 53000.00, 58, 10, 'Kg'),
('Malam Batik Tulis Halus', 'BAHAN-013', 'Bahan Baku', 41000.00, 59000.00, 52, 10, 'Kg'),
('Malam Cap Cirebon', 'BAHAN-014', 'Bahan Baku', 35000.00, 51000.00, 64, 12, 'Kg'),
('Malam Batik Solo', 'BAHAN-015', 'Bahan Baku', 39000.00, 56000.00, 57, 11, 'Kg'),

-- Pewarna (25 jenis)
('Pewarna Naptol Merah', 'WARNA-001', 'Bahan Kimia', 40000.00, 60000.00, 25, 5, 'Kaleng'),
('Pewarna Naptol Biru', 'WARNA-002', 'Bahan Kimia', 42000.00, 62000.00, 30, 6, 'Kaleng'),
('Pewarna Naptol Kuning', 'WARNA-003', 'Bahan Kimia', 38000.00, 58000.00, 28, 5, 'Kaleng'),
('Pewarna Naptol Hijau', 'WARNA-004', 'Bahan Kimia', 41000.00, 61000.00, 26, 5, 'Kaleng'),
('Pewarna Indigosol Orange', 'WARNA-005', 'Bahan Kimia', 45000.00, 65000.00, 22, 5, 'Kaleng'),
('Pewarna Indigosol Violet', 'WARNA-006', 'Bahan Kimia', 46000.00, 66000.00, 20, 4, 'Kaleng'),
('Pewarna Indigosol Pink', 'WARNA-007', 'Bahan Kimia', 44000.00, 64000.00, 24, 5, 'Kaleng'),
('Pewarna Rapid Merah', 'WARNA-008', 'Bahan Kimia', 39000.00, 59000.00, 27, 5, 'Kaleng'),
('Pewarna Rapid Biru Navy', 'WARNA-009', 'Bahan Kimia', 43000.00, 63000.00, 23, 5, 'Kaleng'),
('Pewarna Rapid Hitam', 'WARNA-010', 'Bahan Kimia', 47000.00, 67000.00, 21, 4, 'Kaleng'),
('Pewarna Remasol Coklat', 'WARNA-011', 'Bahan Kimia', 40000.00, 60000.00, 25, 5, 'Kaleng'),
('Pewarna Remasol Ungu', 'WARNA-012', 'Bahan Kimia', 41000.00, 61000.00, 24, 5, 'Kaleng'),
('Pewarna Alami Indigo', 'WARNA-013', 'Bahan Kimia', 55000.00, 80000.00, 15, 3, 'Kg'),
('Pewarna Alami Soga', 'WARNA-014', 'Bahan Kimia', 52000.00, 75000.00, 18, 4, 'Kg'),
('Pewarna Alami Kunyit', 'WARNA-015', 'Bahan Kimia', 35000.00, 50000.00, 30, 6, 'Kg'),
('Pewarna Alami Mengkudu', 'WARNA-016', 'Bahan Kimia', 48000.00, 70000.00, 20, 4, 'Kg'),
('Pewarna Napthol Maroon', 'WARNA-017', 'Bahan Kimia', 44000.00, 64000.00, 22, 5, 'Kaleng'),
('Pewarna Napthol Tosca', 'WARNA-018', 'Bahan Kimia', 43000.00, 63000.00, 23, 5, 'Kaleng'),
('Pewarna Napthol Fanta', 'WARNA-019', 'Bahan Kimia', 42000.00, 62000.00, 25, 5, 'Kaleng'),
('Pewarna Napthol Coklat Tua', 'WARNA-020', 'Bahan Kimia', 45000.00, 65000.00, 21, 4, 'Kaleng'),
('Pewarna Indigosol Gold', 'WARNA-021', 'Bahan Kimia', 48000.00, 68000.00, 19, 4, 'Kaleng'),
('Pewarna Indigosol Turqoise', 'WARNA-022', 'Bahan Kimia', 46000.00, 66000.00, 20, 4, 'Kaleng'),
('Pewarna Procion Merah', 'WARNA-023', 'Bahan Kimia', 50000.00, 72000.00, 18, 4, 'Kaleng'),
('Pewarna Procion Biru', 'WARNA-024', 'Bahan Kimia', 51000.00, 73000.00, 17, 3, 'Kaleng'),
('Pewarna Procion Kuning', 'WARNA-025', 'Bahan Kimia', 49000.00, 71000.00, 19, 4, 'Kaleng'),

-- Peralatan Batik (40 jenis)
('Canting Tulis Tembaga', 'ALAT-001', 'Peralatan', 15000.00, 25000.00, 50, 10, 'Pcs'),
('Canting Tulis Kecil', 'ALAT-002', 'Peralatan', 12000.00, 22000.00, 60, 12, 'Pcs'),
('Canting Tulis Sedang', 'ALAT-003', 'Peralatan', 14000.00, 24000.00, 55, 11, 'Pcs'),
('Canting Tulis Besar', 'ALAT-004', 'Peralatan', 16000.00, 26000.00, 48, 10, 'Pcs'),
('Canting Tembok', 'ALAT-005', 'Peralatan', 18000.00, 28000.00, 45, 9, 'Pcs'),
('Canting Cecekan', 'ALAT-006', 'Peralatan', 13000.00, 23000.00, 52, 11, 'Pcs'),
('Canting Klowong Halus', 'ALAT-007', 'Peralatan', 15500.00, 25500.00, 48, 10, 'Pcs'),
('Canting Isen-isen', 'ALAT-008', 'Peralatan', 14500.00, 24500.00, 50, 10, 'Pcs'),
('Cap Batik Tembaga Motif Parang', 'ALAT-009', 'Peralatan', 350000.00, 500000.00, 15, 3, 'Pcs'),
('Cap Batik Tembaga Motif Kawung', 'ALAT-010', 'Peralatan', 380000.00, 530000.00, 12, 3, 'Pcs'),
('Cap Batik Tembaga Motif Truntum', 'ALAT-011', 'Peralatan', 360000.00, 510000.00, 14, 3, 'Pcs'),
('Cap Batik Tembaga Motif Lereng', 'ALAT-012', 'Peralatan', 340000.00, 490000.00, 16, 3, 'Pcs'),
('Cap Batik Tembaga Motif Mega Mendung', 'ALAT-013', 'Peralatan', 400000.00, 550000.00, 10, 2, 'Pcs'),
('Cap Batik Tembaga Motif Sekar Jagad', 'ALAT-014', 'Peralatan', 390000.00, 540000.00, 11, 3, 'Pcs'),
('Wajan Malam Tembaga Besar', 'ALAT-015', 'Peralatan', 85000.00, 120000.00, 25, 5, 'Pcs'),
('Wajan Malam Tembaga Sedang', 'ALAT-016', 'Peralatan', 75000.00, 110000.00, 30, 6, 'Pcs'),
('Wajan Malam Tembaga Kecil', 'ALAT-017', 'Peralatan', 65000.00, 95000.00, 35, 7, 'Pcs'),
('Kompor Minyak Batik', 'ALAT-018', 'Peralatan', 150000.00, 200000.00, 20, 4, 'Pcs'),
('Gawangan Batik Kayu Jati', 'ALAT-019', 'Peralatan', 250000.00, 350000.00, 18, 4, 'Pcs'),
('Gawangan Batik Bambu', 'ALAT-020', 'Peralatan', 120000.00, 180000.00, 25, 5, 'Pcs'),
('Bak Pewarna Plastik Besar', 'ALAT-021', 'Peralatan', 45000.00, 65000.00, 40, 8, 'Pcs'),
('Bak Pewarna Plastik Sedang', 'ALAT-022', 'Peralatan', 35000.00, 55000.00, 50, 10, 'Pcs'),
('Bak Pewarna Stainless Steel', 'ALAT-023', 'Peralatan', 180000.00, 250000.00, 15, 3, 'Pcs'),
('Kuas Batik Set', 'ALAT-024', 'Peralatan', 25000.00, 40000.00, 60, 12, 'Set'),
('Pensil Batik Khusus', 'ALAT-025', 'Peralatan', 5000.00, 10000.00, 100, 20, 'Pcs'),
('Penggaris Batik Metal 50cm', 'ALAT-026', 'Peralatan', 15000.00, 25000.00, 45, 9, 'Pcs'),
('Sarung Tangan Karet', 'ALAT-027', 'Peralatan', 8000.00, 15000.00, 80, 16, 'Pasang'),
('Masker Batik Anti Uap', 'ALAT-028', 'Peralatan', 12000.00, 20000.00, 70, 14, 'Pcs'),
('Celemek Batik Anti Air', 'ALAT-029', 'Peralatan', 35000.00, 50000.00, 40, 8, 'Pcs'),
('Ember Plastik 20 Liter', 'ALAT-030', 'Peralatan', 25000.00, 38000.00, 55, 11, 'Pcs'),
('Timbangan Digital Batik', 'ALAT-031', 'Peralatan', 150000.00, 220000.00, 12, 3, 'Pcs'),
('Thermometer Malam', 'ALAT-032', 'Peralatan', 45000.00, 65000.00, 30, 6, 'Pcs'),
('Saringan Malam Halus', 'ALAT-033', 'Peralatan', 20000.00, 32000.00, 50, 10, 'Pcs'),
('Kertas Pola Batik', 'ALAT-034', 'Peralatan', 3000.00, 8000.00, 200, 40, 'Lembar'),
('Benang Jahit Batik Putih', 'ALAT-035', 'Peralatan', 5000.00, 10000.00, 150, 30, 'Roll'),
('Benang Jahit Batik Hitam', 'ALAT-036', 'Peralatan', 5000.00, 10000.00, 140, 28, 'Roll'),
('Benang Jahit Batik Warna', 'ALAT-037', 'Peralatan', 6000.00, 12000.00, 130, 26, 'Roll'),
('Jarum Jahit Batik Set', 'ALAT-038', 'Peralatan', 15000.00, 25000.00, 65, 13, 'Set'),
('Gunting Kain Premium', 'ALAT-039', 'Peralatan', 45000.00, 70000.00, 35, 7, 'Pcs'),
('Meteran Kain 5 Meter', 'ALAT-040', 'Peralatan', 10000.00, 18000.00, 90, 18, 'Pcs')

-- === BAGIAN 2: 100 DATA PRODUK BATIK JADI ===
-- (Lanjutan dari INSERT sebelumnya)
, 
-- Kemeja Batik Pria (30 jenis)
('Kemeja Batik Tulis Pola Parang', 'BAJU-001', 'Pakaian Jadi', 250000.00, 450000.00, 12, 5, 'Pcs'),
('Kemeja Batik Tulis Pola Kawung', 'BAJU-002', 'Pakaian Jadi', 260000.00, 460000.00, 15, 5, 'Pcs'),
('Kemeja Batik Tulis Mega Mendung', 'BAJU-003', 'Pakaian Jadi', 280000.00, 480000.00, 10, 4, 'Pcs'),
('Kemeja Batik Cap Parang Rusak', 'BAJU-004', 'Pakaian Jadi', 180000.00, 320000.00, 20, 6, 'Pcs'),
('Kemeja Batik Cap Truntum', 'BAJU-005', 'Pakaian Jadi', 175000.00, 315000.00, 22, 6, 'Pcs'),
('Kemeja Batik Cap Sekar Jagad', 'BAJU-006', 'Pakaian Jadi', 185000.00, 325000.00, 18, 6, 'Pcs'),
('Kemeja Batik Printing Modern', 'BAJU-007', 'Pakaian Jadi', 120000.00, 220000.00, 35, 8, 'Pcs'),
('Kemeja Batik Printing Abstrak', 'BAJU-008', 'Pakaian Jadi', 115000.00, 215000.00, 40, 9, 'Pcs'),
('Kemeja Batik Lengan Pendek Parang', 'BAJU-009', 'Pakaian Jadi', 150000.00, 280000.00, 28, 7, 'Pcs'),
('Kemeja Batik Lengan Pendek Kawung', 'BAJU-010', 'Pakaian Jadi', 155000.00, 285000.00, 26, 7, 'Pcs'),
('Kemeja Batik Slim Fit Modern', 'BAJU-011', 'Pakaian Jadi', 200000.00, 350000.00, 18, 5, 'Pcs'),
('Kemeja Batik Reguler Fit Klasik', 'BAJU-012', 'Pakaian Jadi', 190000.00, 340000.00, 20, 6, 'Pcs'),
('Kemeja Batik Sutra Tulis Premium', 'BAJU-013', 'Pakaian Jadi', 450000.00, 750000.00, 8, 3, 'Pcs'),
('Kemeja Batik Sutra Cap Mewah', 'BAJU-014', 'Pakaian Jadi', 380000.00, 650000.00, 10, 3, 'Pcs'),
('Kemeja Batik Kombinasi Polos', 'BAJU-015', 'Pakaian Jadi', 170000.00, 310000.00, 24, 6, 'Pcs'),
('Kemeja Batik Koko Pria', 'BAJU-016', 'Pakaian Jadi', 160000.00, 290000.00, 25, 6, 'Pcs'),
('Kemeja Batik Executive', 'BAJU-017', 'Pakaian Jadi', 220000.00, 380000.00, 16, 5, 'Pcs'),
('Kemeja Batik Casual Santai', 'BAJU-018', 'Pakaian Jadi', 145000.00, 265000.00, 30, 7, 'Pcs'),
('Kemeja Batik Formal Kantor', 'BAJU-019', 'Pakaian Jadi', 195000.00, 345000.00, 19, 5, 'Pcs'),
('Kemeja Batik Resmi Acara', 'BAJU-020', 'Pakaian Jadi', 210000.00, 370000.00, 17, 5, 'Pcs'),
('Kemeja Batik Anak Muda', 'BAJU-021', 'Pakaian Jadi', 135000.00, 245000.00, 32, 8, 'Pcs'),
('Kemeja Batik Vintage', 'BAJU-022', 'Pakaian Jadi', 165000.00, 295000.00, 23, 6, 'Pcs'),
('Kemeja Batik Gradasi Warna', 'BAJU-023', 'Pakaian Jadi', 185000.00, 330000.00, 21, 6, 'Pcs'),
('Kemeja Batik Motif Geometric', 'BAJU-024', 'Pakaian Jadi', 175000.00, 320000.00, 22, 6, 'Pcs'),
('Kemeja Batik Premium Exclusive', 'BAJU-025', 'Pakaian Jadi', 320000.00, 550000.00, 11, 4, 'Pcs'),
('Kemeja Batik Lereng Modern', 'BAJU-026', 'Pakaian Jadi', 168000.00, 305000.00, 24, 6, 'Pcs'),
('Kemeja Batik Sogan Klasik', 'BAJU-027', 'Pakaian Jadi', 195000.00, 350000.00, 18, 5, 'Pcs'),
('Kemeja Batik Pekalongan Asli', 'BAJU-028', 'Pakaian Jadi', 230000.00, 400000.00, 14, 5, 'Pcs'),
('Kemeja Batik Solo Tradisional', 'BAJU-029', 'Pakaian Jadi', 240000.00, 410000.00, 13, 4, 'Pcs'),
('Kemeja Batik Cirebon Unik', 'BAJU-030', 'Pakaian Jadi', 225000.00, 395000.00, 15, 5, 'Pcs'),

-- Blouse/Atasan Batik Wanita (25 jenis)
('Blouse Batik Wanita Tulis', 'ATASAN-001', 'Pakaian Jadi', 220000.00, 380000.00, 18, 5, 'Pcs'),
('Blouse Batik Wanita Cap', 'ATASAN-002', 'Pakaian Jadi', 165000.00, 295000.00, 24, 6, 'Pcs'),
('Atasan Batik Kutubaru', 'ATASAN-003', 'Pakaian Jadi', 190000.00, 340000.00, 20, 6, 'Pcs'),
('Atasan Batik Kebaya Modern', 'ATASAN-004', 'Pakaian Jadi', 280000.00, 480000.00, 12, 4, 'Pcs'),
('Blouse Batik Lengan Panjang', 'ATASAN-005', 'Pakaian Jadi', 175000.00, 315000.00, 22, 6, 'Pcs'),
('Blouse Batik Lengan Pendek', 'ATASAN-006', 'Pakaian Jadi', 160000.00, 290000.00, 26, 7, 'Pcs'),
('Atasan Batik Casual Wanita', 'ATASAN-007', 'Pakaian Jadi', 145000.00, 265000.00, 28, 7, 'Pcs'),
('Atasan Batik Formal Kantor', 'ATASAN-008', 'Pakaian Jadi', 185000.00, 335000.00, 21, 6, 'Pcs'),
('Blouse Batik Sutra Mewah', 'ATASAN-009', 'Pakaian Jadi', 380000.00, 650000.00, 9, 3, 'Pcs'),
('Atasan Batik Kombinasi Brokat', 'ATASAN-010', 'Pakaian Jadi', 250000.00, 430000.00, 14, 5, 'Pcs'),
('Blouse Batik Peplum', 'ATASAN-011', 'Pakaian Jadi', 195000.00, 350000.00, 19, 5, 'Pcs'),
('Atasan Batik Loose Fit', 'ATASAN-012', 'Pakaian Jadi', 155000.00, 285000.00, 25, 6, 'Pcs'),
('Blouse Batik Crop Top', 'ATASAN-013', 'Pakaian Jadi', 135000.00, 245000.00, 30, 7, 'Pcs'),
('Atasan Batik Tunik Panjang', 'ATASAN-014', 'Pakaian Jadi', 170000.00, 310000.00, 23, 6, 'Pcs'),
('Blouse Batik Sabrina', 'ATASAN-015', 'Pakaian Jadi', 165000.00, 300000.00, 24, 6, 'Pcs'),
('Atasan Batik Halterneck', 'ATASAN-016', 'Pakaian Jadi', 175000.00, 320000.00, 21, 6, 'Pcs'),
('Blouse Batik Batwing', 'ATASAN-017', 'Pakaian Jadi', 180000.00, 325000.00, 20, 6, 'Pcs'),
('Atasan Batik Bustier', 'ATASAN-018', 'Pakaian Jadi', 145000.00, 270000.00, 27, 7, 'Pcs'),
('Blouse Batik Kimono Style', 'ATASAN-019', 'Pakaian Jadi', 200000.00, 360000.00, 17, 5, 'Pcs'),
('Atasan Batik Premium Exclusive', 'ATASAN-020', 'Pakaian Jadi', 295000.00, 510000.00, 11, 4, 'Pcs'),
('Blouse Batik Printing Modern', 'ATASAN-021', 'Pakaian Jadi', 125000.00, 230000.00, 33, 8, 'Pcs'),
('Atasan Batik Ethnic Chic', 'ATASAN-022', 'Pakaian Jadi', 190000.00, 345000.00, 19, 5, 'Pcs'),
('Blouse Batik Romantic', 'ATASAN-023', 'Pakaian Jadi', 185000.00, 330000.00, 20, 6, 'Pcs'),
('Atasan Batik Contemporary', 'ATASAN-024', 'Pakaian Jadi', 205000.00, 370000.00, 16, 5, 'Pcs'),
('Blouse Batik V-Neck Elegant', 'ATASAN-025', 'Pakaian Jadi', 175000.00, 315000.00, 22, 6, 'Pcs'),

-- Rok & Bawahan Batik (15 jenis)
('Rok Batik Span Panjang', 'ROK-001', 'Pakaian Jadi', 150000.00, 280000.00, 25, 6, 'Pcs'),
('Rok Batik Lilit Pendek', 'ROK-002', 'Pakaian Jadi', 120000.00, 230000.00, 30, 7, 'Pcs'),
('Celana Batik Kulot Wanita', 'ROK-003', 'Pakaian Jadi', 165000.00, 300000.00, 22, 6, 'Pcs'),
('Celana Batik Panjang Pria', 'ROK-004', 'Pakaian Jadi', 175000.00, 315000.00, 20, 6, 'Pcs'),
('Rok Batik Plisket', 'ROK-005', 'Pakaian Jadi', 140000.00, 260000.00, 26, 7, 'Pcs'),
('Celana Batik Kulot Panjang', 'ROK-006', 'Pakaian Jadi', 170000.00, 310000.00, 21, 6, 'Pcs'),
('Rok Batik Midi A-Line', 'ROK-007', 'Pakaian Jadi', 145000.00, 270000.00, 24, 6, 'Pcs'),
('Celana Batik Jogger', 'ROK-008', 'Pakaian Jadi', 155000.00, 285000.00, 23, 6, 'Pcs'),
('Rok Batik Maxi Sutra', 'ROK-009', 'Pakaian Jadi', 280000.00, 480000.00, 10, 4, 'Pcs'),
('Celana Batik Palazzo', 'ROK-010', 'Pakaian Jadi', 160000.00, 290000.00, 22, 6, 'Pcs'),
('Rok Batik Wrap Pendek', 'ROK-011', 'Pakaian Jadi', 125000.00, 240000.00, 28, 7, 'Pcs'),
('Celana Batik Chino Pria', 'ROK-012', 'Pakaian Jadi', 185000.00, 335000.00, 18, 5, 'Pcs'),
('Rok Batik Pensil Formal', 'ROK-013', 'Pakaian Jadi', 135000.00, 250000.00, 27, 7, 'Pcs'),
('Celana Batik Cargo', 'ROK-014', 'Pakaian Jadi', 195000.00, 350000.00, 16, 5, 'Pcs'),
('Rok Batik Tutu Modern', 'ROK-015', 'Pakaian Jadi', 165000.00, 305000.00, 20, 6, 'Pcs'),

-- Dress & Gamis Batik (15 jenis)
('Dress Batik Midi Casual', 'DRESS-001', 'Pakaian Jadi', 195000.00, 350000.00, 18, 5, 'Pcs'),
('Dress Batik Maxi Elegant', 'DRESS-002', 'Pakaian Jadi', 240000.00, 420000.00, 14, 5, 'Pcs'),
('Gamis Batik Syari', 'DRESS-003', 'Pakaian Jadi', 220000.00, 390000.00, 16, 5, 'Pcs'),
('Dress Batik A-Line Modern', 'DRESS-004', 'Pakaian Jadi', 185000.00, 335000.00, 20, 6, 'Pcs'),
('Gamis Batik Kombinasi', 'DRESS-005', 'Pakaian Jadi', 235000.00, 410000.00, 15, 5, 'Pcs'),
('Dress Batik Shift Simple', 'DRESS-006', 'Pakaian Jadi', 165000.00, 300000.00, 22, 6, 'Pcs'),
('Dress Batik Wrap Bohemian', 'DRESS-007', 'Pakaian Jadi', 175000.00, 320000.00, 21, 6, 'Pcs'),
('Gamis Batik Busui Friendly', 'DRESS-008', 'Pakaian Jadi', 215000.00, 380000.00, 17, 5, 'Pcs'),
('Dress Batik Tulis Premium', 'DRESS-009', 'Pakaian Jadi', 320000.00, 550000.00, 10, 4, 'Pcs'),
('Gamis Batik Sutra Mewah', 'DRESS-010', 'Pakaian Jadi', 380000.00, 650000.00, 8, 3, 'Pcs'),
('Dress Batik Shirt Dress', 'DRESS-011', 'Pakaian Jadi', 170000.00, 310000.00, 20, 6, 'Pcs'),
('Dress Batik Pesta Malam', 'DRESS-012', 'Pakaian Jadi', 350000.00, 600000.00, 9, 3, 'Pcs'),
('Gamis Batik Casual Daily', 'DRESS-013', 'Pakaian Jadi', 195000.00, 350000.00, 18, 5, 'Pcs'),
('Dress Batik Off Shoulder', 'DRESS-014', 'Pakaian Jadi', 190000.00, 340000.00, 19, 5, 'Pcs'),
('Dress Batik Mini Playful', 'DRESS-015', 'Pakaian Jadi', 155000.00, 285000.00, 23, 6, 'Pcs'),

-- Kain Batik Jadi & Aksesoris (15 jenis)
('Kain Batik Tulis 2 Meter Parang', 'KAIN-JADI-001', 'Kain Jadi', 350000.00, 600000.00, 20, 5, 'Potong'),
('Kain Batik Tulis 2 Meter Kawung', 'KAIN-JADI-002', 'Kain Jadi', 360000.00, 610000.00, 18, 5, 'Potong'),
('Kain Batik Cap 2 Meter Truntum', 'KAIN-JADI-003', 'Kain Jadi', 220000.00, 380000.00, 30, 7, 'Potong'),
('Kain Batik Printing 2 Meter Modern', 'KAIN-JADI-004', 'Kain Jadi', 145000.00, 265000.00, 45, 10, 'Potong'),
('Sarung Batik Pria Premium', 'KAIN-JADI-005', 'Kain Jadi', 185000.00, 330000.00, 25, 6, 'Pcs'),
('Sarung Batik Wanita Elegan', 'KAIN-JADI-006', 'Kain Jadi', 175000.00, 315000.00, 27, 7, 'Pcs'),
('Selendang Batik Sutra', 'AKSESORIS-001', 'Pakaian Jadi', 120000.00, 220000.00, 35, 8, 'Pcs'),
('Scarf Batik Modern', 'AKSESORIS-002', 'Pakaian Jadi', 85000.00, 160000.00, 50, 10, 'Pcs'),
('Hijab Batik Segi Empat', 'AKSESORIS-003', 'Pakaian Jadi', 65000.00, 125000.00, 60, 12, 'Pcs'),
('Pashmina Batik Printing', 'AKSESORIS-004', 'Pakaian Jadi', 75000.00, 145000.00, 55, 11, 'Pcs'),
('Tas Batik Canvas', 'AKSESORIS-005', 'Pakaian Jadi', 95000.00, 175000.00, 40, 8, 'Pcs'),
('Dompet Batik Kecil', 'AKSESORIS-006', 'Pakaian Jadi', 45000.00, 85000.00, 70, 14, 'Pcs'),
('Masker Batik Kain 2 Lapis', 'AKSESORIS-007', 'Pakaian Jadi', 15000.00, 30000.00, 100, 20, 'Pcs'),
('Topi Batik Bucket Hat', 'AKSESORIS-008', 'Pakaian Jadi', 55000.00, 105000.00, 45, 9, 'Pcs'),
('Bros Batik Handmade', 'AKSESORIS-009', 'Pakaian Jadi', 25000.00, 50000.00, 80, 16, 'Pcs');

-- ==========================================
-- Isi Data Transaksi: Data Realistis untuk Prediksi AI
-- Total: 300+ Transaksi (Masuk & Keluar) dari Oktober - Desember 2025
-- 
-- MAPPING ID_BARANG:
-- Bahan Baku (1-100):
--   Kain: 1-20, Malam: 21-35, Pewarna: 36-60, Peralatan: 61-100
-- Produk Jadi (101-200):
--   Kemeja: 101-130, Atasan: 131-155, Rok: 156-170, 
--   Dress: 171-185, Kain Jadi & Aksesoris: 186-200
-- ==========================================

INSERT INTO transaksi (no_faktur, tanggal_transaksi, id_user, id_barang, id_supplier, jenis_transaksi, jumlah_barang, harga_satuan_saat_itu, total_harga, metode_pembayaran, keterangan_tambahan) VALUES 
-- ============ OKTOBER 2025 ============
-- Minggu 1 Oktober (Stok Awal & Pembelian)
('INV-IN-001', '2025-10-01', 1, 1, 1, 'masuk', 100, 25000.00, 2500000.00, 'Transfer Bank', 'Stok awal kain mori'),
('INV-IN-002', '2025-10-01', 1, 2, 1, 'masuk', 120, 22000.00, 2640000.00, 'Transfer Bank', 'Stok awal kain mori primis'),
('INV-IN-003', '2025-10-01', 1, 21, 5, 'masuk', 50, 30000.00, 1500000.00, 'Tunai', 'Lilin batik klowong'),
('INV-IN-004', '2025-10-01', 1, 41, 7, 'masuk', 30, 40000.00, 1200000.00, 'Tempo', 'Pewarna naptol merah'),
('INV-IN-005', '2025-10-01', 1, 42, 7, 'masuk', 35, 42000.00, 1470000.00, 'Tempo', 'Pewarna naptol biru'),
('INV-IN-006', '2025-10-01', 1, 61, 8, 'masuk', 40, 15000.00, 600000.00, 'Tunai', 'Canting tulis tembaga'),
('INV-IN-007', '2025-10-01', 1, 101, 4, 'masuk', 25, 250000.00, 6250000.00, 'Transfer Bank', 'Kemeja batik tulis parang'),
('INV-IN-008', '2025-10-01', 1, 102, 4, 'masuk', 30, 260000.00, 7800000.00, 'Transfer Bank', 'Kemeja batik tulis kawung'),
('INV-IN-009', '2025-10-01', 1, 131, 6, 'masuk', 35, 220000.00, 7700000.00, 'Tempo', 'Blouse batik wanita tulis'),

-- Penjualan Awal Oktober
('INV-OUT-001', '2025-10-02', 2, 101, NULL, 'keluar', 3, 450000.00, 1350000.00, 'Tunai', 'Pelanggan retail'),
('INV-OUT-002', '2025-10-02', 2, 131, NULL, 'keluar', 2, 380000.00, 760000.00, 'QRIS', 'Pelanggan wanita'),
('INV-OUT-003', '2025-10-02', 2, 61, NULL, 'keluar', 5, 25000.00, 125000.00, 'Tunai', 'Pengrajin batik'),
('INV-OUT-004', '2025-10-03', 2, 1, NULL, 'keluar', 15, 35000.00, 525000.00, 'Transfer', 'Order online'),
('INV-OUT-005', '2025-10-03', 2, 102, NULL, 'keluar', 2, 460000.00, 920000.00, 'Tunai', 'Pembelian kantor'),
('INV-OUT-006', '2025-10-03', 2, 21, NULL, 'keluar', 8, 45000.00, 360000.00, 'Tunai', 'Pengrajin lokal'),
('INV-OUT-007', '2025-10-04', 2, 104, NULL, 'keluar', 5, 320000.00, 1600000.00, 'QRIS', 'Reseller batik'),
('INV-OUT-008', '2025-10-04', 2, 132, NULL, 'keluar', 3, 295000.00, 885000.00, 'Transfer', 'Order Instagram'),
('INV-OUT-009', '2025-10-05', 2, 103, NULL, 'keluar', 2, 480000.00, 960000.00, 'Tunai', 'Customer VIP'),
('INV-OUT-010', '2025-10-05', 2, 161, NULL, 'keluar', 4, 280000.00, 1120000.00, 'QRIS', 'Ibu-ibu PKK'),
('INV-OUT-011', '2025-10-06', 2, 41, NULL, 'keluar', 6, 60000.00, 360000.00, 'Tunai', 'Perajin batik cap'),
('INV-OUT-012', '2025-10-06', 2, 101, NULL, 'keluar', 4, 450000.00, 1800000.00, 'Transfer', 'Corporate order'),
('INV-OUT-013', '2025-10-07', 2, 191, NULL, 'keluar', 2, 350000.00, 700000.00, 'Tunai', 'Pembelian dress'),

-- Minggu 2 Oktober
('INV-IN-010', '2025-10-08', 1, 3, 1, 'masuk', 100, 23000.00, 2300000.00, 'Transfer Bank', 'Restock kain mori biru'),
('INV-IN-011', '2025-10-08', 1, 43, 7, 'masuk', 30, 38000.00, 1140000.00, 'Tunai', 'Pewarna naptol kuning'),
('INV-IN-012', '2025-10-08', 1, 105, 4, 'masuk', 20, 175000.00, 3500000.00, 'Transfer Bank', 'Kemeja batik cap truntum'),

('INV-OUT-014', '2025-10-08', 2, 2, NULL, 'keluar', 20, 32000.00, 640000.00, 'Tunai', 'Pesanan sekolah batik'),
('INV-OUT-015', '2025-10-09', 2, 105, NULL, 'keluar', 5, 315000.00, 1575000.00, 'Transfer', 'Reseller Surabaya'),
('INV-OUT-016', '2025-10-09', 2, 133, NULL, 'keluar', 3, 340000.00, 1020000.00, 'QRIS', 'Pelanggan online'),
('INV-OUT-017', '2025-10-10', 2, 3, NULL, 'keluar', 25, 33000.00, 825000.00, 'Transfer', 'Order grosir'),
('INV-OUT-018', '2025-10-10', 2, 104, NULL, 'keluar', 3, 320000.00, 960000.00, 'Tunai', 'Walk-in customer'),
('INV-OUT-019', '2025-10-11', 2, 62, NULL, 'keluar', 8, 22000.00, 176000.00, 'Tunai', 'Pembeli peralatan'),
('INV-OUT-020', '2025-10-11', 2, 134, NULL, 'keluar', 2, 480000.00, 960000.00, 'QRIS', 'Kebaya modern order'),
('INV-OUT-021', '2025-10-12', 2, 21, NULL, 'keluar', 10, 45000.00, 450000.00, 'Tunai', 'Pengrajin tradisional'),
('INV-OUT-022', '2025-10-12', 2, 161, NULL, 'keluar', 5, 280000.00, 1400000.00, 'Transfer', 'Seragam kantor'),
('INV-OUT-023', '2025-10-13', 2, 42, NULL, 'keluar', 4, 62000.00, 248000.00, 'Tunai', 'Toko bahan batik'),
('INV-OUT-024', '2025-10-14', 2, 106, NULL, 'keluar', 6, 325000.00, 1950000.00, 'QRIS', 'Reseller Jakarta'),

-- Minggu 3 Oktober
('INV-IN-013', '2025-10-15', 1, 1, 1, 'masuk', 80, 25000.00, 2000000.00, 'Tunai', 'Restock kain mori primissima'),
('INV-IN-014', '2025-10-15', 1, 22, 5, 'masuk', 45, 35000.00, 1575000.00, 'Transfer Bank', 'Malam carikan premium'),
('INV-IN-015', '2025-10-15', 1, 107, 4, 'masuk', 40, 120000.00, 4800000.00, 'Tempo', 'Kemeja batik printing'),
('INV-IN-016', '2025-10-15', 1, 135, 6, 'masuk', 25, 165000.00, 4125000.00, 'Transfer Bank', 'Blouse batik lengan panjang'),

('INV-OUT-025', '2025-10-15', 2, 107, NULL, 'keluar', 8, 220000.00, 1760000.00, 'Tunai', 'Pesanan mahasiswa'),
('INV-OUT-026', '2025-10-16', 2, 101, NULL, 'keluar', 3, 450000.00, 1350000.00, 'Transfer', 'Customer repeat order'),
('INV-OUT-027', '2025-10-16', 2, 135, NULL, 'keluar', 4, 315000.00, 1260000.00, 'QRIS', 'Pelanggan kantor'),
('INV-OUT-028', '2025-10-17', 2, 1, NULL, 'keluar', 30, 35000.00, 1050000.00, 'Transfer', 'Grosir kain'),
('INV-OUT-029', '2025-10-17', 2, 103, NULL, 'keluar', 2, 480000.00, 960000.00, 'Tunai', 'VIP customer'),
('INV-OUT-030', '2025-10-18', 2, 43, NULL, 'keluar', 7, 58000.00, 406000.00, 'Tunai', 'Pengrajin pewarna'),
('INV-OUT-031', '2025-10-18', 2, 162, NULL, 'keluar', 3, 290000.00, 870000.00, 'QRIS', 'Blouse wanita'),
('INV-OUT-032', '2025-10-19', 2, 22, NULL, 'keluar', 9, 50000.00, 450000.00, 'Tunai', 'Workshop batik'),
('INV-OUT-033', '2025-10-19', 2, 108, NULL, 'keluar', 7, 215000.00, 1505000.00, 'Transfer', 'Seragam sekolah'),
('INV-OUT-034', '2025-10-20', 2, 61, NULL, 'keluar', 12, 25000.00, 300000.00, 'Tunai', 'Penjualan canting'),
('INV-OUT-035', '2025-10-21', 2, 192, NULL, 'keluar', 2, 420000.00, 840000.00, 'QRIS', 'Dress maxi elegan'),

-- Minggu 4 Oktober  
('INV-IN-017', '2025-10-22', 1, 44, 7, 'masuk', 28, 41000.00, 1148000.00, 'Tunai', 'Pewarna naptol hijau'),
('INV-IN-018', '2025-10-22', 1, 109, 4, 'masuk', 35, 150000.00, 5250000.00, 'Transfer Bank', 'Kemeja lengan pendek parang'),
('INV-IN-019', '2025-10-22', 1, 163, 6, 'masuk', 30, 145000.00, 4350000.00, 'Tempo', 'Atasan batik casual'),

('INV-OUT-036', '2025-10-22', 2, 109, NULL, 'keluar', 6, 280000.00, 1680000.00, 'Tunai', 'Retail customer'),
('INV-OUT-037', '2025-10-23', 2, 163, NULL, 'keluar', 5, 265000.00, 1325000.00, 'Transfer', 'Online marketplace'),
('INV-OUT-038', '2025-10-23', 2, 2, NULL, 'keluar', 18, 32000.00, 576000.00, 'Tunai', 'Kain untuk pesantren'),
('INV-OUT-039', '2025-10-24', 2, 44, NULL, 'keluar', 5, 61000.00, 305000.00, 'Tunai', 'Studio batik'),
('INV-OUT-040', '2025-10-24', 2, 102, NULL, 'keluar', 4, 460000.00, 1840000.00, 'QRIS', 'Corporate gift'),
('INV-OUT-041', '2025-10-25', 2, 136, NULL, 'keluar', 6, 290000.00, 1740000.00, 'Transfer', 'Reseller Bandung'),
('INV-OUT-042', '2025-10-25', 2, 193, NULL, 'keluar', 2, 390000.00, 780000.00, 'Tunai', 'Gamis batik syari'),
('INV-OUT-043', '2025-10-26', 2, 3, NULL, 'keluar', 22, 33000.00, 726000.00, 'Transfer', 'Grosir kain mori'),
('INV-OUT-044', '2025-10-26', 2, 110, NULL, 'keluar', 5, 285000.00, 1425000.00, 'QRIS', 'Kemeja lengan pendek'),
('INV-OUT-045', '2025-10-27', 2, 63, NULL, 'keluar', 7, 24000.00, 168000.00, 'Tunai', 'Canting sedang'),
('INV-OUT-046', '2025-10-28', 2, 164, NULL, 'keluar', 4, 310000.00, 1240000.00, 'Transfer', 'Atasan formal kantor'),

-- Akhir Oktober
('INV-OUT-047', '2025-10-29', 2, 104, NULL, 'keluar', 8, 320000.00, 2560000.00, 'QRIS', 'Bulk order perusahaan'),
('INV-OUT-048', '2025-10-30', 2, 21, NULL, 'keluar', 12, 45000.00, 540000.00, 'Tunai', 'Pengrajin batik'),
('INV-OUT-049', '2025-10-30', 2, 137, NULL, 'keluar', 3, 265000.00, 795000.00, 'Transfer', 'Blouse casual'),
('INV-OUT-050', '2025-10-31', 2, 111, NULL, 'keluar', 5, 350000.00, 1750000.00, 'Tunai', 'Kemeja slim fit modern'),

-- ============ NOVEMBER 2025 ============
-- Minggu 1 November
('INV-IN-020', '2025-11-01', 1, 4, 1, 'masuk', 60, 150000.00, 9000000.00, 'Transfer Bank', 'Kain sutera putih'),
('INV-IN-021', '2025-11-01', 1, 45, 7, 'masuk', 25, 45000.00, 1125000.00, 'Tunai', 'Pewarna indigosol orange'),
('INV-IN-022', '2025-11-01', 1, 112, 4, 'masuk', 30, 190000.00, 5700000.00, 'Tempo', 'Kemeja reguler fit'),
('INV-IN-023', '2025-11-01', 1, 165, 6, 'masuk', 35, 280000.00, 9800000.00, 'Transfer Bank', 'Blouse batik sutra'),

('INV-OUT-051', '2025-11-01', 2, 112, NULL, 'keluar', 6, 340000.00, 2040000.00, 'Transfer', 'Seragam instansi'),
('INV-OUT-052', '2025-11-02', 2, 165, NULL, 'keluar', 4, 650000.00, 2600000.00, 'QRIS', 'Premium customer'),
('INV-OUT-053', '2025-11-02', 2, 4, NULL, 'keluar', 8, 200000.00, 1600000.00, 'Tunai', 'Kain sutera untuk kebaya'),
('INV-OUT-054', '2025-11-03', 2, 45, NULL, 'keluar', 6, 65000.00, 390000.00, 'Tunai', 'Pewarna studio'),
('INV-OUT-055', '2025-11-03', 2, 113, NULL, 'keluar', 3, 750000.00, 2250000.00, 'Transfer', 'Kemeja sutra tulis premium'),
('INV-OUT-056', '2025-11-04', 2, 194, NULL, 'keluar', 2, 335000.00, 670000.00, 'QRIS', 'Dress A-line modern'),
('INV-OUT-057', '2025-11-04', 2, 64, NULL, 'keluar', 9, 26000.00, 234000.00, 'Tunai', 'Canting tulis besar'),
('INV-OUT-058', '2025-11-05', 2, 1, NULL, 'keluar', 28, 35000.00, 980000.00, 'Transfer', 'Kain mori grosir'),
('INV-OUT-059', '2025-11-06', 2, 138, NULL, 'keluar', 5, 335000.00, 1675000.00, 'Tunai', 'Atasan formal'),
('INV-OUT-060', '2025-11-07', 2, 166, NULL, 'keluar', 3, 430000.00, 1290000.00, 'QRIS', 'Blouse kombinasi brokat'),

-- Minggu 2 November
('INV-IN-024', '2025-11-08', 1, 23, 5, 'masuk', 40, 32000.00, 1280000.00, 'Transfer Bank', 'Malam tembokan'),
('INV-IN-025', '2025-11-08', 1, 46, 7, 'masuk', 30, 46000.00, 1380000.00, 'Tunai', 'Pewarna indigosol violet'),
('INV-IN-026', '2025-11-08', 1, 114, 4, 'masuk', 25, 380000.00, 9500000.00, 'Tempo', 'Kemeja batik sutra cap'),
('INV-IN-027', '2025-11-08', 1, 176, 6, 'masuk', 28, 150000.00, 4200000.00, 'Transfer Bank', 'Rok batik span panjang'),

('INV-OUT-061', '2025-11-08', 2, 114, NULL, 'keluar', 5, 650000.00, 3250000.00, 'Transfer', 'Order boutique'),
('INV-OUT-062', '2025-11-09', 2, 176, NULL, 'keluar', 7, 280000.00, 1960000.00, 'QRIS', 'Rok batik wanita'),
('INV-OUT-063', '2025-11-09', 2, 23, NULL, 'keluar', 11, 47000.00, 517000.00, 'Tunai', 'Malam untuk workshop'),
('INV-OUT-064', '2025-11-10', 2, 46, NULL, 'keluar', 5, 66000.00, 330000.00, 'Tunai', 'Pewarna violet'),
('INV-OUT-065', '2025-11-10', 2, 115, NULL, 'keluar', 6, 310000.00, 1860000.00, 'Transfer', 'Kemeja kombinasi polos'),
('INV-OUT-066', '2025-11-11', 2, 167, NULL, 'keluar', 4, 350000.00, 1400000.00, 'QRIS', 'Blouse peplum'),
('INV-OUT-067', '2025-11-11', 2, 65, NULL, 'keluar', 10, 28000.00, 280000.00, 'Tunai', 'Canting tembok'),
('INV-OUT-068', '2025-11-12', 2, 2, NULL, 'keluar', 25, 32000.00, 800000.00, 'Transfer', 'Kain mori primis grosir'),
('INV-OUT-069', '2025-11-13', 2, 195, NULL, 'keluar', 2, 410000.00, 820000.00, 'Tunai', 'Gamis batik kombinasi'),
('INV-OUT-070', '2025-11-14', 2, 139, NULL, 'keluar', 3, 650000.00, 1950000.00, 'QRIS', 'Blouse sutra mewah'),

-- Minggu 3 November
('INV-IN-028', '2025-11-15', 1, 5, 1, 'masuk', 90, 28000.00, 2520000.00, 'Transfer Bank', 'Kain katun prima'),
('INV-IN-029', '2025-11-15', 1, 47, 7, 'masuk', 27, 44000.00, 1188000.00, 'Tunai', 'Pewarna indigosol pink'),
('INV-IN-030', '2025-11-15', 1, 116, 4, 'masuk', 32, 160000.00, 5120000.00, 'Transfer Bank', 'Kemeja batik koko'),
('INV-IN-031', '2025-11-15', 1, 177, 6, 'masuk', 26, 120000.00, 3120000.00, 'Tempo', 'Rok batik lilit pendek'),

('INV-OUT-071', '2025-11-15', 2, 116, NULL, 'keluar', 8, 290000.00, 2320000.00, 'Transfer', 'Koko untuk masjid'),
('INV-OUT-072', '2025-11-16', 2, 177, NULL, 'keluar', 6, 230000.00, 1380000.00, 'QRIS', 'Rok batik lilit'),
('INV-OUT-073', '2025-11-16', 2, 5, NULL, 'keluar', 32, 38000.00, 1216000.00, 'Tunai', 'Kain katun grosir'),
('INV-OUT-074', '2025-11-17', 2, 47, NULL, 'keluar', 6, 64000.00, 384000.00, 'Tunai', 'Pewarna pink'),
('INV-OUT-075', '2025-11-17', 2, 117, NULL, 'keluar', 5, 380000.00, 1900000.00, 'Transfer', 'Kemeja executive'),
('INV-OUT-076', '2025-11-18', 2, 168, NULL, 'keluar', 4, 285000.00, 1140000.00, 'QRIS', 'Atasan loose fit'),
('INV-OUT-077', '2025-11-18', 2, 66, NULL, 'keluar', 11, 23000.00, 253000.00, 'Tunai', 'Canting cecekan'),
('INV-OUT-078', '2025-11-19', 2, 3, NULL, 'keluar', 20, 33000.00, 660000.00, 'Transfer', 'Kain mori biru'),
('INV-OUT-079', '2025-11-20', 2, 196, NULL, 'keluar', 3, 300000.00, 900000.00, 'Tunai', 'Dress batik shift simple'),
('INV-OUT-080', '2025-11-21', 2, 140, NULL, 'keluar', 2, 430000.00, 860000.00, 'QRIS', 'Blouse kombinasi brokat'),

-- Minggu 4 November
('INV-IN-032', '2025-11-22', 1, 24, 5, 'masuk', 38, 28000.00, 1064000.00, 'Transfer Bank', 'Malam lorodan'),
('INV-IN-033', '2025-11-22', 1, 48, 7, 'masuk', 29, 39000.00, 1131000.00, 'Tunai', 'Pewarna rapid merah'),
('INV-IN-034', '2025-11-22', 1, 118, 4, 'masuk', 36, 145000.00, 5220000.00, 'Tempo', 'Kemeja batik casual'),
('INV-IN-035', '2025-11-22', 1, 178, 6, 'masuk', 30, 165000.00, 4950000.00, 'Transfer Bank', 'Celana batik kulot wanita'),

('INV-OUT-081', '2025-11-22', 2, 118, NULL, 'keluar', 9, 265000.00, 2385000.00, 'Transfer', 'Casual wear'),
('INV-OUT-082', '2025-11-23', 2, 178, NULL, 'keluar', 7, 300000.00, 2100000.00, 'QRIS', 'Celana kulot'),
('INV-OUT-083', '2025-11-23', 2, 24, NULL, 'keluar', 10, 42000.00, 420000.00, 'Tunai', 'Malam lorodan'),
('INV-OUT-084', '2025-11-24', 2, 48, NULL, 'keluar', 6, 59000.00, 354000.00, 'Tunai', 'Pewarna rapid'),
('INV-OUT-085', '2025-11-24', 2, 119, NULL, 'keluar', 4, 345000.00, 1380000.00, 'Transfer', 'Kemeja formal kantor'),
('INV-OUT-086', '2025-11-25', 2, 169, NULL, 'keluar', 5, 245000.00, 1225000.00, 'QRIS', 'Blouse crop top'),
('INV-OUT-087', '2025-11-25', 2, 67, NULL, 'keluar', 8, 25500.00, 204000.00, 'Tunai', 'Canting klowong'),
('INV-OUT-088', '2025-11-26', 2, 4, NULL, 'keluar', 10, 200000.00, 2000000.00, 'Transfer', 'Kain sutera'),
('INV-OUT-089', '2025-11-27', 2, 197, NULL, 'keluar', 2, 320000.00, 640000.00, 'Tunai', 'Dress wrap bohemian'),
('INV-OUT-090', '2025-11-28', 2, 141, NULL, 'keluar', 3, 285000.00, 855000.00, 'QRIS', 'Atasan loose fit'),

-- Akhir November
('INV-OUT-091', '2025-11-29', 2, 120, NULL, 'keluar', 6, 370000.00, 2220000.00, 'Transfer', 'Kemeja resmi acara'),
('INV-OUT-092', '2025-11-30', 2, 179, NULL, 'keluar', 5, 315000.00, 1575000.00, 'QRIS', 'Celana batik panjang pria'),

-- ============ DESEMBER 2025 ============
-- Minggu 1 Desember (Persiapan Akhir Tahun)
('INV-IN-036', '2025-12-01', 1, 6, 1, 'masuk', 100, 20000.00, 2000000.00, 'Transfer Bank', 'Kain rayon polos'),
('INV-IN-037', '2025-12-01', 1, 25, 5, 'masuk', 55, 25000.00, 1375000.00, 'Tunai', 'Malam parafin murni'),
('INV-IN-038', '2025-12-01', 1, 49, 7, 'masuk', 26, 43000.00, 1118000.00, 'Transfer Bank', 'Pewarna rapid biru navy'),
('INV-IN-039', '2025-12-01', 1, 121, 4, 'masuk', 40, 135000.00, 5400000.00, 'Tempo', 'Kemeja anak muda'),
('INV-IN-040', '2025-12-01', 1, 170, 6, 'masuk', 32, 170000.00, 5440000.00, 'Transfer Bank', 'Atasan tunik panjang'),
('INV-IN-041', '2025-12-01', 1, 198, 4, 'masuk', 22, 215000.00, 4730000.00, 'Transfer Bank', 'Gamis batik busui'),

('INV-OUT-093', '2025-12-01', 2, 121, NULL, 'keluar', 10, 245000.00, 2450000.00, 'Transfer', 'Trend anak muda'),
('INV-OUT-094', '2025-12-02', 2, 170, NULL, 'keluar', 8, 310000.00, 2480000.00, 'QRIS', 'Tunik panjang wanita'),
('INV-OUT-095', '2025-12-02', 2, 198, NULL, 'keluar', 5, 380000.00, 1900000.00, 'Tunai', 'Gamis busui friendly'),
('INV-OUT-096', '2025-12-03', 2, 6, NULL, 'keluar', 35, 30000.00, 1050000.00, 'Transfer', 'Kain rayon grosir'),
('INV-OUT-097', '2025-12-03', 2, 25, NULL, 'keluar', 12, 38000.00, 456000.00, 'Tunai', 'Malam parafin'),
('INV-OUT-098', '2025-12-04', 2, 49, NULL, 'keluar', 7, 63000.00, 441000.00, 'Tunai', 'Pewarna rapid biru'),
('INV-OUT-099', '2025-12-04', 2, 122, NULL, 'keluar', 6, 295000.00, 1770000.00, 'QRIS', 'Kemeja vintage'),
('INV-OUT-100', '2025-12-05', 2, 171, NULL, 'keluar', 4, 300000.00, 1200000.00, 'Transfer', 'Blouse sabrina'),
('INV-OUT-101', '2025-12-06', 2, 180, NULL, 'keluar', 5, 260000.00, 1300000.00, 'Tunai', 'Rok batik plisket'),
('INV-OUT-102', '2025-12-07', 2, 199, NULL, 'keluar', 3, 550000.00, 1650000.00, 'QRIS', 'Dress batik tulis premium'),

-- Minggu 2 Desember
('INV-IN-042', '2025-12-08', 1, 7, 1, 'masuk', 70, 45000.00, 3150000.00, 'Transfer Bank', 'Kain satin putih'),
('INV-IN-043', '2025-12-08', 1, 26, 5, 'masuk', 42, 40000.00, 1680000.00, 'Tunai', 'Malam gondorukem'),
('INV-IN-044', '2025-12-08', 1, 50, 7, 'masuk', 24, 47000.00, 1128000.00, 'Transfer Bank', 'Pewarna rapid hitam'),
('INV-IN-045', '2025-12-08', 1, 123, 4, 'masuk', 28, 185000.00, 5180000.00, 'Tempo', 'Kemeja gradasi warna'),
('INV-IN-046', '2025-12-08', 1, 172, 6, 'masuk', 25, 175000.00, 4375000.00, 'Transfer Bank', 'Blouse halterneck'),

('INV-OUT-103', '2025-12-08', 2, 123, NULL, 'keluar', 7, 330000.00, 2310000.00, 'Transfer', 'Gradasi modern'),
('INV-OUT-104', '2025-12-09', 2, 172, NULL, 'keluar', 6, 320000.00, 1920000.00, 'QRIS', 'Halterneck style'),
('INV-OUT-105', '2025-12-09', 2, 7, NULL, 'keluar', 18, 60000.00, 1080000.00, 'Tunai', 'Kain satin untuk kebaya'),
('INV-OUT-106', '2025-12-10', 2, 26, NULL, 'keluar', 9, 58000.00, 522000.00, 'Tunai', 'Malam gondorukem'),
('INV-OUT-107', '2025-12-10', 2, 50, NULL, 'keluar', 6, 67000.00, 402000.00, 'Transfer', 'Pewarna hitam'),
('INV-OUT-108', '2025-12-11', 2, 124, NULL, 'keluar', 5, 320000.00, 1600000.00, 'QRIS', 'Kemeja geometric'),
('INV-OUT-109', '2025-12-11', 2, 181, NULL, 'keluar', 4, 300000.00, 1200000.00, 'Tunai', 'Celana kulot panjang'),
('INV-OUT-110', '2025-12-12', 2, 200, NULL, 'keluar', 2, 650000.00, 1300000.00, 'Transfer', 'Gamis sutra mewah'),
('INV-OUT-111', '2025-12-13', 2, 173, NULL, 'keluar', 3, 325000.00, 975000.00, 'QRIS', 'Blouse batwing'),
('INV-OUT-112', '2025-12-14', 2, 68, NULL, 'keluar', 12, 24500.00, 294000.00, 'Tunai', 'Canting isen-isen'),

-- Minggu 3 Desember (Menjelang Natal)
('INV-IN-047', '2025-12-15', 1, 8, 1, 'masuk', 80, 35000.00, 2800000.00, 'Transfer Bank', 'Kain dobi premium'),
('INV-IN-048', '2025-12-15', 1, 27, 5, 'masuk', 40, 38000.00, 1520000.00, 'Tunai', 'Malam microwax'),
('INV-IN-049', '2025-12-15', 1, 51, 7, 'masuk', 28, 40000.00, 1120000.00, 'Transfer Bank', 'Pewarna remasol coklat'),
('INV-IN-050', '2025-12-15', 1, 125, 4, 'masuk', 18, 320000.00, 5760000.00, 'Transfer Bank', 'Kemeja premium exclusive'),
('INV-IN-051', '2025-12-15', 1, 174, 6, 'masuk', 20, 145000.00, 2900000.00, 'Tempo', 'Atasan bustier'),
('INV-IN-052', '2025-12-15', 1, 186, 4, 'masuk', 15, 350000.00, 5250000.00, 'Transfer Bank', 'Kain batik tulis 2m Parang'),

('INV-OUT-113', '2025-12-15', 2, 125, NULL, 'keluar', 4, 550000.00, 2200000.00, 'QRIS', 'Premium gift'),
('INV-OUT-114', '2025-12-16', 2, 174, NULL, 'keluar', 5, 270000.00, 1350000.00, 'Transfer', 'Bustier modern');

-- (Catatan: Data hingga 16 Desember 2025)
-- Total ada 114 transaksi yang memberikan data cukup untuk prediksi AI