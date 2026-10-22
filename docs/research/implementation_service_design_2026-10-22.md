# Thiết kế lại Kho Việc Làm và Tủ Hồ Sơ — Everyday services

Ngày 22/10/2026, theo yêu cầu xây lại bố cục sau khi bản trước còn tạo cảm giác tuyển dụng. Công việc đã thực hiện local, chưa commit/push/deploy.

## Nghiên cứu và lựa chọn

Đã nghiên cứu 10 trang dịch vụ/nền tảng trong và ngoài nước, cùng Refero Styles; xem bố cục thực bằng Chrome ở các trang truy cập được. Taskrabbit, Airtasker, Urban Company và Helpling bổ sung cho sáu nguồn Việt Nam người dùng đưa ra. Airtasker đọc được nội dung qua web tool nhưng Chrome gặp kiểm tra truy cập; Thumbtack và Yoojo không dùng làm chứng cứ thị giác vì không tải được. Không vượt kiểm tra truy cập. Chi tiết, link nguồn và lý do chọn nằm trong [bảng nghiên cứu trước triển khai](service_design_references_2026-10-22.md).

Chọn trải nghiệm khám phá dịch vụ đời thường vì:

1. Đầu việc, ảnh đang thực hiện và icon nghề giúp nhận ra sửa đồ, nấu ăn, chăm cây, dạy kèm, việc số ngay từ đầu. Cấu trúc này phù hợp hơn với ghép việc theo giờ/ca/đầu ra.
2. Kho phục vụ phía cần người và người tìm việc; Tủ giúp người nhận làm thể hiện khả năng và quản lý nội dung riêng. Chung hệ thiết kế, khác mục đích và cấu trúc.
3. Tìm/lọc theo nghề và ngữ cảnh cho thấy độ đa dạng mà không cần số người dùng, đánh giá hoặc lời đảm bảo chưa có thật.

[Design system](../design-system/everyday-services.md) ghi màu, kiểu chữ, spacing, icon, ảnh, chuyển động và giới hạn sản phẩm. Dùng skill `ui-ux-pro-max` để rà tương tác, accessibility và responsive; không lấy gợi ý layout doanh nghiệp của dataset làm mẫu trang chủ.

## Giao diện đã thay

- Kho: tiêu đề giữa trang, tìm theo đầu việc, dải năm ảnh có nhịp, danh mục chín nghề, ba tình huống tương tác, danh sách đầu việc thực và hai lối cần người/nhận làm. Bỏ hero hai cột và dãy ba thẻ tuyển dụng làm trục chính.
- Danh sách Kho: danh mục icon, bộ lọc theo điều kiện, thẻ việc trình bày ảnh/đầu việc/lịch/khu vực/ngân sách. Bộ lọc dùng route và dữ liệu thật; input được giữ theo GET.
- Tủ guest: nền ấm, thông điệp nhận làm, gallery riêng, chọn nhóm khả năng và hướng dẫn giới thiệu. Không công khai hồ sơ riêng để lấp nội dung.
- Tủ đăng nhập: gallery trước tủ, phạm vi mine/all đúng quyền, ảnh minh họa nhóm việc, nội dung nhận làm và thao tác mở/chỉnh sửa/xóa đúng vai trò. Form tạo hồ sơ có thể điền tên gợi ý từ danh mục; nội dung vẫn chỉnh được, bước lưu vẫn kiểm server.
- Chung: điều hướng, nút, icon và footer; trang chi tiết và form dùng cùng màu/chữ/controls. Tủ ưu tiên tạo hồ sơ, Kho ưu tiên đăng nhu cầu. TA.CARE giữ trang chủ quỹ đạo và vai trò ghép nối.

Đã tải và xem 11 ảnh ứng viên; chọn **9 ảnh chụp mới** cho các nghề, tự host WebP. Hai ảnh không chọn được chuyển về runtime tham khảo ignored. Có **36 SVG duotone Phosphor**, giữ giấy phép MIT và tài liệu nguồn. [Nguồn ảnh](../../source/apps/tacare/addons/tacare_website/static/src/img/services/SOURCES.md), [nguồn icon](../../source/apps/tacare/addons/tacare_website/static/src/icons/phosphor/SOURCES.md). Ảnh stock chỉ minh họa công việc, không là danh tính hay minh chứng của hồ sơ. Kho gallery dùng repair/cleaning/digital, Tủ dùng cooking/garden/pets; không trùng tập ảnh carousel. Các gallery mặc định tạm dừng, điều khiển bằng nút/bàn phím và hỗ trợ reduced motion.

## Source và dữ liệu

- `sites/khovieclam/views/service_design.xml`: trang chủ và danh sách Kho.
- `sites/tuhoso/views/service_design.xml`: trang chủ, gallery, tủ cá nhân/admin và tạo hồ sơ.
- `views/shared/service_design.xml`: điều hướng, danh mục, tình huống, thẻ việc và thành phần chung.
- `controllers/service_design.py`: metadata thiết kế công khai, không truy vấn hồ sơ người dùng. `controllers/seasonal.py` cung cấp context qua dữ liệu nhu cầu đã công bố.
- `static/src/scss/service_design.scss`: style/token dùng chung; giữ tương thích SCSS Odoo. `flexible_work.js` hỗ trợ gallery mặc định tạm dừng bằng data attribute.
- Helper ảnh chọn asset services theo nghề, bản nháp chưa chọn nghề dùng placeholder SVG trung tính; giữ model/XML ID, các URL và guard hiện có. Manifest website lên `19.0.11.0.0`.

Không đổi schema, tài khoản, mật khẩu, owner, consent hoặc seed sản phẩm. DB backup trước cập nhật view: ignored `backups/services_redesign_20261022/tacare_local.dump`, đã kiểm tra danh mục bằng `pg_restore --list`, thư mục riêng tư. Sau dọn QA vẫn **15 việc thời vụ, 3 hồ sơ, 12 mục nhận làm**. Các receipt/backup đầy đủ của lần bỏ tuyển dụng trước vẫn giữ.

## Kiểm tra

- Nâng addon local bằng `--stop-after-init`, QWeb nạp thành công; restart Odoo.
- Parse **78 Python / 37 XML**, `node --check` JS thay đổi và hai script browser, `git diff --check`.
- `homepage_contract_smoke.py`: ba home HTTP 200 với `tc-jobs`, `tc-profiles`, `tc-hub`; ba login HTTP 200.
- `service_design_browser_check.cjs`: 320/375/768/1440px, so sánh chín icon/nhãn giữa Kho và Tủ, gallery tạm dừng/bàn phím, bộ lọc thực, ảnh chi tiết, dropdown, tủ cá nhân/admin, cấm scope all cho cá nhân, tên hồ sơ gợi ý, reduced motion và ảnh/icon không lỗi HTTP/JS.
- `seasonal_browser_check.cjs`: cá nhân/doanh nghiệp đăng nhu cầu, giữ input lỗi; C2C gửi/nhận, chặn tài khoản ngoài cuộc, grant/revoke email đúng bên thuê; admin chỉnh hồ sơ/ba ví dụ; hồ sơ mới chỉ nhận việc thời vụ. QA là dữ liệu hư cấu, credential ignored; đã dọn sau kiểm thử.
- Các cặp màu chính đã tính contrast: chữ 12,22:1; chữ phụ 6,20:1; nút trắng/xanh 11,72:1; heading xanh 4,32:1 và olive 4,57:1. Không tuyên bố đã kiểm định toàn bộ WCAG.
- Kiểm tra helper bản nháp chưa có nghề dùng placeholder SVG bằng Odoo shell, giao dịch rollback; không thêm bản ghi sản phẩm.
- Scanner repo kiểm 272 text file, không tìm thấy mẫu credential/server IP bị cấm. Ảnh tham khảo của đối thủ và thông tin QA nằm trong runtime ignored, không đóng gói addon.

Ảnh bàn giao nằm trong [screenshots](../screenshots/everyday-services-20261022/); ảnh guest được chụp sau dọn QA, ảnh workspace/detail chụp với tài khoản QA hư cấu để kiểm tra chức năng. Có kiểm tra bằng trình duyệt thật; chưa có nghiên cứu usability với người dùng thực.

## Xem local và giới hạn

- Kho: http://khovieclam.localhost:8069/
- Tủ: http://tuhoso.localhost:8069/

Đây là thay đổi thiết kế. Ghép nối vẫn là đề nghị/đồng ý trao đổi; chưa thêm GPS, booking, xác minh nghề, thu tiền hoặc bảo hiểm. Không thay server, DNS/TLS hoặc release script; chưa commit, push hay deploy.
