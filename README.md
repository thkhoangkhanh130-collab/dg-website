# Website Dương Gia — xnkduonggia.vn

Website công ty TNHH TMDV XNK Dương Gia — nhà phân phối lốp WYNSTAR tại Việt Nam.

- Trang tĩnh, đăng bằng GitHub Pages (nhánh `main`, thư mục gốc), tên miền trong tệp `CNAME`.
- Giá niêm yết và tình trạng kho được đọc trực tiếp từ hệ thống DG Đặt Hàng khi tải trang (cổng công khai, không có giá đại lý). Nội dung trong HTML là bản chụp lúc dựng, dùng khi không kết nối được hệ thống.
- Biểu mẫu "Yêu cầu báo giá" và "Đăng ký đại lý" gửi vào danh bạ khách của DG Đặt Hàng (gắn tag "tiềm năng") và gửi email cho Dương Gia.
- Mã nguồn bộ dựng: `_nguon/` (Jekyll bỏ qua thư mục bắt đầu bằng dấu gạch dưới nên không đăng ra web). Dựng lại: `python3 _nguon/build.py site`.
