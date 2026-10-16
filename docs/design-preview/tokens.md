# TA.CARE — token màu cho ba bản xem trước

**Phạm vi:** ba HTML tĩnh trong thư mục này. Chưa nạp `assets.css` vào Odoo và chưa thay đổi giao diện thật. Dữ liệu trên các trang đều là dữ liệu mô phỏng.

## Nguồn logo và cách lấy màu

`views/live.xml` hiện tải ảnh theo `tacare_website/static/src/img/%s.png`. Đây là các file được dùng cho token và được liên kết trực tiếp trong HTML, giữ nguyên tỉ lệ ảnh:

| Website | File logo đang dùng | Kích thước gốc | Nhận diện thấy trong ảnh |
| --- | --- | --- | --- |
| Kho Việc Làm | `source/apps/tacare/addons/tacare_website/static/src/img/khovieclam.png` | 470 × 436 | Xanh lá, vàng; khối giống ngăn hồ sơ, người, mũi tên và sao; chữ “Kho việc làm”. |
| Tủ Hồ Sơ | `source/apps/tacare/addons/tacare_website/static/src/img/tuhoso.png` | 1118 × 1150 | Xanh lá, vàng; nét cong, chiếc lá, mũi tên, sao; chữ “TỦ HỒ SƠ”. |
| TA.CARE | `source/apps/tacare/addons/tacare_website/static/src/img/tacare.png` | 1090 × 751 | Xanh dương, xanh lá; hai hình người, nhịp nối giữa biểu tượng hồ sơ và cặp công việc; chữ “TA.CARE” có chấm đỏ. |

Thư mục local `TA.CARE project/logo/` cũng có ba file cùng tên. SHA-256 của từng cặp **trùng nhau**, vì vậy không có bản logo khác cần chọn. Màu gốc dưới đây là **giá trị RGB đúng của pixel ảnh**: đã giải mã PNG RGBA 8-bit, bỏ pixel alpha dưới 245 và lấy màu lặp nhiều trong vùng màu liên quan. Logo có chuyển sắc nên đây là các màu đại diện được *lấy mẫu*, không phải mã thương hiệu do nhà thiết kế công bố. Màu hover/nền/viền được **suy ra từ màu mẫu** và gắn nhãn riêng; không trình bày chúng như pixel gốc.

## Token thương hiệu

| Site | Token | Mã màu | Nguồn và cách dùng |
| --- | --- | --- | --- |
| Kho | `--primary`, `--primary-ink` | `#35764A` | Pixel xanh lá của logo; nút chính, liên kết, mục chọn. |
| Kho | `--primary-hover` | `#245A36` | Biến thể đậm suy ra; hover. |
| Kho | `--primary-soft`, `--primary-border` | `#EAF3EC`, `#B9D8C2` | Biến thể nhạt suy ra; nền/vùng chọn và viền. |
| Kho | `--accent` | `#F4AA22` | Pixel vàng cam của logo; điểm nhấn nhỏ. |
| Kho | `--accent-soft`, `--accent-border`, `--accent-ink` | `#FFF5DB`, `#EFD18C`, `#183028` | Nền/viền nhạt suy ra; chữ đậm trên nền vàng. |
| Tủ | `--primary`, `--primary-ink` | `#155E38` | Pixel xanh lá trong chữ của logo; nút, liên kết, mục chọn. |
| Tủ | `--primary-hover` | `#10472A` | Biến thể đậm suy ra. |
| Tủ | `--primary-soft`, `--primary-border` | `#EAF5ED`, `#B8D9C1` | Biến thể nhạt suy ra. |
| Tủ | `--accent` | `#F4C948` | Pixel vàng trong hình logo; nhãn/điểm nhấn nhỏ. |
| Tủ | `--accent-soft`, `--accent-border`, `--accent-ink` | `#FFF8DF`, `#EBD58A`, `#183028` | Biến thể nhạt suy ra; chữ đậm trên nền vàng. |
| TA.CARE | `--primary` | `#3A70D1` | Pixel xanh dương của logo; nền nút chính. |
| TA.CARE | `--primary-hover`, `--primary-ink` | `#1355C0` | Pixel xanh dương đậm khác trong logo; hover và chữ trên nền sáng. |
| TA.CARE | `--primary-soft`, `--primary-border` | `#EDF3FF`, `#BAD0F5` | Biến thể nhạt suy ra. |
| TA.CARE | `--accent` | `#06AD4C` | Pixel xanh lá sáng của logo; chỉ dùng làm điểm nhấn nhỏ, không đặt chữ trắng lên màu này. |
| TA.CARE | `--accent-ink`, `--accent-soft`, `--accent-border` | `#086B36`, `#E9F8EF`, `#B9E4C8` | Biến thể đậm/nhạt suy ra để nhãn xanh lá vẫn đọc được. |

Chấm đỏ trong logo TA.CARE được giữ nguyên trong **ảnh logo**; nó không trở thành màu trạng thái lỗi hoặc màu hành động của giao diện.

## Nền và trạng thái dùng chung

Các màu trung tính không giả là màu lấy từ logo. Chúng tạo nền sáng cho form dài và dùng chung ở ba trang: `--canvas #F7F8F5`, `--surface #FFFFFF`, `--ink #183028`, `--muted #526159`, `--line #D7E2DB`. Trường nhập có viền `#81988B`, placeholder `#607268`, focus `#8C5600`. Khoảng cách dùng thang 4/8/12/16/20/24/32/40/48 px; form, nút, thẻ, chip và nhãn trạng thái dùng cùng cấu trúc CSS, đổi màu qua class `site-kvl`, `site-tu`, `site-ta`.

| Trạng thái nghiệp vụ | Nền | Chữ và dấu chấm | Ngữ cảnh |
| --- | --- | --- | --- |
| Nháp | `#EEF1F4` | `#44515F` | Tin tuyển dụng |
| Đang hiển thị | `#E5F4EA` | `#155E38` | Tin tuyển dụng |
| Tạm ngừng | `#FFF2D6` | `#7A4A00` | Tin tuyển dụng |
| Đã đóng | `#ECEDEF` | `#40464D` | Tin tuyển dụng |
| Chờ phản hồi | `#E8EEFF` | `#244B8F` | Đề nghị/lời mời |
| Chấp nhận | `#E5F4EA` | `#155E38` | Đề nghị/lời mời |
| Từ chối | `#FCE9E5` | `#923F31` | Đề nghị/lời mời |
| Đã hủy | `#ECEDEF` | `#40464D` | Đề nghị/lời mời |

Minh chứng có **nhãn riêng** “Tự khai”, “Có file”, “Đã xác minh” và chỉ tái sử dụng các *cặp màu* trung tính/xanh dương/xanh lá trên. Màu không thay cho nội dung nhãn. “Đã xác minh” trong trang mẫu là tình huống giả, không phải một bản ghi đã được Odoo xác minh.

## Kiểm tra tương phản

Đo theo công thức WCAG `(L_sáng + 0,05) / (L_tối + 0,05)` với sRGB tuyến tính hóa. Ngưỡng dùng cho chữ thường: **AA ≥ 4,5:1**; viền điều khiển/focus: **≥ 3:1**. Các số được làm tròn hai chữ số thập phân.

| Cặp sử dụng | Kho | Tủ | TA.CARE | Kết quả |
| --- | ---: | ---: | ---: | --- |
| Chữ trắng / nút primary | 5,47 | 7,81 | 4,75 | AA đạt |
| Chữ trắng / nút hover | 8,11 | 10,73 | 6,80 | AA đạt |
| Chữ `primary-ink` / nền trắng | 5,47 | 7,81 | 6,80 | AA đạt |
| Chữ `primary-ink` / `primary-soft` | 4,82 | 6,98 | 6,11 | AA đạt |
| Chữ hover / `primary-soft` | 7,15 | 9,60 | 6,11 | AA đạt |
| Chữ phụ `#526159` / `primary-soft` | 5,77 | 5,85 | 5,87 | AA đạt |
| Chữ `accent-ink` / `accent-soft` | 12,96 | 13,23 | 6,04 | AA đạt |
| Chữ chính `#183028` / `primary-soft` | 12,42 | 12,59 | 12,64 | AA đạt |

| Cặp trung tính hoặc trạng thái | Tỉ lệ | Kết quả |
| --- | ---: | --- |
| Chữ chính / nền trang; chữ chính / bề mặt trắng | 13,20; 14,07 | AA đạt |
| Chữ phụ / nền trang; chữ phụ / bề mặt trắng | 6,13; 6,54 | AA đạt |
| Placeholder / trắng; viền trường nhập / trắng | 5,12; 3,09 | Chữ AA đạt; viền điều khiển đạt 3:1 |
| Viền focus `#8C5600` / trắng | 6,09 | Focus đạt 3:1 |
| Nháp; Đang hiển thị/Chấp nhận; Tạm ngừng; Đã đóng/Đã hủy | 7,16; 6,86; 6,74; 8,14 | AA đạt |
| Chờ phản hồi; Từ chối | 7,31; 6,02 | AA đạt |
| Chữ xanh lá TA.CARE `#086B36` / nền xanh dương nhạt | 5,96 | AA đạt |

**Cặp cố ý không dùng cho chữ:** `#06AD4C`/trắng chỉ **2,96:1**. `#3A70D1`/nền trang chỉ **4,46:1**, nên chữ liên kết/nhãn TA.CARE dùng `--primary-ink #1355C0`; `#3A70D1` chỉ làm nền nút với chữ trắng 4,75:1. Các mảng màu nhạt và viền trang trí không được dùng một mình để truyền đạt trạng thái.

## Typography và khả năng đưa vào repo sau khi duyệt

Odoo core trong workspace có Bootstrap **5.3.3**. Addon hiện đóng `website.scss`, `live.scss`, `live_polish.scss`, `kvl.scss` và JS vào `web.assets_frontend`; preview **không dùng CDN, không cài font hoặc dependency**. `assets.css` dùng CSS custom properties thuần, có thể ánh xạ sang SCSS/Bootstrap tokens trong giai đoạn triển khai nếu được duyệt. Không sửa SCSS thật ở giai đoạn này.

Font xem trước là `system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif`, tránh phụ thuộc vào font thương mại của các style tham khảo. Cần kiểm tra trực tiếp trên thiết bị người dùng cho chuỗi: **“Chuyên viên Chăm sóc khách hàng — Thương mại điện tử”**; đặc biệt các dấu ơ, ư, ệ, ố và dấu gạch dài. Không sử dụng serif trang trí cho nhãn/form. Focus hiện rõ, có liên kết bỏ qua điều hướng, nhãn form hiển thị, trạng thái có chữ, và tắt chuyển động khi người dùng chọn giảm chuyển động.

## Cách xem

Mở `kho-viec-lam.html`, `tu-ho-so.html`, `ta-care.html` ngay trong thư mục này. Đường dẫn logo tương đối trỏ tới file thật trong addon; giữ nguyên vị trí thư mục để ảnh hiển thị. Nút tìm kiếm, lọc, lưu và đăng là nút minh họa, không truy vấn hay thay đổi database.
