# Push nhánh, tạo pull request và deploy TA.CARE

> **Thay đổi phạm vi phát hành 23/10:** chủ dự án đã chọn thay toàn bộ database và filestore bằng local, sau đó sắp xếp lại các doanh nghiệp demo. Luồng merge ở dưới chỉ triển khai code, không làm phần thay database. Có thể push nhánh để review; đợt hiện tại cần phối hợp merge/cutover theo [bản chuẩn bị dữ liệu đầy đủ](deploy_data_preparation_2026-10-23.md) sau khi kiểm tra server và staging. Không coi Actions xanh là đã chuyển xong dữ liệu local.

Nhánh cho đợt chuyển sang thời vụ và làm mới giao diện: `update/seasonal-platform-ui`, được tạo từ local `main`. Đây là hướng dẫn chạy bởi chủ dự án; agent chỉ tạo nhánh và commit local, không push/merge/deploy.

## Đợt hiện tại

Tại thư mục dự án, kiểm tra nhánh và cây làm việc:

```bash
git branch --show-current
git status
```

Nhánh phải là `update/seasonal-platform-ui`. Sau khi commit, working tree phải sạch. Nếu có chỉnh sửa mới, xem lại và commit phần đó trước khi làm tiếp.

Đẩy nhánh lên GitHub:

```bash
git push -u origin update/seasonal-platform-ui
```

Lệnh này tạo/cập nhật nhánh tương ứng trên remote và đặt upstream cho nhánh local. Không push trực tiếp `main` trong bước này.

Nếu có người đã cập nhật `main` từ lúc bạn bắt đầu sửa, cập nhật nhánh trước khi push:

```bash
git fetch origin
git merge origin/main
```

Nếu có conflict, xử lý từng file, kiểm tra lại và commit merge; không dùng reset/force-push để bỏ qua. Sau đó chạy lệnh push nhánh ở trên. Nếu không có thay đổi mới trên main thì không phát sinh merge commit.

Mở [trang so sánh để tạo pull request](https://github.com/nguyenmanhhung3105/TA_CARE/compare/main...update/seasonal-platform-ui?expand=1), chọn:

- **base:** `main`
- **compare:** `update/seasonal-platform-ui`

Tiêu đề đề xuất: **Chuyển TA.CARE sang việc thời vụ và làm mới ba website**.

Nội dung đề xuất:

```markdown
TA.CARE tập trung vào ghép nối việc thời vụ: cá nhân có thể đăng nhu cầu và nhận việc; bỏ luồng tuyển dụng, giữ kiểm tra quyền sở hữu và consent. Kho Việc Làm, Tủ Hồ Sơ và TA.CARE có giao diện, điều hướng và bảng màu phân biệt; Tủ có trang chủ tổng quan và thư viện riêng không carousel.

Làm rõ tiền công theo công việc, sửa bố cục tin/form/bộ lọc, bổ sung gợi ý và ba ví dụ minh họa trên TA.CARE. Gói import có nội dung tuyển dụng bị từ chối.

Đã kiểm tra local Python/XML/JS, phân quyền rollback, các luồng trình duyệt và responsive; bằng chứng và giới hạn trong docs/backend_local.md. Source không chứa credentials/server IP theo scanner hiện có; runtime, backups và database local không nằm trong commit.

Phát hành code-only. Việc xoá dữ liệu tuyển dụng và dữ liệu mẫu local không tự áp dụng lên production; không có data bundle hoặc migration xoá dữ liệu trong lần merge này.
```

Nhấn **Create pull request**, xem lại Files changed và các yêu cầu review/check của repository. Khi sẵn sàng phát hành, chọn **Merge pull request → Confirm merge** (hoặc **Squash and merge** nếu đó là phương thức repository cho phép).

Merge làm `main` thay đổi nên workflow [Deploy TA.CARE](https://github.com/nguyenmanhhung3105/TA_CARE/actions/workflows/deploy-tacare.yml) được kích hoạt. Push nhánh tính năng và mở pull request không chạy workflow deploy này. Theo dõi run đúng merge commit SHA; chỉ xem là triển khai thành công khi job hoàn tất thành công.

Workflow hiện tại trong `.github/workflows/deploy-tacare.yml` mặc định là **code-only**, truyền exact commit SHA tới script server. Không thêm trailer chọn data bundle trong đợt này. Git chỉ chuyển mã nguồn/assets/tài liệu đã commit, không chuyển database, filestore người dùng, mật khẩu local hay các file ignored. Tự động xoá dữ liệu tuyển dụng production chưa được chuẩn bị hoặc cấp quyền trong đợt commit này.

Sau khi merge, đồng bộ local main:

```bash
git switch main
git pull --ff-only origin main
```

## Các lần sửa sau

Bắt đầu từ main đã cập nhật rồi tạo nhánh cho đợt sửa mới:

```bash
git switch main
git pull --ff-only origin main
git switch -c update/ten-dot-sua
```

Làm việc và kiểm tra trên nhánh đó. Trước khi stage, chạy `python3 tools/security/check_repository.py`, xem `git diff`; stage các đường dẫn đã rà soát rồi commit. Push bằng `git push -u origin update/ten-dot-sua`, tạo PR vào main và merge khi muốn phát hành. Khi PR chưa merge, có thể tiếp tục dùng cùng nhánh, commit và `git push` để cập nhật PR.

Nguồn thao tác GitHub: [tạo PR](https://docs.github.com/en/pull-requests/how-tos/create-pull-requests/creating-a-pull-request), [merge PR](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/merging-a-pull-request). Điều kiện trigger và chế độ deploy được đối chiếu trực tiếp với workflow trong repository.
