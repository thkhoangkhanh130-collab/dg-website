# -*- coding: utf-8 -*-
"""Dữ liệu dựng website Dương Gia.
SKU: bản chụp cổng `catalog` của hệ thống DG Đặt Hàng lúc 00:35 ngày 02/11/2026 (khách chưa đăng nhập — chỉ giá niêm yết).
Thông số kỹ thuật chi tiết: catalog nhà máy "Wynstar catalog-Trailer-2026 V4 - Duong Gia (v2)" (catalog_specs.json).
Khi chạy trên website, giá và tình trạng hàng được đọc lại trực tiếp từ hệ thống."""

SNAPSHOT_AT = '02/11/2026'

# ma_sp, quy_cach, gai, pr, tai_trong, toc_do, mam, tinh_trang, gia_niem_yet
SKUS = [
    ('WYNSTAR 10.00R20-18 D387', '10.00R20', 'D387', '18PR', '149/146', 'J', '2026-05-07', 'Tạm hết hàng', 7370000),
    ('WYNSTAR 11.00R20-18* D563', '11.00R20', 'D563', '18PR', '152/149', 'J', '8', 'Sắp hết', 8080000),
    ('WYNSTAR 11.00R20-18 D526', '11.00R20', 'D526', '18PR', '152/149', 'D', '', 'Còn hàng', 7950000),
    ('WYNSTAR 11R22.5-18 D303', '11R22.5', 'D303', '18PR', '149/146', 'L', '8.25', 'Sắp hết', 6080000),
    ('WYNSTAR 11R22.5-18 D506', '11R22.5', 'D506', '18PR', '149/146', 'G', '8.25', 'Tạm hết hàng', 6330000),
    ('WYNSTAR 11R22.5-16 D585', '11R22.5', 'D585', '16PR', '146/143 (148/145)', 'L', '8.25', 'Tạm hết hàng', 6110000),
    ('WYNSTAR 12.00R20-22* D929', '12.00R20', 'D929', '22*PR', '158/155', 'D', '2026-05-08', 'Tạm hết hàng', 10410000),
    ('WYNSTAR 12.00R20-22* D939', '12.00R20', 'D939', '22*PR', '158/155', 'D', '2026-05-08', 'Tạm hết hàng', 10640000),
    ('WYNSTAR 12.00R20-20* D567', '12.00R20', 'D567', '22PR', '156/153', 'J', '2026-05-08', 'Còn hàng', 9650000),
    ('WYNSTAR 12.00R20-20* D526', '12.00R20', 'D526', '20*PR', '156/153', 'J', '2026-05-08', 'Tạm hết hàng', 9610000),
    ('WYNSTAR 12.00R20-22 D506', '12.00R20', 'D506', '22PR', '158/155', 'F', '2026-05-08', 'Tạm hết hàng', 9920000),
    ('WYNSTAR 12.00R20-20 D563', '12.00R20', 'D563', '20PR', '156/153', 'J', '2026-05-08', 'Tạm hết hàng', 9120000),
    ('WYNSTAR 12R22.5-18 D303Pro', '12R22.5', 'D303Pro', '18PR', '152/149', 'L', '9', 'Còn hàng', 7320000),
    ('WYNSTAR 12R22.5-18 D589 Q', '12R22.5', 'D589', '18PR', '152/149', 'F', '9', 'Sắp hết', 7410000),
    ('WYNSTAR 12R22.5-18 D387', '12R22.5', 'D387', '18PR', '152/149', 'L', '9', 'Tạm hết hàng', 7680000),
    ('WYNSTAR 12R22.5-18 RS02', '12R22.5', 'RS02', '18PR', '152/149', 'L', '9', 'Tạm hết hàng', 6910000),
    ('WYNSTAR 12R22.5-18 D307', '12R22.5', 'D307', '18PR', '152/149', 'J', '9', 'Tạm hết hàng', 7080000),
    ('WYNSTAR 12R22.5-18 D320', '12R22.5', 'D320', '18PR', '152/149', 'J', '9', 'Tạm hết hàng', 6350000),
    ('WYNSTAR 12R22.5-18 D506', '12R22.5', 'D506', '18PR', '152/149', 'F', '9', 'Còn hàng', 7600000),
    ('WYNSTAR 12R22.5-18 D520', '12R22.5', 'D520', '18PR', '152/149', 'L', '9', 'Tạm hết hàng', 7960000),
    ('WYNSTAR 12R22.5-18 D555', '12R22.5', 'D555', '20PR', '152/149', 'J', '9', 'Sắp hết', 7870000),
    ('WYNSTAR 12R22.5-18 D979+', '12R22.5', 'D979+', '18PR', '152/149', 'D', '9', 'Tạm hết hàng', 8280000),
    ('WYNSTAR 385/65R22.5-24 D517', '385/65R22.5', 'D517', '24PR', '164', 'K', '11.75', 'Tạm hết hàng', 8490000),
    ('WYNSTAR 6.50R16LT-12 D806', '6.50R16LT', 'D806', '12PR', '110/105', 'L', '5.50F', 'Tạm hết hàng', 2410000),
    ('WYNSTAR 7.00R16LT-14 D806', '7.00R16LT', 'D806', '14PR', '118/114', 'L', '5.50F', 'Tạm hết hàng', 2910000),
    ('WYNSTAR 7.50R16LT-14 D300', '7.50R16LT', 'D300', '14PR', '122/118', 'J', '6.00G', 'Tạm hết hàng', 3440000),
    ('WYNSTAR 7.50R16LT-16 D806', '7.50R16LT', 'D806', '16PR', '125/121', 'L', '6.00G', 'Tạm hết hàng', 3470000),
    ('WYNSTAR 7.50R16LT-16 D205', '7.50R16LT', 'D205', '16PR', '', '', '', 'Tạm hết hàng', 3910000),
    ('WYNSTAR 8.25R16LT-18 D205', '8.25R16LT', 'D205', '18PR', '132/128', 'L', '6.50H', 'Tạm hết hàng', 4560000),
    ('WYNSTAR 8.25R16LT-18 D387', '8.25R16LT', 'D387', '18PR', '132/128', 'J', '6.50H', 'Tạm hết hàng', 4640000),
    ('WYNSTAR 8.25R20-16 D320', '8.25R20', 'D320', '16PR', '139/137', 'K', '2026-05-06', 'Tạm hết hàng', 4870000),
    ('WYNSTAR 9.00R20-16* D526', '9.00R20', 'D526', '16*PR', '144/142', 'J', '7', 'Tạm hết hàng', 6480000),
]

# Mẫu gai có ảnh (thư mục anh_san_pham của app)
IMAGES = {'D303', 'D303PRO', 'D307', 'D320', 'D387', 'D506', 'D520', 'D526', 'D555', 'D563', 'D567', 'D585', 'D589', 'RS02'}

# Tuyến đường theo "road conditions" trong catalog nhà máy
ROUTE = {'RS02': 'cao-toc', 'D303': 'cao-toc', 'D303PRO': 'cao-toc', 'D307': 'cao-toc', 'D320': 'cao-toc', 'D387': 'cao-toc',
         'D520': 'cao-toc', 'D555': 'cao-toc', 'D567': 'cao-toc', 'D585': 'cao-toc',
         'D506': 'hon-hop', 'D526': 'hon-hop', 'D563': 'hon-hop', 'D589': 'cong-trinh'}
ROUTE_LABEL = {'cao-toc': 'Cao tốc · Quốc lộ', 'hon-hop': 'Hỗn hợp · Đường xấu', 'cong-trinh': 'Mỏ · Công trình'}
ROAD_VI = {'expressway': 'đường cao tốc', 'first-class highway': 'quốc lộ', 'first-class roads': 'quốc lộ', 'paved road': 'đường nhựa',
           'mixed roads': 'đường hỗn hợp', 'mining road': 'đường mỏ', 'construction sites': 'công trường'}

CTY = {
    'ten': 'CÔNG TY TNHH THƯƠNG MẠI DỊCH VỤ XNK DƯƠNG GIA',
    'ten_en': 'DUONG GIA XNK TRADING SERVICES COMPANY LIMITED',
    'ngan': 'Dương Gia',
    'mst': '6001782664',
    'dia_chi': 'KM 10 Quốc lộ 27, Thôn 8, Xã Ea Ktur, Tỉnh Đắk Lắk',
    'hotline': '0973 929 321', 'tel': '0973929321', 'tel_intl': '+84973929321',
    'email': 'xuatnhapkhau.duonggia@gmail.com',
    'dai_dien': 'Trần Hoàng Khanh', 'chuc_vu': 'Giám đốc',
    'zalo': 'https://zalo.me/0973929321',
    'app': 'https://dathang.xnkduonggia.vn',
    'domain': 'https://xnkduonggia.vn',
    'slogan': 'Bạn đồng hành trên mọi nẻo đường',
}

# Quyền lợi hạng — bản chụp từ app (thongTin.hang_ds); website đọc lại trực tiếp khi tải trang
TIERS = [
    ('Bạc', 'Khi mở tài khoản đại lý', 'Xem giá đại lý và đặt hàng trên ứng dụng'),
    ('Vàng', 'Xét theo doanh số đã thanh toán mỗi quý', 'Ưu tiên phân bổ hàng khi khan hiếm · hỗ trợ bảng hiệu, ấn phẩm'),
    ('Kim Cương', 'Đối tác chiến lược do Giám đốc mời', 'Ưu tiên cao nhất · hỗ trợ bảng hiệu lớn · quà cuối năm'),
]

PROMO = {'title': 'Mua 10 tặng 1', 'text': 'Ưu đãi khách hàng mua lần đầu tại Dương Gia — tặng 1 lốp cùng mã khi mua 10 lốp. Áp dụng 01/10 – 30/11/2026.', 'until': '2026-11-30'}
