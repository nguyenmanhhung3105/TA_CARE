> Yêu cầu mới tiếp theo: đăng nhập/đăng xuất đồng bộ theo vai trò đã được triển khai local. Phần phiên riêng trong tài liệu này là trạng thái trước SSO; xem [triển khai SSO](implementation_sso_2026-10-20.md).

# Khôi phục TA.CARE, thư viện hồ sơ và đăng nhập — 20/10/2026

Đây là kết quả trên **local Odoo 19 / `tacare_local`**. Không push, không deploy, không dùng database production. Quyết định trong tài liệu này thay thế phần giao diện TA.CARE và quyền đăng nhập cả ba website của đợt làm trước.

## Giao diện và nội dung

- Khôi phục `home_hub.xml` từ bản chụp nguồn `backups/profile_refresh_20261020/source_before.tar.gz`: sân khấu xanh, các thẻ nổi, hành trình ba điểm chạm, phần đối chiếu và câu chuyện. Giữ ảnh chụp thật đã có nguồn. Không đưa carousel ảnh vào TA.CARE.
- Tủ Hồ Sơ đặt carousel trong phần đầu tiên của nội dung, trước thư viện khi đăng nhập; ảnh đứng trước phần giới thiệu cả trên mobile. Kho và Tủ vẫn có hai bộ ảnh và cấu trúc carousel khác nhau.
- Tủ bổ sung nội dung cụ thể về hai mục đích hồ sơ, thông tin năng lực, điều kiện nhận việc, minh chứng tùy chọn và cách quản lý nhiều hồ sơ. Có nút **Đến TA.CARE** ngay trên thanh điều hướng và liên kết trong nội dung.
- Có thanh chuyển hệ thống trên cả ba website, đánh dấu hệ thống đang mở. Liên kết điều hướng/tab tiếp tục hiển thị trạng thái được chọn.

## Quyền truy cập được xác nhận lại

| Vai trò | Hệ thống sử dụng |
| --- | --- |
| Doanh nghiệp | Kho Việc Làm + TA.CARE |
| Ứng viên / người nhận việc | Tủ Hồ Sơ + TA.CARE |
| Quản trị hệ thống (`base.group_system`) | Cả ba |
| Khách | Xem trang chủ; chức năng yêu cầu đăng nhập |

Trang chủ của hệ thống ngoài quyền vẫn mở để tham khảo. Truy cập chức năng bằng URL trực tiếp vẫn bị kiểm tra trên máy chủ; POST không đúng quyền trả 403. Chốt chức năng cũng áp dụng trên host local dự phòng, tránh dùng host không nhận diện để đọc danh sách khi chưa đăng nhập. Không thể đổi sang namespace `/kvl/*` trên host Tủ để vượt quyền ứng viên, hoặc `/tuhoso/*` trên host Kho để vượt quyền doanh nghiệp. Vẫn giữ các kiểm tra quyền sở hữu, tổ chức và đồng ý chia sẻ trong controller/model hiện có.

Luồng tuyển dụng từ đối chiếu TA.CARE dùng `/tacare/job/<id>?profile_id=...` để ứng viên xem tin đã xuất bản và form ứng tuyển ngay trong TA.CARE. Endpoint dùng lại controller hiện có, chỉ nhận tin tuyển dụng; giữ đúng hồ sơ đã chọn, từ chối hồ sơ người khác. Không cần mở quyền Kho cho ứng viên. Không thay thuật toán matching hay mở matching việc linh hoạt.

Tài khoản được dùng chung trong DB, **phiên đăng nhập vẫn riêng theo tên miền**. Thanh chuyển hệ thống không phải SSO và không tự đăng nhập sang tên miền khác. Tài khoản chưa được cấp vai trò không tự có quyền ứng viên/doanh nghiệp.

## Admin và hồ sơ

Database hiện có 20 hồ sơ và 12 công việc nhận làm gắn với hồ sơ. Không tạo lại hay xóa hồ sơ cũ. Hai tài khoản ứng viên đã yêu cầu trước đó vẫn có hai hồ sơ mỗi tài khoản.

Trước đây thư viện dùng riêng công ty Odoo đang chọn; dữ liệu 20 hồ sơ nằm trong công ty 1, còn admin hiện có được cấp nhiều công ty. Tab **Tất cả hồ sơ** và trang chi tiết của admin hiện lấy theo `user.company_ids`, tránh danh sách trống khi chuyển công ty đang chọn. Đây là nguyên nhân kỹ thuật có thể gây tình trạng trống; không khẳng định mọi trường hợp người dùng gặp đều do nguyên nhân này. Tủ khi chuyển tên miền nhưng chưa đăng nhập cũng chỉ hiện trang giới thiệu.

Admin đăng nhập Tủ sẽ mặc định thấy tất cả hồ sơ. Có tab riêng **Hồ sơ của tôi**. Ứng viên luôn bị giới hạn theo tài khoản sở hữu; yêu cầu `scope=all` trả 403, URL hồ sơ người khác trả 404.

## Popup đăng nhập

- Mỗi website có logo, màu và nội dung riêng; desktop có ảnh thật, mobile tập trung vào form.
- Form POST trực tiếp `/web/login`, có CSRF và `data-captcha="login"`. Controller gọi xác thực gốc của Odoo; không tạo cơ chế kiểm tra mật khẩu riêng, không bỏ CAPTCHA hoặc MFA.
- Đăng nhập sai mở lại popup, giữ tên đăng nhập và xóa mật khẩu; thông báo lỗi không tiết lộ tài khoản tồn tại hay không. Đăng nhập thành công về chức năng đã chọn, hoặc trang chủ.
- Giữ đường dẫn quay về và trạng thái chọn với tiền tố ngôn ngữ Odoo đang bật (ví dụ `/en/`, `/vi/`). Giới hạn đường dẫn quay về trong các namespace sản phẩm; từ chối URL ngoài, đường dẫn backend và giá trị không an toàn.
- Có nhãn input, tự đưa focus vào tên đăng nhập, giới hạn focus bằng native dialog, Escape, nút đóng, trả focus về nút mở và nút hiện/ẩn mật khẩu.
- Giữ endpoint xác thực bổ sung, tài nguyên và bản dịch nền để trang chủ vẫn hoạt động với phiên đăng nhập không đúng website.

## Kiểm tra đã chạy

| Kiểm tra | Kết quả |
| --- | --- |
| Python AST, XML và `node --check` | Đạt |
| Update `tacare_account_access,tacare_website`, restart local | Đạt |
| `homepages_browser_check.cjs` | Ba trang tại 1440/768/375/320px; marker, font, ảnh, anchor, không tràn ngang, carousel và giảm chuyển động đạt |
| `authentication_browser_check.cjs` | Popup ba trang; focus/Escape; POST form gốc sai/đúng; giữ tên, xóa mật khẩu; quyền 2/3 và 3/3; hồ sơ ứng viên/admin; xem tin/form ứng tuyển trong TA.CARE giữ đúng hồ sơ; phiên trên host sai bị chặn cả khi POST có CSRF hợp lệ đạt |
| `dev_auth_restore_check.py` | Chính admin hiện có (ID 2): đủ hồ sơ khi lần lượt chọn từng công ty được cấp; tab của tôi đúng chủ; đường dẫn quay về an toàn và quyền host đạt, rollback |
| `dev_profile_library_check.py` | Nhiều hồ sơ, quyền chủ sở hữu, kỹ năng/consent độc lập và giữ nguyên tài khoản đạt, rollback |
| `dev_schema_check.py` | Cách ly tổ chức/hồ sơ, chặn portal ghi trực tiếp, consent và thu hồi đạt, rollback |
| `dev_flexible_check.py` | 20 bài (5 tuyển dụng + 15 linh hoạt), 15 hồ sơ demo ban đầu, 10 capability ban đầu còn nguyên; tổng hiện tại 20 hồ sơ / 12 capability; validation và ACL đạt, rollback |
| `homepage_contract_smoke.py` | Ba trang chủ và đăng nhập HTTP 200, đủ `tc-hub`, `tc-jobs`, `tc-profiles` |

Không thử CAPTCHA bằng khóa dịch vụ thật, quy trình TOTP với tài khoản bật TOTP, hoặc SSO giữa các domain. Mã vẫn đi qua form/controller gốc Odoo cho các bước đó; không coi là đã kiểm thử dịch vụ bên ngoài.

Ảnh kiểm tra: `docs/screenshots/auth-restore-20261020/`. Ảnh thư viện admin đã che hồ sơ có sẵn ngoài dữ liệu giả; không chụp mật khẩu. Các tài khoản và mật khẩu hiện có được giữ nguyên, không đưa bí mật vào fixture hay tài liệu.

Backup trước sửa: `backups/login_restore_20261020/` gồm dump DB, nguồn addon, hướng dẫn và diff; thư mục bị Git ignore. Không cần sửa Odoo core hay đổi tên model. Phiên bản website: `19.0.6.1.0`.

## Xem demo

- TA.CARE: http://tacare.localhost:8069/
- Tủ Hồ Sơ: http://tuhoso.localhost:8069/
- Tab admin: http://tuhoso.localhost:8069/tuhoso/profiles?scope=all
- Kho Việc Làm: http://khovieclam.localhost:8069/

Nếu chưa có phiên trên website đích, chọn Đăng nhập ngay trên website đó. Phiên ở website trước không tự được chia sẻ.
