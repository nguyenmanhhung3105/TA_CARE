# Tách website và hoàn thiện dữ liệu, 21/10/2026

Phạm vi được chủ dự án yêu cầu: giữ giao diện, tách code theo ba website, sửa nút và đường chỉnh sửa, bổ sung ảnh và nút xem chi tiết, hồ sơ từ tài khoản có sẵn, tin/hồ sơ chi tiết, ví dụ đối chiếu TA.CARE. Đã đọc tài liệu Word `Hệ thống TACARE.docx` trong thư mục `TA.CARE project/Task cho nhóm` và đối chiếu với policy tài khoản/consent hiện hành.

## Cấu trúc code

Trong addon `tacare_website`, ba package ở `sites/khovieclam`, `sites/tuhoso`, `sites/tacare`. Mỗi package có controller nghiệp vụ và QWeb riêng. `controllers/live.py` ghép các lớp và giữ điểm import tương thích. `controllers/profiles.py` giữ lớp override cuối của Odoo; parser/upload/authorization của form linh hoạt và layout/xác thực dùng chung được giữ riêng. Xem `sites/README.md`.

Odoo chỉ phục vụ asset dưới `static/`: CSS/JS riêng nằm ở `static/src/khovieclam` và `static/src/tuhoso`; các token, font, ảnh có nguồn và tương tác chung không nhân ba. Tên addon, model, SQL table, mọi XML ID gốc và phụ thuộc đều được giữ. Không tạo ba database hoặc ba addon độc lập. Version `19.0.8.0.0`; không có migration đổi model.

## Chức năng

- Kho: ảnh thật có nguồn được dùng cả trên thẻ việc và trang chi tiết; ảnh chỉ minh họa lĩnh vực, không đại diện người đăng. Ảnh người đăng tải vẫn là mục riêng có route kiểm quyền. Tuyển dụng có ảnh; thẻ cả hai nhánh có nút Xem chi tiết. Dùng lại `PHOTO_SOURCES.md`, không tạo ảnh AI.
- Quản lý trạng thái chỉ hiện thao tác hợp lệ theo trạng thái hiện tại; khoảng cách và kích thước nút phù hợp mobile. Server kiểm tra lại transition, field allowlist và điều kiện mở tin. Select có khoảng trống cho indicator. Admin tra cứu việc linh hoạt trong các công ty được phép, thay vì chỉ công ty đang kích hoạt.
- Tủ: hồ sơ và công việc nhận làm dùng `profile_id` cụ thể, kiểm chủ sở hữu; thiếu lựa chọn không được tự chọn một hồ sơ linh hoạt có sẵn để ghi. Trang tổng quan có nút sang TA.CARE và form quyền chia sẻ cho đúng hồ sơ, kể cả hồ sơ linh hoạt. Không tự cấp consent cho tài khoản thật.
- TA.CARE: đối chiếu linh hoạt dùng cùng hàm `_care_compare_profile` qua nhánh `_care_compare_flexible`. So nhóm nghề, cách thực hiện, tỉnh/thành, khoảng ngày, ngày trong tuần, giờ, mức tiền cùng đơn vị/cách tính và đầu việc tự khai. Xung đột tường minh loại khỏi gợi ý. Thiếu dữ liệu là chưa biết, không có điểm phần trăm. Cần xác nhận khu vực cụ thể, di chuyển, dụng cụ, chi phí và lịch trống; không suy diễn bán kính từ tỉnh/thành.
- Chủ tin chỉ xem các gợi ý cho tin thuộc quyền xử lý; tài khoản ứng viên chọn hồ sơ của mình. Luồng gửi mong muốn nhận việc / lời mời dùng `tacare.connection`, có thông báo và phản hồi hai phía. Việc linh hoạt không tạo `hr.applicant`. Quyền liên hệ vẫn cần connection accepted + consent contact đúng tổ chức, field email.
- `/tacare/examples`: ba tình huống hư cấu (dọn căn hộ, Frontend, lịch chăm vườn mâu thuẫn) để thử giao diện; tách rõ ví dụ với kết quả của tài khoản. Không tự tạo consent, kết nối hay kết quả matching đã chốt từ những ví dụ này.

Không mở booking, thanh toán, OCR, upload CV, matching snapshot hay vận tải hành khách. Ví dụ theo chuyến tắt matching; offer xe tạm ngừng. Policy business Kho+TA.CARE / candidate Tủ+TA.CARE được giữ theo hướng dẫn đã xác nhận trước đó.

## Dữ liệu local

Backup trước cập nhật: ignored `backups/refresh_20261021/tacare_local.dump` (pg_dump custom format). Script thao tác bằng ORM và chỉ chạy thủ công, kiểm tra `tacare_local` cùng ba domain localhost; không có install hook.

`tests/refresh_account_demo.py` đã chạy một lần:

- Chuyển 10 offer cần giữ sang hồ sơ thuộc `ungvien1`, `ungvien2`, `student.test`, rồi xóa đúng 15 hồ sơ `profile-01`…`profile-15` thuộc tài khoản `demo-flex-*`. Không xóa tài khoản. Các hồ sơ này đều có tài khoản demo kỹ thuật; việc loại bỏ nhằm bỏ bộ hồ sơ demo cũ, không phải kết luận chúng là bản ghi mất FK.
- Giữ hồ sơ admin gốc; giữ hai hồ sơ của mỗi `ungvien1`, `ungvien2`; tạo hai hồ sơ mẫu cho `student.test`. Tổng 7 hồ sơ thuộc tài khoản hoạt động, 12 công việc nhận làm; mẫu chuyến xe tạm ngừng. Hồ sơ hư cấu có nhãn trong giới thiệu, kinh nghiệm và kỹ năng chưa xác minh.
- Giữ 20 tin (5 tuyển dụng, 15 linh hoạt), bổ sung quy trình, phạm vi, bàn giao, chuẩn bị, chi phí, yêu cầu/quyền lợi/lịch tuyển dụng. Tin demo được gắn tài khoản doanh nghiệp có sẵn `hr.hozota`; nội dung vẫn là hư cấu, không là cam kết thật của doanh nghiệp.
- Không thay mật khẩu, vai trò, active hay login của bất kỳ tài khoản nào (kiểm fingerprint trước/sau). Không thay consent. Không tìm thấy login `tadudu` trong bản local được kiểm tra; không tạo lại hoặc xóa tài khoản mang tên tương tự. Các admin và tài khoản có sẵn giữ nguyên.

Hồ sơ mẫu vẫn riêng tư nếu chủ tài khoản chưa bật chia sẻ. Đăng nhập Tủ, chọn đúng hồ sơ, mở chi tiết, chọn phạm vi thành viên và cho phép tìm thấy/đối chiếu rồi lưu để có gợi ý thật. Trang ví dụ TA.CARE xem được ngay sau đăng nhập.

## Cập nhật và kiểm chứng

Đã chạy `docker compose up -d db tacare gateway`, backup local, cập nhật addon bằng `docker compose run --rm --no-deps tacare -c /etc/odoo/local.conf -d tacare_local -u tacare_account_access,tacare_website --stop-after-init` và restart `tacare`. Các lần cập nhật kế tiếp sửa đường dẫn asset dùng `-u tacare_website`.

Đã kiểm tra Python AST, XML, đường dẫn manifest, bảo toàn toàn bộ XML ID từ `views/live.xml` cũ, `git diff --check`, homepage/login HTTP trên ba domain. `dev_schema_check.py`, `dev_forms_v2_check.py`, `dev_account_matching_check.py` là các kiểm tra rollback đã đạt.

Kiểm thử Chrome dùng tài khoản QA hư cấu tạm (`seed_account_matching_qa.py`), secrets trong ignored runtime; `cleanup_account_matching_qa.py` xóa đúng prefix QA và các bản ghi phụ thuộc. Chrome headless đã đạt: nút Xem chi tiết và ảnh của cả tuyển dụng/linh hoạt; ảnh trang chi tiết; nút trạng thái không chồng và chỉ hiện thao tác đúng trạng thái; đường chỉnh sửa có tiền tố `/vi`; sửa/lưu tin và capability; thư viện chỉ hiện hai hồ sơ của chủ QA; cấm tài khoản khác xem hồ sơ hoặc sửa tin; gợi ý linh hoạt; gửi mong muốn nhận việc, thông báo liên kết đúng connection, bên thuê chấp nhận; ba ví dụ và bố cục 320/375/1440px. Script `account_matching_browser_check.cjs` hoàn tất exit 0. Đã chạy cleanup sau lượt cuối; database trở về 20 tin và 7 hồ sơ, không còn tài khoản/bản ghi nghiệp vụ QA. Audit event append-only của QA được giữ theo thiết kế. Ảnh ví dụ ở `docs/screenshots/account-refresh-20261021/tacare-examples.png`; chỉ chứa dữ liệu minh họa.

Các bài kiểm tra/seed lịch sử ngày 19–20/10 có assertion số lượng 15/20 hồ sơ cũ không mô tả bộ dữ liệu hiện tại; không chạy lại các seeder đó để khôi phục dữ liệu đã được yêu cầu bỏ. Kiểm tra mới thay thế phần assertion dataset; kiểm tra schema và semantics không phụ thuộc dataset vẫn được giữ.

## Giới hạn môi trường và release

Ảnh lỗi của chủ dự án là trên `khovieclam.vn` với ID tin 22. Database local không có tin 22, nên không thể xác nhận hay sửa bản ghi production đó chỉ từ local. Đã kiểm tra các route sửa trên bản ghi local, gồm tiền tố `/vi`; bản sửa cần được phát hành riêng mới có mặt trên domain thật.

Không push, không gọi release.py, không truy cập server/DB production. Contract gói dữ liệu release ngày 20/10 vẫn giới hạn bộ demo cũ (19 hồ sơ/18 account); dữ liệu local mới không được tự động coi là bundle đã được duyệt. Không tái sử dụng bundle cũ để ghi đè hoặc chuyển hồ sơ mới sang production trong phiên này.
