# Đối chiếu ERD, Database và Odoo DEV

> **Hiện hành 20/10/2026:** theo yêu cầu mới, `tacare.profile.user_id` là quan hệ nhiều hồ sơ/một user; đã gỡ constraint `tacare_profile_unique_user` bằng migration 19.0.6.0.0 và thêm `profile_title`. Giữ model, ID hồ sơ và mọi FK cũ. Kỹ năng, capability, minh chứng, consent và kết nối tiếp tục gắn đúng `profile_id`, không gộp theo user. Các đoạn “một hồ sơ/user” bên dưới là quyết định cũ, đã được thay bằng [triển khai này](research/implementation_profile_refresh_2026-10-20.md).

> **Bổ sung local 19/10/2026:** [demo việc linh hoạt](research/implementation_flexible_demo_2026-10-19.md) mở rộng `hr.job` bằng `care_opportunity_kind` và nhóm trường `flex_*`; dùng lại `care.profile.capability` cho nhiều việc nhận làm trên **một `tacare.profile`/user**. `flex_category_id`, `flex_rate_min/max` của capability là alias tới `category_id`, `rate_min/max` hiện có. Đã có form capability, ảnh tùy chọn và quyền owner/admin; các dòng “chưa có form” bên dưới là trạng thái lịch sử. Chưa dùng `care.availability`/`care.service.area` để tính lịch, bản đồ hay matching mới.


> **Form v2 hiện hành 17/10/2026:** thêm `care.job.position`, nhóm nghề/khu vực, nội dung yêu cầu/quyền lợi, cấu trúc thu nhập và các trường hồ sơ đối ứng trên model cũ. Xem [mapping và giới hạn triển khai](research/implementation_forms_homepages_2026-10-17.md). Không đổi tên model hay tạo kho hồ sơ song song.

> Cập nhật Kho việc làm 17/10/2026: `care.job.sector` và `care.job.requirement` bổ sung cho F01–F12. Số “33 model” bên dưới là phạm vi bản vẽ gốc, không phải tổng số model sau mở rộng. Xem [bảng đối chiếu Kho việc làm](kho_viec_lam_traceability.md).

Nguồn đọc toàn bộ: `Database.json` (draw.io 32.4.5, trang 00–06, mục tiêu v0.3 ngày 08/10/2026), `ERD.json` (draw.io 32.5.1, trang 00–06), `TA_CARE_Prompt_Codex_UI_3_Websites.md`, mã Odoo 19 Community và custom addons. `cells` kiểu `node` mang tên model, cột, ghi chú; `edge` là quan hệ/cardinality; vị trí, màu, HTML, kích thước và mũi tên chỉ là trình bày, không phải schema. `FK` trong nhãn là `Many2one`; `M:N` chỉ dùng Many2many khi bảng liên kết không có thuộc tính riêng. ERD giúp xác định chiều quan hệ; Database giúp xác định cột và kiểu. Các lựa chọn enum trong bản vẽ chưa phải danh mục nghiệp vụ được phê duyệt.

**Xung đột cần quyết định trước production:** bản vẽ đặt `care.profile`, `care.profile.skill`, `care.evidence`, `care.connection`; code đang chạy đã có `tacare.profile`, `tacare.profile.skill`, `tacare.profile.evidence`, `tacare.connection`. DEV mở rộng các model hiện có để giữ dữ liệu và XML ID, không tạo kho dữ liệu song song. Nếu cần đúng tên kỹ thuật theo sơ đồ, phải có kế hoạch migration riêng. Bản vẽ gợi ý nhiều hồ sơ theo `company+partner+profile_type` với một bản active; code hiện có ràng buộc **một hồ sơ trên user**. DEV giữ ràng buộc cũ. `res.company` là đơn vị vận hành Odoo, không phải mỗi doanh nghiệp tuyển dụng; `res.partner` và `care.org.member` biểu diễn tổ chức và thành viên. `parent_id` của partner không tự cấp quyền tổ chức.

| Thực thể thiết kế | Model Odoo / phần đã có trước | Bổ sung trên DEV / phần còn thiếu | Quan hệ và ràng buộc chính | Chưa rõ cần xác nhận |
| --- | --- | --- | --- | --- |
| `res.company` | Odoo chuẩn | `care_unit_kind` | `partner_id → res.partner`; phạm vi DB vận hành | Giá trị `other` sử dụng khi nào? |
| `res.partner` | Odoo chuẩn | `care_employer_state`, `care_company_intro` | Tổ chức `is_company`; `parent_id` không xác thực membership | Quy trình duyệt employer thực tế? |
| `res.users` | Odoo chuẩn; `tacare_account_role`, host login | `care_org_member_ids`, `care_organization_ids`, nhóm role đồng bộ | partner/company/groups chuẩn; portal không tự nâng role | Quy trình mời/gỡ thành viên? |
| `res.groups` | Odoo chuẩn | Hai nhóm business/candidate, imply portal | ACL và record rules theo nhóm | Phân nhóm recruiter/viewer chi tiết? |
| `website` | Odoo chuẩn; ba bản ghi local | `care_site_kind` | Cùng backend và DB; mỗi website có domain | Domain Tủ Hồ Sơ: Markdown và môi trường hiện dùng `.com`; logo dẫn `tuhoso.vn`. Cần xác nhận domain production. |
| `auth.oauth.provider` | Model chuẩn của addon `auth_oauth`, addon chưa cài | Không tạo lại; chưa bật OAuth | User/provider/uid do Odoo quản lý | Nhà cung cấp OAuth và luồng liên kết tài khoản? |
| `care.org.member` | Mới | company, organization, user, role, state | Unique `(company, organization, user)`; tổ chức `is_company`; viewer chỉ đọc | Tài khoản cũ đang dùng fallback commercial partner cho đến migration membership được duyệt. |
| `hr.job` | Odoo chuẩn; `tacare_*` owner/sector/type/mode/location/skills/status | `care_*` alias hoặc trường bổ sung: employer/state/deadline/location, experience, salary/currency, operators, revision, matching flag | Employer là `res.partner`, `company_id` là Odoo scope; ngày/lương hợp lệ; sửa tin published qua revision ở web | Cần phê duyệt enum sector/type/state, đơn vị lương và vòng đời phê duyệt đăng tin mới. |
| `hr.job.skill` | Chuẩn `hr_skills` | `care_mandatory`, `care_weight`; form tin đồng bộ dòng native | `job, skill, skill_level`; weight 0–100 | Cách chấm trọng số thực tế? |
| `care.job.revision` | Mới | version, JSON payload, submit/review/publish | Unique `(job,version)`; published bất biến; chỉ admin áp dụng allowlist | Nội dung nào cần review và SLA? |
| `hr.skill.type` | Chuẩn `hr_skills` | Dùng lại; tạo loại `TA.CARE` nếu kỹ năng nhập chưa có | Skill type → skills/levels 1:N | Ai duyệt từ mới do portal nhập? |
| `hr.skill` | Chuẩn `hr_skills` | `care_code`, `care_active`; skill form gắn vào catalog | Code unique nếu có; thuộc một type | Taxonomy chuẩn nào và quy tắc gộp tên? |
| `hr.skill.level` | Chuẩn `hr_skills` | Dùng lại, không tạo model | Level thuộc type; profile/job skill phải cùng type | Ánh xạ 4 mức UI sang `level_progress`? |
| `care.profile` | Map sang **`tacare.profile`** đã có user/name/skills/evidence/visibility | company/partner related, type, operators, degree, bio, status/version, verification/reputation, tọa độ | `user_id` unique cũ; version tăng khi sửa; hồ sơ private theo mặc định | Một user có nhiều profile/team hay không? |
| `care.profile.skill` | Map sang **`tacare.profile.skill`** đã có name/level/use | `skill_id`, level catalog, years, verified metadata | FK profile và hr.skill; cặp profile/name unique; năm không âm; verified chỉ admin | Chuẩn hóa duplicate theo `skill_id` hay tên? |
| `care.capability.category` | Mới | code/name/parent/risk/active | Code unique; không có vòng parent | Danh mục và cấp rủi ro chuẩn? |
| `care.profile.capability` | Model hiện có; đã có form demo local 19/10 | Dùng lại profile/category/title/description/rate/currency; thêm lịch, cách làm, địa điểm tĩnh, đơn vị/phạm vi giá, ảnh và trạng thái | Nhiều capability trên một profile; owner/admin; giá hữu hạn, không âm; portal không ghi trực tiếp | Matching và vận hành giao dịch để sau; xem báo cáo demo |
| `care.availability` | Mới, chưa có form | lịch tuần/ngày, giờ, múi giờ, active | Nhiều lịch/profile; khoảng giờ 0–24 | Chồng lấn lịch có bị cấm? |
| `care.service.area` | Mới, chưa có form | remote/city/radius, tọa độ, active | Nhiều vùng/profile; tọa độ/bán kính hợp lệ | Nguồn geocoding và địa giới? |
| `care.preference` | Mới, chưa có form | loại cơ hội, mức tối thiểu, khoảng cách, thời gian, excluded categories | M:N categories không metadata; số không âm | Một hay nhiều dòng theo loại cơ hội? |
| `care.document` | Mới; `ir.attachment` chuẩn | metadata private, profile/evidence/attachment, kind/state/retention | Attachment unique, `public=False`, ready cần file; chưa có upload UI | Chính sách loại file, dung lượng và lưu/xóa? |
| `ir.attachment` | Odoo chuẩn | Gắn tài liệu vào `care.document`, không tạo bảng mới | `res_model/res_id` là tham chiếu đa hình, không SQL FK | Thời hạn lưu file và quy trình xóa? |
| `care.evidence` | Map sang **`tacare.profile.evidence`** đã có title/role/description/result/URL | category, profile skill, issued by/date, verification, visibility, supersedes, documents | Profile/skill phải cùng chủ; verified cần verifier; mặc định private | Ai xác minh, chuẩn điểm và loại minh chứng? |
| `care.consent` | Mới; form chia sẻ đã nối discovery/matching/contact | purpose, recipient, field_scope, version, state/thời hạn/thu hồi | Contact chỉ cấp cho **một organization**; chỉ chủ profile grant; kiểm tra hiệu lực lúc đọc | Phiên bản văn bản đồng ý và thời hạn mặc định? |
| `care.ocr.job` | Mới, **chỉ metadata** | trạng thái, provider, extracted JSON, version, confirm | Tài liệu cùng profile; requester/confirm là chủ; chưa chạy OCR | Provider OCR, lưu nội dung và human review? |
| `care.match.config` | Mới, **chỉ schema** | version/algorithm/weights/rules/taxonomy snapshot | Version unique | Công thức và ngưỡng eligibility được phê duyệt? |
| `care.match.session` | Mới, **chỉ schema** | config/requester, job XOR profile, trạng thái, idempotency | Chỉ một đầu vào khởi tạo, idempotency unique | Batch/cadence và hạn dùng session? |
| `care.match.input` | Mới, **chỉ schema** | job XOR profile, consent, source version, hash/payload | Profile input phải có matching consent hiện hành | Hash, retention và snapshot field scope? |
| `care.match.result` | Mới, **chỉ schema** | hai input, scores/explanation/eligibility/disclosure | Cùng session; đúng loại job/profile; score 0–100 | Kho hiện chỉ nêu căn cứ và thiếu dữ liệu, không hiển thị điểm phần trăm; snapshot/công thức chưa được phê duyệt. |
| `care.connection` | Map sang **`tacare.connection`** đã có type/job/profile/sender/receiver/status/result | company/org/recipient/result/consent/timestamps aliases | Không trùng cặp job+profile ở pending/accepted; contact grant đúng org | Có cho phép gửi lại sau từ chối/hủy và thời hạn tự hết? |
| `care.feedback` | Mới, chưa có form | tác giả, result XOR connection, rating/reason | Rating 1–5 | Ai được đánh giá ai, công khai hay nội bộ? |
| `care.audit.event` | Mới, **chưa nối mọi thao tác** | action/actor/target/time/correlation; append only | `target_model,target_res_id` là tham chiếu đa hình, không FK | Retention và danh sách sự kiện bắt buộc? |
| `care.integration.event` | Mới, **chỉ metadata** | source/event unique, state/retry/correlation | Unique `(source,event_id)`; chưa có worker/outbox | Nguồn tích hợp, retry và idempotency contract? |

## Luồng đã nối với DB

- Form job tạo/sửa `hr.job`; kỹ năng form đồng bộ `hr.job.skill` và `hr.skill`. Sửa tin đang published tạo `care.job.revision` chờ admin; admin duyệt mới ghi vào job.
- Form hồ sơ, kỹ năng, minh chứng ghi `tacare.profile` và các child; kỹ năng cũng liên kết `hr.skill`. Minh chứng mới private theo mặc định; trang công khai lọc theo visibility và discovery consent.
- Form chia sẻ tạo/thu hồi `care.consent` discovery/matching. Matching UI hiển thị căn cứ đối chiếu tính trực tiếp, không có điểm phần trăm và không ghi `care.match.result` đã chốt. Chỉ hồ sơ có consent mới vào tìm kiếm/gợi ý.
- Ứng tuyển tạo `hr.applicant` và `tacare.connection` nhưng không ghi email ứng viên vào applicant trước consent. Phản hồi/lời mời, kết quả, thông báo lưu trong DB. Email chỉ hiện khi connection accepted và contact consent hiện hành cho đúng tổ chức; thu hồi chặn ngay.
- `care.document`, OCR, feedback, matching snapshots, audit/outbox mới ở mức schema và constraint; không gọi là đã tích hợp chức năng. Không có migration production hay tạo bảng PostgreSQL thủ công.

## Quyết định DEV và giới hạn

Các enum đang dùng là lựa chọn tạm của prototype, chưa được phê duyệt từ JSON. Dữ liệu text trong form kỹ năng có thể tạo mục `hr.skill` dưới type `TA.CARE`; cần quy trình duyệt taxonomy trước vận hành thật. ACL portal cho model riêng chỉ cho đọc những bản ghi của mình; mutation đi qua controller với xác thực role/owner/state. Admin Odoo giữ quyền native. Một số ràng buộc chống trùng đang ở ORM Python nên đồng thời ghi rất cao cần thiết kế index module và migration khi chốt nghiệp vụ. Các model schema chưa có menu/form admin riêng; có thể xem bằng ORM trên DEV.

## SSO — local implementation, 20/10/2026

The owner authorized synchronized sign-in/out across the role-permitted websites. `care.auth.session` stores a browser group linked to `res.users`, its role, expiry, revocation timestamp and private native-credential validity stamp. `care.auth.handoff` stores a short-lived, one-use browser-bound transition; it is unrelated to `care.match.session`. Native Odoo session cookies/files remain the actual website sessions. Portal users have no direct ACL on either model; server controllers scope and validate every transition. See [SSO implementation](research/implementation_sso_2026-10-20.md).
