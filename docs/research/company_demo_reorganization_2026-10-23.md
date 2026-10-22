# Phân công ty và doanh nghiệp demo — 23/10/2026

Chủ dự án chọn thay toàn bộ dữ liệu server bằng bản local sau backup, rồi yêu cầu sắp xếp các liên hệ demo đang để lẫn ở TAA. Việc dưới đây đã áp dụng trên local; chưa có kết nối hoặc thay đổi server.

## Dữ liệu và cấu trúc

Giữ cây công ty Odoo sẵn có: TAA là mẹ, TACARE / KHO VIEC LAM / TU HO SO là ba đơn vị con. Website TA.CARE trước đó gắn TAA nay gắn đúng TACARE và một public user riêng chỉ có nhóm public. Hai website còn lại giữ đúng công ty cũ.

Tạo năm doanh nghiệp **hư cấu** dưới phạm vi KHO VIEC LAM, bằng `res.partner.is_company` và tài khoản portal có membership owner đang hoạt động. Không tạo thêm năm công ty Odoo:

| Doanh nghiệp mẫu | Tài khoản | Nhóm tin thời vụ |
| --- | --- | --- |
| Dịch vụ Nhà Việt · Demo | `nhaviet.demo@khovieclam.vn` | Dọn nhà, nấu ăn, thú cưng |
| Cảnh quan Vườn Xanh · Demo | `vuonxanh.demo@khovieclam.vn` | Vườn, nông nghiệp |
| Dịch vụ Tiện Ích · Demo | `tienich.demo@khovieclam.vn` | Chuyển đồ, sửa chữa, theo chuyến |
| Xưởng Sáng Tạo Số · Demo | `sangtao.demo@khovieclam.vn` | Việc số |
| Không gian Học Tốt · Demo | `hoctot.demo@khovieclam.vn` | Dạy kèm |

Mật khẩu ban đầu cho tài khoản doanh nghiệp mới được tạo theo quy tắc chủ dự án yêu cầu, tính khi tạo và không ghi literal mật khẩu/hash vào source, tài liệu hoặc log. Khi chạy lại công cụ không đặt lại mật khẩu các account đã tạo.

Giữ 15 tin thời vụ và ID/nội dung của chúng, chuyển company sang Kho và phân chủ tin/tổ chức theo nhóm ở trên. Đây là các tin demo được chủ dự án cho phép phân lại, đã kiểm tra không có kết nối hoặc lịch sử phụ thuộc trước khi chuyển. HOZOTA cùng các tài khoản gốc vẫn giữ; không dùng tài khoản HOZOTA đứng tên toàn bộ các ví dụ nữa.

Giữ 16 liên hệ cũ (15 dòng Hồ sơ demo và một liên hệ điều phối), đổi tên phù hợp thành Mẫu dịch vụ và gắn dưới doanh nghiệp tương ứng, đặt `company_id` Kho. Các login `demo-flex-00` đến `demo-flex-15` được lưu trữ, thu hồi nhóm SSO; **không xóa user hoặc partner**, partner vẫn active để tra cứu. Tài khoản demo quản trị `demo-flex-99` không nằm trong nhóm này và được giữ nguyên.

Giữ ba hồ sơ của `ungvien1`, `ungvien2`, `student.test` cùng 12 mục nhận làm, đúng ID/chủ cũ. Tài khoản cá nhân có main company Tủ; cấp thêm phạm vi Kho để đăng nhu cầu thời vụ. Profile/children vẫn liên kết company theo owner; không đổi schema. Các mật khẩu gốc được đối chiếu fingerprint trước/sau và giữ nguyên.

Danh sách liên hệ Odoo thêm cột Công ty vận hành và Doanh nghiệp / tổ chức để phân biệt hai khái niệm. Quản trị chọn TAA cùng các công ty con vẫn có thể xem tổng hợp theo quy tắc Odoo; không dùng việc ẩn dòng để giả lập phân quyền.

## Code và quyền

`tools/company_demo.py` là công cụ thủ công local-only, preview mặc định, yêu cầu receipt backup DB+filestore đã khôi phục thử khi apply. Không có install hook hoặc route chạy nó. Membership được gắn rõ công ty/tổ chức/user; lần chạy lại không tạo bản sao. Lần apply thực tế đã commit transaction sau kiểm tra toàn vẹn.

Nâng addon website lên `19.0.14.0.0`. Các lookup tin/kết nối/hồ sơ của tài khoản dùng danh sách công ty được cấp, kèm owner/organization checks, thay vì chỉ công ty active của website. Discovery giữa Kho và Tủ chỉ tìm trong công ty Tủ và vẫn lọc consent đúng purpose/recipient/field; admin vẫn bị giới hạn bởi company được cấp. Luồng gửi lời mời cho phép tin Kho/hồ sơ Tủ sau các kiểm tra đó. Tạo nhu cầu luôn ghi company Kho được cấp, kể cả khi gọi từ hub. Chỉnh tin flexible của doanh nghiệp dùng cùng membership capability check như `_own_job`, chặn cả chủ tin có membership đã bị đình chỉ. ACL portal vẫn read-only, không mở thư viện cá nhân cho doanh nghiệp.

## Kiểm chứng và phát hành

Backup trước sắp xếp là `backups/full_local_release_20261022T194854Z/`, ngoài Git, đã restore thử và kiểm tra đủ các tệp attachment tham chiếu. Diễn tập reorganization trong transaction rollback đạt trước khi apply thật. Lần preview đầu vướng cơ chế clone public user của Odoo; đã chuyển sang tạo public user riêng có nhóm public rõ ràng, không sửa core.

Upgrade local `tacare_account_access,tacare_website` exit 0, restart. `dev_company_scope_check.py` rollback đạt cho năm account, ACL hồ sơ riêng, hai doanh nghiệp không sửa chéo, membership suspended bị chặn, chọn đúng hồ sơ từ công ty Kho, discovery theo tổ chức/thu hồi và người tham gia kết nối giữa công ty. Test chỉ đọc hash trong bộ nhớ để kiểm quy tắc password mới, không in hash hoặc mật khẩu. Không có consent của kiểm tra được giữ lại.

`dev_seasonal_scope_check.py` rollback đạt các chặn tuyển dụng/context defaults/portal writes và membership cũ. `seasonal_browser_check.cjs` bản cuối exit 0: ba homepage, responsive 320/375/1440, form cá nhân/doanh nghiệp và giữ input lỗi, C2C, gửi/nhận lời mời, chặn người gửi tự nhận, consent liên hệ cấp/thu hồi đúng bên thuê, route tuyển dụng bị chặn, admin chỉnh hồ sơ, ba ví dụ và tạo hồ sơ thời vụ. Bổ sung ca doanh nghiệp company Kho tìm thấy hồ sơ được chia sẻ ở company Tủ, gửi lời mời và người nhận chấp nhận; không lỗi JavaScript.

Chrome `/tmp/tacare-company-businesses.cjs` bản cuối exit 0: đăng nhập thực tế cả năm doanh nghiệp mới bằng quy tắc đã yêu cầu, kiểm đúng số tin riêng 3/4/4/2/2, sửa tin doanh nghiệp khác bị 403. Tài khoản doanh nghiệp mở namespace thư viện Tủ bị chuyển về home báo `reason=role` theo guard hiện có (có thể có tiền tố ngôn ngữ), không render hồ sơ riêng. Ba homepage public giữ đủ marker deploy. Các kỳ vọng 403 trực tiếp cho namespace và tên hồ sơ hiển thị được sửa trong bài kiểm tra để phản ánh đúng guard/template hiện tại; không nới quyền để làm test đạt.

QA đã dọn: không còn account `qa-seasonal-*`, giữ đúng 15 tin/3 hồ sơ/12 mục nhận làm và audit. Xóa user trong Odoo giữ lại partner, nên lưu trữ riêng 55 contact QA mồ côi của các lượt kiểm thử, không xóa tham chiếu audit hoặc đụng 16 liên hệ demo vừa phân doanh nghiệp. Cleanup helper được cập nhật để không tích lũy các contact đó ở những lượt sau. Tệp credentials QA đã xóa. Diễn tập chạy lại reorganization trong rollback xác nhận không thêm bản sao user/partner/tin/hồ sơ/offer/membership, không đổi password đã tồn tại.

Python AST 82 file, XML 40 file, Node syntax cho bài kiểm tra sửa đổi, security scanner 291 text files và git whitespace đạt trước commit. Không sửa Odoo core. Gói JSON demo cũ không bao phủ năm chủ tin mới và không được dùng để phát hành đợt này. Snapshot trước sắp xếp chỉ dùng rollback local; bản chuyển server phải xuất lại từ trạng thái cuối sau commit, restore thử và kiểm checksum ảnh/tệp, kèm archive addon đúng commit. Metadata riêng nằm ở `runtime/releases/current-full-local-restore.json`, không chọn file theo tên mới nhất. Máy chưa có SSH config/alias hiệu lực `tacare-server` (đã kiểm tra cả `ssh -G`); chưa kiểm tra được script/config đang chạy trên server, chưa chuyển gói hoặc restore production.
