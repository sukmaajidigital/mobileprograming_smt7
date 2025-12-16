-- Database: Sistem Informasi Kasir Batik
-- Created: 2025-11-27

-- Hapus database jika sudah ada (opsional)
-- DROP DATABASE IF EXISTS db_kasir_batik;

-- Buat database
CREATE DATABASE IF NOT EXISTS db_kasir_batik;
USE db_kasir_batik;

-- ========================================
-- Tabel Produk
-- ========================================
CREATE TABLE produk (
    id_produk INT PRIMARY KEY AUTO_INCREMENT,
    kode_produk VARCHAR(20) NOT NULL UNIQUE,
    nama_produk VARCHAR(100) NOT NULL,
    jenis_batik VARCHAR(50) NOT NULL,
    ukuran VARCHAR(10) NOT NULL,
    harga DECIMAL(10,2) NOT NULL,
    stok INT NOT NULL DEFAULT 0,
    INDEX idx_kode_produk (kode_produk),
    INDEX idx_jenis_batik (jenis_batik)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ========================================
-- Tabel Pelanggan
-- ========================================
CREATE TABLE pelanggan (
    id_pelanggan INT PRIMARY KEY AUTO_INCREMENT,
    nama_pelanggan VARCHAR(100) NOT NULL,
    jenis_kelamin ENUM('Laki-laki', 'Perempuan') NOT NULL,
    no_hp VARCHAR(15) NOT NULL,
    email VARCHAR(100),
    alamat TEXT NOT NULL,
    tanggal_daftar DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_nama_pelanggan (nama_pelanggan),
    INDEX idx_no_hp (no_hp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ========================================
-- Tabel Transaksi
-- ========================================
CREATE TABLE transaksi (
    id_transaksi INT PRIMARY KEY AUTO_INCREMENT,
    kode_transaksi VARCHAR(30) NOT NULL UNIQUE,
    id_pelanggan INT NOT NULL,
    tanggal_transaksi DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    total_item INT NOT NULL DEFAULT 0,
    total_bayar DECIMAL(12,2) NOT NULL DEFAULT 0,
    metode_pembayaran ENUM('Tunai', 'Transfer') NOT NULL,
    FOREIGN KEY (id_pelanggan) REFERENCES pelanggan(id_pelanggan) ON DELETE RESTRICT ON UPDATE CASCADE,
    INDEX idx_kode_transaksi (kode_transaksi),
    INDEX idx_tanggal_transaksi (tanggal_transaksi),
    INDEX idx_id_pelanggan (id_pelanggan)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ========================================
-- Tabel Detail Transaksi
-- ========================================
CREATE TABLE detail_transaksi (
    id_detail INT PRIMARY KEY AUTO_INCREMENT,
    id_transaksi INT NOT NULL,
    id_produk INT NOT NULL,
    kode_produk VARCHAR(20) NOT NULL,
    nama_produk VARCHAR(100) NOT NULL,
    jumlah_beli INT NOT NULL,
    harga_satuan DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(12,2) NOT NULL,
    diskon_item DECIMAL(10,2) NOT NULL DEFAULT 0,
    total_item DECIMAL(12,2) NOT NULL,
    FOREIGN KEY (id_transaksi) REFERENCES transaksi(id_transaksi) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (id_produk) REFERENCES produk(id_produk) ON DELETE RESTRICT ON UPDATE CASCADE,
    INDEX idx_id_transaksi (id_transaksi),
    INDEX idx_id_produk (id_produk)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ========================================
-- Tabel User
-- ========================================
CREATE TABLE user (
    id_user INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL,
    hak_akses ENUM('admin', 'kasir', 'pemilik') NOT NULL,
    akses_terakhir DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ========================================
-- Insert Data Sample Produk
-- ========================================
INSERT INTO produk (kode_produk, nama_produk, jenis_batik, ukuran, harga, stok) VALUES
('BTK001', 'Batik Parang Solo', 'Tulis', 'M', 350000.00, 15),
('BTK002', 'Batik Mega Mendung', 'Cap', 'L', 275000.00, 20),
('BTK003', 'Batik Kawung Klasik', 'Tulis', 'XL', 425000.00, 10),
('BTK004', 'Batik Sekar Jagad', 'Printing', 'M', 150000.00, 30),
('BTK005', 'Batik Truntum Modern', 'Kombinasi', 'L', 380000.00, 12),
('BTK006', 'Batik Sogan Jogja', 'Tulis', 'M', 400000.00, 8),
('BTK007', 'Batik Pekalongan Pesisir', 'Cap', 'XL', 320000.00, 18),
('BTK008', 'Batik Lasem Kontemporer', 'Printing', 'S', 125000.00, 25);

-- ========================================
-- Insert Data Sample Pelanggan
-- ========================================
INSERT INTO pelanggan (nama_pelanggan, jenis_kelamin, no_hp, email, alamat, tanggal_daftar) VALUES
('Siti Nurhaliza', 'Perempuan', '081234567890', 'siti.nurhaliza@email.com', 'Jl. Sudirman No. 45, Jakarta Pusat', '2025-01-15 10:30:00'),
('Budi Santoso', 'Laki-laki', '082345678901', 'budi.santoso@email.com', 'Jl. Gatot Subroto No. 12, Bandung', '2025-02-20 14:15:00'),
('Dewi Kartika', 'Perempuan', '083456789012', 'dewi.kartika@email.com', 'Jl. Ahmad Yani No. 78, Surabaya', '2025-03-10 09:45:00'),
('Ahmad Rifai', 'Laki-laki', '084567890123', 'ahmad.rifai@email.com', 'Jl. Diponegoro No. 23, Yogyakarta', '2025-04-05 16:20:00'),
('Rina Wulandari', 'Perempuan', '085678901234', 'rina.wulandari@email.com', 'Jl. Thamrin No. 56, Semarang', '2025-05-18 11:00:00');

-- ========================================
-- Insert Data Sample User
-- ========================================
INSERT INTO user (username, password, hak_akses) VALUES
('admin', '123', 'admin'),
('kasir', '123', 'kasir'),
('pemilik', '123', 'pemilik');
