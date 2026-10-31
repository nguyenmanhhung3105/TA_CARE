# UAT trên server — 31/10/2026

Owner yêu cầu bỏ staging local, dựng UAT trên server hiện tại, lấy source đang
chạy trên server làm bản đầu tiên. Sau này push nhánh `uat` triển khai UAT; sau
nghiệm thu, merge vào `main` triển khai code lên production. Dữ liệu UAT không
được promote sang production. Không chạy lại full restore cũ để phát hành code.

## Phạm vi và trạng thái

**Kết quả server mới nhất:** owner xác nhận gói sửa `36d87a55798c` preview qua
(private DB rỗng, 20 connections/64 locks) rồi `--apply` thành công. Unit
`tacare-uat-resume.service` exit 0 và báo **UAT BOOTSTRAP PASSED**: private lock
setting đã được tăng, dump cũ restore lại, filestore/integrity/account-owner,
neutralized upgrade và cả ba home/login probes qua. Nginx UAT đã được thêm và
graceful reload; production addon/database/Odoo không đổi. Đây là bootstrap
server thật đã qua, supersedes lỗi restore ban đầu; không chạy setup/resume lại.

**Publish đã qua trên server:** owner xác nhận gói `79c23608976f --apply` báo
`UAT HTTPS PUBLISHED`. Công cụ đã kiểm lại TLS, anonymous 401, authenticated
homepage/noindex trên ba site, nhận đúng `snap.certbot.renew.timer`, cài hook
lineage UAT, xác nhận timer active và ghi state `published`. Chứng chỉ, access
credentials, Nginx, source và database hiện có được giữ nguyên trong bản sửa.
Kiểm tra ngoài sandbox sau publish xác nhận cả ba hostname có certificate hợp
lệ và trả HTTP 401 cho khách chưa đăng nhập. Không chạy setup/resume hoặc reset
clone này. Hai lỗi khởi tạo trước đã được xử lý, giữ ghi chép ở phần phục hồi.

Basic Auth chung ba host: username `uat`, password sinh riêng và lưu root-only
trong `/var/lib/tacare-uat/private/access.json`; không chép vào tài liệu/chat.
Sau lớp này, tài khoản Odoo dùng thông tin trong snapshot production lúc clone.
Browser SSO/form thực tế, ACME renewal dry-run và CI vẫn chưa được xác nhận.

Máy local chưa có
SSH alias `tacare-server`, người vận hành đang dùng terminal server riêng. Không
có commit/push/PR/merge hoặc production deploy nào được thực hiện trong đợt này.

Ba script live được owner cung cấp SHA256 ngày 31/10 khớp bản đã inspected:
`deploy.sh`, `worker.sh`, `helper.py`. Dịch vụ production active, Nginx test qua.
Production: DB `tacare_prod`, user `odoo`, HTTP 8069, workers 0, addons
`/opt/odoo/apps/tacare/addons`, data `/var/lib/odoo-tacare`.
RAM 3.8 GiB, available 2.2 GiB, swap 3.8 GiB; disk available 44 GiB lúc kiểm tra.
8169/8172 chưa sử dụng lúc owner kiểm tra. Installer kiểm tra lại khi chạy.

## Cấu trúc

- `/opt/tacare-uat/core`, `venv`: bản sao bộ core/runtime đang chạy, không sửa core nguồn.
- `/opt/tacare-uat/releases/bootstrap`: **copy addon server**, sau đó vá adapter UAT
  khi từng file gốc khớp SHA256. Không copy toàn bộ working tree local, Mapbox trial,
  SCSS/photo hoặc các thay đổi giao diện local chưa phát hành. Manifest server giữ
  nguyên assets, chỉ tăng version và thêm override ẩn banner đã được owner yêu cầu.
- `/opt/tacare-uat/current`: con trỏ release UAT, root quản lý.
- `/etc/odoo-tacare-uat.conf`: cấu hình riêng, không copy password/config production.
- `/var/lib/tacare-uat/app`: filestore/session UAT, user `odoo-uat`.
- `/var/lib/tacare-uat/private`: dump clone, log, backup, state và credentials, root-only.
- PostgreSQL 16 instance riêng, dùng binaries **đã cài**, không cài thêm PostgreSQL,
  không sửa pg_hba/role/ACL của cluster production. Chỉ Unix socket riêng,
  không TCP; DB `tacare_uat`, application role `odoo_uat` không superuser/createdb/
  createrole. Odoo được mở DB UAT và maintenance DB `postgres` rỗng của **cluster riêng**.
- `postgresql-tacare-uat.service`: user `postgres-uat`, MemoryMax 384M.
- `odoo-tacare-uat.service`: user `odoo-uat`, MemoryMax 1G, CPUQuota 100%, HTTP 8169,
  workers 0, cron threads 0, `TACARE_ENVIRONMENT=uat`.
- Firewall egress riêng cho UID UAT, IPv4/IPv6; native neutralization; mask đường
  dẫn production trong sandbox. Request bản đồ từ browser vẫn cần Internet.

Bootstrap pg_dump production bằng snapshot PostgreSQL, rsync filestore rồi kiểm
size/SHA1 **tất cả file được dump tham chiếu**. Vì attachment lưu theo content hash,
file dư không ảnh hưởng snapshot; file bị mất/thay đổi khiến setup dừng. Không dừng
Odoo production và không thực hiện SQL write trên DB production. Baseline tài khoản,
password hash và owner được so sánh trước/sau upgrade trong clone. Consent không
được tự gia hạn hoặc thay đổi để làm đầy giao diện.

## 1. Build và upload trên Terminal Mac

```bash
cd /Users/hung/Documents/MyProject/TA_CARE
python3 tools/deploy/uat_package.py --upload
```

Nhập đích SSH/cổng/identity đang dùng trong terminal riêng. Không nhập mật khẩu
vào ô hostname; OpenSSH xử lý xác thực. Không ghi thông tin thật vào source/chat.
SSH StrictHostKeyChecking được giữ; nếu máy Mac chưa biết host key, xác minh host
key qua kênh đang dùng trước khi thêm vào known_hosts.

Tool build archive nhỏ trong ignored `runtime/releases/uat-bootstrap/`, chỉ gồm
adapter và root tools, không có dump/filestore/credentials. Tool không phụ thuộc
release report/full snapshot cũ. Nó in tên archive upload có checksum trong tên và
SHA256 đầy đủ. Không tự chạy sudo hoặc thay ứng dụng trên server.

## 2. Preview và bootstrap trong terminal server

Đặt **đúng** tên archive và SHA256 từ uploader, không chọn file mới nhất/glob:

```bash
UAT_BOOTSTRAP_ARCHIVE="$HOME/tacare-uat-bootstrap-REPLACE_WITH_PRINTED_HASH_PREFIX.tar.gz"
UAT_BOOTSTRAP_SHA256='REPLACE_WITH_PRINTED_FULL_SHA256'
printf '%s  %s\n' "$UAT_BOOTSTRAP_SHA256" "$UAT_BOOTSTRAP_ARCHIVE" | sha256sum --check -
```

Chỉ tiếp tục khi checksum OK:

```bash
UAT_SETUP_DIR=$(mktemp -d "$HOME/tacare-uat-setup.XXXXXXXX")
tar -xzf "$UAT_BOOTSTRAP_ARCHIVE" -C "$UAT_SETUP_DIR"
sudo python3 "$UAT_SETUP_DIR/tacare-uat-bootstrap/uat.py" setup
```

Preview phải báo `PREVIEW PASSED`. Unknown source hash, existing UAT resources,
existing UAT server_name hoặc production pending state sẽ chặn trước bootstrap.
Original production `--check` chạy ngoài shared lock của UAT để tránh khóa lồng nhau.

```bash
sudo systemd-run --unit=tacare-uat-setup --wait --pipe --collect \
  /usr/bin/python3 "$UAT_SETUP_DIR/tacare-uat-bootstrap/uat.py" setup --apply
```

Systemd giữ tiến trình setup khi SSH ngắt; có thể xem `sudo journalctl -u
tacare-uat-setup --no-pager` để biết bước. Raw restore/ORM diagnostics giữ ở
root-only `/var/lib/tacare-uat/private/setup.log`; không gửi nguyên log chứa dữ liệu.
Không chạy lại setup mù nếu báo lỗi hoặc đã tạo state; giữ phần UAT để chẩn đoán,
production không bị reset. Thành công phải có `UAT BOOTSTRAP PASSED`.

## 3. HTTPS và giới hạn truy cập

DNS của **cả ba** tên phải trỏ đúng server:

- `uat.tacare.vn`
- `uat.khovieclam.vn`
- `uat.tuhoso.com`

Installer chỉ thêm `/etc/nginx/conf.d/tacare-uat.conf`; yêu cầu include conf.d đã
có và không ghi đè vhost UAT do người khác cấu hình. Trước publish, HTTP trả 503
ngoài đường dẫn ACME, HTTPS từ chối handshake. Chưa phục vụ clone công khai.

Server hiện cài Certbot qua Snap, dùng timer đã có
`snap.certbot.renew.timer` (owner xác nhận enabled); không cài thêm bản apt hoặc
tạo timer `certbot.timer` để né lỗi. Kiểm tra:

```bash
command -v certbot
systemctl show snap.certbot.renew.timer -p LoadState -p ActiveState -p UnitFileState
```

Sau khi DNS sẵn sàng:

```bash
sudo python3 /usr/local/lib/tacare-uat/uat.py publish
```

Certbot dùng webroot của UAT, cert riêng `tacare-uat`, không sửa certificate
production. Nếu chưa có tài khoản ACME phù hợp, đăng ký không email bằng cờ rõ
ràng. Công cụ mới chọn timer Snap/package đang có và thêm hook reload Nginx;
không tạo một scheduler cạnh tranh. Basic Auth áp dụng cả ba site,
assets và ảnh; `noindex` giữ nguyên. Mỗi lần đổi Nginx đều test, graceful reload,
kiểm ba homepage production; lỗi thì phục hồi **file UAT** trước đó và reload.

Xem credentials **riêng trên terminal của bạn**, không gửi nội dung vào chat:

```bash
sudo cat /var/lib/tacare-uat/private/access.json
```

Đây là lớp truy cập UAT trước Odoo. Tài khoản Odoo được copy từ production giữ
password hiện tại. Native session/SSO secret riêng; logout UAT không logout production.
Owner giữ quyết định không hiển thị native database-testing banner; neutralization,
noindex, cron/mail/integration guards vẫn được giữ.

### Tự đổi tài khoản/mật khẩu cửa UAT

Owner yêu cầu tự đặt lại Basic Auth. Chỉ sửa `access.json` không đổi xác thực
Nginx; cần đồng bộ `private/access.json` và `/etc/nginx/tacare-uat.htpasswd`.
Lệnh tương tác ở `tools/deploy/server/change_uat_access.py` dùng helper đã cài,
cho nhập username qua `/dev/tty`, password qua getpass hai lần, không đưa mật
khẩu vào argv/history/output. Có thể dán nguyên nội dung script vào `sudo python3
- <<'PY' ... PY` trong terminal server; không cần update helper hoặc upload lại
bootstrap. Enter ở username giữ tên hiện tại.

Lệnh giữ shared deploy lock khi ghi; phát hiện thay đổi đồng thời, backup cả hai
file trong private directory root-only, tạo SHA512-crypt qua stdin, atomic replace
với mode/GID Nginx cũ, test/reload Nginx và xác thực HTTPS cả ba host. Kiểm tra
thất bại thì phục hồi hai file cũ. Không sửa tài khoản Odoo hoặc DB. Đây là thao
tác do owner chạy với secret tự nhập; agent chưa thấy hoặc đổi secret trên server.
4 synthetic filesystem tests qua: đồng bộ/backup/mode, rollback khi HTTPS fail,
password confirmation mismatch và chống chèn entry qua username.

## 4. GitHub Actions sau khi bootstrap/publish qua

Tạo key Ed25519 riêng cho UAT ở máy vận hành, giữ private key ngoài Git. Chuyển
**public key** lên server rồi chạy:

```bash
sudo python3 /usr/local/lib/tacare-uat/uat.py authorize-key /ABSOLUTE/PATH/TO/UAT_PUBLIC_KEY.pub
```

Tool tạo account `tacare-uat-deploy` riêng. Authorized key có forced command và
`restrict`; chỉ được gọi wrapper UAT với exact commit SHA, không shell/forwarding/
production sudo entry point. Existing account `tacare-deploy` giữ production flow.

Trong GitHub Actions Secrets thêm:

| Secret | Ý nghĩa |
| --- | --- |
| `UAT_DEPLOY_HOST` | Host server riêng trong Secrets |
| `UAT_DEPLOY_USER` | `tacare-uat-deploy` |
| `UAT_DEPLOY_PORT` | Cổng SSH; bỏ trống dùng 22 |
| `UAT_DEPLOY_SSH_KEY` | Private key UAT mới |
| `UAT_DEPLOY_KNOWN_HOSTS` | Host key đã xác minh |

Không copy key production sang UAT. Secrets production `DEPLOY_*` giữ riêng.
Workflow dùng repository secrets để không giả định gói GitHub hỗ trợ Environments.

Commit/push/PR/merge do owner thực hiện sau review. Nhánh `uat` cần chứa adapter
UAT của hai addon cùng workflow mới. Không push `main` như một phép thử. Khi push
`uat`, server fetch exact origin/uat HEAD, tạo release và backup UAT DB/files/code
trước upgrade. Lỗi thì dừng UAT và giữ backup; không chạy code cũ trên DB đã upgrade.

Nghiệm thu bằng browser thật đủ ba site, role business/candidate/admin, guest,
SSO/logout, public catalog, owner/foreign profile access, matching/consent, form,
map và responsive. Chưa tuyên bố luồng này qua từ HTTP homepage probes.

Sau review merge PR `uat → main`. Workflow production gọi wrapper mới, đối chiếu
**Git tree của addon** với bản UAT đã qua probe. Merge commit/Squash có SHA khác
vẫn hợp lệ nếu addon tree giống hệt; conflict resolution làm đổi code thì bị chặn
để thử lại. Bootstrap copy từ server chưa có Git-backed UAT pass, nên chưa đủ để
vượt gate phát hành. Không hỗ trợ with-data trailer/JSON trong workflow phát hành
code này; các cơ chế full restore cũ vẫn là thao tác operator riêng.

Hai workflow cùng concurrency group; worker cùng shared server lock. Trước gọi
worker production cũ, wrapper dừng riêng UAT để trả RAM cho staging tạm; xong mở
lại. Giữ nguyên ba script production đã inspected và recovery của chúng. Không
copy DB UAT, password/session/config UAT vào production.

## Trạng thái và phục hồi

### Hoàn tất publish trên server dùng Snap Certbot

Owner xác nhận publish.log chỉ lỗi `Failed to enable unit: Unit file certbot.timer
does not exist`; inventory có `snap.certbot.renew.timer` enabled. HTTPS/auth đã
qua các probe trước lỗi; state chưa được ghi `published` và hook chưa được cài.
Gói sửa riêng pin helper đang chạy từ `36d87a55798c`, backup helper rồi nhận diện
timer thật. Không tạo lại chứng chỉ, không chạy lại Certbot issuance, không ghi
đè Nginx, không đổi Basic Auth credentials và không restore DB/source.

Trên Mac:

```bash
python3 tools/deploy/uat_package.py --repair-publish --upload
```

Chỉ tiếp tục khi uploader báo `Uploaded and verified`. Dùng đúng tên archive
được in ra, giải nén vào `$UAT_PUBLISH_FIX_DIR`, rồi preview:

```bash
sudo python3 "$UAT_PUBLISH_FIX_DIR/tacare-uat-publish-repair/repair.py"
```

Sau `PUBLISH REPAIR PREVIEW PASSED`:

```bash
sudo python3 "$UAT_PUBLISH_FIX_DIR/tacare-uat-publish-repair/repair.py" --apply
```

Preview và apply kiểm lại backend, certificate/HTTP 401, authenticated proxy và
noindex bằng credentials qua stdin, không qua argv/log. Apply chỉ cài hook có
guard lineage UAT, bảo đảm đúng timer đang hoạt động, rồi ghi phase/timer vào
private state. Timer bị masked/missing hoặc nhiều timer không phân biệt được sẽ
bị chặn; không tắt scheduler nào đang có. Owner đã xác nhận `UAT HTTPS PUBLISHED`
thực tế cho gói `79c23608976f`. Sau đó có thể kiểm riêng renewal UAT:

```bash
sudo certbot renew --cert-name tacare-uat --dry-run --run-deploy-hooks
```

Không dùng renew toàn bộ production certificates làm phép thử UAT. Dry-run thật
vẫn cần kết quả server; unit tests không chứng minh ACME renewal đã thành công.

### Tiếp tục lỗi restore thiếu lock của lần khởi tạo đầu

Owner cung cấp chẩn đoán: `pg_restore ... ERROR: out of shared memory`, dump đọc
được; production active, private PG active và không restart. Bản bootstrap đầu
giảm `max_connections` xuống 20 nhưng giữ `max_locks_per_transaction` mặc định
64. Restore một transaction có thể vượt shared lock table dù process còn RAM.
Không tăng MemoryMax hoặc cấu hình PostgreSQL production để xử lý lỗi này.

`uat.py` mới đặt lock capacity 1024 cho bootstrap sau này. Gói sửa nhỏ chỉ thay
helper UAT sau khi hash khớp bản đã cài từ gói `6ec6583afc31`; backup helper cũ
và private postgresql.auto.conf. Nó yêu cầu state `initializing`, Odoo UAT inactive,
chưa có filestore/Nginx UAT/sudoers, đúng socket/port/data directory/DB owner và
**không có relation/function ứng dụng** sau rollback. Config Odoo UAT cũng được
kiểm các đích DB/source/data trước khi chạy. Sai guard sẽ dừng, không reset DB.

Trên Mac:

```bash
python3 tools/deploy/uat_package.py --repair-restore --upload
```

Dùng đúng tên/checksum uploader in ra, giải nén gói `tacare-uat-restore-repair`
trong thư mục riêng trên server. Preview:

```bash
sudo python3 "$UAT_REPAIR_DIR/tacare-uat-restore-repair/repair.py"
```

Sau `REPAIR PREVIEW PASSED`:

```bash
sudo systemd-run --unit=tacare-uat-resume --wait --pipe --collect \
  /usr/bin/python3 "$UAT_REPAIR_DIR/tacare-uat-restore-repair/repair.py" --apply
```

Apply chỉ `ALTER SYSTEM` trên private PG, restart `postgresql-tacare-uat.service`,
kiểm setting mới rồi restore lại **dump cũ đang có** bằng single transaction. Không
drop/recreate DB hoặc copy lại source; sau restore mới tiếp tục filestore,
neutralize, upgrade và probes. Lỗi restore ghi root-only `private/resume-restore.log`.
Không chạy lại setup đầu. Chưa coi server qua đến khi có `UAT BOOTSTRAP PASSED`.

Local: 19 offline tests qua, thêm guards config/DB rỗng và chỉ restart private PG.
Rehearsal kiểm soát 5.000 bảng trống tái hiện atomic restore hết lock ở 20
connections/64 locks và rollback rỗng; cùng dump qua với 1024 locks, giữ 384 MiB.
Sau đó fixture Odoo restore/upgrade/672 referenced files/3 homepages/role/mail/cron
đều qua dưới cấu hình private PG mới. Snapshot Odoo lịch sử riêng lẻ không tái
hiện lỗi live; thử catalog lớn dùng để xác thực cơ chế và bản sửa. Owner sau đó
xác nhận áp dụng gói sửa trên server thành công như trạng thái ở đầu tài liệu.

```bash
sudo python3 /usr/local/lib/tacare-uat/uat.py status
sudo systemctl status postgresql-tacare-uat odoo-tacare-uat --no-pager
```

Nếu **deploy code UAT** đã vào backup rồi upgrade/probe thất bại:

```bash
sudo python3 /usr/local/lib/tacare-uat/uat.py recover
```

Recovery chỉ dùng private UAT socket và fixed DB `tacare_uat`, khôi phục cùng lúc
code pointer/DB/files. Bootstrap thất bại có quy trình chẩn đoán riêng; không dùng
recovery này để xóa hoặc reset clone đang khởi tạo. Production recovery vẫn qua
entry point cũ; không tự xóa pending state hoặc production-release marker.

## Kiểm chứng local

`python3 tools/deploy/tests/test_uat.py`: domain/role boundary, source patch hash,
không copy local UI/Mapbox, archive traversal/link, firewall chỉ UID UAT, Nginx
closed/auth, forced SSH và production Git-tree gate. Native rehearsal dùng hai
container không mạng và socket volume dùng một lần, snapshot cũ **chỉ làm fixture**,
không chạm application DB local hoặc production. Mọi container/volume tạm được dọn.
Server systemd/firewall/certbot, SSH secrets, Actions và browser UAT phải được xác
nhận bằng kết quả live; không suy ra từ local rehearsal.

Kết quả local đã chạy: 14 offline boundary tests và 9 deploy/workflow regressions
qua (Git commit/push trong test chỉ dùng bare repository tạm); Python/shell/YAML parse và
security scan qua. Rehearsal PostgreSQL/Odoo native qua: peer role bị chặn ở DB
khác; restore/upgrade giữ credentials và owner; 672 referenced files khớp; cả ba
homepage có marker, link UAT, noindex và không có banner; domain ngoài UAT bị
chặn; native role checks business/candidate/admin qua; SMTP/cron tắt, handoffs
thu hồi. Nginx fixture không mạng qua syntax/TLS/Basic Auth trên ba host, chặn
anonymous pages/assets/files và cho authenticated proxy kèm noindex. Container
và socket volume được dọn sau kiểm tra.
