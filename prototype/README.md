# TA.CARE three-site local prototype

Run from repo root:

```sh
python3 prototype/serve.py
```

Open [http://127.0.0.1:4173/](http://127.0.0.1:4173/) or directly `/khovieclam`, `/tuhoso`, `/tacare`. The server binds only `127.0.0.1`. No npm install or Odoo database is needed. If port 4173 is occupied, stop the other local process before starting this server.

Use **Xem với tài khoản** at the top to switch between Đức Mạnh, Sen Digital, Nam Hà Logistics and other sample accounts. Use **Khôi phục dữ liệu mẫu** to clear all local changes for this version. Data is stored only in this browser's localStorage on this origin. Use fictional data; do not upload a real CV or enter real contact details.

Suggested demo:

1. Choose **Sen Digital** → Kho Việc Làm → **Bảng tin doanh nghiệp** → **Tạo tin mới**. Try **Đăng tin** with blank fields to see inline errors, then fill the form, **Xem trước**, and **Đăng tin**.
2. Switch to **Nam Hà Logistics** and open the new job edit URL; the prototype blocks edits to Sen Digital's job.
3. Switch to **Đức Mạnh** → Tủ Hồ Sơ. Edit skills and sharing; browse an opportunity and **Gửi đề nghị ứng tuyển**.
4. Switch to **Sen Digital** → TA.CARE → **Kết nối**. Open the same request ID and **Đồng ý trao đổi**. Add a separate exchange result; switch back to Đức Mạnh to see status and notification.
5. As Sen Digital, open **Phù hợp**, select a published job and **Mời trao đổi** with a candidate. Switch to that candidate to accept or decline. Hide the profile and observe its removal from future discovery.

Validation actually run: `node --check prototype/{data,state,app}.js`, `node --test prototype/tests/state.test.js`, and Playwright browser smoke using local Chrome at `prototype/tests/browser_smoke.py` (requires an installed Playwright Python package and Chrome). Browser smoke checks three logos, desktop/mobile widths, field errors, job publication, ownership block, skill edits, application, invitation, response, feedback, profile hiding, empty filters, matching, notifications and refresh. Screenshots are in `docs/screenshots/`.

This is an independent frontend and state simulation. It does not change Odoo core, addons, database, production services or domain sessions. See `docs/source_audit.md`, `docs/prototype.md`, and `docs/prototype_assumptions.md` for source evidence, design and integration notes.
