# Odoo backend local for three websites

## DB and Docker audit

On 14–15 October 2026, `tacare_local` held three website records (`khovieclam.localhost:8069`, `tuhoso.localhost:8069`, `tacare.localhost:8069`) and nine existing users (four active, five archived). The role field showed one business account, one candidate account and seven pending accounts. Only Odoo system administrators are treated as web admin. `khovieclam_local` and `tuhoso_local` were legacy separate DBs; they were inspected but left untouched. Local pre-update dumps are in ignored `backups/tacare_local_before_odoo_ui_20261014.dump` and `backups/tacare_local_before_schema_20261014.dump`.

The local Compose override now runs one Odoo process (`tacare`), PostgreSQL and the Nginx gateway. Ports 8070 and 8071 remain aliases to the same backend and rewrite their Host header to the relevant website. Use the three `*.localhost:8069` addresses as primary entry points. No production server, DNS or remote DB was changed.

## Run and update

```bash
docker compose up -d db tacare gateway
docker compose ps
```

After changing addon Python, restart local Odoo with `docker compose restart tacare`. After changing manifests, models, views or assets, back up the local DB and update the addons:

```bash
docker compose run --rm tacare -c /etc/odoo/local.conf -d tacare_local -u tacare_account_access,tacare_website --stop-after-init
docker compose restart tacare
```

Log in through the normal Odoo login form. Existing passwords were not changed. Browser cookies are host scoped, so the same account may need to sign in again on another website; cross-domain SSO is not implemented.

## Role and data map

| Role | Sign-in websites | Can change |
| --- | --- | --- |
| Odoo system admin | All three | Organization jobs and revision review through web form; native Odoo backend according to Odoo groups. |
| Business portal user | Kho Việc Làm, TA.CARE | Jobs of active member organizations; `can_manage_jobs` grants tin management and `can_handle_candidates` grants applicant processing. Organization owner has both; existing `recruiter` members retain applicant handling. Existing account without membership uses its commercial partner until membership migration. |
| Candidate portal user | Tủ Hồ Sơ, TA.CARE | Their `tacare.profile`, skills, evidence, consent and their applications/replies. |
| Guest | All public pages | Nothing; protected routes redirect to login. |

`hr.job` from `hr_recruitment` and `website_hr_recruitment` stores opportunities. `hr.job.skill` and `hr.skill` from `hr_skills` store the structured catalog behind the text form. Published jobs appear on Kho Việc Làm and TA.CARE matching. A candidate application creates both `hr.applicant` for Odoo recruitment and `tacare.connection` for the shared request flow; `email_from` is withheld until an explicit contact grant. The custom `tacare.profile`, skill, evidence, connection and notification models live in `tacare_website` alongside the new `care.*` schema. Portal users have read-only direct ACL on scoped own data where needed; web routes verify role, owner and state before scoped privileged writes. Jobs are linked to an organization partner, not a new `res.company` per customer. See [the 33-entity mapping](database_mapping.md) for every field family, constraint, conflict and pending decision.

Public visitors can browse jobs and public profiles only when discovery consent permits. A candidate can create/edit profile, skills and evidence, set visibility and consent, find matching jobs and apply. A business account can create/publish/pause/close its jobs, select a job, see consented profiles and invite. Edits to an already published job are held as `care.job.revision` until a system admin approves. Both sides can see a connection; the recipient can accept/decline and the sender can cancel while pending. Accepted connections can record a follow-up result; agreement to talk does not mean hired. Email access needs a separate contact consent for that organization and is removed immediately on revocation. Notifications are per account.

## Local QA evidence

The module update installed Odoo's `hr_recruitment`, `website_hr_recruitment` and `hr_skills` dependencies. Public home pages and jobs returned HTTP 200; protected edit/profile/matching routes redirected guests to Odoo login. Temporary QA accounts proved allowed logins on the correct websites for each role and rejection on the wrong website. HTTP forms created/published a job; saved a profile, catalog skill, private evidence and discovery/matching consent; created an applicant/application; accepted a connection; granted and revoked organization-specific email access; saved a result; submitted and admin-approved a published-job revision. DB readback confirmed `hr.job.skill`, `hr.skill` and `care.consent`. A rollback-only ORM test in `tacare_website/tests/dev_schema_check.py` checks two businesses, two candidates and cross-record isolation. QA accounts and their records were removed; the original total remains nine users.

Final readback after cleanup: nine users total, 36 catalog skills, zero QA users, zero jobs/profiles/connections/consents/revisions/documents. No demo candidate or business records were left in the application database. Docker `db`, `tacare` and `gateway` were running; all three local home pages returned HTTP 200. Updated desktop/mobile screenshots are in `docs/screenshots/odoo-*.png` and a Chrome check found no horizontal overflow at 375px.

The [standalone prototype](../prototype/README.md) still contains fictional seed data (including Đức Mạnh, Mạnh Hùng, Anh Tuấn and An Nhật) for visual/design review. Those names are not Odoo users and were not written into real account records.

Final public page screenshots from local Docker: [Kho Việc Làm](screenshots/odoo-khovieclam.png), [Tủ Hồ Sơ](screenshots/odoo-tuhoso.png), [TA.CARE](screenshots/odoo-tacare.png). The earlier design demo screenshots are alongside them in `docs/screenshots/`.

## UI refresh on 15 October 2026

The live Odoo pages now follow the standalone design's type scale and spacing. All three sites share a single header pattern, 1240px content width, aligned buttons and cards, and consistent mobile layouts. Kho Việc Làm has a sidebar filter and uniform result cards; the home pages use the actual Odoo records and display an empty state when no jobs exist. Typography is explicitly scoped to `.tc-live` so Odoo's default heading font cannot override it; Tủ Hồ Sơ retains its serif hero. The presentation changes are in `views/live.xml` and `static/src/scss/live_polish.scss`.

The `tacare_local` database was backed up to ignored `backups/tacare_local_before_ui_20261015.dump` before updating `tacare_website`. Chrome checked all three home pages and the jobs list at 1440px and 390px: HTTP 200, expected heading fonts and no horizontal overflow. The current [jobs desktop](screenshots/odoo-jobs.png) and [jobs mobile](screenshots/odoo-jobs-mobile.png) captures are included with the refreshed home page screenshots. No jobs or accounts were added for this visual update.

## Production homepage probe contract

The GitHub Actions workflow at `.github/workflows/deploy-tacare.yml` deploys pushes to `main` through the existing server script. Its isolated staging HTTP probe expects `tc-hub` on the TA.CARE homepage, `tc-jobs` on Kho Việc Làm and `tc-profiles` on Tủ Hồ Sơ. The active `live_home` template inherits `live_layout`, so these marker classes belong on the rendered layout's `#wrap`. Keep them when changing the homepage. The DEV database banner is shown only on `*.localhost`; production uses the same layout without the local database label. The server's deploy scripts are outside this repository and were not changed here.

After a local addon update, run `python3 source/apps/tacare/addons/tacare_website/tests/homepage_contract_smoke.py` to check the same three markers and all three login pages through HTTP. This only checks local Odoo; the server's isolated staging and production gates still run when a commit is pushed to `main`.

## Current limits

- The structured capability, availability, service area, preference, document, OCR, match snapshot, feedback, audit and integration models are installed but have no complete user flow yet. CV upload, OCR processing, verifier workflow and cross-domain SSO are not implemented.
- Matching remains calculated live and does not write `care.match.result`. Kho việc làm now shows evidence, unknowns, preferences and explicit work-mode conflicts without a percentage score or hiring decision.
- Business account assignment remains an admin task in Odoo; no public self-grant of business role was enabled.
- The JSON design is a target, with unresolved naming/cardinality/enum decisions listed in `docs/database_mapping.md`. This DEV implementation did not rename existing models or migrate production data.
- Legacy DBs and stopped old app containers were kept to avoid deleting user data.

## Kho việc làm F01–F12 on DEV, 17 October 2026

The live Kho website now uses Odoo `hr.job` plus `care.job.sector` (administrator-managed catalog), `care.job.requirement` (one record per mandatory/preferred criterion), `tacare.connection`, `care.job.revision`, `care.consent`, and `care.audit.event.changes`. Employer activity sectors and market scope live on `res.partner`, independently from job sector, education major and position. Work mode, work fraction, days/week, duration, shift, income type/period and specialist flags are separate fields. Only a title of at least two characters is needed for a draft. Publishing also needs position, sector, type, work mode, location unless remote, description, future deadline and one mandatory criterion or skill. Existing `tacare_*` fields and Odoo core IDs were preserved.

Admins configure sector records under **Kho việc làm · Quản trị → Ngành nghề** and assign `can_manage_jobs` / `can_handle_candidates` under **Quyền nhân sự** on an active `care.org.member`. A membership with role `owner` has both; existing `recruiter` members retain applicant handling; other combinations need explicit capability flags. A legacy business account without membership retains its commercial partner fallback until migration is agreed. Neither capability is granted by changing a web form or by login role alone.

Screens: `/` on `khovieclam.localhost:8069`, `/kvl/manage`, `/kvl/job/new`, `/kvl/job/<id>/preview`, `/kvl/job/<id>/history`, `/kvl/candidates?job=<id>`, `/kvl/job/<id>/candidate/<profile_id>`, `/tacare/connections?type=application` and `?type=invitation` on the same host. Business organization fields are at `/kvl/organization/<id>`. Candidate application and invitation reply still use shared TA.CARE connection routes; the full candidate website was not rebuilt in this phase.

The DEV database was backed up to ignored `backups/tacare_local_before_kvl_20261017.dump` before `-u tacare_website`. Upgrade completed with exit code 0 on Odoo 19 Community. The three public homepages, three login pages, jobs list and guest-to-login redirect returned expected HTTP statuses. A temporary fictitious-account HTTP run passed F01–F12, including invalid transitions, published revision review, old pending application on a paused job, duplicate invite, withdrawal, closed/reopened job, draft-only deletion, organization/role isolation and direct URL checks. An HTML check confirmed a fictitious private email and evidence URL were absent for unconsented HR access. `tests/dev_kvl_form_check.py` passed as a rollback-only Odoo shell check for four sectors, publish requirements and invalid weekly schedule. Temporary QA accounts, jobs, profiles and connections were removed after verification; append-only `care.audit.event` entries from QA remain in DEV. Production was not accessed.

Run the form/schema check after a DEV backup with:

```bash
docker compose run --rm --no-deps -T tacare shell -c /etc/odoo/local.conf -d tacare_local < source/apps/tacare/addons/tacare_website/tests/dev_kvl_form_check.py
```

The template changes preserve `tc-jobs`, `tc-profiles` and `tc-hub`. The workflow still deploys only `source/apps/tacare/addons/` on push to `main`; no push or server deploy was made here. The addon version is `19.0.3.0.0`; no Python system dependency or manual SQL migration is needed. Updating the addon creates new ORM tables/columns. The existing published-job revision review remains in place. Contact email still needs separate organization-specific consent after connection acceptance. The profile comparator uses exact declared skill names, disclosed education and shared evidence titles; it marks absent data unknown, so it is not a verified ranking algorithm. Structured candidate availability and source verification are outside this Kho phase.
