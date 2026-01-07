-- phpMyAdmin SQL Dump
-- version 4.7.4
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jan 06, 2026 at 05:20 AM
-- Server version: 10.1.29-MariaDB
-- PHP Version: 7.2.0

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `2025_db_mad_proyek_uas`
--

-- --------------------------------------------------------

--
-- Table structure for table `pasien`
--

CREATE TABLE `pasien` (
  `id_pasien` int(11) NOT NULL,
  `nik_pasien` varchar(20) NOT NULL,
  `nama_pasien` varchar(100) NOT NULL,
  `jk_pasien` enum('Pria','Wanita') NOT NULL,
  `tgl_lahir_pasien` date NOT NULL,
  `alamat_pasien` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `pasien`
--

INSERT INTO `pasien` (`id_pasien`, `nik_pasien`, `nama_pasien`, `jk_pasien`, `tgl_lahir_pasien`, `alamat_pasien`) VALUES
(1, '3275011201010001', 'Ahmad Fauzi', 'Pria', '1990-01-12', 'Jl. Merdeka No. 12, Bandung'),
(2, '3275012202020002', 'Siti Aisyah', 'Wanita', '1995-02-22', 'Jl. Sudirman No. 45, Bandung'),
(3, '3275011503030003', 'Budi Santoso', 'Pria', '1988-03-15', 'Jl. Asia Afrika No. 78, Bandung'),
(4, '3275011804040004', 'Dewi Lestari', 'Wanita', '1992-04-18', 'Jl. Cihampelas No. 10, Bandung'),
(5, '3275012505050005', 'Rizky Ramadhan', 'Pria', '2000-05-25', 'Jl. Setiabudi No. 22, Bandung'),
(6, '3275011206060006', 'Nurul Hidayah', 'Wanita', '1998-06-12', 'Jl. Dago No. 99, Bandung'),
(7, '3275013007070007', 'Andi Pratama', 'Pria', '1985-07-30', 'Jl. Diponegoro No. 5, Bandung'),
(8, '3275012108080008', 'Fitri Laili', 'Wanita', '1997-08-21', 'Jl. Pasteur No. 18, Bandung'),
(9, '3275011409090009', 'Agus Salim', 'Pria', '1991-09-14', 'Jl. Braga No. 3, Bandung'),
(10, '3275011010100010', 'Lina Marlina', 'Wanita', '1994-10-10', 'Jl. Antapani No. 44, Bandung');

-- --------------------------------------------------------

--
-- Table structure for table `riwayat_periksa`
--

CREATE TABLE `riwayat_periksa` (
  `id_riwayatperiksa` int(11) NOT NULL,
  `imt` decimal(4,1) DEFAULT NULL,
  `gula_darah` int(11) DEFAULT NULL,
  `tekanan_darah` int(11) DEFAULT NULL,
  `diagnosis` varchar(100) DEFAULT NULL,
  `risiko` text,
  `lama_rawat` int(11) NOT NULL,
  `tanggal_entri` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `id_pasien` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `riwayat_periksa`
--

INSERT INTO `riwayat_periksa` (`id_riwayatperiksa`, `imt`, `gula_darah`, `tekanan_darah`, `diagnosis`, `risiko`, `lama_rawat`, `tanggal_entri`, `id_pasien`) VALUES
(1, '23.5', 110, 120, 'Infeksi Ringan', 'Rendah', 6, '2025-12-14 22:33:04', 1),
(2, '29.0', 160, 150, 'PPOK', 'Tinggi', 2, '2025-12-14 22:33:04', 2),
(3, '21.8', 95, 120, 'Gastritis', 'Rendah', 1, '2025-12-14 22:33:04', 3),
(4, '30.2', 150, 165, 'Gagal Jantung', 'Tinggi', 10, '2025-12-14 22:33:04', 4),
(5, '27.5', 140, 140, 'Hipertensi', 'Sedang', 4, '2025-12-14 22:33:04', 5),
(6, '24.0', 105, 125, 'Asma', 'Rendah', 5, '2025-12-14 22:33:04', 2),
(7, '31.0', 170, 155, 'Stroke Ringan', 'Tinggi', 12, '2025-12-14 22:33:04', 2),
(8, '22.0', 90, 115, 'Demam', 'Rendah', 2, '2025-12-14 22:33:04', 2),
(9, '23.8', 100, 120, 'Infeksi', 'Rendah', 7, '2025-12-14 22:33:04', 3),
(10, '28.5', 155, 145, 'Diabetes', 'Sedang', 3, '2025-12-14 22:33:04', 4);

-- --------------------------------------------------------

--
-- Table structure for table `riwayat_ulasan`
--

CREATE TABLE `riwayat_ulasan` (
  `id_riwayatulasan` int(11) NOT NULL,
  `ulasan` text NOT NULL,
  `sentimen` text,
  `tanggal_entri` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `id_pasien` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `riwayat_ulasan`
--

INSERT INTO `riwayat_ulasan` (`id_riwayatulasan`, `ulasan`, `sentimen`, `tanggal_entri`, `id_pasien`) VALUES
(1, 'Pelayanan sangat baik dan cepat', 'Positif', '2025-12-14 22:33:04', 1),
(2, 'Antrian lama dan sistem buruk', 'Negatif', '2025-12-14 22:33:04', 2),
(3, 'Perawat cukup ramah', 'Netral', '2025-12-14 22:33:04', 3),
(4, 'Dokter menjelaskan dengan detail dan jelas', 'Positif', '2025-12-14 22:33:04', 4),
(5, 'Ruang tunggu panas dan penuh', 'Negatif', '2025-12-14 22:33:04', 5),
(6, 'Pelayanan administrasi cukup membantu', 'Netral', '2025-12-14 22:33:04', 2),
(7, 'Dokter kurang komunikatif', 'Negatif', '2025-12-14 22:33:04', 2),
(8, 'Fasilitas bersih dan perawat sigap', 'Positif', '2025-12-14 22:33:04', 2),
(9, 'Proses pendaftaran online mudah', 'Positif', '2025-12-14 22:33:04', 3),
(10, 'Pelayanan lambat saat jam ramai', 'Negatif', '2025-12-14 22:33:04', 4);

-- --------------------------------------------------------

--
-- Table structure for table `user`
--

CREATE TABLE `user` (
  `id_user` int(11) NOT NULL,
  `username` varchar(100) NOT NULL,
  `password` varchar(100) NOT NULL,
  `hak_akses` enum('admin','pemilik') NOT NULL,
  `akses_terakhir` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `user`
--

INSERT INTO `user` (`id_user`, `username`, `password`, `hak_akses`, `akses_terakhir`) VALUES
(1, 'admin', '123', 'admin', '2026-01-06 10:57:46'),
(2, 'pemilik', '123', 'pemilik', '2025-11-17 07:17:59');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `pasien`
--
ALTER TABLE `pasien`
  ADD PRIMARY KEY (`id_pasien`);

--
-- Indexes for table `riwayat_periksa`
--
ALTER TABLE `riwayat_periksa`
  ADD PRIMARY KEY (`id_riwayatperiksa`);

--
-- Indexes for table `riwayat_ulasan`
--
ALTER TABLE `riwayat_ulasan`
  ADD PRIMARY KEY (`id_riwayatulasan`);

--
-- Indexes for table `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`id_user`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `pasien`
--
ALTER TABLE `pasien`
  MODIFY `id_pasien` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=14;

--
-- AUTO_INCREMENT for table `riwayat_periksa`
--
ALTER TABLE `riwayat_periksa`
  MODIFY `id_riwayatperiksa` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT for table `riwayat_ulasan`
--
ALTER TABLE `riwayat_ulasan`
  MODIFY `id_riwayatulasan` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT for table `user`
--
ALTER TABLE `user`
  MODIFY `id_user` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
