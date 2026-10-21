# Chuyển code và dữ liệu hiện tại lên server

Các thay đổi website và công cụ chuyển dữ liệu đang ở working tree để rà soát trước khi commit lại. Hai commit local vừa tạo đã được hủy theo yêu cầu chủ dự án. Chưa push hoặc kết nối/thay đổi server.

Thông tin host, tài khoản SSH và key thật được giữ ngoài Git theo [cấu hình riêng](security_configuration.md). Tài liệu dùng SSH alias `tacare-server`, biến tên gói và checksum; không chứa thông tin truy cập hoặc checksum gói cụ thể.

## Phạm vi gói hiện tại

Bundle `tacare.demo.v2` chọn 20 việc làm, 6 hồ sơ, 12 mục nhận việc, 11 kỹ năng và 3 mục mỗi nhóm kinh nghiệm/học tập/minh chứng. Tổng 58 bản ghi nghiệp vụ, bốn tài khoản portal liên quan. Các tài khoản admin, sessions/SSO/MFA, cấu hình domain/email, kết nối/ứng tuyển, audit và tài liệu upload nằm ngoài gói. Mật khẩu tài khoản đích đã có mapping được giữ; trùng login chưa mapping thì dừng để đối chiếu.

Ảnh binary và mô tả HTML/text của bản ghi được chọn được chuyển trong gói; ảnh giao diện/logo/danh mục đi cùng addon. Hồ sơ/minh chứng nhập riêng tư, không tự cấp consent hay bật matching. Không xóa dữ liệu đích khi local không còn bản ghi đó. Bộ demo cũ cần đối chiếu chủ tin/offer và hồ sơ cũ trước khi chuyển đổi.

## 1. Chuẩn bị ở máy local

Sau khi rà soát và commit code, chạy tại thư mục repository. Không push main trước khi hoàn tất chuẩn bị server và duyệt gói.

```bash
python3 tools/security/check_repository.py
python3 tools/deploy/build_server_package.py
bash tools/deploy/export_local_demo.sh
```

Exporter in đường dẫn file private và SHA256, không in nội dung hay mật khẩu. File JSON chỉ ở ignored runtime. Ghi lại đúng file/hash vào nơi riêng; không dùng quy tắc chọn gói mới nhất.

Đặt đường dẫn chính xác vừa xuất trong shell local; tự thay placeholder:

```bash
TACARE_BUNDLE_FILE='runtime/tacare/EXACT_PRIVATE_BUNDLE.json'
TACARE_DATA_SHA=$(shasum -a 256 "$TACARE_BUNDLE_FILE" | awk '{print $1}')
scp runtime/releases/tacare-deploy-modes-v1.tar.gz tacare-server:~/tacare-deploy-modes.tar.gz
scp "$TACARE_BUNDLE_FILE" tacare-server:~/tacare-release-data.json
ssh tacare-server
```

Không dùng biến local làm giả định cho shell SSH: biến cần thiết được tính lại ở bước server.

## 2. Preview và cập nhật gate trên server

```bash
mkdir -p ~/tacare-deploy-modes
tar -xzf ~/tacare-deploy-modes.tar.gz -C ~/tacare-deploy-modes
sudo python3 ~/tacare-deploy-modes/install_modes.py
```

Installer đọc script đang chạy và in diff. Nếu script khác hợp đồng đã kiểm tra hoặc có deploy chưa recover thì dừng để đối chiếu. Khi preview hợp lệ và người vận hành đã xem bản sửa:

```bash
sudo python3 ~/tacare-deploy-modes/install_modes.py --install
sudo /usr/local/lib/tacare-deploy/deploy.sh --check
```

Bộ cài backup script root-only, chưa nhập DB hoặc restart Odoo. Package `modes-v1` hiện hỗ trợ cả bundle v1/v2. Staging/backup/rollback giữ nguyên.

## 3. Đối chiếu bộ dữ liệu cũ

Ở server, các lệnh sau chỉ đọc thống kê:

```bash
sudo -u postgres psql -d tacare_prod -c "SELECT model, count(*) FROM ir_model_data WHERE module = 'tacare_transfer' GROUP BY model ORDER BY model;"
sudo -u postgres psql -d tacare_prod -c "SELECT count(*) AS old_demo_profiles FROM tacare_profile WHERE flex_demo_key ~ '^profile-[0-9]{2}$';"
```

Nếu có bộ demo cũ hoặc account trùng chưa mapping, cần đối chiếu tài khoản/chủ bản ghi trước khi phát hành. Không xóa mapping/hashes hoặc chạy lại seed để vượt lỗi. Các bước sau không tự đổi chủ/xóa hồ sơ cũ có lịch sử. Bộ local mới đã sắp xếp lại chủ tin/offer, nên dữ liệu server ở bộ cũ có thể làm staging dừng.

## 4. Duyệt gói ở server

```bash
chmod 600 ~/tacare-release-data.json
TACARE_DATA_SHA=$(sha256sum "$HOME/tacare-release-data.json" | awk '{print $1}')
printf '%s\n' "$TACARE_DATA_SHA"
```

Đối chiếu checksum với kết quả exporter đã ghi riêng ở máy local. Chỉ khi hai bên trùng nhau:

```bash
sudo python3 /usr/local/lib/tacare-deploy/data_bundle.py approve \
  "$HOME/tacare-release-data.json" "$TACARE_DATA_SHA"
sudo python3 /usr/local/lib/tacare-deploy/data_bundle.py inspect "$TACARE_DATA_SHA"
```

Gate giữ bản root-owned chỉ đọc. `approve`/`inspect` chỉ duyệt file, chưa nhập database hoặc chứng minh nội dung hợp lệ với DB đích.

## 5. Phát hành từ máy local

Quay lại terminal local sau khi gate đạt, dữ liệu cũ đã đối chiếu và gói được duyệt. Trong cùng shell đã đặt `TACARE_BUNDLE_FILE`, kiểm tra lại checksum rồi phát hành:

```bash
git status --short
TACARE_DATA_SHA=$(shasum -a 256 "$TACARE_BUNDLE_FILE" | awk '{print $1}')
python3 tools/deploy/release.py with-data --data-sha256 "$TACARE_DATA_SHA"
```

Lệnh cuối tạo commit release và push main, bắt đầu deploy production. Yêu cầu nhánh main và working tree sạch. Cần cấu hình GitHub Secrets host/user trước lần push này. Actions nâng cấp/nhập thử trên staging trước, sau đó mới backup và cập nhật production trong phạm vi rollback. Lỗi mapping/đổi chủ/chỉnh sửa đích hoặc validation làm staging dừng trước production; đối chiếu lỗi rồi mới phát hành lại.

## 6. Kiểm tra

Actions của commit release phải thành công, log nhập có `TA.CARE DATA OK` và thống kê v2. Kiểm tra ba website, admin xem/sửa hồ sơ chi tiết, ảnh/card/chi tiết việc làm và đăng nhập tài khoản đích bằng thông tin đã có. Chủ hồ sơ tự quyết định chia sẻ/matching. Tổng số server có thể lớn hơn local do dữ liệu ngoài gói được giữ.

Các lần chỉ sửa code: commit rồi chạy `python3 tools/deploy/release.py code`. Không phải cài lại gate nếu cơ chế/format không đổi. Đổi dữ liệu local muốn chuyển thêm thì xuất, chuyển và duyệt đúng gói mới.

## Kiểm chứng local

Odoo rollback đã đạt cho 4 portal + 58 bản ghi, nhập lặp/cập nhật, giữ credential đích, chống ghi đè/đổi chủ, kiểm v1→v2. Tám test deploy offline và container Linux không mạng đã đạt; push test chỉ tới bare repo tạm. Chưa chạy worker đầy đủ hoặc nhập dữ liệu trên server thật.
