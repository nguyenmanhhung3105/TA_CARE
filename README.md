# TA.CARE local

Three websites run on one Odoo Community 19 backend and the `tacare_local` database.

```bash
docker compose up -d db tacare gateway
```

- Kho Việc Làm: <http://khovieclam.localhost:8069/>
- Tủ Hồ Sơ: <http://tuhoso.localhost:8069/>
- TA.CARE: <http://tacare.localhost:8069/>

Public pages are viewable without login. An Odoo system admin can sign in on all three sites; a business account can sign in on Kho Việc Làm and TA.CARE; a candidate can sign in on Tủ Hồ Sơ and TA.CARE. Creating or changing records requires login. Opportunities use Odoo `hr.job`/`hr.job.skill`; applications also create `hr.applicant`. The new DEV schema and unresolved design decisions are in [the database mapping](docs/database_mapping.md). See [the local backend guide](docs/backend_local.md) for DB audit, module update, roles, flows and limitations.

The earlier standalone design demo remains in [prototype/](prototype/README.md); its sample role switch is not Odoo authentication.

The running website source is the custom Odoo addon at [`source/apps/tacare/addons/tacare_website/`](source/apps/tacare/addons/tacare_website/) (QWeb views, SCSS, controllers, ORM models and security). The shared account policy is in [`tacare_account_access/`](source/apps/tacare/addons/tacare_account_access/). The design demo's category board, profile folio and blue bridge are now reflected in the Odoo pages without importing its fictional records.
