> Cập nhật tiếp: phần thiết kế TA.CARE và quyền 3/3 của tài liệu này đã được thay thế theo yêu cầu mới. Xem [khôi phục giao diện và đăng nhập](implementation_auth_restore_2026-10-20.md).

# Làm lại Tủ Hồ Sơ, ảnh và điều hướng — demo local 20/10/2026

Đợt triển khai theo góp ý ảnh chụp của chủ dự án. Thay đổi trên Odoo Community 19, database `tacare_local`; không push/deploy hoặc thay đổi production.

## Xem bản mới

| Màn hình | URL |
| --- | --- |
| Kho Việc Làm | http://khovieclam.localhost:8069/ |
| Tủ Hồ Sơ: khách xem giới thiệu; đăng nhập thấy hồ sơ ngay | http://tuhoso.localhost:8069/ |
| Hồ sơ thuộc tài khoản hiện tại | http://tuhoso.localhost:8069/tuhoso/profiles?scope=mine |
| Toàn bộ hồ sơ, chỉ admin | http://tuhoso.localhost:8069/tuhoso/profiles?scope=all |
| Tạo một hồ sơ mới | http://tuhoso.localhost:8069/tuhoso/profiles/new |
| TA.CARE | http://tacare.localhost:8069/ |

Hai tài khoản được yêu cầu đã tạo: **`ungvien1@tacare.vn`** và **`ungvien2@tacare.vn`**, dùng mật khẩu do chủ dự án cung cấp. Không ghi mật khẩu vào source, tài liệu hoặc ảnh chụp. Các tài khoản chia sẻ backend nhưng phiên trình duyệt vẫn theo từng domain.

## Giao diện và nội dung

**Tủ Hồ Sơ đã thay phần trình bày cũ.** Bỏ chuỗi nội dung bộ sưu tập/ghi chép, nhân vật mẫu, dự án thiết kế và lời dẫn dài. Khách xem giới thiệu ngắn, hai mục đích tạo hồ sơ, ba bước sử dụng. Sau đăng nhập, thư viện thật xuất hiện đầu trang; phần giới thiệu/carousel ở dưới. Không lấy thư viện hồ sơ của người khác làm nội dung công khai.

Thư viện có tên hồ sơ, tên người sở hữu, loại hồ sơ, tóm tắt liên quan, thông tin đã khai và các thao tác. Từ thư viện có thể mở chi tiết, chỉnh sửa hồ sơ tuyển dụng hoặc thêm việc nhận làm vào hồ sơ linh hoạt. Bộ lọc thu gọn để nội dung hồ sơ được ưu tiên; mở lọc sẽ giữ lựa chọn đang dùng.

Người thường mặc định thấy **tất cả hồ sơ của chính mình**, rồi chọn tuyển dụng/việc linh hoạt. Đây là sửa nguyên nhân màn hình trống trước đó: tài khoản có hồ sơ linh hoạt nhưng trang cũ mặc định lọc tuyển dụng. Admin có hai tab **Hồ sơ của tôi / Tất cả hồ sơ**, mặc định xem tất cả. Người thường yêu cầu trực tiếp `scope=all` bị chặn ở máy chủ.

**Kho Việc Làm:** đổi hai thao tác đầu trang thành **Đăng việc / Quản lý tin**. Loại bỏ ký tự mũi tên trang trí khỏi phần nội dung QWeb tùy biến. Menu, tab, bộ lọc và điều khiển carousel có trạng thái đang chọn, hover, focus và nhấn rõ ràng. Trang quản lý việc linh hoạt có lối sang quản lý tin tuyển dụng hiện có.

**TA.CARE:** thay bố cục cũ bằng giới thiệu ngắn, ba vai trò trong hệ sinh thái, phần đối chiếu thông tin, giải đáp và liên kết. Bỏ carousel, hình nổi, bộ câu chuyện cuộn và đường cong trong ảnh góp ý. Phần đối chiếu hiện là ba khối thẳng hàng: công việc/năng lực, điều kiện, thông tin cần bổ sung. Không khẳng định dữ liệu chưa khai là không đáp ứng.

### Ảnh và carousel

Tái sử dụng các ảnh chụp đã tải từ Unsplash và có nguồn trong [PHOTO_SOURCES.md](../../source/apps/tacare/addons/tacare_website/static/src/img/PHOTO_SOURCES.md); không tạo ảnh AI trong đợt này. Ảnh stock minh họa nội dung, không phải minh chứng tay nghề của các hồ sơ demo.

| Website | Ảnh hiện dùng trong phần chính | Cấu trúc |
| --- | --- | --- |
| Kho | `work-team`, `work-cleaning`, `work-warehouse`, `work-tools` | Bốn ảnh ngang, chữ và liên kết nằm trên ảnh, nền điều khiển tối |
| Tủ | `work-digital`, `work-craft`, `work-cooking` | Ba ảnh, chú thích riêng bên dưới ảnh, điều khiển sáng; giới thiệu nằm cạnh carousel |
| TA.CARE | `work-team` | Một ảnh tĩnh cạnh phần giới thiệu; không carousel |

Hai bộ ảnh carousel không trùng nhau. Cùng giữ chức năng trước/sau, chọn ảnh, tạm dừng, bàn phím, dừng khi focus/hover/ẩn tab và giảm chuyển động. Đã kiểm tra chữ nằm trong khung ở 320px, không chỉ kiểm tra tổng chiều rộng trang.

## Nhiều hồ sơ cho một ứng viên

Theo yêu cầu mới, **một user có nhiều `tacare.profile`**. Thay quyết định cũ giữ một hồ sơ/user; không tạo model hồ sơ song song.

- Thêm `profile_title` để đặt tên từng hồ sơ; `name` vẫn là tên người sở hữu.
- Migration `19.0.6.0.0/pre-migrate.py` gỡ đúng constraint `tacare_profile_unique_user`. Không đổi ID hồ sơ, FK, tên model hay dữ liệu hiện có.
- Mỗi bộ kỹ năng, minh chứng, capability, consent và kết nối tiếp tục thuộc đúng `profile_id`.
- Form hồ sơ và các form kỹ năng/minh chứng/chia sẻ mang ID hồ sơ cụ thể. User có nhiều hồ sơ mà POST ghi thiếu ID bị từ chối, tránh cập nhật ngầm hồ sơ đầu tiên.
- Controller tra cứu theo owner + company trước khi dùng `sudo()`. URL hồ sơ/công việc nhận làm của tài khoản khác trả 404; ghi chéo bị chặn. Portal vẫn không có ACL tạo/sửa trực tiếp.
- Tạo công việc nhận làm có bộ chọn hồ sơ của chính tài khoản. Sửa mục nhận việc giữ nguyên hồ sơ cha; không cho đổi cha bằng cách giả trường POST.
- Ở chi tiết tin tuyển dụng và trang đối chiếu, ứng viên chọn hồ sơ tuyển dụng cụ thể. Consent vẫn được kiểm tra theo hồ sơ đó; không lấy quyền chia sẻ của hồ sơ này dùng cho hồ sơ khác.

Chưa bổ sung matching mới cho việc linh hoạt. Không đưa các công việc linh hoạt vào thuật toán tuyển dụng cũ.

## Dữ liệu hiện có

Giữ **20 tin công việc cũ: 5 tuyển dụng + 15 linh hoạt** và toàn bộ 15 hồ sơ demo đã có. Một hồ sơ quản trị đã phát sinh trước đợt sửa cũng được giữ nguyên. Thêm bốn hồ sơ theo hai tài khoản mới:

| Tài khoản | Hồ sơ tuyển dụng | Hồ sơ nhận việc |
| --- | --- | --- |
| Ứng viên 1 | Ứng tuyển Frontend Junior | Nhận chăm cây cuối tuần |
| Ứng viên 2 | Ứng tuyển Content Marketing | Dọn nhà theo giờ |

Sau dọn QA: **20 job, 20 profile, 12 capability**. Trong 20 hồ sơ có 8 hồ sơ tuyển dụng và 12 hồ sơ linh hoạt ở dữ liệu hiện tại. Mỗi tài khoản mới có đúng hai hồ sơ. Tài khoản và nội dung thử là dữ liệu demo; không tạo đánh giá hoặc dấu xác minh giả.

Các login, hash mật khẩu, active và role của **toàn bộ tài khoản khác** được so sánh dấu vân tay trước/sau và giữ nguyên. File chứa mật khẩu đầu vào chỉ ở runtime gitignored, quyền 0600. Seed và cleanup là script thủ công local; không chạy khi cài addon hoặc deploy.

## Code chính

- Model: `models/profile.py`; migration phiên bản `19.0.6.0.0`.
- Controller thư viện/tạo/chi tiết: `controllers/profiles.py` kế thừa controller hiện có.
- `controllers/live.py`: chọn profile ID, form con và redirect đúng hồ sơ.
- `controllers/flexible_work.py`: chọn hồ sơ khi tạo mục nhận việc và giữ hồ sơ cha khi sửa.
- QWeb: `views/profile_workspace.xml`, `views/work_homepages.xml`, `views/home_hub.xml`, điều chỉnh nhãn và context ở các view hiện có.
- SCSS/JS: `profile_refresh.scss`, `navigation.js`; tái sử dụng JS carousel hiện có với hai thành phần giao diện khác nhau.

## Kiểm tra

Các kiểm tra trên local, không dùng production:

- Nâng addon và migration; registry/XML nạp thành công. Có sửa thứ tự validation của view kế thừa cũ khi thay trang TA.CARE và sửa điều kiện chọn nav trong bước nạp thử; lỗi nạp đầu đã rollback.
- Python AST, XML parse, `node --check`, `git diff --check`.
- `homepages_browser_check.cjs` — PASS: ba trang chủ tại 1440/768/375/320px; marker, ảnh/font, anchor, không tràn ngang; Kho có chọn lĩnh vực, Tủ carousel có reduced motion, TA.CARE tĩnh.
- `profile_refresh_browser_check.cjs` — PASS: đăng nhập hai tài khoản mới; chỉ thấy hai hồ sơ của mình; tab admin; tạo hồ sơ thứ ba, lưu/đọc lại; lỗi dữ liệu giữ nội dung; ghi thiếu ID/chéo owner bị chặn; kỹ năng độc lập; chọn hồ sơ nhận việc và chặn đổi cha; các trang/form ở bốn chiều rộng. QA được dọn theo ID sau kiểm tra.
- `dev_profile_library_check.py` — PASS: rollback; nhiều profile trên một user; ACL/rule; kỹ năng và consent riêng; giữ ID hồ sơ demo cũ và thông tin tài khoản khác.
- `dev_schema_check.py`, `dev_forms_v2_check.py`, `dev_flexible_check.py`: hồi quy tuyển dụng, tổ chức, consent, kiểu dữ liệu, alias và quyền portal — PASS.
- `flexible_work_browser_check.cjs` — PASS: hồi quy tin công khai 20/5/15, bộ lọc, owner/admin, tạo/sửa/đăng/tạm ngừng, ảnh lỗi/ảnh hợp lệ và chặn truy cập/POST chéo. Dọn đúng tin/mục nhận việc QA sau test, không xóa các hồ sơ người dùng.
- `profile_visual_check.cjs` — PASS: kiểm tra bộ ảnh khác nhau, không còn mũi tên trang trí, chữ carousel không tràn khung, menu chọn đúng trên danh sách/chi tiết/tạo/quản lý, bộ chọn hồ sơ trong tuyển dụng và đối chiếu; chụp thư viện sạch sau QA.

Ảnh kiểm tra tại [screenshots/profile-refresh-20261020](../screenshots/profile-refresh-20261020). Ảnh thư viện admin che một thẻ hồ sơ có từ trước để không đưa thông tin riêng vào artifact; số đếm vẫn giữ nguyên.

## Backup và giới hạn

Backup trước thay đổi tại `backups/profile_refresh_20261020/`: source, diff đang có, PostgreSQL dump và filestore. Không restore toàn DB cho một thay đổi giao diện vì sẽ ghi đè dữ liệu phát sinh sau backup. Việc quay lại constraint một hồ sơ/user không thể làm trực tiếp khi đã có nhiều hồ sơ; cần xử lý dữ liệu riêng nếu sau này đổi quyết định.

Chưa có map/geocoding, matching linh hoạt, đặt lịch, thanh toán, xác minh ảnh/tay nghề/xe hoặc đăng nhập một lần giữa các domain. Địa chỉ vẫn là thông tin tĩnh do người đăng khai báo. Không thay đổi production, DNS/TLS hoặc dịch vụ ngoài local trong đợt này.
