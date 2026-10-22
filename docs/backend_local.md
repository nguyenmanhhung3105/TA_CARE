> **Thiết kế hiện tại 22/10/2026:** Kho/Tủ đã chuyển sang Everyday services sau nghiên cứu các marketplace. Xem [thiết kế và kiểm tra local](research/implementation_service_design_2026-10-22.md). Addon website 19.0.11.0.0; dữ liệu nghiệp vụ không đổi trong lần sửa giao diện này.

> **Phạm vi mới 22/10/2026, sau trao đổi mentor:** chỉ việc thời vụ/đầu việc, bỏ tuyển dụng. Cá nhân được dùng cả ba site và đăng nhu cầu; doanh nghiệp dùng Kho + TA.CARE. Đã backup local, xóa 5 tin + 3 hồ sơ tuyển dụng; còn 15 tin thời vụ, 3 hồ sơ, 12 mục nhận làm. Không còn tạo `hr.applicant` từ kết nối. Các mô tả tuyển dụng và con số 20/6 bên dưới là lịch sử, không dùng làm hướng dẫn phát hành hiện tại. Gói dữ liệu cũ chứa tuyển dụng bị từ chối; chưa chuẩn bị hoặc triển khai gói mới. Xem [phạm vi hiện tại](project_scope.md), [triển khai local](research/implementation_seasonal_only_2026-10-22.md).

# Odoo backend local for three websites

> **Phát hành 20/10/2026:** [hai chế độ code / kèm dữ liệu demo](deploy_modes.md) đã được chuẩn bị và kiểm tra local. Chưa cài trên server, chưa commit/push đợt này. Người vận hành tự cài script bằng bộ lệnh trong hướng dẫn; mặc định không nhập dữ liệu local.

> **Hiện hành 20/10/2026:** [làm lại Tủ Hồ Sơ, ảnh/carousel và nhiều hồ sơ](research/implementation_profile_refresh_2026-10-20.md). Tủ hiển thị hồ sơ ngay sau đăng nhập; có tab admin xem tất cả. Mỗi ứng viên được tạo nhiều hồ sơ. Kho/Tủ có carousel riêng, TA.CARE dùng ảnh tĩnh. Hai tài khoản ứng viên được yêu cầu đã có hai hồ sơ mỗi tài khoản. Các số liệu ngày 19/10 bên dưới là lịch sử trước đợt sửa này.

> **Hiện hành 19/10/2026:** [demo tuyển dụng và việc linh hoạt](research/implementation_flexible_demo_2026-10-19.md) đã chạy trên Odoo local. Có 20 công việc (5 tuyển dụng + 15 linh hoạt), 15 hồ sơ (5 tuyển dụng + 10 có mục nhận việc). Chín tài khoản gốc được giữ nguyên. Có carousel ảnh chụp thật và form mới; Tủ yêu cầu đăng nhập, chỉ chủ hoặc admin xem dữ liệu. Số liệu 0 tin/0 hồ sơ ngày 17/10 bên dưới là lịch sử trước seed demo.


> **Hiện hành 17/10/2026:** xem [triển khai form v2 và ba trang chủ độc lập](research/implementation_forms_homepages_2026-10-17.md). Ba homepage đã thay cấu trúc riêng, không còn dùng một mẫu hero/card chung. Form mới, consent và quyền tổ chức đã kiểm tra lại. Sau dọn QA: 9 tài khoản gốc giữ nguyên login/password/active/role; 0 tin, 0 hồ sơ, 0 kết nối; 10 lĩnh vực, 48 nhóm nghề. Các mục ngày cũ bên dưới là lịch sử.

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

The live Odoo pages now follow the standalone design's type scale and spacing. All three sites share a single header pattern, 1240px content width, aligned buttons and cards, and consistent mobile layouts. Kho Việc Làm has a sidebar filter and uniform result cards; the home pages use the actual Odoo records and display an empty state when no jobs exist. Typography is explicitly scoped to `.tc-live` so Odoo's default heading font cannot override it. The presentation changes are in `views/live.xml` and `static/src/scss/live_polish.scss`.

The `tacare_local` database was backed up to ignored `backups/tacare_local_before_ui_20261015.dump` before updating `tacare_website`. Chrome checked all three home pages and the jobs list at 1440px and 390px: HTTP 200, expected heading fonts and no horizontal overflow. The current [jobs desktop](screenshots/odoo-jobs.png) and [jobs mobile](screenshots/odoo-jobs-mobile.png) captures are included with the refreshed home page screenshots. No jobs or accounts were added for this visual update.

## Three-site structure applied locally on 17 October 2026

The approved previews in `docs/design-preview/` are applied to Odoo Website/Portal. `static/src/scss/approved_design.scss` supplies shared Vietnamese typography, spacing, focus, forms, buttons and status labels with a logo-based palette for each site. `static/src/scss/site_structures.scss` loads after it and gives each website its own page structure. Kho Việc Làm has a centered public search, sector chips, a full-width opportunity band and a horizontal job filter; its authenticated employer area has a separate management rail and sectioned posting form. Tủ Hồ Sơ uses a document page with a table of contents and context rail; the editable profile uses a document workspace. TA.CARE centers search and presents the two destination paths and the reasons for matching below it. These follow the selected Wellfound/Workable, Notion and cord.com layout directions, with the selected Perplexity-style flat filter and explanation treatments. Colors continue to come from the actual logos.

`views/live.xml` retains the three homepage probe markers and the shared `kvl_job_card` QWeb component. `views/kvl_pages.xml` uses that card for employer job management and keeps existing routes, record checks and form field names. The visual select control in `approved_design.scss` fixes the uneven native arrow and padding seen on the sector filter. This was a layout change; it did not add new backend routes or change access rules.

Before the structure update, the local database and filestore were backed up to ignored `backups/tacare_local_before_structure_20261017.dump` and `backups/tacare_local_filestore_before_structure_20261017.tar.gz`. The previous UI backup remains at `backups/tacare_local_before_approved_ui_20261017.dump` and the corresponding filestore archive. Local Odoo screenshots at 375px and 1440px are in `docs/screenshots/approved-*.png`, including public pages, `/kvl/jobs`, authenticated `/kvl/manage` and `/kvl/job/new`. The public browser check verified no horizontal overflow, loaded logos and the three marker classes at both widths. Temporary business accounts used for authenticated screenshots were removed. The design previews remain static and use simulated data.

## Production homepage probe contract

The GitHub Actions workflow at `.github/workflows/deploy-tacare.yml` deploys pushes to `main` through the existing server script. Its isolated staging HTTP probe expects `tc-hub` on the TA.CARE homepage, `tc-jobs` on Kho Việc Làm and `tc-profiles` on Tủ Hồ Sơ. The active `live_home` template inherits `live_layout`, so these marker classes belong on the rendered layout's `#wrap`. Keep them when changing the homepage. The DEV database banner is shown only on `*.localhost`; production uses the same layout without the local database label. The server's deploy scripts are outside this repository and were not changed here.

After a local addon update, run `python3 source/apps/tacare/addons/tacare_website/tests/homepage_contract_smoke.py` to check the same three markers and all three login pages through HTTP. This only checks local Odoo; the server's isolated staging and production gates still run when a commit is pushed to `main`.

## Current limits

- The structured capability, availability, service area, preference, document, OCR, match snapshot, feedback, audit and integration models are installed but have no complete user flow yet. CV upload, OCR processing and verifier workflow are not implemented. Cross-domain SSO was added locally on 20 October 2026; see the latest SSO update below.
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

## Local update — restoration and login dialogs, 20 October 2026

Current behavior is documented in [restoration and authentication](research/implementation_auth_restore_2026-10-20.md). TA.CARE restores the original orbit/story design without a photo carousel. Tủ starts with its carousel, then the owner/admin library, and includes a prominent TA.CARE link. Businesses use Kho + TA.CARE; candidates use Tủ + TA.CARE; only system admins use all three. Other homepages remain public; functions require a permitted login on the server. Login dialogs post the native Odoo login form and preserve CSRF/CAPTCHA/MFA hooks. Sessions remain separate per domain.

Admin all-profiles views use allowed companies rather than only the active company. The local dataset remains 20 jobs (5 recruitment + 15 flexible), 20 profiles and 12 profile capabilities. Two requested candidates still have two profiles each; existing credentials were preserved. Local addon version is `19.0.6.1.0`. Python/XML/JS checks, responsive Chrome checks, role/login and profile isolation checks, existing-admin company checks, rollback schema/profile/flexible checks, and all three homepage/login HTTP probes passed. No production service was accessed or deployment triggered.

## Local update — synchronized sign-in/out, 20 October 2026

The owner explicitly requested SSO. [Current implementation and validation](research/implementation_sso_2026-10-20.md) supersedes the earlier separate-login behavior. Native cookies stay host-only; short-lived browser-bound handoffs synchronize the permitted sites after complete Odoo authentication. Global logout revokes the browser group on the server, and open tabs update within about three seconds while visible or when focused. Other browsers/devices remain independent. Account switching clears the previous account at excluded sites. No session ID or password travels in a handoff URL.

Addon versions: `tacare_account_access` 19.0.3.0.0; `tacare_website` 19.0.7.0.0. Local backup: ignored `backups/sso_20261020/`. New technical models: `care.auth.session` and `care.auth.handoff`; no existing business model or credentials were renamed or reset. Production was not accessed or deployed.


## Local update — product packages and account-owned demo, 21 October 2026

See [implementation and checks](research/implementation_account_refresh_2026-10-21.md). Addon `tacare_website` 19.0.8.0.0 now groups product controllers/templates under `sites/khovieclam`, `sites/tuhoso`, `sites/tacare`; shared models/authentication and XML IDs remain intact. Website-specific assets use Odoo's required `static/` path.

The local dataset supersedes the counts above: 20 detailed jobs, 7 profiles attached to existing accounts, 12 work offers. Old 15 demo profile shells were removed after rehoming useful offers. No existing account credentials/roles or consents were changed. Profile sharing is still opt-in by the owner. TA.CARE has live explainable flexible comparisons and `/tacare/examples` with three clearly fictional UI scenarios. No booking/payment/transport operation or persisted matching snapshot was added. Production was not accessed or deployed; the ID 22 shown in the production screenshot does not exist locally.


## Local update — admin removal and visual polish, 21 October 2026

Addon `tacare_website` is now 19.0.8.1.0. See [behavior, implementation and tests](research/implementation_admin_polish_2026-10-21.md). System admins have scoped confirmation/POST deletion for Kho jobs and Tủ profiles/offers; linked history is retained outside active lists. Kho's candidate navigation tab is removed. TA.CARE's admin homepage shows current consent-checked pairs and three clearly fictional examples after the orbit. A final shared stylesheet normalizes reading hierarchy across all three sites and moves native select chevrons 16px inside the field. The local sample dataset remains unchanged after disposable QA cleanup. Production was not accessed or deployed.


## Local update — detailed recruitment profiles and admin editing, session 21 October 2026

Addon `tacare_website` 19.0.9.0.0 adds structured work and education entries to the existing profile, fuller job preferences/portfolio/salary range, and an explicit owner/admin editor at `/tuhoso/profile/<id>/edit`. Admin content editing stays separate from owner-only consent. Three existing fictional recruitment profiles are enriched without account or sharing changes. See [behavior, schema, data and validation](research/implementation_recruitment_profile_2026-10-21.md). Production was not accessed or deployed.

Kiểm chứng bổ sung hồ sơ tuyển dụng: Chrome PASS admin/owner/cross-profile/consent và form tạo/sửa, 1440/375/320 px; ORM recruitment + schema rollback PASS; HTTP ba trang chủ/login PASS. Đã dọn QA, đối chiếu 20 việc làm / 6 hồ sơ gắn account / 12 offer và 3 kinh nghiệm + 3 học tập mẫu. Xem `docs/research/implementation_recruitment_profile_2026-10-21.md`.

22/10/2026: đã chuẩn bị bundle `tacare.demo.v2`, kiểm thử Odoo rollback và công cụ deploy offline/container; 4 portal + 58 bản ghi nghiệp vụ gồm các mục hồ sơ mới. Gói JSON riêng ở ignored runtime, không commit hash mật khẩu. Hướng dẫn vận hành hiện tại: `docs/deploy_current_data_2026-10-22.md`. Chưa push/cài gate hoặc nhập server.


### Điều hướng và trang bên trong — 22/10/2026, addon 19.0.12.0.0

Giữ nguyên nội dung/bố cục trang chủ Kho và Tủ theo phê duyệt; navbar ba sản phẩm có Trang chủ, tên mục rõ và nền màu cho tab hiện tại. TA.CARE dùng trang chủ mới giới thiệu hai phía và căn cứ ghép nối. Chi tiết việc, form nhu cầu/dịch vụ, giới thiệu hồ sơ, trang ghép nối/kết nối dùng bố cục thống nhất.

Trang hồ sơ mở từ gợi ý dùng `/tacare/matching/<job_id>/profile/<profile_id>` với chủ tin/quyền tổ chức và consent hiện hành; các route tuyển dụng cũ vẫn khóa. Xem [ghi chú triển khai, nguồn tham khảo và kiểm tra](research/navigation_interiors_2026-10-22.md), ảnh trong `docs/screenshots/navigation-interiors-20261022/`. Chỉ cập nhật local, không push/deploy.


### Rà soát tối 22/10/2026 — addon 19.0.13.0.0

Header ba website hiển thị tên người đăng nhập. Khung nội dung dùng chung max 1280px; danh sách chủ tin chiếm toàn hàng khi không có sidebar; nhãn bộ lọc 16px. TA.CARE chuyển sang plum/lavender, đưa gợi ý theo tài khoản và ba thẻ ví dụ có ảnh ngay sau hero. Trang ví dụ trình bày riêng hai phía và các căn cứ. Matching khi chưa có nhu cầu đủ điều kiện có hướng dẫn và CTA đăng mới trên đúng Kho host. [Chi tiết, nguồn ảnh và kiểm tra](research/hub_review_2026-10-22.md). Không đổi schema hoặc deploy production.


### Chiều ngang màn hình rộng — 23/10/2026

Theo yêu cầu làm rõ, bỏ trần 1280px tại `hub_review.scss`; khung ba sản phẩm co theo màn hình với lề 48/24/20px. Trước sửa, viewport 1920px chỉ có khung 1280px và lề 320px mỗi bên. Chỉ đổi CSS và restart local; không cập nhật database, commit hoặc deploy.

Đã đo bằng Chrome headless trên `/vi` của cả ba home tại 320/375/768/1100/1440/1920/2560px: khung header bằng khung nội dung, đúng lề và không tràn ngang/lỗi JS. Ở 1920px, nội dung rộng 1824px, lề 48px mỗi bên. Ảnh trong `docs/screenshots/fluid-width-20261023/`. Security scan 282 tệp và `git diff --check` PASS.


### Header hai hàng — 23/10/2026

Theo yêu cầu mới, `service_navigation` có `.sx-brand-row` chứa logo và tên tài khoản, `.sx-navigation-row` chứa navbar và `.sx-header-actions` (Cách hoạt động, đăng nhập/đăng xuất, Đăng nhu cầu/Tạo hồ sơ). Giữ active tab, liên kết và native auth. Đã backup ignored `backups/header_rows_20261023/tacare_local.dump`, kiểm tra pg_restore list, update addon và restart local. Chrome kiểm tra guest và một tài khoản QA có tên dài trên cả ba website, 320/375/768/1100/1280/1440/1920px: tên ở trên, desktop menu/nút chung hàng, không tràn, tab đúng và logout thật PASS. XML, security scan 282 tệp và diff whitespace PASS. Ảnh tại `docs/screenshots/header-rows-20261023/`; tài khoản QA và file credentials riêng được dọn. Không commit/push/deploy.


### Header theo trạng thái đăng nhập — 23/10/2026

Yêu cầu mới thay phần phân hàng ở trên: khách có Cách hoạt động / Đăng nhập / Đăng nhu cầu hoặc Tạo hồ sơ căn giữa theo chiều dọc giữa hàng thương hiệu và navbar trên desktop. Người đăng nhập có tên tài khoản và Đăng xuất ở hàng trên; Cách hoạt động và CTA ngang hàng navbar bên dưới. Shared QWeb thêm trạng thái guest/authenticated và nhóm account/logout; CSS cuối dùng grid cho guest, responsive wrap cho màn hình nhỏ. Native URL đăng nhập, SSO, logout và trạng thái tab giữ nguyên.

- Backup local mới: `backups/header_states_20261023/tacare_local.dump`, quyền thư mục 700 / tệp 600; `pg_restore --list` thành công.
- Cập nhật `tacare_website` bằng Odoo `--stop-after-init` trên `tacare_local`, exit 0; restart local. Không đổi schema.
- XML parser chuẩn Python PASS (máy host không có lxml); security scanner PASS 282 tệp; `git diff --check` PASS.
- Chrome/Playwright `/tmp/tacare-header-states-check.cjs`: cả 3 homepage guest và đăng nhập, viewport 320/375/768/1100/1280/1440/1920 PASS; kiểm tra nhóm nút guest căn giữa, tên dài + logout hàng trên, help/create cùng navbar desktop, không chồng lấn/tràn ngang, active Trang chủ, native login + SSO + logout, không lỗi JavaScript. Ảnh ở `docs/screenshots/header-states-20261023/`; đã xem ảnh desktop cả hai trạng thái và mobile đăng nhập.
- Một tài khoản QA hư cấu tạm thời được tạo và xoá sau kiểm tra; tệp credentials private đã xoá. Không sửa jobs/profiles hoặc dữ liệu demo hiện có.
- Chỉ áp dụng local; chưa commit, push hay deploy production.


### Thử tông màu ba website — 23/10/2026

Chủ dự án yêu cầu đổi thử màu độc lập với logo. Bản thử: Kho cobalt/apricot, Tủ terracotta/cream, TA.CARE petrol/ice. `service_palette.scss` đăng ký cuối asset bundle; CSS service/interior/hub review chuyển màu cố định của giao diện sang token. Giữ nguyên layout, ảnh, logo, routes, quyền và dữ liệu hiện có. Chi tiết token trong `docs/design-system/everyday-services.md`.

- Backup local `backups/palette_trial_20261023/tacare_local.dump`, quyền thư mục 700/tệp 600, `pg_restore --list` PASS. Update `tacare_website --stop-after-init` exit 0, restart local; không đổi schema.
- Chrome/Playwright `/tmp/tacare-palette-check.cjs` PASS: cả ba home guest + đăng nhập, logo/nav không đổi cấu trúc, native login và SSO, tab hiện tại, dialog/hover, Kho danh sách + chi tiết + form, Tủ form mới, hub ví dụ + matching. Kiểm tra viewport 320/375/768/1440 không tràn ngang, không lỗi JS, cả ba homepage marker đúng. Đo contrast token chữ/nền chính/soft/panel/footer >=4.5:1; nút trắng/brand và hover >=4.5:1; control border/trắng >=3:1; focus form hiện rõ. Đây là kiểm tra các cặp màu và trang nêu trên, không phải audit WCAG toàn hệ thống.
- Đã xem ảnh ba homepage desktop, chi tiết Kho desktop và form Tủ mobile. Ảnh ở `docs/screenshots/palette-trial-20261023/`; báo cáo màu riêng không chứa tài khoản ở `/tmp/tacare-palette-report.json`.
- Manifest parse + kiểm tra không có vòng token PASS; security scan 283 tệp PASS; diff whitespace PASS. Một account QA hư cấu tạm đã xoá, file credentials private đã dọn. Không thêm/sửa jobs/profiles.
- Chỉ cập nhật local để chủ dự án đánh giá màu; chưa commit/push/deploy.

### Điều chỉnh tiếp màu Kho/Tủ — 23/10/2026

Chủ dự án giữ palette TA.CARE, yêu cầu đổi lại Kho/Tủ. Chỉ hai block `tc-jobs`/`tc-profiles` trong `service_palette.scss` đổi về xanh đậm – kem trước bản thử; toàn bộ token hub giữ nguyên. Restart local, không upgrade database, không đổi schema/dữ liệu. Chrome `/tmp/tacare-palette-refinement-check.cjs` PASS ba homepage HTTP/marker, màu thực render, contrast chữ/nút >=4.5:1, viewport 320/375/768/1440 không tràn/lỗi JS; đã xem ảnh Kho/Tủ desktop. Evidence `docs/screenshots/palette-refinement-20261023/`. Security scan 283 tệp + diff whitespace PASS. Không tạo account QA, commit, push hay deploy.

### Kho/Tủ xanh sâu hơn — 23/10/2026

Theo yêu cầu tiếp theo, chỉ token Kho/Tủ trong `service_palette.scss` đổi sang forest green `#0b2e24`, hover `#061f18`, ink `#162b21`, accent `#24513b`, control border `#70846f`. Block TA.CARE đã đối chiếu giữ nguyên. Restart Odoo local, không upgrade database. Chrome `/tmp/tacare-deeper-green-check.cjs` PASS cả ba homepage HTTP/marker, palette thực tế, contrast, không tràn tại 320/375/768/1440 và không lỗi JavaScript. Chữ chính Kho/Tủ trên nền kem đạt 14.35:1; nút/hover chữ trắng đạt >=4.5:1. Đã xem ảnh Kho desktop; ảnh cả ba tại `docs/screenshots/palette-deeper-green-20261023/`. Security scan 283 tệp và diff whitespace PASS. Không đổi dữ liệu hoặc commit/push/deploy.


### Bỏ nhãn “trọn việc”, làm rõ đơn vị tiền công — 23/10/2026

Owner chỉ ra nhãn cũ vẫn còn. `PAY_UNITS` đổi nhãn `task` thành “Công việc”; shared formatter dùng “900.000đ / công việc”. Không sửa key, số tiền, phạm vi giá hoặc đơn vị lưu trong jobs/offers. Shared detail template giải thích mức cho toàn bộ phạm vi mô tả; shared-profile offer trong hub gọi cùng note. Form Kho/Tủ có hướng dẫn được select liên kết bằng `aria-describedby`. Nhãn mới tự áp dụng cho bộ lọc, thẻ tin và gợi ý dùng formatter.

Backup ignored `backups/work_price_labels_20261023/tacare_local.dump`, quyền 700/600 và pg_restore list PASS. Python/XML parse PASS; update addon exit 0 và restart local. `/tmp/tacare-work-price-check.py` Odoo shell PASS formatter trên job/offer bản ghi không lưu, giá khoảng/cả nhóm/mỗi người/giờ/chưa khai, template note có cho task và không có cho hour; transaction rollback. Chọn đọc tin task demo 900.000đ để kiểm tra HTTP, không đổi tin.

Chrome `/tmp/tacare-work-price-browser-check.cjs` PASS: bộ lọc task/thẻ, chi tiết Kho và hub hiển thị nhãn + giải thích, form Kho/Tủ option mới + hướng dẫn + default hour giữ nguyên, native login/SSO, 3 home marker; 320/375/1440 không tràn và không lỗi JS. Không submit form. Ảnh `docs/screenshots/work-price-20261023/`, đã xem chi tiết Kho desktop đúng 900.000đ / công việc. Một tài khoản QA hư cấu được tạo rồi xoá; tệp private credentials đã xoá. Security scan 283 tệp và git diff whitespace PASS. Không commit/push/deploy production.


### Tủ Hồ Sơ: trang tổng quan và thư viện riêng — 23/10/2026

Theo yêu cầu chủ dự án về cấu trúc khác và bỏ banner ảnh trong Hồ sơ của tôi, homepage Tủ hiện là nội dung tổng quan chung; root không tự gọi private library sau đăng nhập nữa. `/tuhoso/profiles` giữ sidebar, ngăn hồ sơ ngang, tìm kiếm, phạm vi mine/all và thao tác; đã bỏ carousel workspace. Gallery minh họa chỉ nằm trên homepage, mặc định dừng. Không sửa domain/ACL/consent/profile ownership. `sites/tuhoso/views/service_design.xml`, CSS riêng `static/src/tuhoso/scss/portfolio.scss` và nhánh index trong `controllers/main.py` là phần triển khai; Kho và hub giữ cấu trúc/màu.

[Quyết định, tham chiếu và kiểm chứng bản cuối](research/tuhoso_portfolio_refresh_2026-10-23.md): backup `backups/tuhoso_portfolio_20261023/tacare_local.dump` đã kiểm tra, addon upgrade exit 0 + restart local. Python/XML/asset checks, Chrome guest/owner/admin, native login/SSO, trang chủ tổng quan sau login, scope/ownership và profile_id, search/empty, gallery keyboard/reduced motion/focus/images, 320–1920 responsive và ba homepage marker PASS. Đã xem ảnh homepage tổng quan và thư viện không banner trong `docs/screenshots/tuhoso-overview-20261023/`. Security scanner 285 tệp + diff whitespace PASS. Dọn đúng 2 account/2 profile/3 offer QA hư cấu, không consent grants, tệp credentials private đã xóa. Không đổi schema hoặc dữ liệu hồ sơ gốc; không commit/push/deploy.


### Nhóm nghề Tủ Hồ Sơ chung một hàng — 23/10/2026

Sửa flex wrap làm Nông nghiệp đứng lẻ trên home Tủ: CSS riêng dùng 9 cột đều trên desktop và một hàng cuộn ngang dưới 1100px; các ô bằng chiều cao. Kho/TA.CARE không đổi. `navigation.js` giữ ô đang focus hiện đủ trong scroller Tủ; chừa đệm để viền focus không bị cắt. Không đổi template/database. Restart Odoo local. Chrome `/tmp/tuhoso-category-row-check.cjs` PASS tại 320/375/768/1100/1110/1280/1440/1600/1920: 9 ô cùng hàng, rộng/cao bằng nhau, desktop vừa đủ cả 9, màn hình nhỏ cuộn/Tab đến Nông nghiệp hiện đủ, không tràn trang hoặc lỗi JS; hai marker home còn lại giữ nguyên. Ảnh `docs/screenshots/tuhoso-category-row-20261023/`, đã xem hàng desktop. Node syntax, security scan 285 tệp và git diff whitespace PASS. Không dữ liệu QA, commit/push/deploy.

### Phân biệt màu Kho/Tủ — 23/10/2026

Theo nhận xét hai sản phẩm dùng cùng xanh lá dễ nhầm, chỉ block Tủ trong `service_palette.scss` đổi sang navy `#24385a`, nền blue-gray `#f5f7fc`, soft surfaces xanh nhạt. Đã đối chiếu phần source còn lại của palette không đổi: Kho forest `#0b2e24`, hub petrol `#116879`. Chỉ CSS token + restart local, không update database/fixtures. Chrome `/tmp/tacare-distinct-palettes-check.cjs` PASS ba homepage, palette thực render, nền tab active, các cặp chữ/body/soft/footer/nút/hover >=4.5:1 và viền control/trắng >=3:1, bố cục 320/375/768/1440 không tràn, 9 nhóm nghề Tủ vẫn chung hàng desktop, các marker đúng và không lỗi JS. Tủ chữ chính/nền 13.07:1, chữ trắng/nút 11.74:1. Ảnh `docs/screenshots/distinct-palettes-20261023/`, đã xem homepage Tủ desktop. Security scan 285 text files và diff whitespace PASS. Không đổi bố cục/quyền/dữ liệu hoặc tạo QA; không commit/push/deploy.


### Chuẩn bị commit nhánh seasonal-platform-ui — 23/10/2026

Theo yêu cầu chủ dự án, tạo nhánh local `update/seasonal-platform-ui` từ `main` để commit đợt chuyển phạm vi thời vụ và giao diện. Không push hoặc merge bởi agent; người vận hành làm theo `docs/git_release_workflow.md`. Workflow deploy đối chiếu trong repository: push main/manual dispatch, mặc định code-only; không có data trailer hoặc bundle mới trong lần commit này. Không tự xoá dữ liệu tuyển dụng production.

Kiểm tra trước stage: Python AST 80 file, XML parse 39 file và Node syntax 20 file PASS; scanner source 286 text files PASS, git whitespace PASS. `dev_seasonal_scope_check.py` Odoo shell rollback PASS: chặn tạo/đổi sang tuyển dụng kể cả context default, vai trò cá nhân ba site, owner isolation, portal write denial và membership capability/suspension. Cập nhật selector logout của các kiểm tra theo vị trí header hiện tại và màu hub petrol.

Đã chạy lại `seasonal_browser_check.cjs` PASS các homepage/responsive, đăng nhu cầu cá nhân/doanh nghiệp, giữ input khi lỗi, lời mời C2C, người gửi không tự nhận, receiver accept, quyền liên hệ đúng bên thuê được cấp/thu hồi, outsider và route tuyển dụng bị từ chối, admin chỉnh metadata và tạo hồ sơ chỉ thời vụ. `service_design_browser_check.cjs` PASS taxonomy, gallery keyboard/paused/reduced-motion, bộ lọc/ảnh chi tiết, thư viện owner/admin, tạo hồ sơ có tên gợi ý và responsive 320/375/768/1440, không lỗi JS/asset. QA hư cấu chỉ local, credentials không stage; cleanup theo script sau kiểm tra. Không đọc hoặc kiểm tra server production trong đợt chuẩn bị commit.

`cleanup_seasonal_qa.py` hoàn tất exit 0: xóa đúng dữ liệu và tài khoản QA của đợt kiểm tra, giữ nguyên 15 việc, 3 hồ sơ, 12 dịch vụ mẫu gốc và audit. Tệp credentials QA trong runtime đã được xóa.
