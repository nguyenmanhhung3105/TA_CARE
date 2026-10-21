# Cấu hình bí mật ngoài Git

Repository chứa tên biến và cấu hình mẫu. Giá trị thật của mật khẩu, private key, API token, địa chỉ máy chủ và tài khoản SSH phải ở kho riêng hoặc GitHub Actions Secrets. Không đặt chúng trong source, tài liệu, screenshot, commit message hoặc gói source.

## GitHub Actions

Trong Settings → Secrets and variables → Actions → Repository secrets, người vận hành cấu hình:

| Secret | Nội dung |
| --- | --- |
| `DEPLOY_HOST` | Host/IP máy chủ thật |
| `DEPLOY_USER` | Tài khoản SSH dùng để deploy |
| `DEPLOY_PORT` | Cổng SSH, tùy chọn; mặc định 22 |
| `DEPLOY_SSH_KEY` | Private key của tài khoản deploy |
| `DEPLOY_KNOWN_HOSTS` | Host key đã được xác minh riêng |

Workflow đọc các secrets này, kiểm tra đầu vào và giữ StrictHostKeyChecking. Thiếu host/user/key/known-hosts thì dừng trước khi kết nối. Không có địa chỉ hoặc user dự phòng được ghi trực tiếp trong workflow. Giá trị host có thể là IPv4 hoặc hostname DNS; định dạng IPv6 chưa được hỗ trợ trong kiểm tra đầu vào hiện tại.

Thay đổi workflow này chưa được push. Người vận hành cần thêm host/user secrets trước lần push tiếp theo. Việc cấu hình GitHub Secrets không thay đổi script hoặc dữ liệu trên server.

## SSH thủ công

Đặt kết nối thật trong `~/.ssh/config` của người vận hành (ngoài repository). Đây là mẫu, tự thay các placeholder ở máy riêng:

```sshconfig
Host tacare-server
    HostName YOUR_SERVER_HOST
    User YOUR_OPERATOR_USER
    Port YOUR_SSH_PORT
    IdentityFile ~/.ssh/YOUR_PRIVATE_KEY_FILE
    IdentitiesOnly yes
```

Tài liệu chung chỉ dùng `ssh tacare-server` hoặc `scp ... tacare-server:~/...`. Tài khoản SSH vận hành thủ công có thể khác tài khoản deploy trong Actions.

## Local và gói dữ liệu

`.env`, `docker/local-config/`, `runtime/`, `backups/`, `.private/` và `.secrets/` nằm ngoài Git. Giữ quyền truy cập riêng cho file cấu hình/credentials. Cấu hình mẫu chỉ có placeholder; không copy giá trị thật vào `.env.example` hoặc `*.conf.example`.

Gói chuyển dữ liệu có thể chứa hash mật khẩu portal, nên vẫn phải ở ignored runtime và kho private trên server; không đưa nội dung gói vào Git hoặc chat. SHA256 lựa chọn gói không phải mật khẩu nhưng tài liệu dùng biến thay cho checksum gói cụ thể. Không sửa/xóa mật khẩu trong database để làm sạch source.

Kiểm tra các file sẽ đưa vào Git bằng:

```bash
python3 tools/security/check_repository.py
```

Công cụ chỉ in file/dòng/loại phát hiện, không in giá trị. Nó rà source hiện tại, không chứng nhận đã xóa dữ liệu khỏi commit cũ, remote, Git reflog, bản sao lưu hoặc nội dung chat. Việc sửa lịch sử remote cần một đợt xử lý riêng; không force-push trong đợt làm sạch working tree này.
