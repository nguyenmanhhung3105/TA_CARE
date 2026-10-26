# Tinh chỉnh Kho, thiết kế lại Tủ/TA.CARE và hàng đối chiếu — 26/10/2026

> **Bản thiết kế này đã bị chủ dự án từ chối.** Hướng được chọn và triển khai thay thế: [mẫu 1 cho Tủ, mẫu 2 cho TA.CARE](selected_homepages_2026-10-26.md). Phần căn hàng matching vẫn được giữ.

Yêu cầu chủ dự án: sửa vị trí figure và nhãn chăm cây của Kho; tham khảo Minimal Gallery/21st.dev để làm mới Tủ Hồ Sơ và TA.CARE; căn các phần tử trong thẻ đối chiếu; ghi nhớ geohash/map cho giai đoạn sau.

## Tham khảo và lựa chọn

Đã duyệt [Minimal Gallery](https://minimal.gallery/), mẫu [Isaac Fayemi](https://minimal.gallery/isaac-fayemi/) và [Causal](https://minimal.gallery/causal/), xem trực quan website nguồn [Fayemi](https://fayemi.design/), [Causal](https://causal.so/) và thư viện [21st.dev Grid](https://21st.dev/community/components/s/grid), cùng nhóm [Hero](https://21st.dev/community/components/s/hero). Ảnh tham khảo trong ignored `runtime/design-reference-20261026/`.

- **Tủ Hồ Sơ:** bố cục portfolio biên tập, tên nội dung lớn, chữ serif nghiêng làm điểm nhấn, ảnh bất đối xứng và mục lục ba phần. Nội dung là tổng quan sản phẩm, không dựng hồ sơ cá nhân hoặc số liệu thành tích. Giữ navy/xanh xám; dùng ảnh dạy kèm, đóng gói và nông nghiệp từ bộ ảnh có nguồn, khác bộ năm ảnh Kho. Phần nội dung đi theo từng chương và danh mục nghề; thư viện riêng vẫn giữ route/owner/admin và không có gallery trang trí.
- **TA.CARE:** khối petrol đậm với tiêu đề lớn, hai phía cần người/nhận làm có ảnh, hành động riêng và câu hỏi mở bằng `details/summary`. Minh họa đầu trang có caption rõ ràng; matching thật tiếp tục nằm riêng ở `#home-suggestions`, theo account và consent. Không đặt minh họa thành cặp matching hoặc hiển thị người riêng tư cho khách.
- Các mẫu chỉ cung cấp hướng phân cấp chữ, khoảng trống, bố cục và cách giới thiệu sản phẩm. Triển khai riêng bằng QWeb/SCSS, giữ stack Odoo, logo và Phosphor hiện có; không nhập source React hoặc ảnh từ mẫu. Header/shell vẫn theo gutter 48/24/20px và marker triển khai ba website.

## Kho và thẻ đối chiếu

`home_arc.scss` đặt garden `left:19%`, digital `right:19%`, cùng `top:100px` trên desktop, giữ vòng cung và giảm chiều cao khung/khoảng cách để title lên gần ảnh. Chăm cây dùng góc bo đều 22px, nhãn nằm trong khung với inset 10px để không bị cắt ở góc lớn. Mobile tiếp tục có ba ảnh và chữ đủ bề ngang.

`pair_alignment.scss` dùng [CSS subgrid](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Grid_layout/Subgrid) cho kích thước hàng chia sẻ: ảnh, tên, tiêu đề, khu vực, lịch, tiền công; đồng bộ cả hai cặp cùng một hàng, badge, nút và chiều cao khung. Lịch/tiêu đề dài được xuống dòng đầy đủ, không dùng clamp để che chênh lệch. Chi tiết cặp cũng đối chiếu hai bên theo cùng hàng; mobile chuyển các panel thành cột dọc. Rule nằm trong `@supports`, giữ style nền cho trình duyệt cũ chưa hỗ trợ. Hai preview công khai Kho cũng có chiều cao/action đồng đều.

Các template kế thừa mới là `sites/tuhoso/views/editorial_home.xml` và `sites/tacare/views/connection_home.xml`; CSS theo từng sản phẩm trong `static/src/{tuhoso,tacare}/scss/`. Không sửa controller/model, data, ranking, consent hoặc quyền.

## Phần để sau

Đã ghi [geohash và ghép nối theo bán kính](../roadmap/geohash_nearby_matching.md), kèm nguồn Mapcn React Native và nguyên lý truy vấn geo. Chưa tích hợp map/GPS/geohash hoặc gọi dịch vụ bản đồ.

## Kiểm chứng

Backup DB local trong ignored `backups/visual_refresh_20261026/`, xác minh danh mục dump rồi nâng addon `tacare_website`. Không commit/push/deploy hoặc thao tác production.

Kết quả kiểm cuối:

- XML/manifest parse, ảnh/icon đều tồn tại; security scanner 337 text files và diff whitespace đạt. Không thêm dependency vào repository.
- Chrome kiểm ba homepage tại 320/375/640/767/768/1024/1440/1920px: HTTP/marker, một h1, ảnh tải, không tràn ngang, đúng 19%/100px và góc chăm cây. Hai thanh trên cùng khớp giữa ba website tại 375/1440px. Root Tủ vẫn tổng quan, khách không có dữ liệu hồ sơ riêng.
- Nút mới đạt tương phản tối thiểu 4.5:1 ở trạng thái thường/hover. Đã xem ảnh desktop/mobile; native details mở/đóng bằng chuột và phím Space, mục lục Tủ đến đúng chương. Reduced-motion giữ bố cục; hai khung chọn hướng TA.CARE có hàng mô tả cùng y tại 768/1024/1440px.
- Account hiện có xem các cặp thật: các hàng ảnh/tên/tiêu đề/khu vực/lịch/tiền công căn đúng trong bốn cột của hai cặp, badge/nút cùng y, khung cùng chiều cao. Hai thẻ đầu tại 1440px cùng cao 761.06px. Tăng độ dài title/lịch tạm trong DOM vẫn căn hàng, không ghi DB. Kiểm list tại bảy độ rộng, chi tiết tại bốn độ rộng; khách vào URL cặp vẫn phải đăng nhập và không có bảng riêng.
- Ảnh/số đo trong ignored `runtime/visual-refresh-20261026/`, gồm `pair-alignment.json`, `shared-header-metrics.json`, homepage và chi tiết. Script Chrome tạm không tạo user/contact/profile/consent/connection. Không thêm fixture mật khẩu vào source.

Không chạy lại schema/write-flow tests vì thay đổi chỉ là template/CSS và tài liệu; không thay thuật toán, quyền hoặc dữ liệu nghiệp vụ.
