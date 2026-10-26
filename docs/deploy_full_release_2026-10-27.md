# Đưa code và toàn bộ dữ liệu hiện tại lên server — 27/10/2026

Chủ dự án yêu cầu đưa tất cả code và dữ liệu hiện tại lên server. Áp dụng quyết định trước đây: thay database ứng dụng và filestore bằng snapshot local, sau backup server và staging. Không hỏi lại lựa chọn code-only/demo-only; không coi push/Actions xanh là đã chuyển đầy đủ dữ liệu.

## Phạm vi bản chuyển

- Code của hai addon hiện có, giữ model/XML IDs, gồm refactor package, tin mở công khai, hồ sơ theo tài khoản, kết nối/đánh giá, giao diện mới, bản đồ/geohash/chỉ đường và các form mới.
- Database `tacare_local` đầy đủ, gồm tài khoản/mật khẩu local đã được chủ dự án yêu cầu đổi, consent, lịch sử và dữ liệu gắn đúng chủ. Số hiện tại: 15 tin, 42 hồ sơ, 51 mục nhận làm. Không dùng JSON demo cũ vì không bao phủ toàn bộ dữ liệu này.
- Filestore đầy đủ và addon archive từ đúng source commit. Ảnh/asset trong addon đi cùng code; attachment trong database phải có tệp tương ứng, đúng kích thước/checksum.
- Không chuyển `.env`, cấu hình Docker local, PostgreSQL authentication, SSH/Git credentials, tệp danh sách mật khẩu dạng rõ, session directory hoặc các cấu hình vận hành localhost sang dịch vụ production. Tài khoản/mật khẩu trong dump là dữ liệu được phép thay thế; danh sách mật khẩu dạng rõ vẫn chỉ giữ trên máy riêng.

## Chuẩn bị local

`tools/deploy/prepare_full_snapshot.py` preview mặc định, không SSH/push. Sau khi review và commit addon:

```bash
python3 tools/security/check_repository.py
python3 tools/deploy/tests/test_full_snapshot.py
python3 tools/deploy/prepare_full_snapshot.py --prepare
```

Lệnh prepare tạm dừng Odoo local để dump DB/filestore cùng một thời điểm rồi mở lại trong `finally`. Giữ backup riêng tư; khôi phục sang DB local tạm, kiểm đếm và kiểm liên kết owner/company. Kiểm mọi attachment tham chiếu trong archive bằng size/SHA1, từ chối đường dẫn vượt thư mục, symlink/device và duplicate paths. Neutralize **bản clone** rồi thử nâng cấp hai addon; không neutralize hoặc thay đổi dữ liệu nguồn. DB/filestore tạm được dọn sau kiểm tra. Gói release luôn chứa dump gốc.

Kết quả xác thực nằm trong ignored `runtime/releases/current-full-local-restore.json`; file này chỉ được cập nhật khi mọi kiểm tra đã qua. Nó chỉ đích danh package, backup, source commit, SHA256, số đếm và trạng thái uploaded/deployed. Không chọn snapshot theo tên mới nhất. Format gói vẫn là `tacare.full-local-restore.v1`, gồm dump, filestore, addon archive và manifest; **không** đưa vào `--with-data` JSON gate.

## Điều kiện nối tiếp trên server

1. Kết nối SSH bằng cấu hình riêng đã xác minh, kiểm tra script/config/service/core/dependency/PostgreSQL và trạng thái deploy/recovery đang chạy. Các file trong `runtime/releases/server-inspection/` là bản lưu trước đây, không chứng minh trạng thái live hiện tại.
2. Giữ nguyên production trong lúc đọc/chuẩn bị. Lấy backup server hiện tại và kiểm tra khả năng rollback code/database/filestore trước cutover; không ghi đè backup bằng local.
3. Tải private package đúng SHA256 và kiểm lại. Thử restore/staging trong phạm vi tách biệt và neutralized, giữ gate chống gửi mail/webhook/cron; kiểm tra code/core compatibility, schema, ba homepage markers và dữ liệu/owner.
4. Chuẩn bị cấu hình production từ **server đang chạy**: domain ba website, DB selector, data_dir, mail/cron, proxy và thu hồi các phiên SSO được sao chép. Không phục vụ nguyên domain localhost hoặc dùng database staging đã neutralize làm database production. Không gửi email tự động từ dữ liệu QA/queue vừa chuyển.
5. Chỉ chuyển sau khi staging qua; phối hợp code + database + filestore trong maintenance gate với rollback đã kiểm tra. Kiểm HTTP/login/role/owner/current consent/map hiện tại và xác nhận 15/42/51 theo bản snapshot. Không push main trước khi sẵn sàng vì workflow tự triển khai code.

Không tự phát minh đường dẫn restore, cấu hình hoặc lệnh root từ bản lưu cũ. Phải đối chiếu server live trước khi sửa worker/cài cơ chế restore đầy đủ.

## Trạng thái truy cập lúc bắt đầu chuẩn bị

Trên máy hiện tại chưa có `~/.ssh/config`/alias `tacare-server`; thử kết nối báo không phân giải được alias. Truy cập SSH GitHub của origin cũng báo thiếu public-key authentication. Người vận hành cần cung cấp/cấu hình kết nối đang dùng trong tệp riêng, không gửi mật khẩu/private key vào repository/chat. Có thể chuyển private package trực tiếp qua SSH sau khi có kết nối và kiểm tra server; không cần đưa dump vào Git. Trạng thái triển khai thực tế phải lấy từ private release report và kết quả live, không từ tài liệu chuẩn bị này.
