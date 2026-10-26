# Áp dụng hai mẫu chủ dự án đã chọn — 26/10/2026

Chủ dự án từ chối bản biên tập/navy và khối petrol trước đó, yêu cầu xem trước ba phương án. Các bản thử độc lập nằm trong ignored `runtime/design-options-20261026/`. Lựa chọn cuối: **mẫu 1 cho Tủ Hồ Sơ, sửa tiêu đề/nhãn rõ nghĩa; mẫu 2 cho TA.CARE**. Đây là thay đổi được triển khai local, không phải chỉ cập nhật bản thử.

## Tủ Hồ Sơ — bảng ghim, nội dung rõ nghĩa

- Hero: “Giới thiệu việc bạn làm được. Tìm việc phù hợp với bạn.” Thay các câu mơ hồ “Kể ở đây”, “Khéo việc số” bằng tên công việc và thao tác cụ thể.
- Ba ảnh giấy ghim: “Thiết kế & công việc số”, “Chăm sóc cây & làm vườn”, “Dạy kèm & chia sẻ kỹ năng”. Dùng ảnh có nguồn hiện có; không phải hồ sơ cá nhân hoặc kết quả matching. Mobile giữ cả ba ảnh, caption xuống dòng đầy đủ.
- CTA “Tạo hồ sơ nhận việc”, “Xem hồ sơ của tôi”; hướng dẫn ba bước tạo hồ sơ, thêm việc nhận làm và chọn quyền chia sẻ. Root vẫn là giới thiệu chung cho cả khách/tài khoản đăng nhập; không đưa thư viện riêng lên home hoặc thêm gallery vào thư viện.
- Tông kem `#fff9ef`, chữ `#292722`, cam đậm `#b94630` cho nút/tab để đủ tương phản, hover `#963522`. Màu được nối với các token form/library hiện có.

## TA.CARE — ảnh lớn, nền sáng

- Hero dùng ảnh có nguồn làm nền, lớp phủ giữ chữ rõ, title “Tìm người. Hợp việc.” và nút “Xem gợi ý phù hợp”. Hai lối vào “Tôi cần người làm” / “Tôi muốn nhận việc” giữ điều kiện role cho phía nhận làm; bản tinh chỉnh mới nhất dùng nền tối trong suốt thay thanh trắng.
- Trắng/đen với điểm vàng nhạt `#f5e79d`; brand `#252525`, hover `#080808`, nền `#fff`. Không còn khối hero petrol của bản bị từ chối. Giữ logo và trạng thái ngữ nghĩa, header/shell theo gutter 48/24/20px.
- Matching thật tiếp tục tại `#home-suggestions`: hai cặp/hàng desktop, các hàng nguồn căn bằng CSS subgrid; không dựng cặp hoặc công khai hồ sơ. Chi tiết và lời mời tiếp tục được chặn theo quyền hiện hành.

## Source và kiểm chứng

Giữ XML IDs `provider_editorial_home` / `hub_connection_home` và các template gốc để tương thích. CSS cũ được thay bằng `static/src/tuhoso/scss/pinboard_home.scss` và `static/src/tacare/scss/cinematic_home.scss`; manifest nạp đúng đường dẫn. Cập nhật block palette của hai sản phẩm, giữ Kho.

Khi kiểm CTA, phát hiện logo trong dialog che nút đóng ở mobile. Thêm `z-index:2` riêng `.tc-login-close` trong `authentication.scss`; không thay form native, CSRF/SSO/CAPTCHA/MFA hoặc quyền xác thực.

- Backup local tại ignored `backups/selected_homepages_20261026/`, kiểm danh mục dump, nâng `tacare_website` và restart thành công.
- XML/manifest/asset paths đạt; security scanner và diff whitespace đạt.
- Chrome kiểm ba homepage tại 320/375/640/767/768/1024/1440/1920px: đúng marker, một h1, ảnh tải, không tràn ngang; header khớp hình học ở mobile/desktop. Không có hồ sơ riêng trên trang chủ khách. Nút/hover đạt tương phản 4.5:1; nhãn Tủ rõ và không còn copy bản thử mơ hồ.
- CTA tạo hồ sơ và gợi ý yêu cầu login đúng; nút đóng được bấm bằng chuột trên cả Tủ/TA.CARE ở 375/1440px. Native details đóng/mở bằng bàn phím.
- Tài khoản hiện có xem matching/chi tiết thật; các hàng nguồn/nút/khung vẫn bằng nhau, kể cả nội dung dài tạm trong DOM. Khách mở URL cặp không thấy bảng riêng. Không tạo account/contact/profile/consent/connection để kiểm giao diện.
- Ảnh và số đo ở ignored `runtime/selected-homepages-20261026/`. Ảnh mobile fresh xác nhận một header, một thanh thông báo, không có iframe lặp.

Không sửa dữ liệu nghiệp vụ, thuật toán, controller/model hoặc quyền truy cập. Geohash/map vẫn để sau theo tài liệu roadmap. Không commit/push/deploy.

## Tinh chỉnh hero tràn ngang và tự chuyển ảnh

Chủ dự án yêu cầu ảnh hòa với hai lối vào, bỏ nền trắng che ảnh, cho hero tràn màn hình và tự chuyển hình. Riêng `.cn-intro`/`.cn-hero` được tràn toàn bộ chiều ngang; header và các nội dung khác giữ gutter 48/24/20px. Hai lối vào dùng nền tối trong suốt, blur nhẹ, chữ/icon trắng, viền mảnh. Đây là ngoại lệ có chủ đích cho hero, không thay chiều rộng toàn bộ ba sản phẩm.

Hero luân phiên bốn ảnh thực có nguồn sẵn: sửa chữa, nấu ăn, dọn dẹp, nông nghiệp. Mỗi 6.500ms đổi ảnh với fade 850ms; chữ và CTA đứng yên. Dùng chung bộ điều khiển gallery có trước/sau, tạm dừng/tiếp tục, phím mũi tên và thông báo ARIA khi chuyển thủ công. Tự dừng khi hover, focus hoặc tab bị ẩn; chọn giảm chuyển động tắt tự chạy và hiệu ứng, vẫn dùng trước/sau được. Sửa hành vi resume chung để bấm “Tiếp tục” thực sự chạy ngay cả khi nút còn focus; các gallery cũ có autoplay=0 vẫn khởi đầu dừng.

Sau dump local đã kiểm danh mục tại ignored `backups/fullbleed_carousel_20261026/`, nâng `tacare_website` và restart thành công. Chrome kiểm full-bleed tại 320/375/640/680/681/767/768/1024/1440/1920px: hero sát header, ảnh tràn chiều ngang, không tràn nội dung hoặc đè CTA, gutter phần dưới và chiều rộng hai trang còn lại giữ nguyên. Kiểm tự chuyển bằng đồng hồ giả, pause/resume, hover/focus, bàn phím/ARIA, giảm chuyển động và gallery mặc định dừng đạt; nút tối thiểu 44px, không che kicker ở tám kích thước. Kiểm giảm chuyển động chờ sự kiện media thực trước khi tiến đồng hồ giả. Đã xem ảnh desktop/mobile tại ignored `runtime/fullbleed-hero-20261026/`. JS/XML hợp lệ, diff whitespace và security scanner đạt. Không tạo dữ liệu hay thay matching/quyền; local only.

## Thêm hai ảnh Tủ và làm rõ tiêu đề TA.CARE

Theo yêu cầu thêm ảnh hai bên, bảng ghim Tủ hiện có năm ảnh: dọn dẹp nhà cửa — thiết kế/công việc số — chăm cây/làm vườn — dạy kèm/chia sẻ kỹ năng — chăm rau/nông nghiệp. Hai ảnh ngoài dùng nguồn có sẵn; giữ ba ảnh giữa và kiểu giấy ghim. Riêng bảng ảnh mở tới 1500px trong shell cũ, không đổi chiều rộng trang/header. Màn hình vừa giảm độ nghiêng để tránh chạm nhau; mobile xếp 2–2–1, giữ đủ nhãn, ghi chú ở hàng riêng.

Chủ dự án yêu cầu sửa tiêu đề TA.CARE; dùng câu rõ nghĩa “Kết nối việc cần làm với người phù hợp.”, mô tả “Đối chiếu đầu việc, khu vực, lịch và tiền công. Hai bên cùng trao đổi để bắt đầu.” Điều chỉnh cỡ h1 theo câu dài, giữ slideshow và hai lối vào.

Backup local đã kiểm danh mục tại ignored `backups/tuhoso_five_photos_20261026/`; cập nhật addon và restart. Chrome kiểm năm ảnh/nhãn đầy đủ, không tràn ngang, không giao nhau giữa ảnh/ghi chú tại 320/375/640/680/681/768/1024/1101/1250/1440/1920px; giữ đủ ba homepage marker. Ảnh ở ignored `runtime/tuhoso-five-photos-20261026/`. Hero TA.CARE với title mới đạt kiểm tra full-bleed/CTA ở mười kích thước. Chỉ giao diện local; không thêm hồ sơ hay sửa dữ liệu/matching/quyền, không commit/push/deploy.

Tinh chỉnh tiếp theo yêu cầu: ảnh dọn dẹp ngoài cùng trái nghiêng +6° ở desktop, đối hướng ảnh thiết kế −5°; giữ góc nhỏ đối hướng hiện có ở tablet/mobile. Khung hai lựa chọn trên ảnh TA.CARE bo 20px, cắt nền hover theo đường bo và đặt focus vào trong để không bị cắt. Chrome kiểm 375/1440px đạt góc đối hướng, bo tròn/hover/focus và không tràn ngang. Chỉ CSS local.
