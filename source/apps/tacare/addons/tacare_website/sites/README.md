# Ba website trong addon TA.CARE

- `khovieclam/`: tin tuyển dụng, việc linh hoạt, tổ chức, ứng viên, quản lý và duyệt tin; QWeb của Kho.
- `tuhoso/`: hồ sơ, kỹ năng, minh chứng, công việc nhận làm; QWeb của Tủ.
- `tacare/`: đối chiếu, kết nối, thông báo, ba ví dụ giao diện; QWeb của TA.CARE.

`controllers/live.py` là điểm ghép tương thích của các lớp controller từng sản phẩm. `controllers/profiles.py` giữ lớp cuối trong chuỗi kế thừa Odoo để các route override không bị mất; `controllers/flexible_work.py` dùng chung parser, upload và kiểm tra quyền cho form việc linh hoạt. Router trang chủ ở `controllers/main.py`.

Các bảng Odoo và phần bảo mật dùng chung nằm tại `models/`, `security/` và addon `tacare_account_access`. Giữ nguyên model, XML ID và tên addon để các bản ghi đang có không bị tạo lại khi nâng cấp. Đây là ba package chức năng trong một addon, không phải ba ứng dụng Odoo độc lập.

Odoo yêu cầu tài nguyên web đi qua `static/`: asset riêng của Kho nằm ở `static/src/khovieclam/`, của Tủ ở `static/src/tuhoso/`. Token, font, ảnh có nguồn, xác thực, carousel và form linh hoạt dùng chung nằm ở `static/src/` và `views/shared/`. Không tạo ba bản sao của quyền/consent/schema hoặc stylesheet chung.

Khi thêm route vào một package, giữ chuỗi kế thừa controller và khai báo `@http.route()` cho override. Khi thêm template, khai báo đường dẫn trong `__manifest__.py` theo thứ tự dependency. Đọc `docs/research/implementation_account_refresh_2026-10-21.md` trước khi chạy seed dữ liệu.
