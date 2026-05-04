-- =============================================
-- CHẠY FILE NÀY TRONG phpMyAdmin TRƯỚC
-- =============================================

CREATE DATABASE IF NOT EXISTS qlnhansu
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE qlnhansu;

CREATE TABLE IF NOT EXISTS nhan_su (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    so_cccd     VARCHAR(12)  NOT NULL UNIQUE,
    ho_ten      VARCHAR(100) NOT NULL,
    ngay_sinh   DATE         NOT NULL,
    gioi_tinh   ENUM('Nam','Nữ','Khác') NOT NULL DEFAULT 'Nam',
    dia_chi     TEXT         NOT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Dữ liệu mẫu
INSERT INTO nhan_su (so_cccd, ho_ten, ngay_sinh, gioi_tinh, dia_chi) VALUES
('001085012345', 'Nguyễn Văn An',  '1990-03-15', 'Nam', '12 Lý Thường Kiệt, Hoàn Kiếm, Hà Nội'),
('034087056789', 'Trần Thị Bích',  '1995-07-22', 'Nữ',  '45 Nguyễn Huệ, Quận 1, TP. Hồ Chí Minh'),
('046092078901', 'Lê Minh Cường',  '1988-11-08', 'Nam', '78 Trần Phú, Hải Châu, Đà Nẵng'),
('079099034567', 'Phạm Thị Dung',  '2000-01-30', 'Nữ',  '23 Lê Lợi, Ngô Quyền, Hải Phòng'),
('082001090123', 'Hoàng Văn Em',   '1985-09-12', 'Nam', '55 Hùng Vương, Ninh Kiều, Cần Thơ');
