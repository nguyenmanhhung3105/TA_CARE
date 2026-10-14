# Three-site prototype: design, flows and integration

## Design direction

The three supplied PNGs are copied unchanged to `prototype/assets/` and shown with their original proportions. Kho Việc Làm's logo has green document drawers, a yellow person/star and a rising green arrow. Options considered: literal storage-room graphics, a category shelf, or a dense job board. The implemented category shelf shapes the hero; filter rail, card fields and tables continue the ordered catalogue idea without warehouse imagery. Tủ Hồ Sơ's green/yellow looping mark, leaf and star suggest both continuity and personal growth. Options considered: timeline, nested folder tabs, or a portfolio cover. The implemented layered folio introduces four profile chapters; the work screens use sections and evidence entries. TA.CARE's blue/green figures and connecting arc suggest two parties meeting. Options considered: a bridge, path or network. The implemented two-node bridge introduces a score panel that always explains matches and gaps.

Shared UI: 16px body, system sans; 4/8px spacing rhythm; 1240px max container; white card surfaces; labeled controls; 44px minimum buttons; inline errors and visible 3px focus ring. Tủ Hồ Sơ uses a Georgia display heading only on its homepage. Site tokens are `--accent`, `--accent-dark`, `--soft`, `--warm`, `--ink`; Kho uses deep green/gold, Tủ uses forest green/leaf gold, TA.CARE uses blue/green. The palette follows the supplied logo colors while keeping body text dark enough on pale surfaces. Lists become single column on narrow screens; tables scroll inside their own panel. Animations are minimal and removed with `prefers-reduced-motion`.

## Screens and main routes

| Site | Screens | Source of demo objects |
| --- | --- | --- |
| Kho Việc Làm `/khovieclam` | Home, `/opportunities` filters/empty state, `/opportunity/:id`, `/dashboard` with status filter, `/job/new`, `/job/:id/edit`, `/candidates`, `/requests` | `jobs`, `orgs`, visible profile projection, incoming requests |
| Tủ Hồ Sơ `/tuhoso` | Home, `/register`, `/dashboard`, `/profile`, `/profile/edit`, `/skills`, `/evidence`, `/sharing`, `/opportunities`, `/apply/:jobId`, `/requests` | `profiles`, skill/evidence, sharing choices, sent requests/invitations |
| TA.CARE `/tacare` | Home, `/dashboard`, `/matching`, `/invite/:jobId/:profileId`, `/connections`, `/connection/:id`, `/notifications` | Same job/profile IDs, score calculation, requests, feedback and notifications |

The demo toolbar selects an account; it is separate from product navigation. Candidate registration makes a local demo account without password or backend role assignment. New records use stable IDs within localStorage and survive refresh on the same origin. Reset restores versioned seed.

## State and action map

| Object | States | Authorized demo action |
| --- | --- | --- |
| Job | `draft → published → paused/closed`; `paused → published/closed`; `closed` terminal | Owner organization manages its job; another business cannot edit. Draft may be deleted. |
| Profile discovery | Visible/hidden; scope public/members/private | Owner candidate changes it. Hidden/private profiles leave search and new invitations, but prior request snapshots remain. |
| Evidence | Unverified → pending | Candidate may record/edit/remove evidence and request verification. Candidate cannot set verified; reviewer workflow is absent. |
| Application | Pending → accepted/declined by business; pending → cancelled by candidate sender | One job/profile/type pair can have one demo request; sending twice is blocked. |
| Invitation | Pending → accepted/declined by candidate; pending → cancelled by business sender | Business must own a published job and choose a discoverable profile. |
| Exchange result | Separate feedback rows | Either party to an accepted connection can add a result; acceptance alone is not hiring. |

Input validation and state checks run in `prototype/state.js`, including ownership, request direction, duplicate prevention and transitions. The UI hides or disables invalid actions as a convenience, but `state.js` also rejects them. This is not a server security boundary. Notifications are addressed by demo user ID and link to the same request ID. Contact email is shown only after acceptance and current candidate consent (plus per-application consent), and can be hidden again by revoking profile consent. Public opportunity/profile pages never show contact email.

## Matching formula

The displayed **Điểm phù hợp mô phỏng** is `65 × mandatory-skill coverage + 20 × preferred-skill coverage + 10 × compatible work mode + 5 × compatible location`, rounded to an integer. Empty skill criteria receive full points for that component; missing candidate mode/location receives no corresponding points and is called out as incomplete information. Required-skill gaps remain explicit even when a score is high. Changes to job requirements or candidate skills recompute the score from the shared data. The number is neither a hiring probability nor an AI model result.

## Odoo integration map (future scope)

| Prototype piece | Likely Odoo surface to design later | Open question |
| --- | --- | --- |
| Public pages and job/profile cards | Extend `tacare_website` QWeb routes/templates and `web.assets_frontend` | Website/domain routing and canonical URLs. |
| Workspaces/forms | Portal controllers/templates, CSRF forms, custom service/model layer | Final job/profile fields and ownership model. |
| Roles | Existing `tacare_account_access` plus `res.groups`, ACL and record rules | Migration from current selection role; self-signup policy. |
| Job and profile records | New custom addons/models, not Odoo core edits | Organization ownership versus `res.company`; attachment privacy. |
| Matching and requests | Service/model logic with record rules, notifications via Odoo mail where suitable | Production scoring policy, consent snapshots, retention. |
| Cross-domain login | Dedicated SSO/session design | Shared account is already partly represented; session continuity is unproven. |

Do not copy localStorage or demo role switching into production. Existing Odoo modules were left untouched. Production security, OCR, eKYC, SSO, payment and SPU integrations are outside this prototype.
