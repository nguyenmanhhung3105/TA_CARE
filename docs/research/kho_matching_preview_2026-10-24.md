# Giới thiệu matching trên trang chủ Kho Việc Làm

Chủ dự án yêu cầu hiện khoảng hai matching nhằm giới thiệu khả năng kết nối. Chi tiết thuộc về tài khoản có tin/hồ sơ phù hợp, không mở cho mọi người chỉ vì đã đăng nhập.

Trang chủ Kho thêm tối đa hai thẻ, hai cột từ 1024px và một cột trên màn hình nhỏ. Mỗi thẻ có ảnh minh họa đã ghi nguồn, thông tin công việc công khai và trạng thái có gợi ý nhận làm. Giữ phần còn lại của trang chủ, kích thước chung, palette và hai thanh đầu trang.

## Dữ liệu và quyền

- `sites/khovieclam/matching_preview.py` chỉ xét tin thời vụ công khai đang mở, còn chỗ, bật matching, có account chủ tin hoạt động. Hồ sơ phải thuộc Tủ, có account hoạt động, đang hiển thị và không riêng tư. Quyền discovery/profile và matching/profile/skills phải còn hạn, đúng tổ chức nhận.
- Thẻ được sinh khi `_care_compare_profile` thực sự trả eligible với rank có căn cứ; tối đa hai nhóm việc khác nhau. Không tạo cặp, tên hồ sơ hay kết luận thủ công. Khi không có kết quả, ẩn khối, không thêm mẫu giả.
- Owner cho phép giới thiệu ẩn danh, không cho phép công khai hồ sơ. Hàm đọc có quyền chỉ trả sáu chuỗi thuộc tin công khai: tiêu đề, nhóm việc, ảnh minh họa, khu vực, kiểu lịch và ngân sách. Không trả ORM record, danh tính, mức nhận, lịch nhận, bảng lý do, ID hồ sơ/capability hay URL cặp. Không tạo/nới/gia hạn consent. Giới hạn duyệt 40 tin và 200 hồ sơ mỗi lần, dừng sau hai nhóm việc; không tuyên bố đây là toàn bộ kết quả hệ thống.
- CTA dẫn tới `/tacare/matching`, không tới cặp của người khác. Khách đi qua form native/SSO hiện có. Doanh nghiệp thấy tin thuộc tổ chức có quyền; cá nhân thấy hồ sơ hoặc tin của mình. Tài khoản chưa có kết quả được hướng dẫn đăng nhu cầu/cập nhật hồ sơ, không tự cấp matching.
- Nếu không chọn job cụ thể và tin mặc định chưa có kết quả, trang matching tìm một tin khác thuộc quyền có gợi ý. Không thay lựa chọn job rõ ràng của người dùng hoặc thuật toán/rank.
- `/tacare/pair/<job>/<profile>` tiếp tục kiểm ownership/company/consent và tính lại eligibility. Route tương thích `/tacare/matching/<job>/profile/<profile>` bổ sung chặn cặp không còn eligible. Chi tiết tin công khai Kho giữ nguyên.

## Kiểm chứng local

Đã backup DB tại ignored `backups/kho_matching_preview_20261024/`, kiểm danh mục dump, cập nhật addon `tacare_website` và restart local.

- `tests/dev_matching_preview_check.py`: Odoo shell, rollback toàn bộ; hai nhóm việc có kết quả thật, đúng allowlist đầu ra, cùng projection khi gọi từ public user. Không có thuật toán/consent hiện hành hoặc hồ sơ riêng tư/tin tắt matching thì không có preview. Chủ tin/chủ hồ sơ mở được cặp; khách và doanh nghiệp khác bị chặn; cặp không eligible bị chặn ở cả hai route. Kiểm default chọn tin thuộc quyền có kết quả và trạng thái hết matching sau thu hồi consent.
- `tests/marketing_preview_browser_check.cjs`: Chrome với account hiện có, không tạo dữ liệu. Khách thấy hai thẻ/ảnh; không có profile/pair identifier hoặc bảng riêng. CTA mở đăng nhập trên TA.CARE, đăng nhập trả về matching của chính tài khoản, chi tiết hiện bảng nguồn. Tài khoản doanh nghiệp khác nhận 403/404 khi thử URL cặp; khách chỉ thấy đăng nhập. Kiểm grid và không tràn ngang tại 320/375/768/1024/1440/1920px. Ảnh trong ignored `runtime/marketing-preview-review/`.
- Python/XML parse bằng thư viện chuẩn, JS syntax, `tools/security/check_repository.py` và `git diff --check` đạt. File tài khoản QA chỉ nằm trong ignored runtime, được xóa sau kiểm tra.

Không tạo/sửa account, hồ sơ, nhu cầu, consent hay kết nối để làm marketing. Chưa commit, push hoặc deploy server. Các snapshot chuyển dữ liệu cũ chưa chứa thay đổi này.
