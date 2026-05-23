-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: May 23, 2026 at 02:13 PM
-- Server version: 8.0.30
-- PHP Version: 8.1.10

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `db_panti_mustika`
--

-- --------------------------------------------------------

--
-- Table structure for table `admin`
--

CREATE TABLE `admin` (
  `id` int NOT NULL,
  `username` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `email` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `password` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `admin`
--

INSERT INTO `admin` (`id`, `username`, `email`, `password`) VALUES
(1, 'admin', 'starseverus@gmail.com', 'scrypt:32768:8:1$4z76ipyMeikohsq9$53f2e46190438bb02f05fc2433031f9bf469b3277ece51ebee3289578d6acac578a2808291ff661aaa39a89f054b2fb31ff45ebfd56df44814d9cf990ba52990');

-- --------------------------------------------------------

--
-- Table structure for table `adopsi`
--

CREATE TABLE `adopsi` (
  `id` int NOT NULL,
  `penghuni_id` int NOT NULL,
  `nama_wali_adopsi` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  `nik_wali_adopsi` varchar(20) COLLATE utf8mb4_general_ci NOT NULL,
  `alamat_wali` text COLLATE utf8mb4_general_ci,
  `no_hp` varchar(20) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `pekerjaan` varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `status_pernikahan` enum('menikah','belum_menikah') COLLATE utf8mb4_general_ci DEFAULT NULL,
  `hubungan_dengan_anak` varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `tanggal_adopsi` date NOT NULL,
  `no_sk_adopsi` varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `instansi_pengesah` varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `adopsi`
--

INSERT INTO `adopsi` (`id`, `penghuni_id`, `nama_wali_adopsi`, `nik_wali_adopsi`, `alamat_wali`, `no_hp`, `pekerjaan`, `status_pernikahan`, `hubungan_dengan_anak`, `tanggal_adopsi`, `no_sk_adopsi`, `instansi_pengesah`, `created_at`) VALUES
(1, 6, 'ENDAH SULISTYOWATI', '3421002691039', 'NGEMPLAK', '082318713487', 'TIDAK/TIDAK BEKERJA', 'menikah', 'lainnya', '2026-05-16', '234', 'PUBLIKASI', '2026-05-16 13:24:55');

-- --------------------------------------------------------

--
-- Table structure for table `donasi`
--

CREATE TABLE `donasi` (
  `id` int NOT NULL,
  `nama_donatur` varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `anonim` tinyint(1) DEFAULT '0',
  `kota` varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `no_hp` varchar(20) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `email` varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `jumlah` int DEFAULT NULL,
  `doa` text COLLATE utf8mb4_general_ci,
  `status` enum('Pending','Paid','Failed') COLLATE utf8mb4_general_ci DEFAULT 'Pending',
  `metode_pembayaran` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `order_id` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `admin_id` int DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `donasi`
--

INSERT INTO `donasi` (`id`, `nama_donatur`, `anonim`, `kota`, `no_hp`, `email`, `jumlah`, `doa`, `status`, `metode_pembayaran`, `order_id`, `created_at`, `admin_id`) VALUES
(1, NULL, 1, 'Bantul', '081326932577', 'mustikatama@yahoo.com', 10000, 'ASD', 'Pending', NULL, 'DONASI-1-1769506865005', '2026-01-27 16:41:02', NULL),
(2, NULL, 1, 'Bantul', '', 'andarisbintang16@gmail.com', 100000, 'Berkah dan berguna bagi panti', 'Pending', NULL, 'DONASI-2-1770859758103', '2026-02-12 08:29:14', NULL),
(11, 'Galih', 0, 'Yogyakarta', '081234567890', 'galih1@email.com', 150000, 'Semoga berkah', 'Paid', 'Transfer Bank', 'ORD001', '2026-05-18 14:43:53', 1),
(12, 'Anonim', 1, 'Sleman', '081298765432', 'anonim1@email.com', 50000, 'Semoga sehat selalu', 'Pending', 'QRIS', 'ORD002', '2026-05-18 14:43:53', 1),
(13, 'Budi Santoso', 0, 'Bantul', '082112223333', 'budi@email.com', 200000, 'Untuk anak-anak panti', 'Failed', 'E-Wallet', 'ORD003', '2026-05-18 14:43:53', 1),
(14, 'Siti Aisyah', 0, 'Kulon Progo', '081377788899', 'siti@email.com', 75000, 'Semoga bermanfaat', 'Paid', 'Transfer Bank', 'ORD004', '2026-05-18 14:43:53', 1),
(15, 'Rahmat Hidayat', 0, 'Gunungkidul', '085266677788', 'rahmat@email.com', 125000, 'Semoga sukses selalu', 'Pending', 'QRIS', 'ORD005', '2026-05-18 14:43:53', 1),
(16, 'Anonim', 1, 'Yogyakarta', '081355566677', 'anonim2@email.com', 300000, 'Tetap semangat', 'Failed', 'E-Wallet', 'ORD006', '2026-05-18 14:43:53', 1),
(17, 'Dewi Lestari', 0, 'Magelang', '082233344455', 'dewi@email.com', 100000, 'Semoga menjadi amal jariyah', 'Paid', 'Transfer Bank', 'ORD007', '2026-05-18 14:43:53', 1),
(18, 'Andi Saputra', 0, 'Solo', '081299900011', 'andi@email.com', 60000, 'Semoga lancar rezekinya', 'Pending', 'QRIS', 'ORD008', '2026-05-18 14:43:53', 1);

-- --------------------------------------------------------

--
-- Table structure for table `mantan_penghuni`
--

CREATE TABLE `mantan_penghuni` (
  `id` int NOT NULL,
  `nama_anak` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  `penghuni_id` int NOT NULL,
  `alasan_keluar` enum('meninggal','diadopsi','kembali_keluarga','pindah_panti','lainnya') COLLATE utf8mb4_general_ci NOT NULL,
  `keterangan` text COLLATE utf8mb4_general_ci,
  `tanggal_keluar` date NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `nama_wali_adopsi` varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `nik_wali_adopsi` varchar(20) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `hubungan_dengan_anak` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  `alamat_wali` text COLLATE utf8mb4_general_ci,
  `no_hp_wali` varchar(20) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `pekerjaan` varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `status_pernikahan` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `tanggal_adopsi` date DEFAULT NULL,
  `no_sk_adopsi` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `instansi_pengesah` varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `mantan_penghuni`
--

INSERT INTO `mantan_penghuni` (`id`, `nama_anak`, `penghuni_id`, `alasan_keluar`, `keterangan`, `tanggal_keluar`, `created_at`, `nama_wali_adopsi`, `nik_wali_adopsi`, `hubungan_dengan_anak`, `alamat_wali`, `no_hp_wali`, `pekerjaan`, `status_pernikahan`, `tanggal_adopsi`, `no_sk_adopsi`, `instansi_pengesah`) VALUES
(1, 'BAGAS LUKMAN NUR HAKIM', 2, 'kembali_keluarga', '', '2026-01-27', '2026-01-27 10:21:20', '', '', 'Tidak ada', '', '08124127477', '', '', NULL, '', ''),
(2, 'BUDIANTO', 1, 'meninggal', '', '2026-02-11', '2026-02-11 16:32:34', '', '', 'Tidak ada', '', '081326932577', '', '', NULL, '', ''),
(3, 'BINTANG', 6, 'diadopsi', 'TIDAK ADA', '2026-05-16', '2026-05-16 13:24:55', 'ENDAH SULISTYOWATI', '3421002691039', 'lainnya', 'NGEMPLAK', '082318713487', 'TIDAK/TIDAK BEKERJA', 'menikah', '2026-05-16', '234', 'PUBLIKASI');

-- --------------------------------------------------------

--
-- Table structure for table `pendaftaran`
--

CREATE TABLE `pendaftaran` (
  `id` int NOT NULL,
  `nik` varchar(20) COLLATE utf8mb4_general_ci NOT NULL,
  `nama_anak` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  `jenis_kelamin` enum('L','P') COLLATE utf8mb4_general_ci NOT NULL,
  `tanggal_lahir` date NOT NULL,
  `usia` int DEFAULT NULL,
  `asal` varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `pendidikan` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `alamat` text COLLATE utf8mb4_general_ci,
  `berkebutuhan_khusus` enum('ya','tidak') COLLATE utf8mb4_general_ci DEFAULT 'tidak',
  `treatment_khusus` text COLLATE utf8mb4_general_ci,
  `nama_wali` varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `no_hp` varchar(20) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `foto` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `alasan` text COLLATE utf8mb4_general_ci NOT NULL,
  `status` enum('menunggu','disetujui','ditolak') COLLATE utf8mb4_general_ci DEFAULT 'menunggu',
  `catatan_admin` text COLLATE utf8mb4_general_ci,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `penghuni_id` int DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `pendaftaran`
--

INSERT INTO `pendaftaran` (`id`, `nik`, `nama_anak`, `jenis_kelamin`, `tanggal_lahir`, `usia`, `asal`, `pendidikan`, `alamat`, `berkebutuhan_khusus`, `treatment_khusus`, `nama_wali`, `no_hp`, `foto`, `alasan`, `status`, `catatan_admin`, `created_at`, `penghuni_id`) VALUES
(1, '3602041211870003', 'BAGAS LUKMAN NUR HAKIM', 'L', '2002-05-12', 23, 'PRAMBANAN', 'TK', 'MAGETAN SELATAN', 'tidak', '', 'SHOLEH', '08124127477', NULL, 'RA SANTUN', 'disetujui', NULL, '2026-01-27 09:38:58', NULL),
(2, '3471035801640001', 'BUDIANTO', 'L', '1998-03-12', 21, 'SURABAYA', 'SMP', 'MAGEAN SELATAN', 'tidak', '', 'SHOLEH', '081326932577', NULL, 'YAPPING', 'disetujui', NULL, '2026-01-27 09:40:49', NULL),
(3, '123422002700002', 'ALEXANDER', 'L', '2015-04-07', 11, 'SURABAYA', 'TK', 'Bantul, Yogyakarta', 'tidak', '', 'Juminten', '08134681029', NULL, 'Kurangnya pantauan orang tua', 'menunggu', NULL, '2026-05-18 05:49:41', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `penghuni`
--

CREATE TABLE `penghuni` (
  `id` int NOT NULL,
  `nik` varchar(20) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `nama_anak` varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `jenis_kelamin` enum('L','P') COLLATE utf8mb4_general_ci DEFAULT NULL,
  `tanggal_lahir` date DEFAULT NULL,
  `usia` int DEFAULT NULL,
  `asal` varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `pendidikan` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `alamat` text COLLATE utf8mb4_general_ci,
  `berkebutuhan_khusus` enum('ya','tidak') COLLATE utf8mb4_general_ci DEFAULT NULL,
  `treatment_khusus` text COLLATE utf8mb4_general_ci,
  `nama_wali` varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `no_hp` varchar(20) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `alasan` text COLLATE utf8mb4_general_ci,
  `foto` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `tanggal_masuk` date DEFAULT NULL,
  `status` enum('aktif','nonaktif') COLLATE utf8mb4_general_ci DEFAULT 'aktif',
  `admin_id` int DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `penghuni`
--

INSERT INTO `penghuni` (`id`, `nik`, `nama_anak`, `jenis_kelamin`, `tanggal_lahir`, `usia`, `asal`, `pendidikan`, `alamat`, `berkebutuhan_khusus`, `treatment_khusus`, `nama_wali`, `no_hp`, `alasan`, `foto`, `tanggal_masuk`, `status`, `admin_id`) VALUES
(1, '3471035801640001', 'BUDIANTO', 'L', '1998-03-12', 21, 'SURABAYA', 'SMP', 'MAGEAN SELATAN', 'tidak', '', 'SHOLEH', '081326932577', 'HYPERAKTIF', NULL, '2026-01-27', 'aktif', NULL),
(2, '3602041211870003', 'BAGAS LUKMAN NUR HAKIM', 'L', '2002-05-12', 23, 'PRAMBANAN', 'TK', 'MAGETAN SELATAN', 'tidak', '', 'SHOLEH', '08124127477', 'RA SANTUN', NULL, '2026-01-27', 'aktif', NULL),
(3, '3602041211870003', 'MARTONO', 'L', '2010-04-12', 15, 'BANTUL', '-', 'PANTI', 'tidak', '', 'TIDAK ADA WALI', '0', 'PANTI', NULL, '2026-02-11', 'aktif', NULL),
(4, '3306132202150002', 'AFKA RESTU ZULFADHLI', 'L', '2015-02-22', 10, 'BANTUL', '-', 'PANTI', 'ya', 'Disabilitas Intelektual : lambat belajar', 'DIURUS PANTI', '0', 'TIDAK ADA', NULL, '2026-02-11', 'aktif', NULL),
(5, '3310185810080002', 'SANTI WAHYU ANGGRAINI', 'P', '2008-10-18', 13, 'BANTUL', '-', '0', 'tidak', '', 'PANTI', '0', 'ANAK TERLANTAR', NULL, '2026-02-11', 'aktif', NULL),
(6, '123354365677566', 'BINTANG', 'L', '2010-03-12', 12, 'Yogyakarta', 'SMP', 'DODOGAN', 'tidak', '', 'RISWANTA', '082318713487', 'TIDAK ADA', 'WIN_20241029_13_14_57_Pro.jpg', '2026-05-16', 'aktif', NULL);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `admin`
--
ALTER TABLE `admin`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`),
  ADD UNIQUE KEY `email` (`email`);

--
-- Indexes for table `adopsi`
--
ALTER TABLE `adopsi`
  ADD PRIMARY KEY (`id`),
  ADD KEY `penghuni_id` (`penghuni_id`);

--
-- Indexes for table `donasi`
--
ALTER TABLE `donasi`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_donasi_admin` (`admin_id`);

--
-- Indexes for table `mantan_penghuni`
--
ALTER TABLE `mantan_penghuni`
  ADD PRIMARY KEY (`id`),
  ADD KEY `penghuni_id` (`penghuni_id`);

--
-- Indexes for table `pendaftaran`
--
ALTER TABLE `pendaftaran`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_pendaftaran_penghuni` (`penghuni_id`);

--
-- Indexes for table `penghuni`
--
ALTER TABLE `penghuni`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_penghuni_admin` (`admin_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `admin`
--
ALTER TABLE `admin`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `adopsi`
--
ALTER TABLE `adopsi`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `donasi`
--
ALTER TABLE `donasi`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=19;

--
-- AUTO_INCREMENT for table `mantan_penghuni`
--
ALTER TABLE `mantan_penghuni`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `pendaftaran`
--
ALTER TABLE `pendaftaran`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `penghuni`
--
ALTER TABLE `penghuni`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `adopsi`
--
ALTER TABLE `adopsi`
  ADD CONSTRAINT `adopsi_ibfk_1` FOREIGN KEY (`penghuni_id`) REFERENCES `penghuni` (`id`),
  ADD CONSTRAINT `fk_adopsi_penghuni` FOREIGN KEY (`penghuni_id`) REFERENCES `penghuni` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `donasi`
--
ALTER TABLE `donasi`
  ADD CONSTRAINT `fk_donasi_admin` FOREIGN KEY (`admin_id`) REFERENCES `admin` (`id`) ON DELETE SET NULL ON UPDATE CASCADE;

--
-- Constraints for table `mantan_penghuni`
--
ALTER TABLE `mantan_penghuni`
  ADD CONSTRAINT `fk_mantan_penghuni_penghuni` FOREIGN KEY (`penghuni_id`) REFERENCES `penghuni` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `mantan_penghuni_ibfk_1` FOREIGN KEY (`penghuni_id`) REFERENCES `penghuni` (`id`);

--
-- Constraints for table `pendaftaran`
--
ALTER TABLE `pendaftaran`
  ADD CONSTRAINT `fk_pendaftaran_penghuni` FOREIGN KEY (`penghuni_id`) REFERENCES `penghuni` (`id`) ON DELETE SET NULL ON UPDATE CASCADE;

--
-- Constraints for table `penghuni`
--
ALTER TABLE `penghuni`
  ADD CONSTRAINT `fk_penghuni_admin` FOREIGN KEY (`admin_id`) REFERENCES `admin` (`id`) ON DELETE SET NULL ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
