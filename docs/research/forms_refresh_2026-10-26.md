# Form đăng nhu cầu và hồ sơ — local, 26 October 2026

Chủ dự án yêu cầu làm rõ giao diện/nút cho phần đăng tin Kho Việc Làm và đăng hồ sơ Tủ Hồ Sơ, sau khi hoàn thiện map. Bản này là lớp trình bày cuối `views/shared/form_design.xml` và `static/src/scss/form_design.scss`, giữ template/model/route native. Không commit/push/deploy.

## Giao diện

- Kho `/kvl/flexible/new`, `/kvl/flexible/<id>/edit`: tiêu đề và hướng dẫn trực tiếp, 5 nhóm công việc/địa điểm/thời gian/tiền công/bổ sung. Sidebar điều hướng theo section ở desktop, lưới liên kết gọn ở mobile. Khung trắng, xanh rừng theo palette đã có.
- Tủ `/tuhoso/work/new?profile_id=…`, `/tuhoso/work/<id>/edit`: cùng cấu trúc dễ điền, màu san hô theo Tủ; khối chọn hồ sơ nổi rõ, giữ explicit ID. Mỗi hồ sơ có nhiều việc nhận làm, không tự chọn hồ sơ khác khi lưu.
- Nút chính màu đặc, nút lưu nháp nền trắng có viền; tên nút nêu rõ kết quả. Khối cuối giải thích lưu/đăng và quyền chia sẻ hồ sơ riêng biệt. Không tạo wizard hoặc bước hoàn thành giả. Skills/weekday vẫn là checkbox native có dấu chọn, phần tùy chọn dùng details native.
- `/tuhoso/profiles/new?kind=flexible`: giải thích hai bước thực: đặt tên hồ sơ rồi thêm việc nhận làm. Bỏ ảnh trang trí trong form, dùng icon Phosphor có sẵn và hướng dẫn. Giữ source-job note/hidden source_job_id. Hồ sơ mới vẫn private, không thêm consent. Trang chủ pinboard/thư viện không đổi.
- `/tuhoso/profile/<id>/edit`: phần giới thiệu được nhóm rõ, nút lưu/quay lại có hình dạng và vùng bấm riêng. Profile version, ID và xử lý lỗi giữ nguyên.
- Bộ chọn bản đồ mở sẵn; địa chỉ đã chọn là nơi xem duy nhất, sửa số nhà/hẻm bên trong details. `flex_location` hidden và `geo_address` đồng bộ khi chọn ghim/sửa tay. Vẫn có trường tỉnh/thành phục vụ đối chiếu, chọn khu vực tham chiếu và phương án tọa độ khi cần.

Inputs tối thiểu 50px, nút chính/phụ tối thiểu 48px, font nhập liệu 16px, focus rõ, reduced motion. Giữ shell fluid 48/24/20px, không ảnh hưởng homepage hay phần bên trong bản đồ. Không thay CSRF, allowlist, ownership, current consent, trạng thái publish/draft hoặc matching/rank.

## Tham khảo thiết kế

Áp dụng hướng dẫn về hình dạng/nền/viền thể hiện nút có thể bấm của [NNGroup — Clickable Elements](https://www.nngroup.com/articles/clickable-elements/) và nhóm trường bằng khoảng cách/nhãn rõ trong [NNGroup — Web Form Design](https://www.nngroup.com/articles/web-form-design/). Không thêm phụ thuộc UI hoặc bản sao phong cách thương hiệu khác.

## Kiểm chứng

- Backup DB trước UI tại ignored `backups/nearby_map_20261026/before_workspace_ui.dump`, có restore list kiểm tra.
- Upgrade `tacare_website` local exit 0, restart; manifest/XML parse, Node syntax, credential scanner, `git diff --check` PASS.
- `tests/form_workspace_browser_check.cjs` Chrome: hai role native, Kho/Tủ create/edit, profile creation/introduction và source-job context; 320/375/390/767/768/1024/1440/1920 không tràn; màu/nút/focus/target; map mở/Photon thực/địa chỉ >250 ký tự vào FormData và preview/hidden; phản hồi chậm không ghi đè sửa tay; remote toggles; lỗi server giữ dữ liệu; explicit profile/source/version IDs; thiếu CSRF/guest bị chặn. Chỉ invalid submissions, không tạo/sửa bản ghi nghiệp vụ.
- `tests/map_workspace_browser_check.cjs` Chrome: khung TA.CARE, login/role controls, source/radius/refresh loading state, links, route/km/fit/clear, 8 widths PASS. Ảnh cuối đợi map ổn định sau resize.
- `tests/dev_nearby_check.py` Odoo shell PASS, rollback: hai chiều/winning offer, consent đúng tổ chức và còn hạn, owner/guest isolation, chặn đọc tọa độ/URL riêng tư và tọa độ sai. `tests/homepage_contract_smoke.py` PASS ba homepage HTTP 200/đúng marker và ba login HTTP 200. Kiểm đếm ORM sau cùng đúng 15/15/24.
- Đã xem ảnh Kho/Tủ desktop/mobile, sửa icon bị CSS ảnh cũ kéo giãn trên mobile. Ảnh ignored tại `runtime/form-workspace-review/`, `runtime/map-workspace-review/`.

Database vẫn 15 jobs / 15 profiles / 24 offers; không thêm account/consent hay đổi mật khẩu. API map/reverse/routing tiếp tục dùng dịch vụ ngoài của bản thử, giới hạn và phạm vi tọa độ như tài liệu nearby; chưa có live dispatch/first-accept booking.
