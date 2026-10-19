# Kho việc làm: đối chiếu yêu cầu và mã Odoo 19 DEV

> **20/10/2026:** [làm lại Tủ và hỗ trợ nhiều hồ sơ](research/implementation_profile_refresh_2026-10-20.md). Ứng viên chọn hồ sơ tuyển dụng cụ thể khi xem tin và đối chiếu. Quyền, kỹ năng và consent vẫn theo hồ sơ được chọn. Nhãn điều hướng Kho đổi thành “Đăng việc” / “Quản lý tin”; bỏ mũi tên trang trí. Luồng F01–F12 vẫn là tuyển dụng.

> **Bổ sung local 19/10/2026:** [nhánh Việc linh hoạt](research/implementation_flexible_demo_2026-10-19.md) có form/lifecycle riêng và hiển thị chung trong Kho. Bảng F01–F12 tiếp tục mô tả **tuyển dụng**; không xem quy trình cá nhân đăng việc là quyền quản lý tuyển dụng của tổ chức. Các kiểm tra hồi quy tuyển dụng/consent vẫn được chạy. Nhánh mới tắt matching, dùng địa chỉ tĩnh và quyền sở hữu bản ghi.


Nguồn: *Kho việc làm.docx*, mục “Vai trò”, các bảng F01–F12; *BÁO CÁO PHÂN TÍCH VÀ ĐỀ XUẤT CẤU TRÚC DỮ LIỆU HỆ T.docx*, phần bốn nhóm ngành và các ví dụ đối chiếu; `docs/database_mapping.md` và addon hiện có. “Đang tạo”, “Đang kiểm tra”, “Đang chỉnh sửa” trong bảng là bước giao diện, không phải trạng thái lưu DB. Ví dụ tên doanh nghiệp, lương và hồ sơ không phải dữ liệu vận hành hoặc quy tắc xét tuyển.

| Yêu cầu / vị trí | Màn hình | Model / trường | Quyền | Điều kiện → kết quả | Hiện có / bổ sung | Cách kiểm tra |
| --- | --- | --- | --- | --- | --- | --- |
| F01, bảng 2 | Form tin | `hr.job`, `tacare_status` | Quản lý tin của tổ chức | Có tên tối thiểu → nháp | Có form; mở rộng trường cấu trúc, kiểm tra chủ | Lưu nháp thiếu trường đăng, tải lại |
| F02, bảng 3 | Xem trước, chi tiết | `hr.job` | Quản lý tin | Nháp + đủ trường → hiển thị | Có chuyển trạng thái; bổ sung xác nhận và kiểm tra thống nhất | Đăng thiếu/đủ trường |
| F03, bảng 4 | Form, lịch sử | `hr.job`, `care.job.revision`, nhật ký | Quản lý tin | Mọi trạng thái, giữ nguyên trạng thái; bản công khai qua duyệt hiện có | Có revision; mở sửa tin đóng, ghi thao tác | Sửa, kiểm tra lịch sử và trạng thái |
| F04, bảng 5 | Chi tiết/quản lý | `hr.job` | Quản lý tin | Hiển thị → tạm ngừng; kết nối cũ giữ nguyên | Có; bổ sung xác nhận | Dừng, kiểm tra tin công khai/kết nối |
| F05, bảng 6 | Chi tiết/quản lý | `hr.job` | Quản lý tin | Tạm ngừng + xác nhận còn nhu cầu + kiểm tra → hiển thị | Có chuyển trạng thái; bổ sung xác nhận | Mở lại thiếu/đủ dữ liệu |
| F06, bảng 7 | Chi tiết/quản lý | `hr.job`, `tacare.connection` | Quản lý tin | Hiển thị/tạm ngừng → đóng; cảnh báo kết nối chờ, giữ nguyên | Có chuyển trạng thái; bổ sung cảnh báo | Đóng với kết nối chờ |
| F07, bảng 8 | Chi tiết/quản lý | `hr.job` | Quản lý tin | Đóng + xác nhận còn nhu cầu + kiểm tra → hiển thị | Chưa có; bổ sung | Mở lại tin đóng |
| F08, bảng 9 | Quản lý | `hr.job` | Quản lý tin | Chỉ nháp → xóa | Chưa có; bổ sung | Xóa nháp / chặn xóa tin đăng |
| F09, bảng 10 | Gợi ý, chi tiết hồ sơ | `tacare.profile`, `care.consent`, minh chứng | Nhân sự xử lý ứng viên | Hồ sơ liên quan + consent → chỉ dữ liệu được phép; email cần consent riêng | Có discovery/matching; thu hẹp theo quyền tổ chức, không gửi email khi chưa cấp | Truy cập URL chéo, rà HTML/email |
| F10, bảng 11 | Gợi ý, lời mời | `tacare.connection` invitation | Nhân sự xử lý ứng viên | Tin hiển thị, nội dung, consent; không trùng chờ → pending | Có route; thêm quyền riêng, chống trùng cùng loại | Gửi hợp lệ/trùng/tin dừng |
| F11, bảng 12 | Đề nghị nhận/chi tiết | `tacare.connection` application | Nhân sự xử lý ứng viên của tổ chức | Pending → accepted/declined, kể cả tin đã dừng; không xử lý lại | Có phản hồi cho receiver duy nhất; mở đúng nhân sự được cấp quyền | Hai HR, xử lý lại, tổ chức khác |
| F12, bảng 13 | Lời mời gửi/chi tiết | `tacare.connection` invitation | Người gửi còn quyền xử lý | Pending → cancelled; không rút kết nối đã có kết quả | Có hủy generic; giới hạn invitation và quyền | Rút pending / chặn accepted |

## Thiết kế biểu mẫu

**Cập nhật v2 17/10/2026:** form chính dùng mô tả/yêu cầu/quyền lợi, kỹ năng chung có chọn bắt buộc và phần điều kiện bổ sung mở rộng. Đăng tin chấp nhận đào tạo không bị ép tạo một điều kiện bắt buộc. Nhóm nghề, tỉnh/thành, thời lượng và yêu cầu ứng viên được kiểm tra khi đăng tin v2. Hạn ứng tuyển có thể trước ngày bắt đầu. Các dòng `care.job.requirement` cũ được giữ để tương thích, không còn là bảng phải nhập trong form mới. Xem [triển khai và kiểm thử hiện hành](research/implementation_forms_homepages_2026-10-17.md). Đoạn tiếp theo mô tả phiên bản đầu trước v2.

`hr.job` chuẩn chứa tên, số lượng, mô tả, company, website; `hr.job.skill` chuẩn chứa kỹ năng. `tacare_sector` cũ giữ tương thích; danh mục ngành mới có thể mở rộng mà không thêm mã selection. `care.job.requirement` lưu từng điều kiện với loại và mức bắt buộc/ưu tiên, thay vì một JSON dài. Lĩnh vực doanh nghiệp (`res.partner`), chuyên ngành học (dòng yêu cầu) và vị trí tuyển dụng (`hr.job`) tách riêng. Hình thức làm việc, thời lượng, lịch và ca tách riêng. Chỉ tên cần để lưu nháp; đăng tin cần tổ chức, vị trí, ngành, loại, hình thức, địa điểm hoặc remote, mô tả, hạn và ít nhất một điều kiện bắt buộc. Các trường đặc thù ngành là tùy chọn; ví dụ thương mại điện tử/kinh doanh/marketing/y tế kiểm tra khả năng nhập, không tự đặt chính sách loại ứng viên.

## Điểm cần chốt trước vận hành chính thức

- Cách cấp quyền mở email vẫn theo `care.consent` riêng cho đúng tổ chức và kết nối đã chấp nhận. Không suy diễn từ kết quả phản hồi.
- Công thức điểm phù hợp cũ trong giao diện là mô phỏng chưa được tài liệu chốt; bỏ điểm phần trăm ở Kho việc làm. Hiển thị căn cứ đã có, chưa đủ thông tin và ưu tiên.
- Bản sửa tin công khai vẫn theo cơ chế `care.job.revision` chờ quản trị hiện có; tài liệu chỉ yêu cầu ghi lịch sử, không quy định bước duyệt. Giữ cơ chế đang chạy tới khi có quyết định khác.
- Membership cũ không có cờ quyền riêng; `owner` có hai quyền và `recruiter` giữ quyền xử lý ứng viên. Các tổ hợp khác do quản trị cấp; fallback tài khoản doanh nghiệp cũ giữ đến khi có migration membership được duyệt.

## Kết quả kiểm tra DEV

| Luồng | Kết quả HTTP với tài khoản QA giả | Nhánh lỗi đã kiểm tra |
| --- | --- | --- |
| F01 | Lưu nháp thiếu dữ liệu đăng, tải lại được | Người chỉ xử lý ứng viên không tạo được tin |
| F02 | Đăng tin đủ điều kiện, hiện công khai | Tin thiếu điều kiện bị chặn; form trả lỗi cạnh trường và giữ input |
| F03 | Sửa tin công khai tạo revision, quản trị duyệt, lịch sử hiện thay đổi | Trạng thái tin giữ nguyên khi gửi duyệt |
| F04 | Tin hiển thị → tạm ngừng | Không còn ở URL công khai, chặn đề nghị mới |
| F05 | Tin tạm ngừng → hiển thị | Cần xác nhận và kiểm tra dữ liệu hiện hành |
| F06 | Tin → đóng, lời mời cũ giữ pending | Chặn lời mời mới |
| F07 | Tin đóng → hiển thị | Cần xác nhận và kiểm tra dữ liệu hiện hành |
| F08 | Xóa được bản nháp | Tin đã đăng không xóa được |
| F09 | Nhân sự xem danh sách, chi tiết và căn cứ | URL doanh nghiệp khác/quản lý tin không có quyền bị 403; email/minh chứng riêng tư vắng trong HTML |
| F10 | Gửi lời mời pending | Chặn trùng pending, tổ chức khác và tin dừng |
| F11 | Nhân sự xử lý đơn cũ khi tin tạm ngừng | Chặn xử lý lại đơn đã accepted |
| F12 | Người gửi rút lời mời pending | Chặn rút lần hai |

Kiểm tra ORM rollback-only xác nhận cả bốn ngành mẫu nhập được điều kiện có cấu trúc và chặn lịch tuần ngoài 0–7. Tài khoản/tin/hồ sơ QA đã được xóa sau kiểm tra; nhật ký `care.audit.event` là append-only nên các sự kiện QA vẫn nằm trong DEV dưới dạng tham chiếu bản ghi đã xóa. Không có kiểm tra production.
