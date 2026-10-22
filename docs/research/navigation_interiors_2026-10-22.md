# Điều hướng, trang chi tiết và không gian TA.CARE — 22/10/2026

## Yêu cầu và lựa chọn thiết kế

Chủ dự án đã duyệt nội dung/bố cục trang chủ Kho Việc Làm và Tủ Hồ Sơ. Lần này giữ nguyên hai template trang chủ, ảnh, danh mục và carousel; chỉ thay navbar dùng chung. Được phép thiết kế lại TA.CARE và các trang bên trong.

Tra cứu bổ sung ngày 22/10/2026 từ trang chính thức:

- [Airtasker — How it works](https://www.airtasker.com/au/how-it-works/): phân biệt người đăng việc/người nhận làm; nêu đầu việc và ngân sách trước khi chọn người. Áp dụng vào cách đặt tên menu và nhóm thông tin trên form.
- [Taskrabbit — How it works](https://www.taskrabbit.com/how-it-works): chọn việc/khu vực, xem khả năng/đơn giá rồi trao đổi để chốt. Áp dụng thứ tự đọc phạm vi, lịch, khu vực, chi phí và hành động kết nối.
- [Grab Việt Nam](https://www.grab.com/vn/): phân luồng theo nhu cầu và phía tham gia trên cùng nền tảng. Áp dụng hai lối vào của TA.CARE và liên kết ba sản phẩm có vai trò riêng.

Đây là diễn giải thiết kế của TA.CARE từ nội dung công khai, không sao chép giao diện hoặc tài sản của các nền tảng trên. Không đưa đánh giá, xác minh nhân thân, đặt lịch hay thanh toán của họ thành tính năng TA.CARE.

Hướng được chọn: dùng tiếp hệ màu Everyday services để người dùng nhận ra cùng hệ thống; TA.CARE thể hiện hai phía qua cặp thẻ nhu cầu/khả năng và các căn cứ đối chiếu. Không dùng carousel tại hub. Tình huống ở hero được ghi rõ là minh họa; không tạo người nhận làm giả, điểm phù hợp hay thống kê không có dữ liệu.

## Điều hướng

- Cả ba có “Trang chủ”, logo về đúng trang chủ, liên kết “Cách hoạt động”, đăng nhập/đăng xuất và nút tạo nội dung theo sản phẩm.
- Kho: Tìm việc thời vụ; Việc tôi đã đăng; Tìm người phù hợp; Kết nối của tôi.
- Tủ: Hồ sơ của tôi; Tất cả hồ sơ chỉ admin; Tìm việc phù hợp; Kết nối của tôi.
- TA.CARE: Tìm người làm; Tìm việc phù hợp cho tài khoản được dùng Tủ; Kết nối của tôi; Thông báo.
- Tab hiện tại có nền xanh, chữ trắng và `aria-current=page`. Xét route con, `scope`, `view`, mặc định theo vai trò và tiền tố ngôn ngữ. Chuyển sản phẩm vẫn đánh dấu sản phẩm hiện tại độc lập với tab.
- Mọi trang bên trong có đường “Trang chủ [tên sản phẩm]”; các breadcrumb chuyên biệt giữ nguyên.

## Trang chi tiết và biểu mẫu

Chi tiết công việc có tiêu đề và hàng thông tin khu vực/lịch/loại tin trước nội dung; ảnh đi cùng phạm vi công việc; cột bên phải dành cho tiền công, lịch và thao tác. Chỉ hiển thị thao tác chuyển trạng thái phù hợp trạng thái hiện tại, tiếp tục dùng route và kiểm tra quyền hiện có. Thiếu khu vực/tỉnh thành được gọi là chưa khai khi làm tại chỗ.

Form công việc vẫn là một form native liên tục: năm nhóm có tiêu đề, giải thích và mục lục nhảy tới từng phần; không bắt người dùng qua wizard JS. Giữ nguyên field names, giá trị lỗi, file enctype, CSRF, ID và profile_id có kiểm tra owner. Form giới thiệu hồ sơ dùng hai nhóm tên/giới thiệu và khả năng/mong muốn; các điều kiện nhận làm thuộc từng dịch vụ, quyền chia sẻ vẫn riêng.

Hub mới gồm hai lối vào, vai trò ba sản phẩm, bốn căn cứ đối chiếu và các bước kết nối. Admin vẫn xem cặp có consent và ba ví dụ; lựa chọn nhu cầu trên trang chủ được giữ. Trang ghép nối đưa bộ chọn hồ sơ/nhu cầu và kết quả lên rõ ràng, có liên kết xem chi tiết trước khi gửi lời nhắn. Kết nối/chi tiết/thông báo dùng cùng hệ chữ, form và trạng thái.

## Phạm vi kỹ thuật

- Website addon `19.0.12.0.0`; không đổi schema, tài khoản, mật khẩu hay consent sản phẩm.
- UI riêng hub ở `sites/tacare/views/service_design.xml`; form/chi tiết dùng shared views; CSS mới chỉ tác động navbar, `.ix-main` và `.hx-*`.
- Route mới `/tacare/matching/<job_id>/profile/<profile_id>` thay liên kết tới route tuyển dụng đã khóa. Kiểm tra chủ tin/quyền xử lý của tổ chức, nhu cầu còn mở, cờ đối chiếu, discovery profile và matching profile/skills hiện hành. Minh chứng tiếp tục cần consent riêng; không đưa email vào trang này. Các route tuyển dụng cũ vẫn 404.
- Homepage `tc-jobs`, `tc-profiles`, `tc-hub` giữ nguyên.
- Backup local trước upgrade: ignored `backups/navigation_interiors_20261022/tacare_local.dump`, private permissions, đã đọc được danh mục bằng `pg_restore --list`.
- Không commit, push hay triển khai production trong đợt này.

## Xác minh

Đã thực thi:

- Parse **68 Python / 37 XML** trong website addon; `node --check` cho navigation và browser check mới; `git diff --check`: PASS.
- Backup DB local và kiểm tra `pg_restore --list`; update `tacare_website` rồi restart Odoo: PASS.
- `homepage_contract_smoke.py`: ba homepage đúng marker/HTTP 200, ba trang login HTTP 200.
- `navigation_interior_browser_check.cjs`: tab nền màu, route con/query/view mặc định/locale; đường về home; menu theo vai trò; chuyển tạm ngừng/mở lại; form dịch vụ lỗi tiền công giữ dữ liệu và đúng profile_id; lưu dịch vụ thật; trang chi tiết hồ sơ hub mới; người không sở hữu tin bị chặn; route tuyển dụng cũ vẫn 404; ba ví dụ admin; không lỗi JS. Bố cục 320/375/768/1440 không tràn ngang.
- `service_design_browser_check.cjs`: hai trang chủ giữ chín nhóm nghề/icon, carousel dừng mặc định/điều khiển bàn phím; bộ lọc thật, ảnh chi tiết, dropdown padding/size, tủ cá nhân/admin, tạo hồ sơ và reduced motion: PASS.
- `seasonal_browser_check.cjs` chạy lại trên bản cuối: cá nhân và doanh nghiệp đăng việc, lỗi form giữ dữ liệu, lời mời C2C từ mẫu matching mới, người gửi không tự chấp nhận, người nhận đồng ý, email có grant/revoke đúng bên thuê, người ngoài bị chặn, admin sửa hồ sơ, ba ví dụ và tạo hồ sơ thời vụ: PASS.
- `dev_matching_profile_check.py`: rollback-only ORM trên QA; chủ tin đọc được; người ngoài/chủ hồ sơ/doanh nghiệp khác bị chặn; thu hồi discovery hoặc matching, hay tắt đối chiếu tin đều trả NotFound: PASS. Không lưu thay đổi consent.
- `tools/security/check_repository.py`: **278 tệp text**, không khớp thông tin đăng nhập nhúng hoặc IP server.

Ảnh desktop/375 px nằm trong `docs/screenshots/navigation-interiors-20261022/`, gồm hub, chi tiết việc, form nhu cầu/dịch vụ, form giới thiệu, hồ sơ được chia sẻ và trang ghép nối/kết nối. Mọi người/tin trong ảnh nội bộ đều hư cấu. Không chụp mật khẩu hoặc email liên hệ. Dữ liệu QA và tệp credentials riêng được dọn sau khi mọi tiến trình kiểm thử kết thúc; giữ dữ liệu sản phẩm ban đầu.

Giới hạn: kiểm tra local bằng Chrome headless; chưa kiểm tra trên thiết bị vật lý hoặc production. Các tính năng định vị trực tiếp, đặt lịch và thanh toán không được bổ sung trong lần sửa UI.
