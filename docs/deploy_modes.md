# Chọn phát hành có hoặc không kèm dữ liệu

Ngày 20/10/2026: đã viết và kiểm tra bộ công cụ **ở local**. Chưa cài trên server, chưa commit thay đổi của đợt này, chưa push hay deploy production. Chủ dự án tự truy cập server để cài bằng các lệnh bên dưới.

| Lựa chọn mỗi lần phát hành | Kết quả |
| --- | --- |
| `code` — mặc định | Deploy addon, nâng cấp cấu trúc và danh mục XML; không nhập dữ liệu local. Giữ dữ liệu đang có trên server. |
| `with-data` | Cập nhật code/cấu trúc, cộng nhập **gói dữ liệu demo local chỉ định bằng SHA256**. Thêm mới/cập nhật bản ghi do công cụ quản lý; không thay toàn database. |

“Không dữ liệu” nghĩa là không đồng bộ tài khoản/tin/hồ sơ local. Update addon vẫn cập nhật danh mục, view, quyền và chạy migration đã viết trong code. Nó cũng không xóa bộ demo đã đưa lên từ lần trước.

## Phạm vi gói đầu tiên

Xuất dữ liệu đang có trong Odoo local, không chạy lại seed mặc định:

- **20 công việc**: 5 tuyển dụng, 15 việc linh hoạt.
- **19 hồ sơ demo**, **12 mục nhận việc**, 4 kỹ năng hồ sơ; **18 tài khoản portal** liên quan, gồm hai tài khoản ứng viên được yêu cầu trước đó.
- Ảnh trên các tin/mục nhận việc được chọn có thể đi qua giá trị binary trong gói riêng. Quan hệ danh mục dùng XML ID, không dùng ID số local.

Hồ sơ gốc còn lại trong tổng 20 hồ sơ local và tài khoản quản trị không thuộc gói. Không chuyển quyền admin/nhóm nội bộ, SSO/MFA/cookie/API key, cấu hình email/domain, consent, kết nối hay lịch sử ứng tuyển. Gói này **không phải bản sao toàn database**, chưa phải công cụ migration mọi loại dữ liệu. Nếu hồ sơ được chọn có minh chứng/lịch chi tiết/vùng phục vụ/sở thích, hoặc tin có lịch sử revision, exporter dừng để bổ sung phạm vi có kiểm tra; không âm thầm bỏ các phần đó.

Gói có **hash mật khẩu** cho tài khoản portal mới để giữ khả năng đăng nhập. Chỉ lưu ở `runtime/` và kho riêng trên server; không commit, gửi vào chat hoặc log. Với tài khoản đã nhập trước đó, công cụ không đặt lại mật khẩu, tên, MFA hay quyền. Trùng login với tài khoản server chưa có mapping thì dừng, không tự nhận làm cùng một người.

Hồ sơ nhập ở phạm vi riêng tư, không tự cấp consent; matching của tin demo tắt. Company đích là XML ID `base.main_company`; tin thuộc website chuẩn `khovieclam.vn`. Không sửa website/domain có sẵn. Nếu server dùng company nghiệp vụ khác, cần chỉnh mapping trước khi nhập.

## 1. Cài bộ chọn chế độ trên server — chỉ một lần

Đã đọc script root-owned do người vận hành gửi. `--check` đã báo PostgreSQL 16 và systemd isolation khả dụng. Sudoers hiện cho `tacare-deploy` gọi `/usr/local/lib/tacare-deploy/deploy.sh` mà không hạn chế danh sách tham số; không cần mở thêm quyền.

Trên **Mac**, tại thư mục dự án:

```bash
python3 tools/deploy/build_server_package.py
scp runtime/releases/tacare-deploy-modes-v1.tar.gz truongnth@123.30.111.85:~/
```

Trên **server**:

```bash
mkdir -p ~/tacare-deploy-modes-v1
tar -xzf ~/tacare-deploy-modes-v1.tar.gz -C ~/tacare-deploy-modes-v1
sudo python3 ~/tacare-deploy-modes-v1/install_modes.py
```

Lệnh cuối chỉ in diff để xem. Sau khi xem bản sửa:

```bash
sudo python3 ~/tacare-deploy-modes-v1/install_modes.py --install
sudo /usr/local/lib/tacare-deploy/deploy.sh --check
```

Installer giữ khóa deploy, từ chối release chưa recover, kiểm tra cú pháp, backup script gốc root-only rồi thay file nguyên tử. Nó không restart Odoo, gọi deploy hoặc thay database. Chạy lại cùng phiên bản không tạo thêm thay đổi. Nếu đoạn worker cần sửa khác bản đã đọc, installer dừng; cần đối chiếu, không bỏ qua kiểm tra này.

Giữ nguyên `helper.py`, HTTP marker, backup database/filestore/addon và rollback. Nhập staging sau upgrade nhưng trước freeze production; nhập production candidate đã backup trước HTTP probe và mốc committed. Recovery dừng cả hai transient unit nhập dữ liệu. Không đưa database staging đã neutralize thành production.

## 2. Commit code chuẩn bị — chưa push

Trên Mac sau khi cài bộ script server:

```bash
git add .github/workflows/deploy-tacare.yml tools/deploy \
  source/apps/tacare/addons/tacare_website/tools \
  source/apps/tacare/addons/tacare_website/tests/dev_data_transfer_check.py \
  docs/deploy_modes.md docs/backend_local.md AGENTS.md
git commit -m "feat: add selectable code and demo data deployments"
```

Lệnh release yêu cầu nhánh `main`, working tree sạch, code đã commit. Nó tạo commit phát hành rỗng ghi lựa chọn rồi **push main, tức bắt đầu deploy production**. Không tự stage file, force-push hay xử lý xung đột Git.

## 3. Cách 1 — push code/cấu trúc

Trên Mac:

```bash
python3 tools/deploy/release.py code
```

`git push origin main` bình thường cũng mặc định code-only, miễn commit cuối không mang trailer dữ liệu bên dưới. Lệnh release tạo commit riêng để lựa chọn lần trước không bị dùng lại.

## 4. Cách 2 — push kèm dữ liệu demo được chọn

Trên Mac, xuất gói mới khi muốn đưa trạng thái local hiện tại lên:

```bash
bash tools/deploy/export_local_demo.sh
```

Lệnh in **PRIVATE FILE** và **SHA256**, không thay database. Dùng đường dẫn vừa in để chuyển gói:

```bash
scp /duong/dan/PRIVATE_FILE.json truongnth@123.30.111.85:~/tacare-release-data.json
```

Trên server, thay `SHA256_CUA_GOI` bằng 64 ký tự vừa in:

```bash
sudo python3 /usr/local/lib/tacare-deploy/data_bundle.py approve \
  "$HOME/tacare-release-data.json" SHA256_CUA_GOI
```

Đây là bước người vận hành duyệt gói: kiểm tra hash/JSON/quyền file, lưu bản root-owned chỉ đọc tại `/var/lib/tacare-deploy/data/<sha>.json`. Chưa nhập database. Tài khoản deploy không được đưa đường dẫn hay SQL tùy ý vào worker.

Trở lại Mac, chọn đúng hash đó:

```bash
python3 tools/deploy/release.py with-data --data-sha256 SHA256_CUA_GOI
```

Commit phát hành mang trailer `Tacare-Data-SHA256: <sha>`. Actions đọc lựa chọn của commit cuối rồi gọi `deploy.sh <commit> --with-data <sha>`. **Một lần push chọn một chế độ**, không cần deploy code-only trước rồi deploy lại với dữ liệu. Git chỉ chứa code và hash lựa chọn, không chứa nội dung gói riêng.

Không tự chọn gói “mới nhất”. Gói chưa duyệt/thiếu/sai hash, thiếu danh mục, tài khoản trùng hay dữ liệu sai thì deploy thất bại. Bản ghi nhập có mapping trong `ir.model.data`, namespace `tacare_transfer`; hash trạng thái trong `ir.config_parameter` giúp chặn ghi đè nội dung đã sửa trên server, kể cả nội dung dịch. Không xóa bản ghi server khi local thiếu; nhập lặp không sinh bản sao.

## Chọn bằng GitHub Actions

Sau khi workflow mới lên main: **Deploy TA.CARE → Run workflow**, chọn nhánh main:

- `deploy_mode = code`, để trống `data_sha256`.
- Hoặc `deploy_mode = with-data`, nhập hash gói đã duyệt trên server.

Server vẫn kiểm tra commit đúng HEAD mới nhất của main. Push/dispatch dùng cùng concurrency group, staging và rollback. Không đổi GitHub Secrets/sudoers.

## Kiểm tra và giới hạn

- 8 regression test offline: lựa chọn mặc định/theo commit/manual; từ chối hash/tham số sai; không dùng lại lựa chọn cũ; import trong biên staging/rollback; code-only không gọi importer; lỗi stage dừng trước production. Push test chỉ tới bare repo tạm ở local.
- Container Linux dùng một lần, không mạng: preview không đổi file, apply/backup/idempotence; root-owned/private bundle, SHA, quyền, work path, symlink. Không gọi systemd/Odoo/database.
- Odoo local, rollback toàn bộ: xuất/nhập 18 tài khoản và 55 bản ghi; nhập lặp, cập nhật tin, giữ mật khẩu đã đổi, chặn sửa trên server/ID số/admin/trường cấm/profile công khai/bản ghi trùng/login trùng chưa mapping. Fingerprint tài khoản và số bản ghi gốc giữ nguyên sau rollback.
- **Chưa chạy worker đầy đủ trên server, chưa kiểm tra systemd import với production, chưa cài script hay nhập dữ liệu production.** Preview và staging thật vẫn cần chạy khi người vận hành cài/phát hành; kiểm thử local không thay thế xác nhận đó.
