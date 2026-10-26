# Tin công khai, tạo hồ sơ từ tin và đánh giá hai chiều — 24/10/2026

## Phạm vi

Chủ dự án yêu cầu cho người nhận việc xem các nhu cầu đang mở của Kho, chuyển từ tin sang tạo hồ sơ Tủ sau đăng nhập, triển khai sao/bình luận theo thiết kế đã thảo luận và bổ sung hồ sơ để thử matching. Thực hiện trên local; không commit, push, sửa production hoặc xuất gói phát hành mới. Giữ nguyên các thay đổi cấu trúc source đang có trong working tree.

## Tin mở và hồ sơ

- GET/HEAD `/kvl/jobs`, `/kvl/job/<id>` và ảnh riêng của tin mở được xem công khai. Bộ lọc bắt buộc: thời vụ, đúng website/công ty Kho, published, `is_published`, chưa hết hạn và còn chỗ. Tin nháp/tạm dừng/đóng/đủ người không được đọc qua đường công khai; đường preview và mọi thao tác ghi vẫn yêu cầu quyền.
- Tủ có liên kết **Việc đang mở** và **Tham khảo công việc đang mở**. Chi tiết tin có **Tạo hồ sơ từ công việc này**.
- Liên kết sang domain Tủ với `source_job_id`. Native login/SSO kiểm tra tài khoản và quyền như trước, giữ đường quay về kèm tin tham khảo; không tạo tài khoản mới và không đưa credential vào URL. Header hiển thị đúng người dùng.
- `tacare.profile.source_job_id` lưu nguồn tham khảo; mỗi lần tạo đều kiểm tra lại tin còn mở. Lưu tên hồ sơ rồi sang form việc nhận làm với `profile_id` cụ thể. Chỉ gợi ý nhóm nghề; không sao chép kỹ năng, lịch, giá hoặc mô tả nhu cầu thành năng lực của người nhận. Hồ sơ mới riêng tư, chưa tự tham gia matching hoặc gửi đề nghị.

## Xác nhận thực hiện

`accepted` của kết nối tiếp tục nghĩa là đồng ý trao đổi. Thêm `care.work.order` và `care.work.participation`, gắn rõ `job_id`, kết nối, hồ sơ, mục nhận làm, bên cần người và tài khoản thực hiện.

Tại **TA.CARE → Kết nối của tôi → Chi tiết → Thực hiện và đánh giá công việc**:

1. Một bên chọn mục nhận làm, ghi thỏa thuận cụ thể về phạm vi/lịch/giá, xác nhận và gửi.
2. Bên còn lại đồng ý cùng thỏa thuận; khi đó mới chốt chỗ.
3. Bắt đầu thực hiện.
4. Mỗi phía xác nhận hoàn thành riêng. Chỉ khi đủ hai phía mới thành `completed` và có `completed_at`.
5. Có thể hủy trước lúc bắt đầu; hủy trả lại chỗ. Bất đồng ở giai đoạn đã chốt/đang làm/chờ hoàn thành chuyển `disputed`, giữ chỗ và chặn review.

Khóa hàng tin rồi hàng lượt thực hiện theo cùng thứ tự trong transaction. Đếm số đã chốt/đang làm/chờ hoàn thành/hoàn thành/bất đồng để kiểm sức chứa `no_of_recruitment`; không đếm proposed/cancelled. `care_remaining_slots` lưu để lọc công khai/matching. Cả route đề nghị và route chốt kiểm ở server. Hoàn thành không mở lại một chỗ của cùng lượt.

Giới hạn rõ: hiện **một lượt công việc đầu tiên cho mỗi tin**, có thể nhiều người tham gia. Tin định kỳ chưa có bộ lịch nhiều lần thực hiện, chưa chống trùng lịch người nhận giữa các tin, chưa có đặt lịch tự động, GPS hay thanh toán. Lịch/giá thỏa thuận đang là nội dung văn bản do hai bên xác nhận, chưa có đối soát tiền. Bất đồng được ghi nhận và khóa đánh giá; chưa có quy trình phân xử/tái mở tự động.

## Sao và bình luận

Mở rộng `care.feedback` thay vì đổi tên bảng/model cũ. Feedback thuật toán cũ không được tính vào sao giao dịch.

- Chỉ hai bên của lượt thực hiện completed được đánh giá. Người đại diện doanh nghiệp phải có membership/capability hiện hành hoặc fallback thương mại đã được phép; không suy phía đánh giá theo người gửi lời mời. Admin chỉ xác nhận/đánh giá khi chính họ là bên tham gia; quyền quản trị không tạo quyền làm thay.
- Mỗi lượt tối đa một đánh giá **mỗi phía**, có unique constraint `(participation_id, author_side)` ở PostgreSQL và khóa khi ghi; nhiều nhân viên cùng doanh nghiệp không tạo thêm lượt đánh giá.
- 1–5 sao, bình luận 5–2.000 ký tự, escaped khi hiển thị; không sửa nội dung/tác giả sau gửi.
- Phương án mặc định đã thông báo trong phiên: công bố khi hai phía cùng gửi hoặc sau 14 ngày kể từ completed. Đánh giá đầu chưa công bố chỉ tác giả và admin được xem. `published` được tính khi đọc, không cần cron để mở sau thời hạn.
- Admin có thể ẩn/hiện lại với lý do và audit. Không xóa đánh giá giao dịch. Đánh giá ẩn không vào thống kê.
- Review từ bên cần người được tổng hợp đúng hồ sơ nhận việc; review từ người nhận việc được tổng hợp đúng cá nhân/tổ chức cần người. Hiển thị tại chi tiết hồ sơ, mục nhận làm, hồ sơ đã chia sẻ được phép và tin công khai của bên cần người. Chưa có đánh giá hiển thị đúng câu đó, không hiện 0 sao. Chưa đưa sao vào xếp hạng matching.
- Portal/public không có direct ACL cho hai model công việc mới hoặc feedback; controller chỉ dùng sudo sau khi kiểm tra kết nối, actor, company, ownership/membership và state. Thao tác ghi dùng POST + CSRF. Việc nhận làm đã có lịch sử sẽ được gỡ khỏi danh sách thay vì xóa mất lịch sử khi admin dùng nút xóa.

## Bộ mẫu matching

Công cụ thủ công `tacare_website/tools/matching_demo.py`, không install hook, chỉ `tacare_local` và đúng ba domain localhost; preview mặc định, apply rõ ràng, chạy lại không nhân bản.

- Dùng các tài khoản đã có: `ungvien1@tacare.vn`, `ungvien2@tacare.vn`, `student.test@tuhoso.com`; không thêm tài khoản hoặc đổi mật khẩu.
- Thêm **12 hồ sơ và 12 mục nhận làm**: 9 ca tương thích theo 9 nhóm nghề cleaning/cooking/loading/garden/farm/repair/tutoring/digital/pets, 3 ca đối chứng giá cao hơn ngân sách. Có nhãn `[Demo matching]`/`[Mẫu thử]` và mô tả hư cấu rõ ràng, phạm vi việc, giới hạn, lịch, giá, dụng cụ và kỹ năng. Không giả ảnh chân dung, xác minh, công việc hoàn thành hoặc đánh giá tốt.
- Chỉ các hồ sơ demo mới có quyền mô phỏng discovery/matching cho **đúng doanh nghiệp của tin tham khảo**, các field profile/skills, hết hạn sau 7 ngày. Không tạo contact consent, không công khai hồ sơ cho khách. Ba hồ sơ gốc và quyết định chia sẻ/mật khẩu gốc giữ nguyên.
- Matching trả `capability_id` của mục nhận làm được chọn. Chiều người nhận nay kiểm quyền matching cho từng job/organization, tương đương chiều bên cần người; không mở rộng quyền khi recipient trống. Thu hồi/hết hạn dừng cả hai chiều.
- Sau tạo mẫu: **15 tin, 15 hồ sơ, 24 mục nhận làm**, không giữ sao/công việc hoàn thành hư cấu từ QA. Tài khoản/filestore gốc không đổi.

Cách thử: đăng nhập một trong ba tài khoản, mở Tủ → Hồ sơ của tôi, chọn hồ sơ có nhãn Demo matching → Xem việc phù hợp. Hoặc doanh nghiệp chọn tin nguồn tại TA.CARE → Tìm người làm. Ca đối chứng giá vượt ngân sách không vào gợi ý tương ứng. Qua 7 ngày cần chủ động cấp quyền mới nếu tiếp tục thử.

## Kiểm chứng local

- Backup DB custom dump + filestore trước thay đổi: ignored `backups/marketplace_reviews_20261024/`; pg_restore listing đã kiểm tra.
- Cập nhật hai addon local; Python/XML parse, JS syntax, security scanner và diff whitespace.
- `dev_work_review_check.py`: rollback, matrix mẫu, quyền actor/portal, chỗ cuối, hai xác nhận, chặn sớm/người ngoài/trùng, công bố hai phía/14 ngày, bất biến, ẩn và tổng hợp đúng chủ thể.
- `dev_demo_matching_check.py`: rollback, matching qua controller cả hai chiều, 9 nghề/3 giá không phù hợp, recipient, thu hồi/hết hạn.
- `seasonal_browser_check.cjs`: Chrome, public homepage markers, 320/375/1440, native auth/SSO, đăng tin, C2C/business kết nối, contact grant/revoke, quyền owner/admin và các route tuyển dụng đã nghỉ.
- `work_review_browser_check.cjs`: Chrome, native đăng nhập và giữ tin nguồn, tên người dùng cả ba site, form do người nhận tự điền, thỏa thuận/hoàn thành/review hai phía, công bố ẩn, chống XSS/trùng/người ngoài, kiểm duyệt, sao hồ sơ và 320/375/1440.
- `work_capacity_browser_check.cjs`: hai POST đồng thời chốt chỗ cuối, đúng một thành công; hủy trả chỗ; bất đồng chặn đánh giá.
- QA hư cấu và credential runtime đã dọn; giữ audit. Ảnh kiểm tra trong ignored `runtime/review-qa-screenshots/`; đã xem ảnh trang hoàn thành.

Không chạy trên production. Gói full-local-restore chuẩn bị trước lần thay đổi này **không chứa code/schema/dữ liệu mới**; cần chuẩn bị và kiểm tra lại gói trước khi dùng, không dùng gói cũ để triển khai bản này.

## Sửa chặn đăng nhập khi bấm tin công khai

Người dùng phát hiện bấm “Xem chi tiết” vẫn mở đăng nhập dù GET trực tiếp trả 200. Nguyên nhân `static/src/js/authentication.js` chặn mọi link cùng origin dưới `/kvl` khi `accessGuest=1`, trước khi trình duyệt gửi request. Đã đồng bộ ngoại lệ read-only catalog với server, chuẩn hóa prefix ngôn ngữ và dấu `/` cuối. Preview, tạo hồ sơ, đăng nhu cầu, explicit login và các chức năng riêng vẫn giữ gate.

`tests/public_job_navigation_browser_check.cjs` tái hiện lỗi trước sửa (click không chuyển tới chi tiết), sau sửa PASS bằng phiên Chrome mới chưa đăng nhập: click navbar, nút chi tiết, tiêu đề và ảnh trên danh sách có/không prefix `/vi`; không bật popup hoặc hiện nút sửa/xóa. Tạo hồ sơ từ tin và đăng nhu cầu vẫn bật đăng nhập. JS syntax, security scan và diff whitespace PASS; restart Odoo local để nạp asset mới. Không thay dữ liệu nghiệp vụ hoặc triển khai server. Kiểm tra HTTP trực tiếp không đủ thay thế phép thử click khi có gate JavaScript.
