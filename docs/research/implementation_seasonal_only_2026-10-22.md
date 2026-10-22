# TA.CARE chuyển sang ghép nối việc thời vụ — local 22/10/2026

## Quyết định và kết quả

Theo yêu cầu mới sau trao đổi mentor, TA.CARE chỉ kết nối người cần hoàn thành việc với người nhận làm thời vụ. Phạm vi tuyển dụng nhân viên bị loại bỏ, thay thế quyết định hỗn hợp ngày 19–21/10. [Phạm vi hiện tại](../project_scope.md) là nguồn chuẩn; tài liệu triển khai cũ giữ để tra lịch sử.

- Kho Việc Làm: nhu cầu theo giờ, ca/buổi hoặc đầu việc, do cá nhân hay doanh nghiệp đăng.
- Tủ Hồ Sơ: hồ sơ nhận làm, có thể nhiều hồ sơ trong một tài khoản; mỗi mục nêu khả năng, lịch, vùng nhận và đơn giá.
- TA.CARE: đối chiếu có giải thích, đề nghị/lời mời, phản hồi và quyền liên hệ. Hai phía cá nhân có thể kết nối C2C.

Role key `candidate` được giữ để tương thích, nhãn là “Cá nhân”; cá nhân dùng cả ba website, doanh nghiệp dùng Kho + TA.CARE. SSO và đăng xuất theo nhóm trình duyệt tiếp tục dùng cơ chế hiện có. Quyền chức năng được kiểm tra ở server, trang chủ vẫn công khai. Tài khoản không đổi vai chỉ vì người dùng chọn phía “cần người” hay “nhận việc”.

## Sao lưu và dữ liệu

Bản đầy đủ trước thay đổi nằm trong thư mục ignored `backups/seasonal_only_20261022_112758/`:

- `tacare_local.dump`: đã xác minh danh mục bằng `pg_restore --list`.
- `filestore.tar.gz`: filestore tương ứng của `tacare_local`.
- `manifest.json`: commit nguồn, dung lượng và SHA256 của hai tệp; thư mục/tệp riêng tư, không đưa lên Git.

Công cụ thủ công `tools/remove_local_recruitment.py` chỉ chạy trên DB local có ba site localhost và receipt backup. Đã kiểm kê các liên kết trước khi xóa: không có connection, applicant, employee, match input/session, tài liệu/OCR, revision hoặc mục nhận làm phụ thuộc vào nhóm cần xóa.

Kết quả: xóa **5 tin tuyển dụng và 3 hồ sơ tuyển dụng** bằng ORM; giữ **15 tin thời vụ, 3 hồ sơ nhận việc, 12 mục nhận làm** với ID/owner cũ. Tất cả tài khoản gốc, mật khẩu, active và role được đối chiếu fingerprint và giữ nguyên. Các mục kỹ năng/lịch sử/học tập/minh chứng thuộc ba hồ sơ tuyển dụng được gỡ cùng hồ sơ; không chuyển chúng sang người khác. Receipt xóa nằm trong ignored `runtime/tacare/seasonal_removal_receipt.json`.

Không xóa bản backup, không đổi tài khoản admin và không đụng dữ liệu server. Các tài khoản/job/profile QA hư cấu được tạo riêng để kiểm thử và dọn bằng `tests/cleanup_seasonal_qa.py`; audit được giữ.

## Giao diện và tổ chức source

Trang chủ dùng hai ý định “Tôi cần người làm” / “Tôi muốn nhận việc”, nhóm nghề và số nhu cầu thật trong DB, có nhãn dữ liệu minh họa. Không dùng CV, số người dùng hoặc đánh giá giả để tạo cảm giác quy mô. Kho và Tủ có bộ ảnh carousel khác nhau; TA.CARE dùng sơ đồ quỹ đạo kết nối, không có carousel. Ảnh giữ nguồn thực trong bộ ảnh đã ghi nhận; không thêm ảnh AI.

Các trang danh sách, tủ hồ sơ, tạo hồ sơ, chi tiết và ghép nối tập trung vào đầu việc, lịch, khu vực, chi phí và điều kiện cần trao đổi. Admin vẫn có chỉnh sửa/xóa, ba tình huống mẫu và tổng quan gợi ý dựa trên consent hiện hành. Chi tiết việc có ảnh và nối sang TA.CARE để đối chiếu.

- Trang riêng nằm trong `sites/khovieclam/`, `sites/tuhoso/`, `sites/tacare/`, bao gồm các file `views/seasonal_marketplace.xml` riêng.
- Thành phần dùng chung ở `views/shared/seasonal_marketplace.xml`; token/font/bố cục responsive dùng asset chung. `controllers/seasonal.py` cung cấp context danh mục/số lượng.
- `models/seasonal_scope.py` giữ rào ghi dữ liệu và route tuyển dụng cũ. Giữ model, addon và XML ID; không sửa Odoo core, không gỡ dependency HR chỉ để thay UI.
- Manifest website `19.0.10.0.0`, account access `19.0.4.0.0`.

Các marker `tc-jobs`, `tc-profiles`, `tc-hub` vẫn nằm trên `#wrap` để giữ hợp đồng HTTP probe hiện tại.

## Quyền và kết nối

Tạo/sửa `hr.job` chỉ chấp nhận loại flexible; hồ sơ không thể bật recruitment, kể cả default context. Các đường dẫn tạo/sửa/ứng tuyển native và Kho tuyển dụng cũ bị chặn; URL chi tiết `/kvl/job/<id>` vẫn được dùng cho **chi tiết thời vụ** đã override, có lookup chỉ tin flexible hợp lệ. Không tạo `hr.applicant` từ đề nghị nhận việc.

Cá nhân chỉ quản lý tin và hồ sơ của mình. Doanh nghiệp giữ ranh giới tổ chức và quyền `can_manage_jobs`/`can_handle_candidates`; ownership không vượt quyền thành viên bị tạm ngừng. Admin có phạm vi các company được phép. Request gửi kết nối kiểm tra owner, company, trạng thái tin/hồ sơ, điều kiện đối chiếu, consent và không cho tự gửi chính mình. Chỉ bên nhận phản hồi; người được ủy quyền xử lý của tổ chức vẫn xử lý đề nghị gửi đến tổ chức.

Email chỉ hiện sau khi kết nối accepted và chủ hồ sơ cấp consent contact cho đúng bên thuê, field email. Thu hồi có hiệu lực khi đọc lại; admin không tự cấp thay chủ hồ sơ. `recipient_kind=organization` là khóa tương thích, nay nhãn “Bên thuê cụ thể”, có thể trỏ tới partner cá nhân trong C2C.

## Nghiên cứu và giới hạn

[Nghiên cứu Grab, Green SM, bTaskee, Taskrabbit](seasonal_platform_benchmark_2026-10-22.md) ghi nguồn chính thức và phân biệt chứng cứ với đề xuất cho TA.CARE. Phù hợp nhất là kết hợp luồng nhu cầu → chọn/đối chiếu người nhận → trao đổi → xác nhận, thay vì sao chép điều phối tài xế cho mọi nghề.

`/how-it-works` có sơ đồ vùng và bộ tính đơn giá/giờ × giờ + vật tư + đi lại để thảo luận thiết kế. **Chưa có bản đồ/GPS, ETA, đặt lịch giữ chỗ, đơn công việc, cổng thanh toán, thu tiền/chi trả, đối soát, hoàn tiền hoặc điều phối tức thời.** Kết nối accepted chỉ là đồng ý trao đổi. Các chức năng đó là giai đoạn phát triển sau; chưa chọn API trả phí hoặc thay chính sách phí.

## Kiểm tra đã chạy

- Nâng hai addon bằng Odoo local `--stop-after-init`, sau đó restart; QWeb nạp thành công.
- `dev_schema_check.py`: cách ly hai tổ chức/hai cá nhân, chặn portal write và consent đúng bên nhận/thu hồi; rollback.
- `dev_seasonal_scope_check.py`: chặn recruitment create/write/default context, projection cá nhân ba site, owner isolation, portal write, quyền xử lý và suspension của business member; rollback.
- `dev_data_transfer_check.py`: v2 chỉ 4 account được chọn, 15 tin, 3 hồ sơ private, 12 offer; lặp/cập nhật, giữ mật khẩu đích, chặn đổi owner/sửa server/input cấm và gói tuyển dụng; rollback. Không tạo gói phát hành lâu dài.
- `seasonal_browser_check.cjs`: Chromium thật, trang chủ 1440/375/320 px; ảnh, carousel riêng, sơ đồ/bộ tính; cá nhân/doanh nghiệp đăng việc, giữ input lỗi; C2C gửi/nhận, chặn người ngoài, grant/revoke email; admin sửa hồ sơ/ba ví dụ; tạo hồ sơ chỉ thời vụ. Credential QA chỉ nằm trong file ignored và được xóa sau kiểm thử.
- `homepage_contract_smoke.py`: cả ba trang chủ HTTP 200, đủ marker `tc-jobs`/`tc-profiles`/`tc-hub`; cả ba login HTTP 200.
- Parse 77 Python/34 XML, `node --check` cho JS mới, scanner bảo mật (223 text file) và `git diff --check`.

Các kiểm tra chỉ áp dụng local. Không có kiểm thử tích hợp bản đồ/thanh toán vì chưa có tích hợp, không có triển khai hoặc kiểm tra trên production.

## Xem local

- Kho: `http://khovieclam.localhost:8069/`
- Tủ: `http://tuhoso.localhost:8069/`
- TA.CARE: `http://tacare.localhost:8069/`
- Luồng và hướng phát triển: `http://tacare.localhost:8069/how-it-works`

Ảnh duyệt giao diện nằm ở [thư mục screenshots](../screenshots/seasonal-only-20261022/). Ảnh admin chụp trong lúc có actor QA hư cấu để kiểm tra consent; ảnh guest chụp sau khi dọn QA.

## Phát hành sau này

Chưa commit, push, merge hoặc deploy. Code-only hiện không tự xóa dữ liệu tuyển dụng cũ trên server; công cụ dọn local không được chạy ở production. Gói v2 cũ chứa tuyển dụng không được dùng lại. Việc phát hành và xử lý dữ liệu server cần một lần chuẩn bị/review riêng dựa trên script đang cài, backup hiện tại và phạm vi được chủ dự án chỉ định; không suy ra từ lần chỉnh local này.
