# Quyền xóa admin, trang chủ đối chiếu và chữ, 21/10/2026

Bổ sung theo yêu cầu chủ dự án lúc 23:02. Chỉ sửa và kiểm tra local, tiếp tục giữ thiết kế orbit của TA.CARE, carousel riêng của Kho/Tủ, logo và token thương hiệu. Version `tacare_website` 19.0.8.1.0; không thêm bảng hay thay tên model/XML ID.

## Quyền xóa

Admin hệ thống có nút Xóa ở thẻ và chi tiết hồ sơ, công việc nhận làm trong Tủ, tin tuyển dụng/linh hoạt trong Kho. Các đường GET mở xác nhận; chỉ POST có CSRF hợp lệ, field allowlist và checkbox xác nhận mới thực hiện. Server kiểm tra `base.group_system` cùng công ty được phép; nút ẩn không thay kiểm tra quyền. Tài khoản thường không có quyền xóa dù sở hữu bản ghi.

- Chưa có lịch sử liên quan: xóa bản ghi và nội dung con bằng ORM. Tài khoản người dùng không bị xóa.
- Đã có kết nối, ứng tuyển, nhân sự, phiên bản tin, đầu vào/phiên đối chiếu hoặc tài liệu cần giữ: gỡ khỏi danh sách hoạt động, giữ lịch sử. Tin thành closed/inactive/unpublished, tắt matching; hồ sơ thành archived/private/invisible, dừng các offer và thu hồi consent. Đề nghị đang chờ bị hủy; kết nối đã phản hồi vẫn còn lịch sử.
- Trang xác nhận nói rõ cách xử lý trước khi thao tác. Lựa chọn giữ lịch sử bảo toàn quan hệ native Odoo và các ràng buộc `restrict`, không âm thầm xóa kết nối hoặc nhân sự.
- Bản ghi đã gỡ không xuất hiện trong thư viện/gợi ý và không được mở lại bằng URL sửa thông thường. Route gửi kết nối kiểm tra hồ sơ active và tài khoản hoạt động.
- Có audit append-only cho xóa/gỡ. Không thực hiện xóa dữ liệu thật trong phiên phát triển; các thao tác trình duyệt dùng bản ghi QA hư cấu tạm.

Code: `models/admin_removal.py`, `controllers/shared/removal.py`, các route trong `sites/khovieclam/routes.py` và `sites/tuhoso/routes.py`. Không mở thêm portal ACL.

## Trang chủ TA.CARE của admin

Ngay sau phần orbit có mục “Các gợi ý đang có căn cứ”, bộ chọn tin và tối đa ba cặp việc–hồ sơ từ các tin được chọn (mặc định sáu tin cập nhật gần nhất). Dùng cùng `_match`/`_care_compare_profile` như trang đối chiếu; công ty được phép và discovery/matching consent còn hiệu lực, đúng tổ chức/phạm vi profile+skills. Hồ sơ riêng tư chưa đồng ý không được đưa vào gợi ý. Có link xem căn cứ và hồ sơ trong TA.CARE; không hiển thị email hay điểm phần trăm.

Bên dưới là “3 ví dụ đối chiếu” với cả nhu cầu, hồ sơ và căn cứ; luôn phân biệt hư cấu với kết quả dữ liệu hiện tại. Có link từ phần orbit để nhảy tới mục này. Khách và tài khoản thường không nhận dữ liệu tổng quan admin. Khi chưa có consent, gợi ý thật hiển thị trạng thái trống có giải thích, ba ví dụ vẫn hiện cho admin. Không tạo snapshot matching hoặc tự cấp consent.

## Điều hướng, dropdown và typography

Bỏ tab Ứng viên trong Kho. Các CTA quản lý dẫn sang kết nối TA.CARE; route cũ giữ để tương thích và tiếp tục kiểm quyền. Không đổi policy business Kho+TA.CARE/candidate Tủ+TA.CARE.

`static/src/scss/interface_polish.scss` áp dụng cuối bundle, có thang chữ chung cho ba sản phẩm. Tiêu đề trang 30–44px, tiêu đề card 20–26px, nội dung card 16px/line-height 1.75, nhãn form/nút 14px semibold, chữ phụ 13–14px. Giảm việc dùng màu/đậm trên nội dung thường; màu thương hiệu cho hành động và thu nhập; phân biệt trạng thái bằng cả chữ và màu. Trang chủ giữ cỡ heading theo bố cục riêng, thống nhất weight 600 và cỡ chữ đọc/navigational trên điện thoại. Font/logo/ảnh gốc được giữ.

Select tiếp tục là native control cho bàn phím và trình đọc màn hình; ẩn chevron mặc định, dùng một SVG chevron ở `right 16px center`, chừa 44px bên phải cho nội dung. Forced-colors dùng lại native indicator. Không dùng ký tự “v” giả làm nút.

## Kiểm tra và môi trường

Backup ignored trước cập nhật: `backups/admin_polish_20261021/tacare_local.dump`. Cập nhật hai addon bằng lệnh nâng cấp local chuẩn, restart `tacare`. Không push/deploy hoặc truy cập production.

Đã đạt:

- Python AST/XML, manifest paths, JS syntax và `git diff --check`.
- `tests/dev_admin_removal_check.py`: rollback xóa không có lịch sử, xóa offer không xóa profile, giữ tài khoản, gỡ bản ghi có kết nối, hủy pending, thu hồi consent, chặn portal và công ty ngoài phạm vi.
- `tests/admin_polish_browser_check.cjs`: Chrome headless ở 320/375/1440px; font heading và chevron inset/padding/font input; không tràn ngang trên ba trang chủ; tab Kho đã bỏ; không có nút xóa và bị 403 với tài khoản thường; admin thấy gợi ý có consent và đúng ba ví dụ; chọn tin trên trang chủ; GET không xóa, POST thiếu xác nhận/CSRF hoặc có field ngoài allowlist bị chặn; xóa hồ sơ/offer/tin QA chưa có lịch sử; gỡ bản ghi đã có lịch sử và còn xem được cuộc trao đổi; chủ tài khoản vẫn đăng nhập được và không thấy hồ sơ đã gỡ.

Ảnh QA hư cấu/khách trong `docs/screenshots/admin-polish-20261021/`, gồm ba trang chủ desktop/mobile và khu đối chiếu admin. Không chụp dữ liệu cá nhân, mật khẩu hay form đăng nhập đã điền.

Kết thúc kiểm chứng: `homepage_contract_smoke.py` đạt cả ba marker và ba trang đăng nhập HTTP 200; `dev_schema_check.py` đạt rollback bảo mật tổ chức/hồ sơ/consent. Cleanup QA đã hoàn tất; kiểm đếm sau cùng vẫn 20 tin, 7 hồ sơ, 12 offer và không còn account QA theo prefix. Chỉ audit append-only của QA được giữ theo thiết kế. Dịch vụ local đã restart với bản code cuối.
