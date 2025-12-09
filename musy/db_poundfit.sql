-- Database: Sistem Informasi Pendaftaran Kelas Poundfit
-- Created: 2025-12-09

-- Hapus database jika sudah ada (opsional)
-- DROP DATABASE IF EXISTS db_poundfit;

-- Buat database
CREATE DATABASE IF NOT EXISTS db_poundfit;
USE db_poundfit;

-- ========================================
-- Tabel User (untuk login)
-- ========================================
CREATE TABLE user (
    id_user INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL,
    hak_akses ENUM('admin', 'instruktur', 'pemilik') NOT NULL,
    akses_terakhir DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ========================================
-- Tabel Peserta
-- ========================================
CREATE TABLE peserta (
    id_peserta INT PRIMARY KEY AUTO_INCREMENT,
    nama_lengkap VARCHAR(100) NOT NULL,
    jenis_kelamin ENUM('Laki-laki', 'Perempuan') NOT NULL,
    alamat TEXT NOT NULL,
    no_hp VARCHAR(15) NOT NULL,
    pekerjaan VARCHAR(100),
    status_keanggotaan ENUM('Aktif', 'Nonaktif', 'Trial') NOT NULL DEFAULT 'Trial',
    tanggal_daftar DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ========================================
-- Tabel Kelas Poundfit
-- ========================================
CREATE TABLE kelas_poundfit (
    id_kelas INT PRIMARY KEY AUTO_INCREMENT,
    nama_kelas VARCHAR(100) NOT NULL,
    hari ENUM('Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu') NOT NULL,
    jam TIME NOT NULL,
    lokasi_kelas VARCHAR(200) NOT NULL,
    tarif DECIMAL(10,2) NOT NULL,
    kapasitas INT NOT NULL DEFAULT 20,
    jumlah_peserta INT NOT NULL DEFAULT 0,
    INDEX idx_hari (hari),
    INDEX idx_nama_kelas (nama_kelas)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ========================================
-- Tabel Pendaftaran
-- ========================================
CREATE TABLE pendaftaran (
    id_pendaftaran INT PRIMARY KEY AUTO_INCREMENT,
    id_peserta INT NOT NULL,
    id_kelas INT NOT NULL,
    nama_peserta VARCHAR(100) NOT NULL,
    tanggal_daftar DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    metode_pembayaran ENUM('Tunai', 'Transfer', 'E-Wallet') NOT NULL,
    status_pembayaran ENUM('Lunas', 'Belum Lunas', 'Pending') NOT NULL DEFAULT 'Pending',
    tanggal_mulai DATE NOT NULL,
    tanggal_berakhir DATE NOT NULL,
    status_kehadiran ENUM('Hadir', 'Tidak Hadir', 'Izin', 'Belum Dimulai') NOT NULL DEFAULT 'Belum Dimulai',
    kode_pendaftaran VARCHAR(30) NOT NULL UNIQUE,
    FOREIGN KEY (id_peserta) REFERENCES peserta(id_peserta) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (id_kelas) REFERENCES kelas_poundfit(id_kelas) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ========================================
-- Insert Data Sample User
-- ========================================
INSERT INTO user (username, password, hak_akses) VALUES
('admin', '123', 'admin'),
('instruktur', '123', 'instruktur'),
('pemilik', '123', 'pemilik');

-- ========================================
-- Insert Data Sample Peserta
-- ========================================
INSERT INTO peserta (nama_lengkap, jenis_kelamin, alamat, no_hp, pekerjaan, status_keanggotaan, tanggal_daftar) VALUES
('Anisa Putri Maharani', 'Perempuan', 'Jl. Merdeka No. 15, Jakarta Selatan', '081234567890', 'Marketing Manager', 'Aktif', '2025-01-10 09:00:00'),
('Rizky Firmansyah', 'Laki-laki', 'Jl. Sudirman No. 88, Jakarta Pusat', '082345678901', 'Software Engineer', 'Aktif', '2025-01-15 10:30:00'),
('Diana Sari', 'Perempuan', 'Jl. Gatot Subroto No. 45, Tangerang', '083456789012', 'Dokter', 'Aktif', '2025-02-01 14:15:00'),
('Eko Prasetyo', 'Laki-laki', 'Jl. Ahmad Yani No. 67, Bekasi', '084567890123', 'Pengusaha', 'Trial', '2025-02-20 11:00:00'),
('Fitri Handayani', 'Perempuan', 'Jl. Kuningan No. 23, Jakarta Selatan', '085678901234', 'Guru', 'Aktif', '2025-03-05 08:30:00'),
('Gunawan Setiawan', 'Laki-laki', 'Jl. Thamrin No. 90, Jakarta Pusat', '086789012345', 'Arsitek', 'Nonaktif', '2025-03-10 16:45:00');

-- ========================================
-- Insert Data Sample Kelas Poundfit
-- ========================================
INSERT INTO kelas_poundfit (nama_kelas, hari, jam, lokasi_kelas, tarif, kapasitas, jumlah_peserta) VALUES
('Poundfit Beginner Morning', 'Senin', '06:00:00', 'Studio A - Lantai 2', 150000.00, 20, 5),
('Poundfit Intermediate', 'Senin', '18:00:00', 'Studio B - Lantai 3', 175000.00, 15, 8),
('Poundfit Advanced', 'Selasa', '19:00:00', 'Studio A - Lantai 2', 200000.00, 12, 10),
('Poundfit Fun Class', 'Rabu', '17:00:00', 'Studio C - Lantai 1', 150000.00, 25, 12),
('Poundfit Power Hour', 'Kamis', '06:30:00', 'Studio B - Lantai 3', 180000.00, 18, 6),
('Poundfit Weekend Special', 'Sabtu', '08:00:00', 'Studio A - Lantai 2', 200000.00, 20, 15),
('Poundfit Express', 'Sabtu', '16:00:00', 'Studio C - Lantai 1', 160000.00, 20, 9),
('Poundfit Sunday Blast', 'Minggu', '09:00:00', 'Studio B - Lantai 3', 190000.00, 15, 7);

-- ========================================
-- Insert Data Sample Pendaftaran
-- ========================================
INSERT INTO pendaftaran (id_peserta, id_kelas, nama_peserta, tanggal_daftar, metode_pembayaran, status_pembayaran, tanggal_mulai, tanggal_berakhir, status_kehadiran, kode_pendaftaran) VALUES
(1, 1, 'Anisa Putri Maharani', '2025-01-10 09:15:00', 'Transfer', 'Lunas', '2025-01-15', '2025-02-15', 'Hadir', 'REG-20250110-001'),
(2, 2, 'Rizky Firmansyah', '2025-01-15 10:45:00', 'E-Wallet', 'Lunas', '2025-01-20', '2025-02-20', 'Hadir', 'REG-20250115-002'),
(3, 3, 'Diana Sari', '2025-02-01 14:30:00', 'Tunai', 'Lunas', '2025-02-05', '2025-03-05', 'Hadir', 'REG-20250201-003'),
(4, 4, 'Eko Prasetyo', '2025-02-20 11:15:00', 'Transfer', 'Pending', '2025-02-25', '2025-03-25', 'Belum Dimulai', 'REG-20250220-004'),
(5, 5, 'Fitri Handayani', '2025-03-05 08:45:00', 'E-Wallet', 'Lunas', '2025-03-10', '2025-04-10', 'Hadir', 'REG-20250305-005'),
(1, 6, 'Anisa Putri Maharani', '2025-03-08 10:00:00', 'Transfer', 'Lunas', '2025-03-15', '2025-04-15', 'Hadir', 'REG-20250308-006');
