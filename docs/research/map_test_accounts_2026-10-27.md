# Tài khoản theo nhóm nghề và nhiều hồ sơ thử bản đồ — 27/10/2026

Chủ dự án yêu cầu đổi tên/mật khẩu tài khoản để nhận biết nghề và dùng các tài khoản có sẵn tạo nhiều hồ sơ cùng nghề, khác nội dung, nhằm thử bản đồ. Đây là ngoại lệ mới cho việc tạo dữ liệu thử local; không khôi phục helper seed cũ, không tạo tài khoản/liên hệ mới hoặc hồ sơ độc lập không có chủ. Chỉ tác động `tacare_local` cùng ba website localhost; không commit/push/deploy.

## Tài khoản

Đổi login, tên hiển thị và mật khẩu của đúng 5 tài khoản bên cần người + 3 tài khoản cá nhân đã có. Giữ nguyên user/partner IDs, vai trò, công ty và nhóm quyền. Không đổi tài khoản quản trị hoặc tài khoản ngoài danh sách.

| Bên cần người | Nhóm nghề |
| --- | --- |
| `nhacua-thucung@khovieclam.vn` | Dọn dẹp, nấu ăn, thú cưng |
| `vuon-nongtrai@khovieclam.vn` | Làm vườn, nông trại |
| `suachua-bocxep@khovieclam.vn` | Sửa chữa, bốc xếp; giữ tin lịch sử khác của cùng chủ |
| `noidungso@khovieclam.vn` | Nội dung số |
| `giasu@khovieclam.vn` | Gia sư |

| Bên nhận việc | Nhóm nghề trong các hồ sơ thử |
| --- | --- |
| `dondep-vuon-giasu@tuhoso.com` | Dọn dẹp, làm vườn, gia sư |
| `nauan-nongtrai-noidungso@tuhoso.com` | Nấu ăn, nông trại, nội dung số |
| `bocxep-suachua-thucung@tuhoso.com` | Bốc xếp, sửa chữa, thú cưng |

Nhóm nghề giữ theo các hồ sơ hiện có của từng chủ; không chuyển hồ sơ giữa tài khoản để gom thành một nghề duy nhất. Login khác email liên hệ; không đổi email liên hệ hay tổ chức. Password mới sinh ngẫu nhiên khi chạy và chỉ lưu trong ignored `runtime/tacare/map_test_accounts_20261027/TAI_KHOAN_TEST_20261027.md` cùng JSON riêng tư quyền 0600, thư mục 0700. Không đưa password vào tài liệu nguồn, fixtures hay log. SSO families cũ của đúng tám user được thu hồi và cần đăng nhập lại. Dùng ORM native để hash password; trong thao tác bảo trì local này có chặn callback gửi security-alert email, không sửa core hoặc tắt thông báo trên ứng dụng.

## Hồ sơ mới

Tạo **27 hồ sơ, mỗi nghề 3 hồ sơ**, trên ba user cá nhân cũ. Mỗi hồ sơ có một mục nhận làm cụ thể và name cùng chủ tài khoản; không tạo ra ba người khác nhau. Title, mô tả, phạm vi, cách chuẩn bị và mức tiền công khác nhau. Giá/nội dung được biên soạn riêng cho thử nghiệm; không tự sao chép kỹ năng, lịch hay tiền công từ source-job. Lịch mới là linh hoạt, cần hẹn/xác nhận; không hứa ngày trống hoặc bịa chứng chỉ/đánh giá.

- 24 hồ sơ trực tiếp thuộc 8 nghề có vị trí thử quanh tin nguồn hiện có, ở khoảng 1,4 / 4,1 / 8,2 km. Ba điểm của mỗi nghề nằm ở ba ô geohash hiển thị khác nhau. `geo_sample=True`; nhãn điểm thử và địa chỉ mô tả khu vực, không dựng số nhà/đường giả. `flex_location` và `geo_address` đồng bộ, URL/geohash do server tính.
- 3 hồ sơ nội dung số là làm từ xa, không ép tọa độ để làm đầy bản đồ; vẫn dùng matching thông thường.
- Chỉ các hồ sơ mới bật scope members + visible và có discovery/matching grant của đúng chủ, đúng tổ chức liên quan tới tin nguồn, thời hạn 14 ngày. Không có contact grant, không mở public/guest và không thay consent cũ. Mỗi lần xem vẫn qua thuật toán và authorization hiện có; không chèn kết quả giả hay đổi rank.
- Giữ nguyên mọi tin cũ, profile/offer IDs và owners/nội dung/quyền chia sẻ cũ. Ba hồ sơ gốc riêng tư vẫn riêng tư. Snapshot hash kiểm tra dùng relational IDs thay vì tên hiển thị, tránh coi đổi tên account là đổi chủ hồ sơ.

Sau áp dụng: **15 tin, 42 hồ sơ, 51 mục nhận làm**. Không thêm user/partner. Các ảnh hiện có dùng lại theo catalog, không thêm ảnh giả/chân dung.

## Công cụ và bảo toàn

`tools/map_test_profiles.py` là helper chạy tay, preview mặc định, chỉ nhận DB/domain local. Có guard không chạy lặp/không tự xoay password lần nữa. Helper cũ `matching_demo.py` chỉ cập nhật cách tìm lại đúng ba account qua alias cũ/mới; vẫn không tạo hoặc khôi phục dữ liệu cũ.

Backup trước áp dụng: ignored `backups/map_accounts_20261027/tacare_local.dump` và `filestore.tar.gz`, đã kiểm tra `pg_restore --list` / `tar -tzf`; thư mục 0700, dump/archive 0600. Chạy toàn bộ một lần ở giao dịch rollback trước khi apply. Guard so sánh hash dữ liệu profile/offer/consent cũ, account ngoài danh sách và shape quyền của account được chọn; không tạo mail. Receipt IDs mới riêng tư nằm cùng thư mục credential, không có password trong audit. Không tự chạy lại helper vị trí hoặc các seed lịch sử. Release/full-restore artifacts trước đây vẫn stale và phải chuẩn bị/kiểm tra lại khi chủ dự án yêu cầu phát hành.

## Kiểm tra đã chạy

- Python AST, Node syntax, repository credential scanner và `git diff --check`: PASS.
- Full rollback rehearsal và apply local: PASS; verify password hash mới của tám user, tất cả guard bảo toàn dữ liệu cũ đạt.
- `tests/dev_map_test_profiles_check.py`: 27 hồ sơ thuộc đúng ba account; 24 có map/3 remote; ba nội dung/giá khác nhau mỗi nghề; actual matching và winning offer hai chiều; đúng 1/2/3 hồ sơ mới khi radius 2/5/10 km; ba ô gần đúng khác nhau; exact-organization consent có hạn, không contact; thu hồi và guest/foreign denial; probes rollback: PASS.
- `tests/map_test_accounts_browser_check.cjs`: đăng nhập native cả tám account/password mới, tên hiện đúng, SSO đúng site, mở đủ 27 hồ sơ theo chủ, chặn hồ sơ khác chủ, map hai chiều + nhiều source/nghề, remote exclusion, 375/1440: PASS. Không ghi dữ liệu nghiệp vụ.
- `tests/dev_nearby_check.py`, `tests/dev_matching_preview_check.py`, `tests/dev_work_review_check.py`: PASS sau đổi login; tất cả rollback. Các kiểm tra dùng alias cũ/mới để vẫn tìm đúng user IDs, không tạo người thay thế.
- Ảnh local đã xem tại ignored `runtime/map-accounts-review/`. Sau resize, dùng **Xem toàn bộ** để khung mới bao trọn các điểm; giữ hành vi bảo toàn camera hiện có.
- Chrome riêng nút **Xem toàn bộ** xác nhận cả bốn icon kết quả nằm trong khung ở 375/1440; cả ba homepage/login vẫn HTTP 200/đúng marker. Kiểm tra credential/receipt riêng tư: tám user/login/password khác nhau, 27 IDs, quyền file đúng 0600; không in mật khẩu.

Không có thay đổi thuật toán, privacy projection, routes, schema hoặc giao diện trong đợt dữ liệu này. Không có GPS liên tục, first-accept dispatch, booking hoặc thanh toán.
