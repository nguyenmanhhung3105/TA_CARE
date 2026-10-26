# Everyday services — Kho Việc Làm / Tủ Hồ Sơ

Quyết định ngày 22/10/2026, theo [nghiên cứu tham chiếu](../research/service_design_references_2026-10-22.md). Đây là hướng được chọn sau khi so sánh, không sao chép giao diện một thương hiệu.

- Nền chính: trắng ấm `#fbfaf6`; surface trắng; chữ `#21372b`; chữ phụ `#526257`.
- Hành động: xanh đậm `#173f31`, chữ trắng; điểm nhấn lime `#d8edaa`, chữ xanh đậm.
- Nghề: mint, vàng bơ, hồng phấn, tím nhạt, xanh trời. Màu nền hỗ trợ icon/nhãn, không mang thông tin một mình.
- Be Vietnam Pro tự host; heading 700, body 400, nhãn 500/600; body 16px/1.65; H1 72px desktop, 40px mobile; H2 40/30px. Không uppercase đoạn văn dài.
- Lưới max 1280px, lề 24–64px desktop / 20px mobile; spacing 8/16/24/32/48/80. Nút tối thiểu 44px, pill; card 20px, ảnh 20–32px; hạn chế đổ bóng.
- Icon Phosphor duotone 24/32/40px. `broom` dọn nhà, `cooking-pot` nấu ăn, `plant` chăm cây, `carrot` nông nghiệp, `package` kho/bốc xếp, `hammer` sửa/lắp, `book-open` dạy kèm, `paint-brush` việc số, `paw-print` thú cưng. Nhãn cạnh icon; SVG trang trí có `aria-hidden`.
- Ảnh: đời thường, đang thực hiện, cắt vừa công việc, không ảnh chân dung giả của hồ sơ. Nguồn và giấy phép lưu cùng asset; responsive width/height, lazy bên dưới fold.
- Chuyển động: phản hồi ngắn ở nút/tab, gallery có điều khiển và mặc định tạm dừng; dừng khi focus và theo reduced-motion. Không parallax, marquee hay hiệu ứng liên tục che nội dung.
- Kho: hero giữa + photo ribbon; danh mục icon; ba tình huống; nhu cầu thực; lời mời đăng nhu cầu/nhận việc.
- Tủ guest: tiêu đề nhận làm + ảnh nghề; chọn khả năng; cách chuẩn bị giới thiệu; quyền riêng tư. Tủ đăng nhập: gallery gọn trước tủ; phạm vi mine/all đúng quyền; dịch vụ cụ thể và thao tác chủ hồ sơ.
- Mọi CTA đi tới route thật. Giữ CSRF, native login, explicit profile_id, trạng thái, owner/admin/organization và consent; không thêm nút booking/payment giả.

Skill `ui-ux-pro-max` được dùng để rà quy tắc tiếp cận và tương tác. Gợi ý mặc định của dataset thiên về ứng dụng doanh nghiệp nên không dùng làm layout; hướng thị giác được chọn từ yêu cầu và tham chiếu thực tế.


## TA.CARE và rà soát bố cục tối 22/10/2026

TA.CARE có brand plum `#514080`, nền lavender `#faf8fd`, chữ `#2d2542`, surface nhạt `#eee8f7` và điểm nhấn peach. Chỉ scope `.tc-hub`; Kho/Tủ giữ tông và bố cục home đã duyệt. Cả ba dùng shell/main/header cùng max 1280px, lề desktop 48px, màn hình vừa 24px và mobile 20px. Nhãn bộ lọc 16px/650. Header có tên người đăng nhập. Danh sách của chủ tin dùng grid kết quả toàn hàng khi không có sidebar. Gợi ý homepage là dữ liệu có consent hiện hành; ảnh đại diện công việc, không giả chân dung. Ba ví dụ hư cấu có thẻ ảnh trên home và trang đối chiếu từng phía. Xem [ghi chú](../research/hub_review_2026-10-22.md).


### Điều chỉnh chiều ngang 23/10/2026

Chủ dự án làm rõ rằng Kho cần trải rộng theo màn hình như Tủ và TA.CARE. Bỏ giới hạn max 1280px ở lớp CSS cuối: `--sx-content-width:none`. Shell, header và nội dung co giãn theo viewport, giữ lề desktop 48px / màn hình vừa 24px / mobile 20px. Nội dung và cấu trúc home không đổi.


### Header hai hàng — 23/10/2026

Theo yêu cầu làm rõ cuối cùng: khách chưa đăng nhập thấy ba nút Cách hoạt động, Đăng nhập và Đăng nhu cầu/Tạo hồ sơ nằm bên phải, căn giữa theo chiều dọc giữa hàng thương hiệu và hàng navbar trên desktop. Khi đăng nhập, tên người dùng và Đăng xuất ở hàng trên; Cách hoạt động và CTA ở hàng dưới cùng navbar. Màn hình nhỏ cho phép xuống dòng để không chồng lấn. Giữ màu tab hiện tại, host đích và native auth/logout.


### Thử bảng màu mới — 23/10/2026

Theo yêu cầu của chủ dự án, màu logo không còn là ràng buộc chọn palette. Đây là bản thử đầu tiên (Kho/Tủ đã được thay ở quyết định sau bên dưới), thay bảng xanh lá/plum ở các mục lịch sử phía trên; bố cục, typography, navbar theo trạng thái đăng nhập và ảnh giữ nguyên.

| Website | Màu hành động | Điểm nhấn | Nền | Chữ |
| --- | --- | --- | --- | --- |
| Kho Việc Làm | Cobalt `#284bc1` | Cam mơ / cam đất `#b4472b` | `#f6f8ff` | `#202b45` |
| Tủ Hồ Sơ | Đất nung `#9d402c` | Xanh sage đậm `#386359` | `#fff9f5` | `#392d2a` |
| TA.CARE | Petrol `#116879` | Cam ấm `#964323` | `#f4fafb` | `#18373e` |

Kho có sắc xanh rõ cho hành động; Tủ có nền kem ấm để nâng ảnh công việc và nội dung cá nhân; TA.CARE dùng xanh băng/petrol cho cảm giác kết nối. Ba website cùng quy tắc nền sáng, surface trắng, chữ đậm, soft surface theo màu sản phẩm. Không dùng ba màu chính để thay thế trạng thái thành công/cảnh báo/lỗi.

`service_palette.scss` là asset cuối, chứa token theo website và cầu nối `--tc-*` cho form/dialog cũ. Các component ở service/interior/hub review dùng semantic token thay màu xanh/plum cố định. Bộ ảnh, logo gốc, nội dung và bố cục không đổi. Để tinh chỉnh bản thử, đổi token ở file palette; không sửa màu rải rác trong component.

Skill `ui-ux-pro-max` được tham khảo cho hệ màu và tiếp cận. Dataset gợi ý local-service xanh/orange; palette thực tế được điều chỉnh theo yêu cầu đổi màu và đo trực tiếp trên CSS đã render. Trên nền chính, chữ chính tương phản 12.03–13.26:1, chữ phụ 5.48–6.10:1, chữ trắng trên nút 6.40–7.33:1. Ảnh xem trước trong `docs/screenshots/palette-trial-20261023/`.


### Chọn lại màu Kho/Tủ — 23/10/2026

Chủ dự án chấp nhận màu TA.CARE, yêu cầu Kho/Tủ đổi lại. Bản hiện tại đưa Kho và Tủ về tông xanh đậm `#173f31`, nền kem `#fbfaf6`, chữ `#21372b`, chữ phụ `#526257`, các surface xanh nhạt/vàng bơ như trước bản thử. Kho nhấn xanh lá `#496f3b`; Tủ nhấn olive `#6d6d3a`. TA.CARE giữ nguyên toàn bộ token petrol/ice ở bảng trên. Chỉ sửa hai block palette theo website; không thay bố cục.


### Xanh đậm hơn cho Kho/Tủ — 23/10/2026

Theo yêu cầu tiếp theo, Kho và Tủ dùng forest green sâu `#0b2e24` (trước đó `#173f31`), hover `#061f18`, chữ chính `#162b21`, nhấn heading xanh `#24513b` và viền control `#70846f`. Giữ nền kem/surface sáng để chữ và ảnh vẫn dễ đọc. Màu TA.CARE giữ nguyên. Chỉ chỉnh token palette, không thay bố cục hoặc dữ liệu.


### Diễn đạt tiền công theo công việc — 23/10/2026

Bỏ nhãn hiển thị “trọn việc”: selection `task` có nhãn “Công việc”; formatter dùng “900.000đ / công việc”, giữ phần “mỗi người”/“cả nhóm” nếu được khai. Giá dạng khoảng và đơn vị giờ/ca/buổi/ngày/sản phẩm/chuyến giữ cách tính cũ; mã dữ liệu `task` không đổi. Trang chi tiết Kho/Tủ và chi tiết việc trong hub giải thích mức tiền cho toàn bộ phạm vi đã mô tả, cần chốt đầu việc và phát sinh. Phần hồ sơ nhận làm được chia sẻ trong hub dùng cùng template giải thích. Form Kho/Tủ có hướng dẫn liên kết bằng `aria-describedby`, yêu cầu làm rõ số lượng, kết quả và khoản đã bao gồm. Đây là thay đổi ngôn ngữ giao diện, không chuyển đổi đơn vị hoặc số tiền của dữ liệu hiện có.


### Tủ Hồ Sơ: tổng quan và không gian riêng — 23/10/2026

Theo yêu cầu mới, homepage Tủ là phần tổng quan chung cho cả khách và người đã đăng nhập: mục đích, các chức năng hồ sơ/việc nhận làm/kết nối, nhóm nghề và quyền riêng tư. Không có sidebar quản lý hoặc dữ liệu hồ sơ riêng trên home. CTA “Mở hồ sơ của tôi” đưa đến `/tuhoso/profiles?scope=mine`; đăng nhập không tự chuyển root thành thư viện. Gallery có ảnh minh họa nghề chỉ nằm ở homepage, mặc định dừng.

Thư viện riêng dùng sidebar phạm vi và các ngăn hồ sơ ngang: bìa ảnh nghề bên trái, giới thiệu và thao tác bên phải. Theo yêu cầu bỏ khối ảnh trượt trong “Hồ sơ của tôi”, workspace không còn carousel. Giữ tìm kiếm, các nút tạo/mở/sửa/xóa theo quyền, profile_id rõ ràng, owner mine/admin all và quyền chia sẻ hiện có. Tông xanh sâu/kem được giữ. Mobile chuyển sidebar thành hàng điều hướng và ngăn hồ sơ xếp dọc. CSS riêng ở `static/src/tuhoso/scss/portfolio.scss`; xem nghiên cứu và quyết định cuối trong `docs/research/tuhoso_portfolio_refresh_2026-10-23.md`.


### Hàng nhóm nghề Tủ Hồ Sơ — 23/10/2026

Sửa lỗi flex tự xuống dòng khiến Nông nghiệp đứng lẻ: `.to-categories .sx-category-grid` dùng 9 cột bằng nhau trên desktop, thẻ cùng chiều cao và icon/nhãn căn đồng nhất. Từ 1100px trở xuống dùng một hàng cuộn ngang với mỗi cột 148px; không ép 9 thẻ nhỏ khó đọc. Giữ đủ 9 link tạo hồ sơ có tên gợi ý và ảnh/icon hiện có. Chỉ CSS Tủ; không thay markup, chức năng hoặc dữ liệu.

Scroller có đệm focus và tự căn ô được chọn bằng bàn phím vào vùng nhìn thấy, scope riêng cho danh mục Tủ; không tự đổi tab hoặc chuyển trang.


### Phân biệt thương hiệu bằng màu — 23/10/2026

Chủ dự án nhận xét Kho và Tủ đang quá giống vì cùng xanh lá đậm. Bản hiện tại chỉ đổi block palette Tủ: navy `#24385a`, hover `#18283f`, nền xanh xám sáng `#f5f7fc`, chữ `#1f2c43`, nhấn slate blue `#445d86`, soft surface `#e7edf7` và điểm nhấn nhạt `#d6e1f4`. Kho giữ forest green `#0b2e24` / kem, TA.CARE giữ petrol `#116879` / xanh băng. Cầu nối token áp dụng màu này cho header, nút/tab, sidebar thư viện và form; không đổi bố cục, logo hoặc dữ liệu. Màu trạng thái giữ ý nghĩa hiện có.

### Tiêu đề và thứ tự ảnh Kho — 24/10/2026

Chủ dự án chốt “Từ việc bạn cần, đến người phù hợp.” cho Kho Việc Làm và yêu cầu thử đưa dải ảnh hiện có lên đầu phần nội dung, ngay dưới điều hướng. `sites/khovieclam/views/service_design.xml` chuyển nguyên dải ảnh lên trước kicker/tiêu đề, mô tả và tìm kiếm; không nhân bản ảnh. Giữ năm ảnh trên desktop, ba ảnh ở mobile theo responsive hiện có. `service_design.scss` chỉnh khoảng cách riêng khối giới thiệu Kho; tiêu đề mobile dùng clamp 28–38px để câu vừa hai dòng tại 320/375px. Không đổi TA.CARE/Tủ, màu, gutter, header hoặc matching.

Đã backup DB local, cập nhật addon và kiểm Chrome tại 320/375/640/768/1440/1920px: đúng tiêu đề/thứ tự, ảnh tải, không tràn ngang, hai matching giới thiệu còn nguyên, tìm kiếm công khai giữ từ khóa và không yêu cầu đăng nhập. Ảnh xem thử ở ignored `runtime/kho-hero-review/`. XML parse, security scanner và diff whitespace đạt. Chỉ triển khai local, chưa commit/push/deploy.

Điều chỉnh tiếp cùng ngày: tăng khoảng cách sau dải ảnh từ 32 lên 64px ở desktop, từ 24 lên 40px ở mobile. Hai ảnh ngoài cùng (sửa chữa/chăm thú cưng) cao 250px, bo vòm đối xứng ở hai góc trên bằng radius phần trăm; giữ nhãn nghề và ảnh hiện có. Chrome kiểm sáu kích thước, hình vòm desktop, khoảng cách responsive, tiêu đề mobile hai dòng, không tràn ngang và tìm kiếm công khai đạt. Ảnh ở ignored `runtime/kho-arch-review/`. Chỉ CSS local, không cập nhật dữ liệu hoặc deploy.

### Đính chính vòng cung quanh tiêu đề Kho — 24/10/2026

Chủ dự án làm rõ: toàn bộ ảnh cần xếp như cầu vồng quanh tiêu đề, thay vì chỉ bo hai ảnh thành vòm. `static/src/khovieclam/scss/home_arc.scss` là lớp CSS riêng Kho: ảnh nấu ăn cao nhất ở giữa, ảnh làm vườn/thiết kế hạ xuống hai phía, sửa chữa/thú cưng nằm thấp hai bên phần chữ. Giữ ảnh, caption và khôi phục hình khung trước thử bo vòm. Tiêu đề nằm giữa khoảng trống bên trong cung; mô tả/tìm kiếm tiếp tục bên dưới. Dưới 768px ba ảnh tạo cung nhỏ phía trên, phần chữ dùng toàn chiều rộng. Không đổi header/gutter hoặc nội dung TA.CARE/Tủ.

Sau backup DB đã kiểm danh mục dump và cập nhật addon để đăng ký asset mới, Chrome kiểm 320/375/640/641/767/768/1024/1440/1920px: đúng thứ tự độ cao, hai ảnh giữa đối xứng, ảnh ngoài không đè khung tiêu đề, không tràn ngang, title mobile hai dòng, ảnh tải được và tìm kiếm công khai giữ từ khóa. Hai marketing matching vẫn hiển thị đúng. Ảnh xem thử ở ignored `runtime/kho-rainbow-review/`. Manifest parse, security scanner và diff whitespace đạt. Không sửa dữ liệu hoặc deploy production.

### Biên tập Tủ, kết nối TA.CARE và các hàng đối chiếu — 26/10/2026

Hướng mới theo yêu cầu tham khảo Minimal Gallery/21st.dev: Tủ dùng portfolio biên tập với chữ lớn, serif nghiêng, bento ảnh và chương nội dung; TA.CARE dùng khối hai phía kết nối có ảnh, native details và matching thật bên dưới. Giữ navy của Tủ, petrol của TA.CARE cùng shell/header fluid. Kho sửa hai ảnh giữa về 19%/100px, đưa title lên và bo đều khung chăm cây để nhãn không bị cắt. CSS subgrid đồng bộ các hàng trong cặp và giữa hai cặp cùng hàng, giữ lịch dài đầy đủ. Chi tiết/kiểm chứng tại [báo cáo triển khai](../research/visual_refresh_2026-10-26.md). Geohash/map chỉ ghi lộ trình, chưa tích hợp.

### Lựa chọn cuối từ ba mẫu — 26/10/2026

Chủ dự án từ chối bản editorial/navy và petrol-stage. Hướng hiện tại là **mẫu 1 cho Tủ Hồ Sơ** (giấy kem/cam, ảnh ghim, tiêu đề và tên việc rõ nghĩa) và **mẫu 2 cho TA.CARE** (ảnh lớn, nền trắng/đen, điểm vàng). Tủ brand #b94630/nền #fff9ef, TA.CARE brand #252525/nền #fff. Kho, logo, trạng thái ngữ nghĩa và kích thước shell/header giữ nguyên. CSS cuối `pinboard_home.scss` / `cinematic_home.scss`; giữ `pair_alignment.scss`. Xem [triển khai hai mẫu được chọn](../research/selected_homepages_2026-10-26.md).

Tinh chỉnh được chủ dự án yêu cầu tiếp: riêng hero TA.CARE tràn chiều ngang màn hình, hai lối vào hòa trên ảnh bằng nền tối trong suốt và chữ trắng. Bốn ảnh nghề có nguồn sẵn tự đổi mỗi 6,5 giây, fade 850ms; chữ/nút đứng yên, có trước/sau và pause/resume. Giảm chuyển động tắt autoplay/fade. Ngoại lệ tự chuyển ảnh này thay quy tắc TA.CARE không có carousel trước đây; không áp dụng cho matching hoặc đổi gutter phần còn lại.
