# CI/CD TA.CARE

Luồng chuẩn: **sửa code → PR vào `uat` → CI → UAT → nghiệm thu → PR vào `main` → CI → production**.
Merge vào `main` là quyết định phát hành; các bước triển khai sau đó tự chạy.

## 1. Chuẩn bị một lần

- Giữ bộ deploy production đã kiểm định: `/usr/local/lib/tacare-deploy/{deploy.sh,worker.sh,helper.py}`.
- UAT hiện đã dựng/publish trên server: `uat.khovieclam.vn`, `uat.tuhoso.com`, `uat.tacare.vn`.
  Giữ database, filestore, session riêng; Basic Auth, noindex, email/cron bị tắt. Không dựng lại UAT đang dùng.
- Kiểm tra trong terminal server:

```bash
sudo /usr/local/lib/tacare-deploy/deploy.sh --check
sudo python3 /usr/local/lib/tacare-uat/uat.py status
sudo test -x /usr/local/lib/tacare-uat/deploy.sh
sudo test -x /usr/local/lib/tacare-uat/release.sh
sudo visudo -cf /etc/sudoers.d/tacare-uat
```

UAT phải có trạng thái `published`. Xác minh tài khoản/key production gọi được wrapper `release.sh`
theo giới hạn SSH/sudo hiện có; không mở quyền sudo hoặc shell rộng để thay cho kiểm tra này.

Tạo key Ed25519 riêng cho Actions UAT, giữ private key ngoài Git. Chuyển **public key** lên server:

```bash
sudo python3 /usr/local/lib/tacare-uat/uat.py authorize-key /ABSOLUTE/PATH/TO/UAT_PUBLIC_KEY.pub
```

Cấu hình GitHub **Settings → Secrets and variables → Actions → Secrets**:

| Production, giữ cấu hình đã dùng | UAT, key riêng |
| --- | --- |
| `DEPLOY_HOST` | `UAT_DEPLOY_HOST` |
| `DEPLOY_USER` | `UAT_DEPLOY_USER` = `tacare-uat-deploy` |
| `DEPLOY_PORT` | `UAT_DEPLOY_PORT` |
| `DEPLOY_SSH_KEY` | `UAT_DEPLOY_SSH_KEY` |
| `DEPLOY_KNOWN_HOSTS` | `UAT_DEPLOY_KNOWN_HOSTS` |

Cổng bỏ trống dùng 22; known_hosts phải được xác minh. Không ghi giá trị bí mật vào source/chat.
Nếu gói GitHub hỗ trợ, bảo vệ `uat`/`main`: yêu cầu PR và hai check CI thành công, chặn push trực tiếp/force-push.
Hai check: `Source and deployment checks`, `Odoo install upgrade security and browser`.

## 2. Đưa thay đổi lên UAT

1. Tạo nhánh `feature/...` hoặc `fix/...` từ phiên bản hiện hành; sửa và kiểm tra code.
2. Chạy `python3 tools/security/check_repository.py`, review diff, chỉ commit các file đã kiểm tra.
   Không đưa `.env`, database, backup, filestore hoặc credentials vào Git.
3. Push nhánh, mở PR vào `uat`. CI tự kiểm tra source, bảo mật, workflow, cài mới/nâng cấp Odoo và trình duyệt.
4. CI xanh thì merge PR. Workflow UAT kiểm tra lại đúng commit sau merge rồi tự deploy.
5. Server xác minh commit mới nhất, backup UAT, nâng cấp addon và kiểm tra ứng dụng.

CI dùng Odoo core/image cố định trong `tools/ci/runtime.json`, database/tài khoản giả lập,
container không mạng và không mở cổng host. Nâng cấp được thử từ commit nền trước thay đổi.
Ảnh/báo cáo kiểm thử được lưu trong Actions Artifacts ba ngày; không upload credentials hay raw runtime logs.

## 3. Nghiệm thu và phát hành production

1. Truy cập ba site UAT; kiểm tra guest, cá nhân/doanh nghiệp/admin, form, SSO/logout,
   tin công khai, hồ sơ riêng, matching/consent và giao diện điện thoại.
2. Giữ nguyên bản UAT đang nghiệm thu; mở PR **`uat → main`**. CI chỉ chấp nhận PR production từ nhánh `uat` cùng repo.
3. Nghiệm thu đạt và CI xanh thì merge. Workflow production tự chạy CI trên commit sau merge.
4. Server đối chiếu **nội dung addon** với bản đã qua UAT; khác nội dung thì phải thử lại trên UAT.
5. Wrapper mới gọi worker production cũ: kiểm tra staging cô lập, backup rồi nâng cấp production và kiểm tra ba website.
6. Theo dõi Actions đúng commit; chỉ kết thúc khi deploy thành công và các luồng chính trên production hoạt động.

Hai deploy dùng chung khóa, không ngắt một đợt triển khai đang chạy. Commit bị thay thế được bỏ qua;
server kiểm tra lại HEAD. UAT tạm dừng khi production cần tài nguyên staging và được mở lại sau đó.

## 4. Phạm vi và vận hành

- Chỉ phát hành `source/apps/tacare/addons/`; nâng cấp module trên database đích. Không chuyển DB UAT sang production.
- Odoo core, dependency, cấu hình hệ thống và full restore là thao tác vận hành riêng.
- Giữ backup code/database/filestore đồng bộ. UAT phục hồi bằng `uat.py recover`;
  production dùng `deploy.sh --recover` của bộ production, sau khi xác minh đúng trạng thái cần phục hồi.
- Không dùng `tools/deploy/release.py` cho luồng này; công cụ lịch sử đó push thẳng `main`.

## 5. Các file điều khiển và trạng thái

| File | Chức năng |
| --- | --- |
| `.github/workflows/ci.yml` | CI cho PR và bộ CI dùng chung qua `workflow_call` |
| `.github/workflows/deploy-uat.yml` | Push `uat` → CI → deploy UAT |
| `.github/workflows/deploy-tacare.yml` | Push `main` → CI → kiểm bản UAT → production |
| `tools/ci/` | Kiểm tra source, runtime cố định, fixture giả lập và kiểm thử Odoo/browser |
| `tools/deploy/server/uat.py` | UAT, đối chiếu addon và gọi bộ deploy production hiện hữu |

**Kiểm chứng tại local ngày 31/10/2026:** source/security/workflow và các test triển khai qua;
pipeline Odoo tạm qua cài mới, nâng cấp, quyền sở hữu/consent, SSO, form và trình duyệt.
**Chưa xác nhận kích hoạt Actions mới:** cần quyền truy cập GitHub, secrets và kiểm tra wrapper/key trên server.
Không coi kiểm thử local là một lần phát hành production thành công.
