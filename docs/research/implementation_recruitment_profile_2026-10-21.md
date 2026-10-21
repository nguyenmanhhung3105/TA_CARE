# Hồ sơ tuyển dụng chi tiết và quyền sửa admin, phiên 21/10/2026

Theo yêu cầu chủ dự án: admin sửa được hồ sơ trong Tủ; rà lại dữ liệu và biểu mẫu tuyển dụng, bổ sung trường thiếu và nội dung chi tiết. Phạm vi local, không push/deploy. Đã backup `backups/recruitment_profile_20261021/tacare_local.dump` trước cập nhật.

## Hành vi

- Thẻ hồ sơ và trang chi tiết có Chỉnh sửa cho chủ hồ sơ và admin hệ thống. URL rõ ràng `/tuhoso/profile/<id>/edit`; URL cũ `/tuhoso/me?profile_id=<id>` vẫn hoạt động. Admin được sửa hồ sơ trong các công ty được phép, không chỉ công ty đang kích hoạt. Tài khoản khác không truy cập hoặc ghi được.
- Nội dung tuyển dụng có giới thiệu/định hướng, vị trí/lĩnh vực, cấp độ nghề nghiệp, khu vực/cách làm/thời lượng, kinh nghiệm liên quan tự khai, lịch bắt đầu, điều kiện mong muốn, thu nhập theo khoảng (cùng tiền tệ/kỳ/gross-net), thương lượng, chuyển nơi ở, portfolio HTTPS, kỹ năng/ngoại ngữ/chứng chỉ và dự án/minh chứng.
- Quá trình làm việc có nhiều mục: đơn vị/nhóm, vai trò, loại kinh nghiệm, thời gian theo tháng, đang làm, nơi làm, trách nhiệm, kết quả và công cụ. Quá trình học có trường/cơ sở, chuyên ngành, trình độ native Odoo, thời gian, đang học và mô tả. Có thêm/sửa/xóa từng mục, lưu riêng sau thông tin chính.
- Văn bản kinh nghiệm và học vấn cũ được giữ làm phần tổng quan/bổ sung. Không biến số tháng các mục thành tổng kinh nghiệm tự động hoặc cộng trùng thời gian. Thiếu ngày/trình độ vẫn là chưa khai; không suy diễn là không có năng lực.
- Trang tạo mới có thông tin tuyển dụng ban đầu (headline, lĩnh vực/nhóm nghề, giới thiệu), giữ lại khi chuyển sang form đầy đủ. Chọn việc linh hoạt sẽ ẩn và disable các trường riêng của tuyển dụng. Hồ sơ mới vẫn private/invisible.
- Trang chi tiết trình bày các mục kinh nghiệm/học tập, mức kỹ năng và ví dụ sử dụng, dự án, thu nhập và điều kiện làm việc thành các nhóm dễ đọc. Gợi ý hoàn thiện chỉ nêu nhóm thông tin còn trống; không phải điểm năng lực hay điểm matching.
- Admin được sửa nội dung, kỹ năng, minh chứng và các mục mới; không thay chủ tài khoản, loại hồ sơ, quyền xác minh hay consent qua form. Admin sửa hồ sơ người khác có thông báo rõ và không có form chia sẻ; backend vẫn kiểm owner-only cho grant/revoke. Admin không được mở rộng visibility của minh chứng thay chủ hồ sơ.
- Hồ sơ linh hoạt có form sửa metadata riêng để tránh việc lưu nội dung chung vô tình biến thành hồ sơ tuyển dụng. Các capability tiếp tục chỉnh riêng bằng luồng cũ.

## Model và quyền

Giữ `tacare.profile`, ID và tham chiếu cũ. Mở rộng thêm `career_level`, `salary_max`, `salary_negotiable`, `relocation`, `portfolio_url`, `preferred_conditions`, dùng lại `education_level_id` native hiện có. Hai model con mới `tacare.profile.experience`, `tacare.profile.education`, chung mixin `tacare.profile.timeline.mixin`; FK `profile_id` ondelete cascade. Không đổi tên model hoặc tạo một kho profile song song.

Portal chỉ đọc các dòng thuộc hồ sơ của chính tài khoản trong công ty được phép; không có quyền ORM create/write/unlink. Controller yêu cầu role, profile_id cụ thể, owner hoặc system admin, công ty hợp lệ, trạng thái chưa archived; các mục con phải thuộc đúng profile đang sửa. Không chọn hồ sơ đầu tiên để ghi. Xử lý thêm/sửa mục có savepoint, lỗi giữ dữ liệu nhập. Các lần sửa nội dung có audit actor và profile, kể cả admin.

Thông tin chính có version trong form và khóa hàng khi lưu, ngăn ghi đè thay đổi từ phiên khác. Mục con tăng version profile khi tạo/sửa/xóa; không chuyển mục sang profile khác. Kiểm ngày kết thúc không trước ngày bắt đầu, mục đang tiếp tục không lưu ngày kết thúc, độ dài, enum, danh mục, vùng VN, giá hữu hạn/không âm và khoảng lương, portfolio HTTPS không userinfo. Không cho sửa user_id/company/status/visibility/verified qua form nội dung.

Dữ liệu mới không được đưa tự động vào thuật toán hoặc snapshot matching. Bộ so sánh đang dùng các trường đã có (bao gồm lương tối thiểu tự khai); các trường bổ sung được trình bày cho người dùng xem xét. Không thêm CV upload, OCR, xác minh tự động hoặc thông tin định danh nhạy cảm.

## Dữ liệu mẫu

`tests/enrich_recruitment_profiles.py` chạy thủ công, kiểm `tacare_local`/ba localhost và chỉ tìm ba key recruitment của ungvien1, ungvien2, student.test. Bổ sung bio, định hướng, trách nhiệm, kết quả, công cụ, điều kiện, khoảng thu nhập, một công việc, một quá trình học và một dự án mẫu mỗi hồ sơ. Mọi đơn vị/trường/kết quả đều được ghi là hư cấu, chưa xác minh. Không sửa tài khoản admin hoặc hồ sơ linh hoạt.

ID/chủ hồ sơ, tài khoản, mật khẩu, vai trò và consent được giữ; script đối chiếu fingerprint tài khoản và nội dung consent trước/sau. Không tự bật sharing để làm đầy gợi ý. Tổng hồ sơ/tin/offer gốc vẫn 6/20/12 sau dọn QA.

## Kiểm chứng

Cập nhật local `tacare_account_access,tacare_website`, sau đó `tacare_website`, bằng lệnh chuẩn `docker compose run --rm --no-deps tacare -c /etc/odoo/local.conf -d tacare_local -u ... --stop-after-init`; restart `tacare`. Version `19.0.9.0.0`. Có hai bảng/nhóm cột mới do ORM tạo, không có migration rename/production.

`dev_recruitment_profile_check.py` rollback đã đạt: thời gian/current, không reparent mục, cách ly portal read và chặn direct write/create, khoảng lương hữu hạn, HTTPS portfolio, version profile và mục con. Kiểm Python/XML/JS, manifest và diff whitespace được chạy.

Kiểm thử HTTP/Chrome `recruitment_profile_browser_check.cjs` đã PASS: admin vào sửa từ thẻ hồ sơ người khác, lưu nội dung chi tiết/kỹ năng/minh chứng, giữ dữ liệu khi sai khoảng lương hoặc ngày học, thêm từng công việc/học tập, chặn ghi đè phiên cũ và chặn trường bảo vệ. Admin không bật consent/visibility thay chủ; tài khoản khác không đọc/sửa được và không dùng ID mục của hồ sơ khác. Tạo hồ sơ tuyển dụng mới giữ headline/bio/nhóm nghề sang editor. Không có lỗi JavaScript; editor và chi tiết không tràn ngang tại 1440/375/320 px.

Đã xem ảnh editor và chi tiết ở desktop/mobile. Ảnh chỉ chứa hồ sơ QA hư cấu: [form desktop](../screenshots/recruitment-profile-20261021/profile-editor-1440.png), [form mobile](../screenshots/recruitment-profile-20261021/profile-editor-375.png), [chi tiết desktop](../screenshots/recruitment-profile-20261021/profile-detail-1440.png), [chi tiết mobile](../screenshots/recruitment-profile-20261021/profile-detail-375.png).

`dev_schema_check.py` rollback PASS (cách ly hai tổ chức/hai ứng viên, chặn portal write, contact consent/revocation). `homepage_contract_smoke.py` PASS: ba trang chủ HTTP 200 đúng tc-hub/tc-jobs/tc-profiles và ba trang login HTTP 200. Đã dọn các tài khoản QA có prefix riêng cùng hồ sơ/tin/mục con; kiểm tra lại 20 việc làm, 6 hồ sơ đều gắn account hoạt động, 12 offer, đúng 3 mục kinh nghiệm + 3 mục học mẫu. Không còn account QA tạm. Không push hoặc triển khai production.

Đối chiếu bản dump trước thay đổi phiên này cũng có đúng 6 hồ sơ (hai hồ sơ cho mỗi tài khoản mẫu); ID/chủ hồ sơ hiện tại trùng bản backup. Con số 7 trong ghi chép phiên trước không phải số lượng tại thời điểm backup lần này.
