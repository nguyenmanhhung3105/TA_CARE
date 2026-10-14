# TA.CARE repository guide

TA.CARE connects people, demonstrated skills and opportunities through Kho Việc Làm, Tủ Hồ Sơ and TA.CARE. Local Odoo Community 19 uses one application DB (`tacare_local`), three website records and shared `res.users` accounts. Shared accounts do not create a shared browser session across distinct domains.

## Repository map

- `source/odoo-server/`: ignored Odoo 19 core checkout; read relevant code, never edit core.
- `source/apps/tacare/addons/tacare_account_access/`: `res.users.tacare_account_role`, website projection and login host restrictions.
- `source/apps/tacare/addons/tacare_website/`: QWeb pages, `hr.job`/`hr.job.skill` extensions, profile and connection models, consent, revision and other `care.*` schema, controller permissions and brand assets.
- `source/apps/khovieclam/addons/`, `source/apps/tuhoso/addons/`: empty historical placeholders.
- `compose.yaml`, `compose.override.yaml`, `docker/`: local PostgreSQL, one Odoo service and Nginx gateway. `runtime/` and `backups/` hold ignored local data.
- `prototype/`: earlier standalone design demo with fictional seed data and a role switch; it does not authenticate with Odoo. `docs/`: audits and guides.

## Working rules

Read related manifests, models, controllers, views, security and workflow before editing. Prefer Odoo 19 Community modules (`website`, `portal`, `hr_recruitment`, `website_hr_recruitment`, `hr_skills`) and extend them in existing custom addons. Keep addon/model/XML IDs and dependencies. The target JSON model names conflict with existing `tacare.*` models; see `docs/database_mapping.md` before changing schema. Do not rename data models or run production migrations for UI changes. `res.users` is an account, `res.partner` a contact/organization, `res.company` an Odoo company scope, and `res.groups` Odoo access groups. Role alone never proves record ownership. `care.org.member` is the intended organization boundary; existing business accounts have a commercial-partner fallback until migration is approved.

Every write route must check authenticated role, record ownership, allowed fields and current state on the server. Portal direct ACLs are read-only and record-scoped; controller `sudo()` is only acceptable after narrow, explicit authorization and a scoped record lookup. Hidden buttons are not permissions. Contact access requires `care.consent` with purpose `contact`, the exact organization, field `email`, and an accepted connection. Profile discovery/matching requires current purpose-specific consent. Do not put real personal data, passwords or uploaded files in fixtures, logs or screenshots.

Use Vietnamese labels, real logos, shared design tokens, responsive layouts, visible focus, labelled forms, retained input on validation errors and reduced motion support. See `docs/prototype.md`, `docs/backend_local.md` and `docs/database_mapping.md` for design and implementation limits. The standalone `prototype/` holds fictional examples and is not Odoo login or storage. Do not report OCR, persisted matching snapshots, audit/outbox workers, or CV upload as integrated until their routes and tests exist.

Run local Odoo with `docker compose up -d db tacare gateway`; open the three `*.localhost:8069` URLs in `docs/backend_local.md`. After a local DB backup, update changed addons with `docker compose run --rm tacare -c /etc/odoo/local.conf -d tacare_local -u tacare_account_access,tacare_website --stop-after-init`, then restart `tacare`. The independent design demo runs with `python3 prototype/serve.py`. Validate Python/XML, Docker HTTP routes, role checks and form flows. The rollback-only ORM security check is `tacare_website/tests/dev_schema_check.py` and runs inside Odoo shell. Do not push, deploy, change DNS/TLS, touch production services or use a production DB without a separate request. Report exactly what ran and any limits.
