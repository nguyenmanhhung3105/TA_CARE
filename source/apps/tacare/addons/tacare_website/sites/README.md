# Ba website trong addon TA.CARE

- `khovieclam/`: khám phá và đăng nhu cầu thời vụ cho cá nhân/doanh nghiệp, quản lý tin; QWeb của Kho. Route tuyển dụng cũ được chặn, giữ XML/model ID để tương thích.
- `tuhoso/`: hồ sơ nhận việc thời vụ, kỹ năng, minh chứng, lịch/khu vực/đơn giá của việc nhận làm; QWeb của Tủ.
- `tacare/`: đối chiếu, kết nối, thông báo, ba ví dụ giao diện; QWeb của TA.CARE.

`controllers/live.py` là điểm ghép tương thích của các lớp controller từng sản phẩm. `controllers/profiles.py` giữ lớp cuối trong chuỗi kế thừa Odoo để các route override không bị mất; `controllers/flexible_work.py` dùng chung parser, upload và kiểm tra quyền cho form việc linh hoạt. Router trang chủ ở `controllers/main.py`.

Các bảng Odoo và phần bảo mật dùng chung nằm tại `models/`, `security/` và addon `tacare_account_access`. Giữ nguyên model, XML ID và tên addon để các bản ghi đang có không bị tạo lại khi nâng cấp. Đây là ba package chức năng trong một addon, không phải ba ứng dụng Odoo độc lập.

Odoo yêu cầu tài nguyên web đi qua `static/`: asset riêng của Kho nằm ở `static/src/khovieclam/`, của Tủ ở `static/src/tuhoso/`. Token, font, ảnh có nguồn, xác thực, carousel và form linh hoạt dùng chung nằm ở `static/src/` và `views/shared/`. Không tạo ba bản sao của quyền/consent/schema hoặc stylesheet chung.

Khi thêm route vào một package, giữ chuỗi kế thừa controller và khai báo `@http.route()` cho override. Khi thêm template, khai báo đường dẫn trong `__manifest__.py` theo thứ tự dependency. Đọc `docs/project_scope.md` và triển khai seasonal-only ngày 22/10/2026. Không chạy lại seed/refresh tuyển dụng cũ. `views/shared/seasonal_marketplace.xml` giữ thành phần chung; mỗi `sites/<sản phẩm>/views/seasonal_marketplace.xml` giữ trang riêng; `models/seasonal_scope.py` chặn route và ghi dữ liệu tuyển dụng.

Giao diện hiện tại: `service_design.xml` riêng của Kho/Tủ là lớp cuối, thành phần dùng chung ở `views/shared/service_design.xml`, metadata công khai ở `controllers/service_design.py`, token/style ở `static/src/scss/service_design.scss`. Xem `docs/design-system/everyday-services.md` và nghiên cứu ngày 22/10/2026 trước khi sửa. Không ghép lại hai trang thành một hero dùng chung.
