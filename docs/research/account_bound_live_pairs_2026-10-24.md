# Dữ liệu gắn tài khoản và cặp ghép nối trực tiếp — 24/10/2026

## Yêu cầu hiện hành

Chủ dự án không cho phép tạo thêm liên hệ/hồ sơ demo rời tài khoản, yêu cầu hồ sơ thông thường của các tài khoản sẵn có, giữ kích thước ba website và trình bày công việc–hồ sơ thành hai cột có ảnh. Tổng quan và phần đối chiếu phải lấy từ thuật toán đang chạy, không viết sẵn kết quả. Đây là yêu cầu thay thế các thẻ ví dụ và nhãn demo ở đợt trước; không tự triển khai lên production.

## Dữ liệu và liên hệ

- Backup local DB custom dump và filestore tại ignored `backups/live_pairs_20261024/`, đã kiểm tra pg_restore listing.
- Không tạo thêm `res.users`, `res.partner`, `tacare.profile` hoặc capability trong đợt này. Chỉnh nội dung **15 hồ sơ và 24 mục nhận làm hiện có**, giữ toàn bộ ID/chủ tài khoản, lịch, khu vực, giá, kỹ năng và quyết định chia sẻ.
- Bỏ tiền tố `[Demo matching]`, `[Mẫu thử]`, các câu mô tả kiểm thử/hư cấu và nhãn demo trên các màn hình hồ sơ/công việc. Dùng tên hiển thị hồ sơ thông thường, mô tả phạm vi và điều kiện tự khai; không thêm chứng chỉ, ảnh chân dung, dấu xác minh, sao hoặc kinh nghiệm được xác minh.
- Tên tổ chức hiển thị bỏ hậu tố Demo; login doanh nghiệp có `.demo` và các mật khẩu không thay đổi. Hai tài khoản cá nhân hiện có dùng `ungvien1@tuhoso.com`, `ungvien2@tuhoso.com`; `student.test@tuhoso.com` giữ nguyên. Không đổi login về đuôi cũ `@tacare.vn`. Helper kiểm tra quyền dựa ID/chủ thực tế và hỗ trợ các login lịch sử để đọc tương thích.
- **40 liên hệ thừa** được lưu trữ: 16 liên hệ của login cũ đã ngừng hoạt động và 24 liên hệ QA mồ côi. Không xóa tài khoản/liên hệ hoặc làm mất tham chiếu lịch sử. Không còn liên hệ cá nhân hoạt động thiếu tài khoản.
- Odoo vẫn cần các partner kỹ thuật của công ty/website. Tổ chức kinh doanh có liên hệ với tài khoản thông qua membership và/hoặc liên hệ con có tài khoản. Không áp constraint “mọi res.partner phải có user”, vì như vậy sẽ phá vòng đời tạo user và các tổ chức gốc của Odoo.
- Contacts mặc định lọc **Có tài khoản hoạt động** cho admin, thêm cột **Tài khoản đang liên kết**. Dữ liệu liên kết được tính từ user hoạt động và membership hiện hành; trường mới chỉ cho system admin đọc. Người quản trị vẫn có thể bỏ filter để tra cứu bản ghi kỹ thuật/lịch sử cần thiết. Module `contacts` đã được cài local và nay được khai báo dependency rõ ràng.
- Công cụ thủ công local `tools/account_bound_records.py` có preview và apply rõ ràng, chỉ xử lý phạm vi đã biết. Snapshot so sánh mật khẩu/login/status, ID owner/company/scope và consent ID/field/time giữ nguyên. Dùng `read(load=None)` khi so liên kết để thay đổi tên hiển thị không bị hiểu sai thành đổi quyền.
- Các bộ tạo dữ liệu cũ `company_demo.py`/`matching_demo.py` không còn được phép apply để tạo/khôi phục liên hệ/hồ sơ demo. Chỉ còn đọc tương thích các ID hiện có. Khoá nguồn kỹ thuật `flex_demo_key` giữ nội bộ cho lịch sử/idempotence, không dùng làm nhãn giao diện hoặc quyết định matching.

Quyền discovery/matching riêng từng doanh nghiệp của hồ sơ hiện có và thời hạn đã cấp vẫn giữ nguyên; không tự chuyển sang public, gia hạn hoặc cấp liên hệ. Ba hồ sơ gốc riêng tư vẫn riêng tư.

## Ghép nối và giao diện

- `_care_compare_flexible` giữ nguyên điều kiện loại và rank, bổ sung `need_value` và `offer_value` vào từng hàng kết quả từ **dữ liệu thực tại của job và capability được chọn**. Không sinh kết luận từ nội dung thiết kế, không thêm phần trăm, không dùng ảnh/nhãn làm tín hiệu.
- `_live_pair` chỉ xây thẻ từ kết quả eligible và đúng `capability_id` trả về. Chi tiết cùng dùng đúng mục nhận làm đó để không so giá/lịch của một dịch vụ với kết quả của dịch vụ khác trong cùng hồ sơ.
- Trang chủ TA.CARE và `/tacare/matching` hiện hai phía: việc/đơn vị cần người và hồ sơ/người nhận cùng nghề, ảnh minh họa có nguồn, lịch, khu vực, mức tiền riêng. Mỗi cặp gắn `data-job-id`, `data-profile-id`, `data-capability-id` để kiểm chứng, không đưa chúng thành nội dung kỹ thuật trong sản phẩm.
- Click **Đối chiếu hai phía** đến `/tacare/pair/<job>/<profile>`. Trang này tính lại kết quả, có bảng so sánh từng tiêu chí và hai giá trị nguồn, lý do met/unknown/unmet do thuật toán trả; sau đó mới có form lời mời/đề nghị. Các trường hợp unknown vẫn cần làm rõ, không tự coi là đạt hoặc thiếu năng lực.
- Trang chủ duyệt các nhu cầu thuộc quyền và tất cả hồ sơ của người đang đăng nhập, không chỉ lấy hồ sơ đầu tiên vốn có thể riêng tư. Phía nhận mặc định chọn đọc một hồ sơ thực sự có gợi ý nếu chưa chọn ID; mọi ghi form vẫn cần `profile_id` cụ thể đã kiểm owner.
- Admin chỉ thấy phạm vi company được phép và hồ sơ có consent hiện hành; doanh nghiệp chỉ thấy cặp cho nhu cầu/tổ chức có quyền; cá nhân thấy cặp với hồ sơ của mình. Chi tiết kiểm job còn mở/còn chỗ, company, owner/membership, discovery/matching theo đúng tổ chức, skills và trạng thái account. Thu hồi consent hoặc thay giá làm cặp không còn eligible thì URL cũ không tiếp tục tiết lộ kết quả.
- Không đưa tên người dùng, liên hệ hoặc hồ sơ riêng lên trang chủ khách. Khách thấy ảnh giới thiệu và lời mời đăng nhập, không có các cặp giả. Tin mở Kho vẫn xem công khai; quyền email vẫn cần accepted + contact consent đúng bên thuê như trước.
- Bỏ các cặp minh họa và ba kết quả dựng sẵn khỏi trang chủ; route tương thích `/tacare/examples` chuyển về matching. Giữ model/XML IDs và các tài liệu lịch sử, không phục hồi ví dụ viết tay thành kết quả hiện hành.

Ảnh dùng các file đã ghi nguồn ở `static/src/img/services/`, icon từ Phosphor MIT hiện có. Ảnh minh họa lĩnh vực, không phải danh tính hoặc minh chứng của người nhận làm. Không thêm carousel TA.CARE, không đổi Kho/Tủ homepage/palette/logo.

## Kích thước và cấu trúc source

CSS mới chỉ trong `.tc-live.tc-hub` với namespace `lp-*`. Không sửa width/padding/font token của shell/header ba website, không khôi phục max-width 1280px. Ghi nhận trước/sau **18 phép đo**: ba website × 320/375/768/1100/1440/1920. `#tc-main`, shell, gutter và overflow khớp. Tại desktop 1440: main 1440, shell 1344, x=48; tablet gutter 24, mobile gutter 20. Bảng đối chiếu override min-width 620px của table legacy **chỉ tại component mới**, không thay rule chung.

Code chính:

- `models/exchange/profile_comparison.py`: kết quả và hai dữ liệu nguồn.
- `sites/tacare/examples.py`: thu thập cặp được phép từ thuật toán; hook ví dụ cũ trả rỗng.
- `sites/tacare/live_pairs.py`: lookup và xác thực trang cặp cụ thể, context danh sách.
- `sites/tacare/views/live_pairs.xml`, `static/src/scss/live_pairs.scss`: thẻ tổng quan, bảng so sánh và responsive.
- `models/foundation/identity.py`, `views/shared/company_contacts.xml`: cột/filter tài khoản liên kết.

## Kiểm chứng

Website addon `19.0.16.0.0`; nâng addon và restart local. Python/XML parse, JS syntax, security scanner và diff whitespace.

- `dev_live_pairs_check.py`: rollback, xác nhận owner hoạt động, không còn người dùng mồ côi trong danh sách, normalize lặp lại không đổi nội dung/version, hai giá trị nguồn đúng formatter, đúng capability thắng, mọi hồ sơ owner được xét, cách ly tổ chức và quyền chia sẻ. So sánh **225 cặp** trên cùng dữ liệu với hàm thuật toán từ HEAD trước sửa: eligible/rank/matched/missing và lý do giữ nguyên. Tăng mức nhận vượt ngân sách và thu hồi consent làm cặp bị loại, URL không tiếp tục trả dữ liệu.
- `live_pairs_browser_check.cjs`: dùng các tài khoản hiện có, không tạo user/contact/profile/connection. Kiểm thẻ và bảng so với kết quả ORM thực, ảnh tải được khi vào viewport, form trỏ đúng job/profile, desktop hai cột, nhiều kích thước, guest và doanh nghiệp khác không đọc cặp riêng. Ảnh xem lại trong ignored `runtime/live-pair-review/`.
- Browser admin dùng tài khoản hiện có chỉ được công ty TAA nên kiểm trạng thái rỗng đúng phạm vi, không thêm quyền để lấp kết quả. Admin có quyền Kho/Tủ được kiểm với helper/trang chi tiết trong rollback ORM và trả cặp thực được chia sẻ. Không đặt lại mật khẩu admin để phục vụ kiểm thử.
- Đo trước/sau bằng Chrome; ghi tại ignored `runtime/widths-before-live-pairs.json`, `runtime/widths-after-live-pairs.json`; giữ nguyên cả 18 trường hợp.
- Kiểm dữ liệu cuối: 15 tin, 15 hồ sơ/24 mục nhận làm; không có owner ngừng hoạt động, nội dung demo trong hồ sơ hoặc liên hệ cá nhân hoạt động không có account; không sinh work completion/rating giả.

Không chạy lại bộ UI lịch sử đòi ba ví dụ dựng sẵn như tiêu chí chấp nhận: yêu cầu đó đã bị thay thế. Không thay thuật toán hiện tại thành AI/ML hoặc hứa đảm bảo chất lượng; cùng ngành rộng vẫn có thể cần xác nhận phạm vi thực tế. Không tạo release bundle, commit/push hay deploy server. Snapshot full-restore trước đợt này không bao gồm thay đổi mới.

## Điều chỉnh phần đầu trang theo yêu cầu tiếp theo

Chủ dự án yêu cầu phần hero giữ giao diện cũ. Khôi phục `hx-connection-scene` nguyên bản với hai thẻ minh họa và caption rõ ràng, cho cả khách và tài khoản đăng nhập. Toàn bộ cặp matching thật chuyển xuống `#home-suggestions`, bao gồm cặp đầu tiên; không bỏ cặp đầu vì trước đây nó từng nằm trong hero. Bảng đối chiếu, dữ liệu và thuật toán giữ nguyên. Không sửa kích thước hoặc CSS chung. Đây là ngoại lệ trình bày được chủ dự án yêu cầu, không biến minh họa trong hero thành kết quả thuật toán.

## Thu gọn matching và đồng nhất hai thanh đầu trang

Theo yêu cầu tiếp theo trong ngày 24/10, danh sách matching ở trang chủ và trang tìm người/việc dùng hai cặp mỗi hàng từ 1024px, một cặp dưới ngưỡng đó. Giảm ảnh tổng quan xuống 120px, khoảng cách và cỡ tiêu đề; giới hạn số dòng ở tiêu đề/lịch dài và giữ nút mở đối chiếu. Trang chi tiết vẫn có mô tả và bảng dữ liệu đầy đủ. Hero cũ giữ nguyên.

Nguyên nhân hai thanh trên cùng thay đổi khi chuyển website là CSS khác nhau: Kho/Tủ dùng chữ thông báo 9px, TA.CARE dùng 12px; khung bên trong thanh thông báo cũng khác bề ngang. File cuối `static/src/scss/shared_topbar.scss` thống nhất chữ thông báo 12px, switcher desktop 13px, line-height, chiều cao, độ rộng tab và căn theo gutter 48/24/20px hiện có. Giữ màu của từng website và kích thước phần nội dung.

Đã backup DB local, nâng `tacare_website` và restart Odoo. Chrome kiểm tra ba website tại 320/375/640/768/1024/1440/1920px: hình học, font và padding của hai thanh khớp hoàn toàn, có đúng một tab đang chọn, không tràn ngang. Ở 1440px thanh thông báo cao 33px, switcher cao 45px (gồm đường viền); cả hai cùng căn nội dung x=48px, rộng 1344px. Kiểm matching với tài khoản hiện có tại 320/375/768/1024/1280/1440/1920px xác nhận đúng số cột, ảnh tải được, liên kết mở bảng đối chiếu thật và mô tả chi tiết còn hiển thị. Không tạo bản ghi. Kết quả đo và ảnh trong ignored `runtime/top-chrome-after.json`, `runtime/compact-topbar-review/`; security scanner và `git diff --check` đạt. Không commit/push/deploy.
