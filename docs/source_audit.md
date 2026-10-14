# Source audit — 14/10/2026

## Confirmed before the local backend work

Git root is `TA_CARE`, branch `main`, HEAD `37adb94fd005e277d5ac83ab190b143dbe1f63a3`, remote `git@github.com:nguyenmanhhung3105/TA_CARE.git`. Worktree was clean before this prototype. `.github/workflows/deploy-tacare.yml` deploys on a push to `main`; this work has not been pushed. Odoo core exists locally under ignored `source/odoo-server/`, so the folder is not limited to custom addons.

| Path read | Confirmed responsibility | Reuse for future Odoo UI | Current limit |
| --- | --- | --- | --- |
| `source/apps/tacare/addons/tacare_website/__manifest__.py` | Addon `tacare_website` depends on `website`; loads three QWeb views and `web.assets_frontend` SCSS. | Keep addon, QWeb, frontend bundle. | No application models, ACLs or workflow. |
| `.../tacare_website/controllers/main.py` | Overrides Website index by website domain; maps local and production hosts to three home templates. | Multiwebsite route entry and `request.render`. | Only index routing; local links cross `*.localhost` hosts. |
| `.../tacare_website/views/{khovieclam,tuhoso,tacare}.xml` | Existing landing templates and `website.page` preview records (`page_khovieclam_preview`, `page_tuhoso_preview`, `page_tacare_preview`). | Brand entry pages and QWeb layout convention. | Static information; no forms, records or flows. |
| `.../tacare_website/static/src/scss/website.scss` | Scoped `tc-site` visual styles. | Asset naming and scoped CSS precedent. | Existing accent colors are not fully based on current logos. |
| `source/apps/tacare/addons/tacare_account_access/__manifest__.py` | Addon `tacare_account_access`, depends on `website`, `portal`, `auth_signup`. | Existing account module and dependency boundary. | No security CSV/XML for job/profile models. |
| `.../tacare_account_access/models/res_users.py` | Extends `res.users` with `tacare_account_role` and computed allowed websites. Host rule maps business to Kho Việc Làm/TA.CARE, candidate to Tủ Hồ Sơ/TA.CARE. | Role entry checks, not ownership. | Selection field, not `res.groups` role design; no ownership record rules. |
| `.../tacare_account_access/models/ir_http.py` | Pre-dispatch host check for signed-in users. | Host access guard precedent. | Does not prove SSO or protect new business records. |
| `.../tacare_account_access/views/res_users_views.xml` | Admin form page for role and allowed sites. | Admin-facing account UI. | No applicant self-signup role assignment flow. |
| `source/odoo-server/addons/website/controllers/main.py`, `.../views/website_templates.xml`, `.../__manifest__.py` | Website index, layout, asset bundle, website routing. | Route/template/asset implementation reference. | Core is read only. |
| `source/odoo-server/addons/portal/controllers/portal.py`, `.../views/portal_templates.xml` | Portal layout and counters. | Future personal workspaces. | No TA.CARE portal data yet. |
| `source/odoo-server/addons/web/controllers/home.py`, `source/odoo-server/addons/auth_signup/controllers/main.py` | Login and signup behavior. | Future account integration. | Signup role policy needs design and server checks. |
| `compose.yaml`, `compose.override.yaml`, `docker/local-nginx.conf` | Local PostgreSQL and three Odoo processes behind gateway. | DEV environment reference. | Current override does not itself demonstrate one shared Odoo app/database target. |
| `.github/workflows/deploy-tacare.yml` | Production deploy trigger. | Release boundary. | Do not push a UI prototype to `main` as an implicit deployment. |

The addon `tacare_account_access_19` mentioned in historical notes is represented here by directory/module `tacare_account_access`; do not rename it. `source/apps/khovieclam/addons/` and `source/apps/tuhoso/addons/` contain only placeholders. No `care.*`, job, profile, matching, invitation, notification or feedback models were found in tracked custom addons. No addon test files were found. No `AGENTS.md` existed in this repo before this task. Source `__init__.py` files were read; they only import the listed model/controller packages.

## Requirement versus demo

The required target is one Odoo Community 19 backend, one application database, three websites and centrally governed accounts. The original local compose override was a three-process setup. The standalone `prototype/` still shares a simulated session and `localStorage` data; it is an interaction test, not evidence of multi-domain SSO or production deployment.

## Local implementation after this audit

The newer user request authorized local Odoo/DB integration and Docker restart. The override now runs one Odoo app/database for the three sites. `tacare_website` now depends on `website_hr_recruitment`, which installs `hr_recruitment`; it adds `hr.job` fields, candidate profiles, connections, notifications, scoped web controllers, QWeb pages and the supplied logos. `tacare_account_access` includes the three local hostnames. These are local changes only; the original observations above describe what was present when source review began. See [backend_local.md](backend_local.md) for live DB findings and validation.

`ui-ux-pro-max` was available and used for a generated marketplace/directory design-system search plus focused form validation guidance. The ECC cache was available; its Codex navigation guide was read for scoped source review and verification. No ECC installer, hooks, copied agents or global configuration were used.
