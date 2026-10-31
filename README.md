# TA.CARE local

Three websites run on one Odoo Community 19 backend and the `tacare_local` database.

```bash
docker compose up -d db tacare gateway
```

- Kho Việc Làm: <http://khovieclam.localhost:8069/>
- Tủ Hồ Sơ: <http://tuhoso.localhost:8069/>
- TA.CARE: <http://tacare.localhost:8069/>

Trang chủ công khai; chức năng riêng yêu cầu đăng nhập và kiểm tra quyền trên server. Cá nhân và quản trị viên dùng cả ba website; doanh nghiệp dùng Kho + TA.CARE. Hệ thống chỉ phục vụ công việc thời vụ/theo đầu việc. `hr.job` giữ tên native để tương thích; luồng hiện tại không tạo ứng tuyển tuyển dụng. Xem [phạm vi sản phẩm](docs/project_scope.md), [cấu trúc source](docs/source_structure.md) và [hướng dẫn local](docs/backend_local.md).

Quy trình phát hành: [CI/CD TA.CARE — từ pull request đến UAT và production](docs/ci_cd.md).

The earlier standalone design demo remains in [prototype/](prototype/README.md); its sample role switch is not Odoo authentication.

The running website source is the custom Odoo addon at [`source/apps/tacare/addons/tacare_website/`](source/apps/tacare/addons/tacare_website/) (QWeb views, SCSS, controllers, ORM models and security). The shared account policy is in [`tacare_account_access/`](source/apps/tacare/addons/tacare_account_access/). The design demo's category board, profile folio and blue bridge are now reflected in the Odoo pages without importing its fictional records.
