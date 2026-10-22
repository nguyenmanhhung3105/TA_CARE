# Chuẩn bị chuyển code, dữ liệu và ảnh — 23/10/2026

**Quyết định tiếp theo:** chủ dự án đã chọn phương án 2, thay toàn bộ database/filestore server bằng local sau backup server. Sau đó yêu cầu [sắp xếp lại công ty và doanh nghiệp demo](research/company_demo_reorganization_2026-10-23.md). Các snapshot/gói liệt kê trong phần chuẩn bị ban đầu bên dưới là bản **trước sắp xếp**, không dùng làm bản phát hành hiện tại. Thông tin gói đầy đủ sau kiểm tra nằm ở ignored `runtime/releases/current-full-local-restore.json`; chỉ sử dụng khi trạng thái xác minh hoàn tất và source commit khớp code đã chọn. Không nhập JSON demo cũ để thay toàn database.

Chủ dự án yêu cầu đưa cả dữ liệu và hình ảnh local lên server, sau commit `dc1f234`. Đã chuẩn bị và kiểm tra các gói local dưới đây; chưa kết nối, nhập dữ liệu hoặc sửa dịch vụ server. Không coi merge PR mặc định là đã đồng bộ dữ liệu.

## Các gói đã chuẩn bị

| Gói | Vị trí local (ignored) | Phạm vi |
| --- | --- | --- |
| Bản sao đầy đủ | `backups/full_local_release_20261022T194854Z/` | `tacare_local.dump`, `filestore.tar.gz`, manifest và checksum. Bao gồm toàn database và kho tệp của database đó. |
| Gói nội dung thời vụ | Đường dẫn chính xác và SHA256 trong `runtime/releases/current-seasonal-bundle.json` | `tacare.demo.v2`: 4 tài khoản portal được chọn, 15 việc, 3 hồ sơ riêng tư, 12 mục nhận làm. Không phải bản sao toàn database. |
| Bộ cài gate | `runtime/releases/tacare-deploy-modes-v1.tar.gz` | Cần preview với script đang cài trên server trước khi cài/cập nhật; chưa xác nhận server hỗ trợ. |

Database local hiện không còn tin hoặc hồ sơ tuyển dụng. Không có mục kỹ năng/kinh nghiệm/học tập/minh chứng hoặc tài liệu hồ sơ trong bộ local hiện tại; không tạo thêm dữ liệu để làm đầy bản xuất. Gói nội dung không có ảnh binary riêng trên các tin/mục nhận làm và không phát hiện URL localhost hoặc `/web/image`, `/web/content` trong các trường xuất. Ảnh minh họa đang dùng từ assets có nguồn trong addon, đi cùng code.

Các tệp database và gói nội dung có dữ liệu xác thực nên giữ ngoài Git. Không đưa nội dung của chúng vào chat hoặc log. Manifest chỉ là metadata kiểm chứng; không phải quyền tự nhập lên server.

## Kiểm chứng đã chạy

- Dừng Odoo local trong lúc xuất database và filestore, sau đó mở lại. Không sửa bản ghi nghiệp vụ.
- Kiểm tra danh mục `pg_restore`, archive filestore và SHA256.
- Khôi phục database vào một database PostgreSQL local tạm, thành công; số đếm SQL: 28 `res.users` (gồm tài khoản hệ thống/inactive), 15 việc, 3 hồ sơ, 12 mục nhận làm, 773 bản ghi attachment.
- 567 attachment có `store_fname` đều tìm thấy trong filestore, đúng kích thước và SHA1. Archive có tổng 910 tệp; bao gồm cả tệp không còn được tham chiếu. Không thiếu tệp attachment được database backup tham chiếu.
- Thống kê attachment qua ORM mặc định là 274 vì Odoo lọc các attachment của binary field khi không chỉ định `res_field`; số SQL 773 bao gồm các attachment đó. Đây không phải mất dữ liệu trong backup.
- Hai database khôi phục thử đã được xóa sau kiểm tra; database gốc giữ nguyên. Lần đầu dừng ở so sánh số attachment ORM/SQL, lần sau đối chiếu toàn bộ tham chiếu tệp thành công.
- Sau backup, HTTP local qua gateway cổng 8069 trả 200 cho cả ba homepage và giữ đúng `tc-jobs`, `tc-profiles`, `tc-hub`. Lần probe đầu dùng nhầm cổng 80 nên bị connection refused, kiểm tra lại đúng cổng thành công.
- Exporter hiện tại thành công và không in nội dung riêng tư; chín test deploy offline đạt. Test push chỉ tới bare repository tạm local, không phải GitHub hoặc production.

## Quyết định cần chốt trước khi nhập

1. **Giữ dữ liệu server, nhập nội dung local:** dùng gói nội dung theo SHA256, sau khi đối chiếu account/mapping/owner/server edits và gate hiện tại. Giữ tài khoản/mật khẩu đích. Gói không tự xóa dữ liệu tuyển dụng cũ, không chuyển consent/kết nối/audit/cấu hình hoặc mọi tài khoản/tệp upload. Các phần ngoài gói cần kiểm kê và chuẩn bị riêng nếu được chọn. Không gọi đây là đồng bộ toàn bộ.
2. **Thay toàn bộ database và filestore bằng local:** làm server có nội dung theo snapshot local, đồng thời thay tài khoản, mật khẩu và lịch sử bằng bản local; dữ liệu chỉ có trên server không còn trong database đang phục vụ. Cần chủ dự án chọn rõ cách này, backup server hiện tại, đọc hợp đồng/script đang chạy và chạy thử trên bản staging trước. Phải chuẩn bị lại domain công khai, cấu hình vận hành, mail/cron và trạng thái xác thực; không phục vụ nguyên cấu hình localhost hoặc đưa staging đã neutralize vào production. Workflow `with-data` hiện tại không phải cơ chế restore dump toàn bộ.

Chủ dự án đã chọn phương án 2; không cần hỏi lại có cho phép thay dữ liệu server hay không. Máy local chưa có entry SSH alias `tacare-server` trong `~/.ssh/config`, chưa có kết nối server. Không yêu cầu gửi mật khẩu/IP/private key vào chat; cấu hình kết nối theo [hướng dẫn riêng](security_configuration.md).

Sau khi có lựa chọn và truy cập vận hành, kiểm kê server rồi chuẩn bị bản xem trước cụ thể cho import/reconcile hoặc restore tương ứng. Chưa có lệnh restore production hoặc kế hoạch tự xóa/đổi chủ bản ghi server trong đợt chuẩn bị này. Không chạy `release.py` vì lệnh đó commit/push main và bắt đầu deploy.

## Kết nối để tiếp tục phương án đã chọn

Trên Mac, mở `~/.ssh/config` bằng trình soạn thảo và thêm entry bên dưới với giá trị thật ở máy riêng; không copy giá trị thật vào repository hoặc chat:

```sshconfig
Host tacare-server
    HostName YOUR_SERVER_HOST
    User YOUR_OPERATOR_USER
    Port YOUR_SSH_PORT
    IdentityFile ~/.ssh/YOUR_EXISTING_PRIVATE_KEY
    IdentitiesOnly yes
```

Dùng tài khoản vận hành có quyền sudo và key đã đăng nhập được server. Đây có thể là tài khoản khác với user chạy GitHub Actions. Nếu cần mở khóa private key bằng passphrase, thực hiện trong terminal/SSH agent của người vận hành. Không xuất giá trị GitHub Secrets ra source.

Kiểm tra bằng `ssh tacare-server` tại terminal Mac, xác minh host key theo thông tin server đã biết; không tắt kiểm tra host key. Khi kết nối hoạt động, có thể tiếp tục đọc các script root-owned hiện tại, cấu hình Odoo/systemd và các phiên bản trước khi chuẩn bị thao tác restore cụ thể. Nếu chưa có quyền sudo hoặc chưa kết nối được, giữ nguyên server; gói private sẵn sàng không đồng nghĩa đã triển khai.
