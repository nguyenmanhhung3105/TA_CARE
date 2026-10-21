# Rà soát thông tin nhạy cảm trước commit

Theo yêu cầu chủ dự án, đã hủy hai commit local vừa tạo (`7fb3929`, `9743871`), đưa main về commit cha và giữ toàn bộ code/tài liệu ở working tree. Không push, deploy, sửa cấu hình GitHub hoặc kết nối server. Không tạo commit thay thế trong đợt này.

Đã bỏ địa chỉ máy chủ và tên tài khoản SSH thật khỏi workflow/tài liệu; Actions đọc host/user/port từ Secrets, kiểm tra đầu vào trước kết nối và giữ kiểm tra host key. Hướng dẫn dùng SSH alias được cấu hình ngoài repository; đường dẫn gói và SHA cụ thể được thay bằng biến do người vận hành chọn rõ ràng. Người vận hành cần cấu hình Secrets host/user trước lần push tiếp theo.

Bổ sung ignore cho kho private, thư mục SSH và các định dạng key/credential store. File bí mật local/database/backups vẫn nằm ngoài Git; không xóa mật khẩu database hoặc thay đăng nhập người dùng. Bộ quét không tìm thấy literal credential/hash mật khẩu/private key/API token hoặc địa chỉ máy chủ ngoài localhost/mạng minh họa trong các file nguồn hiện tại được rà soát. Tên field/password và code đăng nhập cần cho chức năng vẫn được giữ.

Kiểm chứng: `python3 tools/security/check_repository.py`; bộ unit test scanner và workflow/deploy (12 test) dùng dữ liệu tổng hợp, SSH giả và bare repo tạm; không có push tới remote thực. Validate Python/XML/manifest/JS và diff whitespace của phần code hiện tại.

Giới hạn: scan file text hiện tại không chứng nhận ảnh, commit cũ, Git object/reflog, remote, bản sao lưu hoặc nội dung chat đã được xóa. Kiểm tra history đã xác nhận địa chỉ máy chủ có trong các commit cũ hơn ở workflow/tài liệu deploy. Hai commit bị hủy không còn là ancestor của main nhưng object/reflog chưa bị purge. Không tự force-push hoặc viết lại lịch sử đã chia sẻ.
