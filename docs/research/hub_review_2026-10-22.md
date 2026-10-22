# Sửa bố cục và trang chủ TA.CARE — rà soát tối 22/10/2026

Chủ dự án yêu cầu tăng nhãn bộ lọc, sửa trang “Việc tôi đã đăng”, sửa trải nghiệm đăng nhu cầu từ ghép nối, hiển thị tên người đăng nhập trên cả ba website, căn chiều ngang và đổi tông TA.CARE kèm gợi ý/ba ví dụ có ảnh ngay trang chủ.

## Nguyên nhân và thay đổi

- Danh sách chủ tin bị ép vào cột bộ lọc 245px: template bỏ `aside` khi `mine=True` nhưng vẫn dùng grid hai cột. Thêm trạng thái `sx-discover-layout-mine` với một cột kết quả chiếm toàn hàng; thẻ 3/2/1 cột theo viewport. Không dùng kiểm tra “không tràn ngang” làm bằng chứng duy nhất: browser check mới còn đo tỷ lệ chiều rộng kết quả và chiều rộng tối thiểu của thẻ.
- Chuẩn hóa shell/main/header của ba website về max 1280px, lề hai bên 48px desktop, 24px ở màn hình vừa và 20px mobile. Giữ cấu trúc/nội dung/ảnh/carousel trang chủ Kho và Tủ đã duyệt.
- Nhãn bộ lọc từ 12–14px lên 16px/650; giữ input 16px và caret nằm trong dropdown.
- Header chung có tên người đăng nhập, in bằng QWeb `t-esc`; khách không thấy tên tài khoản. Tên dài được xuống dòng, không cắt mất thông tin hoặc tràn navbar.
- Dropdown nhu cầu trống trên TA.CARE không chứng minh lỗi lưu tin: chỉ liệt kê tin đang mở, bật đối chiếu, đúng company và chủ tin/quyền xử lý của tổ chức. Khi không có tin đủ điều kiện, hiển thị hướng dẫn và CTA đăng mới/kiểm tra tin đã đăng; không để selector trống cùng nút đối chiếu vô tác dụng. Liên kết đăng mới đi sang host Kho chuẩn. Không gán lại owner hoặc nới quyền để làm xuất hiện dữ liệu.

## TA.CARE

- Tông plum/lavender: brand `#514080`, nền `#faf8fd`, chữ `#2d2542`, màu phụ peach. Kho/Tủ giữ tông riêng; trạng thái đáp ứng/cần làm rõ/khác điều kiện vẫn có chữ và màu mang ý nghĩa riêng.
- Gợi ý của tài khoản nằm ngay sau hero. Cá nhân xem được hai hướng cần người/nhận việc; doanh nghiệp chỉ có phía cần người; admin giữ tổng quan và bộ chọn nhu cầu trong phạm vi quản trị.
- `_hire_matching_data` và `_receive_matching_data` là cùng nguồn chính sách dùng cho homepage và trang matching. Chỉ đọc dữ liệu theo company, owner/tổ chức, trạng thái/cờ matching, consent hiện hành và tiêu chí eligible. Không lưu snapshot, tạo kết nối hoặc cấp consent khi đọc trang chủ. Tối đa ba gợi ý mỗi phía.
- Ba ví dụ hư cấu xuất hiện trên cả homepage công khai và trang ví dụ cho người đăng nhập. Dùng ảnh thật có nguồn đã có trong addon (`cleaning.webp`, `digital.webp`, `garden.webp`), minh họa đầu việc, không đại diện người dùng thật.
- Trang ví dụ có ảnh, hai phía tham gia, lịch/tiền công từng phía và căn cứ theo hàng. Ba kết quả khác nhau: có thể trao đổi; cần bổ sung thông tin; lịch không phù hợp. Không tạo phần trăm hay đánh giá giả. Giữ số tiền 80.000đ bên cần và từ 65.000đ bên nhận riêng biệt trong ví dụ dọn nhà.

## Phạm vi vận hành

Website addon `19.0.13.0.0`. Không đổi schema, tài khoản gốc, mật khẩu, owner, consent hoặc dữ liệu sản phẩm. Backup local trước update: ignored `backups/ui_review_20261022/tacare_local.dump`, private permissions, `pg_restore --list` thành công. Không commit/push/deploy.

## Kiểm tra

Đã chạy và PASS:

- Parse 69 Python / 37 XML; `node --check` browser test mới; `git diff --check`.
- Backup DB, kiểm tra danh mục dump, update addon 19.0.13.0.0 và restart Odoo local.
- `hub_review_browser_check.cjs`: chiều ngang header/main ba sản phẩm, thẻ chủ tin rộng tối thiểu và kết quả chiếm toàn hàng, nhãn 16px, tên đăng nhập, đúng tông hub, ba ảnh/ví dụ, link anchor, gợi ý đúng tài khoản, người ngoài không thấy gợi ý của người khác. Luồng doanh nghiệp: tắt đối chiếu → hướng dẫn thay dropdown trống → CTA sang Kho → đăng thật → tin xuất hiện ở matching. Kiểm tra 320/375/768/1024/1100/1440/1680 px và assets/JS.
- `/tmp/tacare-hub-review-final.cjs`: xác minh tinh chỉnh cuối cho gợi ý đơn nằm ngang, tên tài khoản dài không tràn, trang chưa có tin không hiện tiêu đề kết quả 0 thừa, ảnh công khai và ba ví dụ; chụp lại ảnh cuối. Các cờ matching của QA được khôi phục sau kiểm tra.
- `dev_home_suggestions_check.py`: rollback-only ORM cho owner/tổ chức, hai hướng cá nhân, giới hạn doanh nghiệp, chặn guest/outsider, thu hồi discovery/matching và tắt matching tin. Dùng cùng policy với trang ghép nối, không giữ thay đổi consent.
- `seasonal_browser_check.cjs`: đăng tin cá nhân/doanh nghiệp, giữ input lỗi, gửi lời mời C2C, người gửi không tự nhận, người nhận phản hồi, email grant/revoke đúng bên thuê, người ngoài bị chặn, admin sửa hồ sơ và ba ví dụ trên home: PASS.
- `service_design_browser_check.cjs`: hai home Kho/Tủ giữ cấu trúc và chín danh mục, gallery dừng/keyboard/reduced-motion, bộ lọc thật, ảnh chi tiết, dropdown, tủ cá nhân/admin, tạo hồ sơ: PASS.
- `homepage_contract_smoke.py`: ba homepage HTTP 200 đúng `tc-hub`, `tc-jobs`, `tc-profiles`; ba trang login HTTP 200.
- `tools/security/check_repository.py`: 282 tệp text, không khớp mật khẩu nhúng hoặc IP server.

QA chỉ dùng người/tin hư cấu; credentials nằm trong runtime bị ignore. Sau khi toàn bộ tiến trình kiểm thử kết thúc, chạy cleanup đúng các QA owner, giữ 15 nhu cầu / 3 hồ sơ / 12 mục nhận làm gốc. Ảnh nằm trong `docs/screenshots/hub-review-20261022/` (guest, tài khoản cá nhân/doanh nghiệp/admin, danh sách, bộ lọc, empty state và ba ví dụ). Không chụp thông tin đăng nhập hoặc liên hệ.

Giới hạn: kiểm tra local bằng Chrome headless; chưa kiểm tra thiết bị vật lý hoặc production. Không có commit, push hoặc triển khai server.
