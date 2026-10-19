# Demo tuyển dụng và việc linh hoạt trên Odoo local

> **Đã có bản tiếp ngày 20/10:** [giao diện mới và nhiều hồ sơ/một ứng viên](implementation_profile_refresh_2026-10-20.md). Số hồ sơ, cấu trúc Tủ và phạm vi carousel trong tài liệu này mô tả demo trước đợt chỉnh tiếp.

Triển khai bắt đầu ngày **19/10/2026**, hoàn tất kiểm tra sau khi sang **20/10/2026**. Chủ dự án đã cho phép can thiệp code để xem demo, thay cho phạm vi nghiên cứu thuần túy trước đó. Đây là trạng thái local, không phải xác nhận đã đưa lên production hoặc đã hoàn thiện nghiệp vụ vận hành.

## Mở demo

| Màn hình | Đường dẫn local |
| --- | --- |
| Trang chủ Kho, carousel và hai hướng công việc | http://khovieclam.localhost:8069/ |
| Tất cả công việc | http://khovieclam.localhost:8069/kvl/jobs |
| Năm tin tuyển dụng | http://khovieclam.localhost:8069/kvl/jobs?kind=recruitment |
| Mười lăm việc linh hoạt | http://khovieclam.localhost:8069/kvl/jobs?kind=flexible |
| Cá nhân đăng nhu cầu cần người | http://khovieclam.localhost:8069/kvl/flexible/new |
| Quản lý việc đã đăng | http://khovieclam.localhost:8069/kvl/flexible/mine |
| Tủ hồ sơ của tôi; admin xem tất cả | http://tuhoso.localhost:8069/tuhoso/profiles |
| Các công việc tôi nhận | http://tuhoso.localhost:8069/tuhoso/profiles?kind=flexible |
| Thêm công việc nhận làm | http://tuhoso.localhost:8069/tuhoso/work/new |
| Trang chủ TA.CARE | http://tacare.localhost:8069/ |

Tủ và các form yêu cầu đăng nhập. Tài khoản candidate/business đã được cấp vai trò có thể đăng nhập cả ba website. Cookie vẫn riêng từng domain; dùng cùng tài khoản nhưng có thể cần đăng nhập lại khi đổi website.

Tài khoản demo được sinh mật khẩu ngẫu nhiên, lưu tại **`backups/demo_flexible_20261019/accounts.json`**, quyền file 0600 và được git bỏ qua. Không gửi file này lên ChatGPT web, không commit. Trong file: số `00` là bên tuyển dụng demo; `01`–`05` có hồ sơ tuyển dụng; `06`–`15` có mục nhận việc linh hoạt; `99` là admin demo. Chín tài khoản gốc giữ nguyên login, mật khẩu, active và role.

## Những gì đã triển khai

- Hai lựa chọn **Tuyển dụng / Việc linh hoạt**. “Việc linh hoạt” bao quát việc theo giờ, ca, đầu việc, sản phẩm hoặc chuyến, tránh giới hạn tất cả thành hợp đồng part time.
- Kho mặc định hiển thị toàn bộ tin công khai của hai nhánh. Có lối đăng nhu cầu cá nhân và lối đăng tin tuyển dụng tổ chức riêng.
- Tủ là không gian cá nhân: người thường chỉ thấy hồ sơ và các mục nhận việc của chính mình; admin xem tất cả. URL chi tiết cũ cũng kiểm tra chủ sở hữu. Quyền xem ứng viên trên Kho vẫn dùng các route và consent riêng.
- Bộ lọc tuyển dụng: từ khóa, lĩnh vực và loại cơ hội ở Kho; từ khóa/lĩnh vực ở Tủ. Bộ lọc linh hoạt: từ khóa, nghề, cách làm, tỉnh/thành, đơn vị tiền công; thêm kiểu lịch ở Kho hoặc trạng thái nhận việc ở Tủ.
- Form đăng nhu cầu và form công việc nhận làm, có lưu nháp, sửa, đọc lại dữ liệu và bật/tạm ngừng. Tin cần người có thêm đóng tin và số người cần.
- Ảnh tự tải tùy chọn, liên kết sản phẩm tùy chọn. Không có ảnh vẫn tạo/đăng được nếu đủ các trường nghiệp vụ.
- Carousel bốn ảnh chụp thật trên ba trang chủ, cùng kích thước, chuyển mờ, nút trước/sau, chọn ảnh, tạm dừng; hỗ trợ bàn phím, dừng khi tập trung/ẩn tab và giảm chuyển động theo hệ điều hành.
- Ảnh minh họa theo nghề: dọn dẹp, bếp, kho, cây, nông nghiệp, dụng cụ sửa chữa, học tập, máy tính, lái xe, mèo. Ảnh stock được tải về phục vụ local, không phụ thuộc tải ảnh từ website khác trong mỗi lượt mở trang.

Ảnh lấy từ CDN Unsplash và mở xem từng ảnh. Không dùng công cụ tạo ảnh AI trong lần triển khai này. Nguồn ảnh và [giấy phép Unsplash](https://unsplash.com/license) được ghi trong [PHOTO_SOURCES.md](../../source/apps/tacare/addons/tacare_website/static/src/img/PHOTO_SOURCES.md). Ảnh stock chỉ minh họa nhóm nghề; không gắn làm bằng chứng tay nghề của hồ sơ hư cấu.

## Bộ trường đã đưa vào form

| Nhóm | Kho: cần người | Tủ: nhận làm |
| --- | --- | --- |
| Công việc | Tiêu đề, nghề, mô tả/phạm vi, số người | Tiêu đề việc nhận làm, nghề, mô tả/phạm vi |
| Kỹ năng | Đầu việc/kỹ năng cần có; ưu tiên riêng | Khả năng/đầu việc tự khai |
| Cách thực hiện | Trực tiếp / từ xa / kết hợp | Cách nhận làm tương ứng |
| Nơi thực hiện | Tỉnh/thành + khu vực tĩnh | Tỉnh/thành + khu vực nhận việc tĩnh |
| Lịch | Một lần / định kỳ / hạn bàn giao / linh hoạt; ngày, giờ, thứ và ghi chú | Cùng cấu trúc; lịch có thể nhận, có thể chưa hẹn ngày cụ thể |
| Thời lượng | Số giờ mỗi ca/buổi/ngày | Thời lượng và số giờ nhận tối thiểu/lần |
| Tiền | Ngân sách từ/đến, VND, đơn vị tính, giá cho mỗi người/cả nhóm/cả gói | Mức mong muốn tương ứng |
| Phạm vi giá | Khoản đã gồm/chưa gồm; thương lượng | Tương tự |
| Chuẩn bị | Bên nào chuẩn bị dụng cụ/vật tư; chi tiết | Tương tự |
| Bổ sung | Kinh nghiệm/điều kiện, ảnh hiện trạng, URL sản phẩm | Kinh nghiệm, ảnh việc đã làm, URL sản phẩm |
| Theo chuyến | Chỉ tài xế / xe kèm tài xế; một chiều / khứ hồi; điểm đến; hành khách; xe/hành lý/chờ | Loại dịch vụ, tuyến nhận và điều kiện tương ứng |

Nhóm chuyến chỉ mở khi đơn vị giá là chuyến. Chọn từ xa ẩn phần địa điểm, đồng thời máy chủ xóa địa điểm không áp dụng; từ xa + theo chuyến bị từ chối. Khi đổi đơn vị chuyến sang đơn vị khác, máy chủ xóa dữ liệu chuyến còn sót trong phần nhập đã ẩn. Địa chỉ chưa geocode, chưa có bán kính hoặc theo dõi vị trí.

Khi đăng/bật nhận việc, máy chủ yêu cầu nghề, cách làm, lịch, mức tiền dương, đơn vị và phạm vi giá, tiêu đề/mô tả. Việc trực tiếp cần tỉnh và khu vực; một lần cần ngày; hạn bàn giao cần ngày kết thúc; định kỳ cần thứ; giá theo ca/buổi/ngày cần số giờ. Chuyến cần điểm đến, loại dịch vụ và chiều chuyến; xe kèm tài xế cần thông tin xe và hành khách. Nháp cho phép thiếu phần lớn dữ liệu; mục nhận làm vẫn phải có nghề theo ràng buộc capability hiện có.

## Dữ liệu giả lập

**20 tin công việc = 5 tuyển dụng + 15 linh hoạt. 15 hồ sơ = 5 hồ sơ tuyển dụng + 10 hồ sơ có mục nhận việc.** Hiện mỗi hồ sơ linh hoạt có một mục; cấu trúc hỗ trợ nhiều mục trên cùng một hồ sơ/user.

Năm tin tuyển dụng: Frontend, vận hành thương mại điện tử, Content Marketing, vận hành kho và thiết kế đồ họa.

| Việc linh hoạt | Tiền mẫu | Điểm thử biểu mẫu |
| --- | --- | --- |
| Dọn căn hộ 60m² | 60.000đ/giờ/người | Một lần, phạm vi phòng và dụng cụ |
| Nấu ăn cho gia đình bốn người | 5.000.000đ/tháng/người | Lịch thứ Hai–Sáu, nguyên liệu riêng |
| Hai người bốc 40 thùng hàng | 150.000đ/ca/người | Hai người, ca bốn giờ, không gồm xe |
| Thay chậu 12 cây | 300.000đ/trọn việc | Khối lượng, vật tư, phần không gồm |
| Cắt cỏ vườn 80m² | 450.000đ/trọn việc | Người làm mang dụng cụ |
| Thu hoạch rau ba ngày | 280.000đ/ngày/người | Sáu giờ làm, nghỉ trưa riêng |
| Chăm bò một tuần | 2.000.000đ/trọn việc | Bảy ngày liên tiếp, giới hạn không điều trị |
| Lắp hai kệ sách | 350.000đ/trọn việc | Phụ kiện và phần không khoan tường |
| Thay vòi bếp | 250.000đ/trọn việc | Chủ có vật tư, kiểm tra phụ phí |
| Gia sư Toán lớp 6 | 180.000đ/buổi/người | Một buổi 90 phút, hai thứ trong tuần |
| Tiếng Anh trực tuyến | 150.000đ/buổi/người | Từ xa, một giờ, cần hẹn lịch |
| Landing page | 2.000.000đ/trọn việc | Hạn bàn giao, số phần/số lần sửa |
| Dựng ba video | 900.000đ/trọn việc | Khối lượng gói, tư liệu khách cung cấp |
| Xe 7 chỗ TP.HCM–Đà Lạt | 1.600.000đ/chuyến | Một chiều, xe kèm tài xế, hành khách/hành lý |
| Ghé chăm hai mèo ba ngày | 120.000đ/ngày/người | Hai lượt/ngày, tổng một giờ, không ở lại |

Mười mục nhận việc: dọn căn hộ, nấu ăn, bốc xếp, chăm cây, thu hoạch, lắp ráp, gia sư Toán, landing page, xe đi tỉnh và chăm mèo. Nội dung viết theo phía người nhận làm, không sao chép nguyên câu “cần người”. Ví dụ hồ sơ dọn nhà nhận tối thiểu hai giờ, giá 65–80 nghìn/giờ; hồ sơ xe báo khoảng 1,6–2,4 triệu/chuyến tùy tuyến. Lịch nhận việc tái sử dụng, không bắt buộc giống ngày thực hiện trong tin.

Tất cả mức tiền, người, đơn vị và nội dung đều hư cấu để thử dữ liệu, không phải bảng giá thị trường. Không tạo đánh giá tốt giả, dấu xác minh giả hoặc consent khám phá/liên hệ giả.

## Cấu trúc kỹ thuật

- Odoo Community 19, database `tacare_local`, ba website, QWeb/SCSS/JavaScript thuần trong addon hiện có. Không sửa Odoo core.
- `hr.job`: thêm `care_opportunity_kind` mặc định `recruitment`; nhóm trường `flex_*` trên mixin `care.flex.mixin`. Luồng tuyển dụng cũ giữ model và các trường cũ.
- `care.profile.capability`: dùng lại cho mỗi mục nhận việc; `profile_id` liên kết hồ sơ gốc. `flex_category_id` và `flex_rate_min/max` là alias tới các trường chuẩn hiện có của capability. Resolve alias trước create/write để đáp ứng cột category bắt buộc.
- `tacare.profile`: vẫn một bản ghi/user; `care_recruitment_enabled` phân biệt có dùng nhánh tuyển dụng hay chỉ có mục nhận việc. Không tạo kho hồ sơ thứ hai.
- Danh mục dùng lại `care.capability.category` và `hr.skill`, thêm mười nhóm nghề và 26 kỹ năng demo. Không tạo taxonomy riêng trùng nghĩa.
- Lịch của demo lưu trên từng tin/capability. Không tuyên bố đã tích hợp lịch tổng hợp `care.availability`, vùng phục vụ `care.service.area` hoặc chống trùng đặt chỗ.
- Controller mới `controllers/flexible_work.py`, model `models/flexible_work.py`, QWeb `views/flexible_work.xml` và `views/work_homepages.xml`; assets `flexible_work.js/.scss`.
- Seed chạy thủ công qua Odoo shell, chỉ chấp nhận DB local và website localhost. Không nạp tài khoản/hồ sơ demo tự động khi cài hoặc deploy addon.

## Quyền và kiểm tra dữ liệu

- Tất cả route ghi yêu cầu đăng nhập; kiểm tra role, company, chủ bản ghi, trường cho phép và trạng thái ở máy chủ trước khi ghi bằng `sudo()`.
- Không cho truyền `profile_id`, `user_id`, owner, trạng thái tùy ý qua form lưu. Portal không có ACL tạo/sửa trực tiếp các model này.
- Tủ và ảnh hồ sơ chỉ chủ/admin xem được. Ảnh tin công khai chỉ phục vụ khi tin được công khai; bản nháp cần quyền chủ/admin.
- Dữ liệu tiền/thời lượng từ chối NaN, vô cực, số âm và khoảng đảo. Ngày/giờ/thứ trong tuần được kiểm tra; ca qua đêm cần tách riêng trong demo này.
- Upload giới hạn 5 MB, tối đa 20 megapixel, đọc/giải mã ảnh rồi tái mã hóa JPEG và bỏ EXIF; không phục vụ nguyên file upload. Mỗi mục hiện hỗ trợ một ảnh.
- URL sản phẩm chỉ HTTPS, không chứa thông tin đăng nhập; mở tab mới có `noopener noreferrer`.
- Lỗi lưu rollback phần ghi dở và giữ nội dung form; người dùng chọn lại file ảnh khi sửa lỗi.
- Các consent và quyền tổ chức tuyển dụng cũ vẫn áp dụng ở các route tuyển dụng. Không cấp quyền xem ứng viên chỉ vì được đăng nhập chéo website.

## Kiểm tra thực tế

Các kiểm tra đã chạy trên local:

1. Update hai addon trong DB đã backup, nạp registry và XML thành công; restart Odoo.
2. Python AST, parse XML, `node --check`, `git diff --check`.
3. `dev_schema_check.py`: quyền tổ chức, ACL portal, consent và thu hồi consent — PASS, rollback.
4. `dev_forms_v2_check.py`: hồi quy biểu mẫu tuyển dụng, dữ liệu thiếu, salary/consent/finite/date — PASS, rollback.
5. `dev_flexible_check.py`: tài khoản gốc, host login, riêng tư hồ sơ/capability, portal write bị chặn, alias và dữ liệu sai — PASS, rollback.
6. `homepages_browser_check.cjs`: ba trang chủ tại 1440/768/375/320, marker, ảnh/font, tương tác và reduced motion — PASS.
7. `flexible_work_browser_check.cjs`: đếm 20/5/15; lọc từ xa/theo chuyến; bộ lọc riêng; owner/admin; URL/POST chéo; tạo/sửa/đọc lại; nháp/đăng/dừng; upload sai/đúng; form/list 1440/375/320; không JS error và không tràn ngang — PASS.
8. Dọn bản ghi QA tạm sau kiểm thử, giữ audit; kiểm tra lại số lượng thực tế **20 job / 15 profile / 10 capability**, dữ liệu đủ điều kiện đăng và dấu vân tay chín tài khoản gốc — PASS. Kiểm tra ba trang chủ lại sau khi chỉnh nhãn thẻ linh hoạt — PASS cả 12 tổ hợp chiều rộng.

Ảnh chụp kiểm tra ở [docs/screenshots/demo-flexible-20261019](../screenshots/demo-flexible-20261019): trang chủ Kho, danh sách linh hoạt desktop/mobile và thư viện admin.

## Backup, chạy lại và giới hạn

Backup trước thay đổi ở `backups/demo_flexible_20261019/`: source, PostgreSQL dump, filestore. Không restore toàn DB chỉ để sửa giao diện vì sẽ ghi đè dữ liệu phát sinh sau backup.

```sh
docker compose up -d db tacare gateway
docker compose run --rm tacare -c /etc/odoo/local.conf -d tacare_local -u tacare_account_access,tacare_website --stop-after-init
docker compose restart tacare
docker compose exec -T tacare python /opt/odoo/odoo-server/odoo-bin shell -c /etc/odoo/local.conf -d tacare_local --no-http < source/apps/tacare/addons/tacare_website/tests/seed_flexible_demo.py
```

Trước mỗi lần nâng addon cần backup local theo `AGENTS.md`. Seed có thể chạy lại theo demo key và không đặt lại mật khẩu tài khoản gốc. Test trình duyệt có tạo dữ liệu QA; chuyển file ID riêng tư `qa_records.json` vào `/var/lib/odoo/flexible_qa_records.json`, chạy `cleanup_flexible_qa.py` để dọn đúng hai bản ghi đó; không xóa audit hoặc dữ liệu người dùng khác.

**Chưa triển khai ở nhánh mới:** map/geocoding/bán kính, matching tự động, đặt lịch/giữ chỗ, lời mời/kết nối việc linh hoạt, mở thông tin liên hệ, thanh toán và xác minh nghề/giấy tờ xe. Các tin demo tắt `care_matching_enabled`; không đưa chúng vào matching tuyển dụng cũ. Phần chuyến chỉ thử trường dữ liệu và giao diện. Lịch hiện là một khung giờ cho các thứ chọn; lịch nhiều ca, ngoại lệ và qua đêm cần mở rộng sau.

Không push, deploy, sửa DNS/TLS hoặc dùng production DB trong đợt này. Những file đã có chỉnh sửa từ trước phiên được giữ; không coi toàn bộ working tree là thay đổi của demo này.
