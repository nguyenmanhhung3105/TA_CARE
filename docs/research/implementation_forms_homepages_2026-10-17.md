# Triển khai local: biểu mẫu v2 và ba trang chủ độc lập

Ngày kiểm tra: 17/10/2026. Phạm vi: source custom addon và database **`tacare_local`**. Chưa push, deploy, đổi DNS/TLS hoặc tác động production. Tài liệu này mô tả trạng thái mới, thay cho phần thiết kế form và cấu trúc trang chủ trước đó trong các nhật ký lịch sử.

## Ba cấu trúc, ba cách sử dụng

| Website | Cấu trúc thực hiện | Tương tác và nội dung |
| --- | --- | --- |
| Kho Việc Làm | Trang khám phá thị trường nghề: tiêu đề bất đối xứng, dải ảnh ba nghề, tìm kiếm ngang, danh mục nghề hai vùng, tin thật, chuyên mục biên tập, dải hành trình, ghi chú nhà tuyển dụng, FAQ | Chọn lĩnh vực để xem các nhóm nghề; tìm kiếm; mở ghi chú nghề nghiệp. Ảnh công nghệ, logistics, y tế. |
| Tủ Hồ Sơ | Trang portfolio như một tập hồ sơ: bìa, ghi chú bên lề, ảnh trên giấy, tuyên ngôn, gallery dự án lệch nhịp, trang hồ sơ mẫu, sổ ghi chép, quyền chia sẻ, checklist, lời mời mở hồ sơ | Chuyển các trang ví dụ dự án/kinh nghiệm/kỹ năng; checklist chuẩn bị không lưu vào DB; mở ghi chú. Font Lora cho tiêu đề trang chủ, Be Vietnam Pro cho giao diện và biểu mẫu. |
| TA.CARE | Sân khấu kết nối: mở đầu toàn chiều rộng trên nền xanh, các thẻ chuyển động, tuyên ngôn lớn, ảnh cộng đồng, ba chương khi cuộn, sơ đồ kết nối, dải câu chuyện cuộn ngang, quyền riêng tư, FAQ, lời mời cuối trang | Tạm dừng/tiếp tục chuyển động; hình minh họa đổi theo chương trên desktop; đường kết nối vẽ theo cuộn; nút điều khiển dải câu chuyện. Mobile dùng cách đọc tuyến tính. |

Mỗi website có header, footer, thứ tự section và template riêng. Chỉ dùng chung nền tảng Odoo, font giao diện, kiểm tra quyền và các thành phần chức năng cần nhất quán. Marker `tc-jobs`, `tc-profiles`, `tc-hub` vẫn nằm trên `#wrap`.

Nội dung biên tập, nhân vật Mai An, dự án và tình huống mẫu là hư cấu, được ghi nhãn trong giao diện. Không tạo chúng thành tài khoản, hồ sơ, nhà tuyển dụng hoặc tin tuyển dụng trong DB. Khu vực tin đang mở chỉ dùng `hr.job` công khai, còn hạn; có trạng thái trống khi chưa có tin.

## Nguồn cấu trúc và cách tìm trên Refero

Đã xem [Refero Styles](https://styles.refero.design/), [trang Design prompts](https://styles.refero.design/ai-agents/design-prompts) và các tham chiếu dưới đây. Lấy cách tổ chức nội dung và đặt hình, giữ màu thương hiệu TA.CARE thay vì sao chép bảng màu của mẫu.

- [teenage engineering](https://styles.refero.design/style/aecf9dda-5cba-4dc7-9e73-59b65d895cdf): cách trưng bày theo catalogue và tổ chức nhãn gọn.
- [Structured](https://styles.refero.design/style/6c0b77d3-71f9-469d-98aa-4ce1d6d76ac8): bố cục gallery, chữ lớn và nhịp trang biên tập.
- [Slush](https://styles.refero.design/style/8b6b547f-a357-4f1b-9842-4579c62dd42b): collage, vật thể nổi và chuyển nhịp giữa những mảng nội dung.
- [Apple gallery](https://styles.refero.design/style/a73148b9-449b-42cd-9f38-86ef694f500e): hình ảnh lớn và các chương giới thiệu.
- [Dala](https://styles.refero.design/style/e5f5f8cf-e68d-4ed1-bbf5-6b67569af648): không gian sân khấu và điểm kết nối thị giác.

Giao diện công khai đã kiểm tra có ô tìm kiếm và DESIGN.md; không thấy hộp chat thiết kế trực tiếp. Đã gửi ba mô tả sau vào ô tìm kiếm, cả bằng nhập và Enter. Các truy vấn dài không trả kết quả phù hợp, nên chọn và đọc các tham chiếu công khai trên danh mục:

1. `editorial marketplace careers discovery image mosaic`
2. `portfolio scrapbook gallery case studies asymmetric`
3. `immersive storytelling scroll animation community`

Brief áp dụng: “Thiết kế ba cấu trúc độc lập cho một marketplace việc làm, một portfolio năng lực và một nền tảng kết nối. Không dùng cùng hero hai cột và cùng chuỗi card. Chọn mẫu dựa vào bố cục, nhịp cuộn và tương tác; bỏ qua palette của mẫu, dùng màu thương hiệu hiện có. Nội dung tiếng Việt, nhiều hình, có bản mobile và reduced motion.”

## Thay nội dung ở đâu?

| Nội dung | File / section |
| --- | --- |
| Header ba trang chủ | `views/home_jobs.xml`, template `home_navigation` có ba nhánh riêng |
| Kho Việc Làm: tiêu đề, ghi chú, chuyên mục và FAQ | `views/home_jobs.xml`; `k-industries`, `k-openings`, `k-journal` |
| Tủ Hồ Sơ: bìa, gallery, nhân vật/hồ sơ mẫu, checklist | `views/home_profiles.xml`; `p-collection`, `p-proof`, `p-notes`, `p-sharing` |
| TA.CARE: tuyên ngôn, chương cuộn, tình huống, FAQ | `views/home_hub.xml`; `h-why`, `h-journey`, `h-people` |
| Hình ảnh | `static/src/img/`; giữ tên file hoặc sửa `src` trong template |
| Bố cục, chuyển động và responsive | `static/src/scss/homepages.scss`, `static/src/js/homepages.js` |
| Font và biểu mẫu chức năng | `static/src/scss/experience.scss`, `views/kvl_pages.xml`, `views/live.xml` |

Hình đầu trang tải ưu tiên, hình phía dưới dùng lazy loading và khai báo kích thước. Reveal không khóa đọc nội dung khi JavaScript tắt. Chuyển động được tắt theo `prefers-reduced-motion`; chuyển động lặp có nút tạm dừng, dừng khi trang bị ẩn hoặc sân khấu ra khỏi màn hình. Không dùng cuộn cưỡng ép.

## Form và schema đã nối

Áp dụng hướng của [nghiên cứu form v2](recruitment_profile_forms_v2_2026-10-17.md), giữ model hiện có và cơ chế duyệt bản sửa công khai.

- Danh mục `care.job.sector` có 10 lĩnh vực, `care.job.position` có 48 nhóm nghề. Có CNTT, thương mại điện tử, marketing, kinh doanh, y tế, logistics, thiết kế cùng các lĩnh vực đã tồn tại. Đây là danh mục nghề, không phải dữ liệu tuyển dụng mẫu.
- Form tuyển dụng gom theo 5 phần: vị trí; nội dung gồm mô tả/yêu cầu/quyền lợi; kỹ năng và kinh nghiệm; nơi làm/thời gian; thu nhập. Điều kiện bổ sung nằm trong phần mở rộng. Kỹ năng nhập chung, chọn kỹ năng bắt buộc bằng chip; có nhóm “chỉ cần một trong”. Các điều kiện cũ vẫn được giữ khi sửa.
- Tách loại cơ hội, thời lượng và hình thức làm việc. Có nhóm nghề và tỉnh/thành theo danh mục. Bản ghi cũ full-time/part-time được trình bày theo hai trục khi sửa.
- Hồ sơ có 9 nhóm: giới thiệu, mong muốn, kinh nghiệm, học vấn, ngoại ngữ, giấy phép, kỹ năng, minh chứng, quyền chia sẻ. Kinh nghiệm liên quan tự khai theo số tháng và đúng nhóm nghề. Đổi nhóm nghề cần xác nhận lại; chưa xác định khác với 0 tháng.
- Kinh nghiệm làm việc, học vấn chi tiết, ngoại ngữ và giấy phép được nhập thành mô tả gộp để giảm thao tác. Chưa có dòng cấu trúc riêng theo từng việc làm/bằng/giấy phép, không tự cộng kinh nghiệm từ lịch sử hay tự xác nhận hiệu lực giấy phép.
- Thu nhập phân biệt khoảng/từ/đến/thỏa thuận, cố định/tổng, tiền tệ, kỳ và gross/net. DEV bật danh mục VND; tin và hồ sơ mới ưu tiên VND khi đồng tiền này active. Không đổi tiền tệ kế toán của company, không đổi tiền tệ bản ghi cũ. Môi trường khác cần bật VND nếu muốn dùng mặc định này.
- Bỏ ràng buộc sai “hạn ứng tuyển phải sau ngày bắt đầu”. Chấp nhận đào tạo từ đầu không bị ép thêm kỹ năng bắt buộc. Sửa lỗi tải lại tiền tệ và giữ checkbox khi form có lỗi.
- Form chính, form kỹ năng và minh chứng giữ dữ liệu khi lỗi có thể sửa được. Chặn số âm/NaN/Infinity, nhóm nghề sai lĩnh vực, URL minh chứng ngoài http/https, sửa dữ liệu người khác.

## Đối chiếu đang thực hiện

Đối chiếu trực tiếp có giải thích, không lưu snapshot hay hiển thị phần trăm. Những nhóm có cấu trúc: nhóm nghề, kỹ năng, kinh nghiệm liên quan, khu vực, loại/thời lượng cơ hội, hình thức, lương khi đủ điều kiện so sánh. Di chuyển và ngày bắt đầu chỉ thêm khi có yêu cầu cụ thể. Hybrid không tự đồng nghĩa đáp ứng remote/office.

Thiếu kỹ năng hoặc dữ liệu chưa chia sẻ là **chưa đủ thông tin**. Kinh nghiệm chỉ dùng khi cùng nhóm nghề và ứng viên xác nhận số tháng. Lương tổng không so với lương cố định; khác tiền tệ/kỳ/gross-net giữ là chưa đủ thông tin. Tin chỉ ghi lương “từ” không bị kết luận thấp hơn mong muốn nếu chưa biết trần lương. Học vấn, ngoại ngữ, giấy phép và lịch dạng mô tả cần kiểm tra trực tiếp; không dùng trùng chuỗi làm bằng chứng đáp ứng.

Discovery/matching kiểm tra consent hiện hành theo mục đích, tổ chức và field scope. Quyền quản lý tin và xử lý ứng viên tách riêng, kể cả trang `/tacare/matching`. Email vẫn cần accepted connection và contact consent cho đúng tổ chức, field email. OCR, upload CV và matching snapshots chưa được tích hợp.

## Dữ liệu, sao lưu và kiểm tra

Trước sửa: 9 tài khoản gốc, 0 tin, 0 hồ sơ, 0 kết nối; vì vậy không có tin cũ để xoá thêm. Sao lưu DB và filestore trước cập nhật:

- `backups/tacare_local_before_form_v2_20261017.dump`
- `backups/tacare_local_filestore_before_form_v2_20261017.tar.gz`

Các bản sao lưu và dữ liệu QA nằm trong thư mục bị git bỏ qua. Chỉ dùng tài khoản, tổ chức và dữ liệu giả tạm khi kiểm tra. Nhật ký QA append-only được giữ dưới dạng tham chiếu bản ghi đã dọn; không xoá audit để che lịch sử.

Kiểm tra đã chạy:

- Parse Python/XML, `node --check`, `git diff --check`; biên dịch SCSS bằng libsass trong container Odoo.
- Cập nhật `tacare_account_access,tacare_website`, khởi động lại local.
- `dev_schema_check.py`: quyền tổ chức, hồ sơ, read-only portal và contact consent; rollback.
- `dev_kvl_form_check.py`: tương thích các ngành/điều kiện cũ; rollback.
- `dev_forms_v2_check.py`: unknown/0 tháng, đúng nghề, hybrid, OR kỹ năng, cơ sở lương, scope dữ liệu, số hữu hạn, hạn trước ngày bắt đầu; rollback.
- Chrome/Playwright: lưu nháp, giữ dữ liệu lỗi, đăng tin không ép kỹ năng bắt buộc, sửa công khai qua duyệt, xem trước/chi tiết, hồ sơ, thêm/sửa/xoá kỹ năng và minh chứng.
- Nhánh lỗi: sửa bản ghi tổ chức/ứng viên khác bị 403, URL javascript bị chặn, NaN không ghi dở, đổi nghề cần xác nhận lại kinh nghiệm, thu hồi matching consent chặn chi tiết ngay.
- Ba trang chủ ở 320/375/768/1440 px: HTTP 200, font và hình tải đủ, không tràn ngang, không lỗi CSS/JS trong lượt cuối. Đã thử chọn nghề, lật trang hồ sơ mẫu, checklist, chuyển chương, carousel điều khiển tay, pause/resume, reduced motion, anchor, tên nút, skip link và một h1 mỗi trang.

Các kết quả này là kiểm thử local, không phải đánh giá thẩm mỹ độc lập hay cam kết điểm xếp hạng bên ngoài. Chưa kiểm tra trình duyệt Safari/Firefox hoặc môi trường production.

Kết quả dọn cuối đã xác nhận bằng DB: xoá 5 tài khoản QA tạm, 1 tin QA, 2 hồ sơ QA; còn đúng 9 tài khoản gốc, 0 tin, 0 hồ sơ, 0 kết nối. Dấu kiểm trên `(id, login, password hash, active, role)` khớp trước/sau; file thông tin đăng nhập QA tạm đã xoá. Kiểm thử hai tổ hợp `manage-only` và `handle-only` đều qua; tin mới mặc định VND.

Ảnh chụp cuối: [Kho Việc Làm](../screenshots/20261017-home-khovieclam.png), [Tủ Hồ Sơ](../screenshots/20261017-home-tuhoso.png), [TA.CARE](../screenshots/20261017-home-tacare.png). [Nguồn ảnh và prompt](homepage_image_assets_2026-10-17.md).

Bộ kiểm tra browser đọc-only nằm ở `tests/homepages_browser_check.cjs`. Playwright chỉ dùng trong môi trường QA ngoài addon; không thêm dependency runtime. Ví dụ trên máy Mac đã có Chrome:

```bash
NODE_PATH=/private/tmp/tacare-ui-qa/node_modules TACARE_CHROME='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' node source/apps/tacare/addons/tacare_website/tests/homepages_browser_check.cjs
python3 source/apps/tacare/addons/tacare_website/tests/homepage_contract_smoke.py
```

Nếu cần lưu screenshot, đặt thêm `TACARE_SCREENSHOTS` trỏ vào thư mục QA. Lượt chạy trong phiên này cần quyền ngoài sandbox cho Docker, Chrome và HTTP local. Kết quả cuối: cả 12 tổ hợp website/kích thước và tương tác đều pass; ba marker deploy và ba trang login đều HTTP 200. Không sửa hoặc nới HTTP probe production.
