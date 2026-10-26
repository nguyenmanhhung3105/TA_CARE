# Cấu trúc source hiện tại

## Điểm bắt đầu

Chỉ một backend Odoo và database ứng dụng `tacare_local` cho ba website. Code chạy nằm trong `source/apps/tacare/addons/`:

| Khu vực | Trách nhiệm |
| --- | --- |
| `tacare_account_access/` | Tài khoản, role, giới hạn website, SSO và thu hồi phiên |
| `tacare_website/models/foundation/` | Tổ chức/thành viên, taxonomy, consent và quyền riêng tư |
| `tacare_website/models/jobs/` | Nhu cầu, yêu cầu và phiên bản sửa tin |
| `tacare_website/models/profiles/` | Hồ sơ, dòng con và các trường tương thích |
| `tacare_website/models/exchange/` | Schema matching, đối chiếu trực tiếp, kết nối/thông báo, lượt thực hiện và đánh giá hai chiều |
| `tacare_website/models/marketplace/` | Trường/validation thời vụ dùng chung và chặn tuyển dụng |
| `tacare_website/models/operations/` | Schema vận hành/audit và helper xoá có kiểm quyền |
| `tacare_website/sites/khovieclam/` | Controller và template Kho |
| `tacare_website/sites/tuhoso/` | Controller và template Tủ |
| `tacare_website/sites/tacare/` | Controller và template hub matching |
| `tacare_website/controllers/shared/` | Kiểm tra quyền/helper và thao tác dùng chung |
| `tacare_website/security/` | ACL và record rules |
| `tacare_website/static/src/` | Asset chung và thư mục riêng từng sản phẩm |
| `tacare_website/tests/` | Kiểm tra DEV; không tự chạy seed/refresh lịch sử |
| `tools/maintenance/` | Công cụ bảo trì local; mặc định kiểm kê trước khi thay đổi |

Đây là các **Python package chức năng trong addon hiện có**, không phải addon độc lập có thể uninstall riêng. Giữ tên addon/model/XML ID, bảng dữ liệu và thứ tự nạp trong `models/__init__.py`. Các lớp mở rộng cùng model vẫn dùng một bảng; tách file không tạo database mới. Helper admin được import từ controller như trước, không đăng ký thêm model.

## Cách sửa chức năng

Đọc route tương ứng trong `sites/`, helper quyền trong `controllers/shared/`, model thuộc nhóm liên quan, ACL/rules và template trước khi sửa. Controller chỉ được `sudo()` sau kiểm tra role, ownership, company, consent và state. Không sao chép kiểm tra quyền theo từng website. Khi sửa import của model, tìm cả controller, tools và tests; không bỏ decorator route khi override.

Các lớp template/style cũ có thể là cha của lớp giao diện mới. File tên `legacy`/`recruitment` và bảng rỗng không đủ căn cứ để xoá: chúng có thể giữ XML ID, trường tương thích, dependency hoặc route chặn. Không uninstall HR hoặc xoá bảng để dọn giao diện. Schema chưa nối vào luồng chạy được ghi rõ trong `database_current_2026-10-24.md`.

`prototype/` là demo độc lập. `source/odoo-server/` là core bỏ qua Git, không chỉnh sửa. `runtime/` là dữ liệu local; `backups/` chứa backup riêng tư. Không xoá volume PostgreSQL, filestore hoặc backup khi dọn source. Các seed/refresh tuyển dụng lịch sử không phải install hook và không được chạy lại.

## Dọn database local ngày 24/10/2026

Đã kiểm tra cấu hình chọn duy nhất `tacare_local`, Nginx trỏ cả ba cổng về cùng Odoo, hai DB cũ không có kết nối/module/bảng nghiệp vụ TA.CARE. Đã xoá `khovieclam_local`, `tuhoso_local` sau khi `pg_dump -Fc`, đọc lại archive bằng `pg_restore --list` và tạo SHA256. Backup: `backups/unused_local_databases_20261024_110958/`. Chưa thử khôi phục toàn bộ backup. Giữ nguyên `tacare_local`, `postgres`, template PostgreSQL và filestore.

Kiểm kê lại (không xoá):

```bash
python3 tools/maintenance/cleanup_unused_local_databases.py
```

Công cụ chỉ cho phép hai tên DB cũ cố định và từ chối DB có kết nối/bảng/module ứng dụng. `--apply` sao lưu tất cả trước khi xoá; không dùng FORCE. Không áp dụng công cụ này cho production.

## Cơ sở tổ chức

Áp dụng cách phân trách nhiệm theo package, manifest, ORM và kế thừa của [Odoo 19 — Building a Module](https://www.odoo.com/documentation/19.0/developer/tutorials/backend.html). Với hệ thống dùng chung tài khoản, consent và schema, giữ hai addon hiện có giúp tránh migration đổi XML ID chỉ để chia thư mục. Chỉ tách thành addon cài riêng khi có nhu cầu lifecycle/dependency độc lập và kế hoạch migration.

## Xác minh sau thay đổi

- Đối chiếu 16 file model đã di chuyển với HEAD: giữ nguyên logic, chỉ đổi import tương đối ở ba file hồ sơ.
- Parse Python và XML thành công; `git diff --check` qua.
- `python3 tools/security/check_repository.py`: qua, 300 file văn bản.
- Restart Odoo local để nạp Python; không đổi manifest/schema/XML nên không chạy upgrade addon.
- `homepage_contract_smoke.py`: ba homepage đúng marker và ba trang login đều HTTP 200. Chạy ngoài sandbox vì lần đầu không phân giải được hostname local.
- Odoo shell: `dev_schema_check.py`, `dev_seasonal_scope_check.py`, `dev_admin_removal_check.py` đều qua và rollback dữ liệu QA. Bài admin đã bỏ phụ thuộc tin tuyển dụng demo cũ, tự tạo nhu cầu QA.
- Chưa chạy trình duyệt end-to-end hoặc mọi bài test lịch sử; chưa thử restore toàn bộ archive. Không commit/push hoặc thao tác production.
