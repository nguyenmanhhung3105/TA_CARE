# Sổ nguồn nghiên cứu tìm việc linh hoạt TA.CARE

Ngày đối chiếu: **19/10/2026**. Đi cùng [báo cáo phân tích](flexible_work_c2c_2026-10-19.md) và [ghi nhận phạm vi](../project_scope.md).

“Trực tiếp” nghĩa là công cụ đọc web trả được nội dung chính của ít nhất một trang của nền tảng, không có nghĩa đã đăng nhập hoặc thực hiện giao dịch. “Chỉ mục” nghĩa là tìm kiếm trả nội dung trang chính thức nhưng mở trực tiếp không đọc được đầy đủ. Không thay nguồn chính thức bằng bài tổng hợp bên thứ ba để khẳng định form/thuật toán.

## 1. Nền tảng: 12 đọc trực tiếp, 3 từ chỉ mục, 1 tham chiếu hạn chế

| Mã | Nền tảng / nguồn chính | Mức bằng chứng và giới hạn |
| --- | --- | --- |
| P01 | [Airtasker – How it works](https://www.airtasker.com/us/how-it-works/) | Trực tiếp. Luồng đăng việc/ngân sách/đề nghị. Bản US; chính sách từng nước có thể khác. |
| P02 | [Taskrabbit – How Do I Hire a Tasker?](https://support.taskrabbit.com/hc/en-us/articles/46260422073755-How-Do-I-Hire-a-Tasker) | Trực tiếp. Hướng dẫn đặt người làm; không công bố thuật toán xếp hạng. |
| P03 | [bTaskee – giúp việc nhà theo giờ](https://www.btaskee.com/vi-VN/giup-viec-nha-theo-gio/) | Trực tiếp. Trang dịch vụ; không dùng bảng giá tham khảo làm giá trả cho cá nhân TA.CARE. |
| P04 | [JupViec – theo giờ](https://jupviec.vn/theo-gio) | Chỉ mục chính thức có nội dung; lượt mở trực tiếp timeout. Không kiểm tra app. |
| P05 | [Việc Làm Tốt – giúp việc theo giờ Thủ Đức](https://www.vieclamtot.com/tags/giup-viec-nha-theo-gio-quan-thu-duc) | Trực tiếp. Không lưu danh tính/liên hệ người đăng; số tin thay đổi theo thời điểm. |
| P06 | [vLance – các mô hình thuê freelancer](https://www.vlance.vn/gioi-thieu-cac-mo-hinh-thue-freelancer-cho-khach-hang) | Trực tiếp. Không thao tác form hoặc gửi chào giá. |
| P07 | [Thumbtack – dog sitting](https://www.thumbtack.com/tx/san-antonio/dog-sitting) | Chỉ mục chính thức có trường lọc; mở trực tiếp cache miss. Không dùng làm nguồn giá. |
| P08 | [Care.com – tìm người chăm sóc](https://help.care.com/s/article/How-do-I-find-a-caregiver?language=en_US) | Chỉ mục chính thức có nội dung hướng dẫn; mở trực tiếp trả shell, không đủ nội dung bài. |
| P09 | [Wonolo – Workers](https://www.wonolo.com/workers) | Trực tiếp. Tài liệu thị trường khác; không xác nhận cơ chế lao động tại Việt Nam. |
| P10 | [Instawork – Worker](https://www.instawork.com/worker) | Trực tiếp. Đường `/workers` chuyển về `/worker`. |
| P11 | [Upwork – hourly và fixed-price](https://support.upwork.com/hc/en-us/articles/211063418-How-hourly-and-fixed-price-contracts-are-different-on-Upwork) | Trực tiếp. Chỉ dùng phân biệt cách giao việc/định giá. |
| P12 | [Fiverr – Portfolio](https://help.fiverr.com/hc/en-us/articles/4413134063633-Using-your-Fiverr-Portfolio) | Trực tiếp. Tham khảo nguồn gốc tác phẩm và quyền trưng bày. |
| P13 | [inDrive – City to City](https://blog.indrive.com/en-id/article/have-app-will-travel-indrive-city-to-city) | Trực tiếp. Bài theo thị trường Indonesia; không xác nhận hoạt động/quy định tại Việt Nam. |
| P14 | [BlaBlaCar – Terms and Conditions](https://legal.blablacar.com/en-gb/terms-and-conditions/) | Trực tiếp. Bản en-gb ghi hiệu lực 15/06/2026; phân biệt nhánh carpooling với dịch vụ khác. |
| P15 | [Chungxe – có lái](https://thuexe.chungxe.vn/co-lai) | Trực tiếp. Form đọc được nhưng có nội dung/placeholder cũ; không dùng cam kết marketing hoặc giá làm chuẩn. |
| P16 | [Mioto](https://www.mioto.vn/) | Hạn chế. Chỉ mục cho thấy định hướng sản phẩm; trang trực tiếp chỉ trả shell. Không dùng để chốt trường/giá/matching. |

Ba nguồn chỉ mục vẫn có giá trị gợi ý, nhưng không phải bằng chứng quyết định duy nhất: lịch/vùng và form đặc thù được kiểm tra chéo với Taskrabbit, Instawork, bTaskee và các nguồn đọc trực tiếp khác. Không gọi khảo sát này là toàn bộ thị trường.

## 2. Nguồn bổ sung về quyền, vùng phục vụ và minh chứng

| Mã | Nguồn | Cách sử dụng / giới hạn |
| --- | --- | --- |
| B01 | [Taskrabbit – vẽ vùng làm việc, bản tiếng Tây Ban Nha](https://support.taskrabbit.com/hc/es-es/articles/46260459320603-C%C3%B3mo-dibujar-el-mapa-de-tu-zona-de-trabajo) | Trực tiếp. Chứng minh có vùng khép kín; URL tiếng Anh thử mở bị lỗi. Không xác nhận nhà cung cấp bản đồ. |
| B02 | [Taskrabbit – rates/minimum hours](https://support.taskrabbit.com/hc/en-gb/articles/46260502667035-Tasker-Rates-Minimum-Hours-Policy) | Chỉ mục chính thức. Tham khảo có chính sách giờ tối thiểu; không áp mức tối thiểu của họ cho TA.CARE. |
| B03 | [Airtasker – không công khai thông tin liên hệ](https://support.airtasker.com/hc/en-us/articles/200989274-Why-can-t-I-post-my-phone-number-or-email) | Chỉ mục chính thức. Căn cứ tham khảo ranh giới công khai/riêng tư, không sao chép toàn bộ chính sách. |
| B04 | [Airtasker – private offers](https://support.airtasker.com/hc/en-au/articles/4410330122905-What-are-private-offers-and-how-do-they-work) | Chỉ mục chính thức. Phạm vi mô tả, giá, nơi làm và hạn; không tạo giao dịch thử. |
| B05 | [Fiverr – How Fiverr Works](https://help.fiverr.com/hc/en-us/articles/360010558038-How-Fiverr-Works) | Chỉ mục chính thức. Tham khảo gói dịch vụ; không lấy tỷ lệ phí làm đề xuất kinh doanh. |
| B06 | [Care.com – ứng tuyển theo loại dịch vụ](https://help.care.com/caregivers/s/article/how-caregivers-respond-to-and-manage-job-postings-on-care-com?language=en_US) | Chỉ mục chính thức. Tham khảo năng lực theo nhóm việc; TA.CARE không sao chép cách tách hồ sơ của họ. |

## 3. Bản đồ, kỹ thuật và chi phí

Các nguồn sau đọc trực tiếp, trừ nơi ghi khác. “Có API” không chứng minh độ chính xác, SLA thực tế, quyền lưu dữ liệu hoặc chất lượng tại mọi địa bàn của TA.CARE. Những lần thử URL Urban Company, Rover và tìm Rada không cung cấp đủ bằng chứng; không tính vào mẫu hoặc dùng để kết luận.

| Mã | Nguồn | Đối chiếu trong báo cáo |
| --- | --- | --- |
| M01 | [Google – Rapido và Mobility services](https://mapsplatform.google.com/resources/blog/how-rapido-is-building-customer-and-rider-trust-in-india-with-google-maps/) | Ví dụ có bằng chứng sử dụng Google; bài công bố năm 2024, không phải khảo sát tỷ lệ phổ biến năm 2026. |
| M02 | [Google – Routes overview](https://developers.google.com/maps/documentation/routes) | Phân biệt route đơn và ma trận. |
| M03 | [Google – Get a route matrix](https://developers.google.com/maps/documentation/routes/compute_route_matrix) | Giới hạn theo chế độ và lỗi từng cặp; không dùng Routes Preferred preview làm mặc định. |
| M04 | [Google – Routes usage and billing](https://developers.google.com/maps/documentation/routes/usage-and-billing) | Đơn vị tính phần tử và SKU theo tính năng. |
| M05 | [Google – giá core services](https://developers.google.com/maps/billing-and-pricing/pricing) | Bảng gốc cho ví dụ chi phí ở §5.7; phải kiểm tra lại lúc mua. |
| M06 | [Google – Geocoding policies](https://developers.google.com/maps/documentation/geocoding/policies) | Lưu trữ, attribution, hiển thị. |
| M07 | [Google – Routes policies](https://developers.google.com/maps/documentation/routes/policies) | Lưu trữ, attribution, hiển thị. |
| M08 | [Google – Service Specific Terms hiện hành](https://cloud.google.com/maps-platform/terms/maps-service-terms) | Bản ngoài EEA; các mục Geocoding/Routes. Không suy ngoại lệ lưu riêng từng người cho phép matching xuyên người dùng. |
| M09 | [Goong – Distance Matrix v2](https://help.goong.io/kb/rest-api-v2/distance-matrix-rest-api-v2/distance-matrix-v2/) | Nội dung chính thức từ chỉ mục; không gọi endpoint thật. |
| M10 | [Goong – tài liệu Matrix cũ](https://document.goong.io/tutorial-Distance-matrix.html) | Chỉ mục. Tên vehicle giữa phiên bản có khác; không lấy ví dụ cũ thay đặc tả v2. |
| M11 | [Goong – bảng giá](https://goong.io/bang-gia/) | Trực tiếp. Chưa chốt quy đổi/billing của cấu hình nhiều điểm; chưa có báo giá riêng. |
| M12 | [VIETMAP – Matrix v4](https://maps.vietmap.vn/docs/map-api/matrix-version/matrix-v4/) | Trực tiếp. Chỉ trả ma trận số, không tự là hình học tuyến. |
| M13 | [VIETMAP – tổng quan tiếng Việt](https://maps.vietmap.vn/docs/vi/map-api/overview/) | Nội dung chính thức từ chỉ mục: cách tính transaction. Chưa gọi API hoặc dùng demo key. |
| M14 | [VIETMAP – Route v4](https://maps.vietmap.vn/docs/map-api/route-version/route-v4/) | Chỉ mục. Nhắc kiểm tra đơn vị trường dữ liệu theo endpoint/phiên bản. |
| M15 | [PostGIS – ST_DWithin](https://postgis.net/docs/ST_DWithin.html) | Trực tiếp. Khả năng công nghệ, không phải trạng thái cài đặt dự án. |
| M16 | [OSMF – Nominatim Usage Policy](https://operations.osmfoundation.org/policies/nominatim/) | Trực tiếp. Giới hạn endpoint công cộng; không phải điều khoản của mọi dịch vụ dựa trên OSM. |

Không dùng bảng so sánh giá Google trên website nhà cung cấp khác để xác nhận giá Google. Không dùng tuyên bố độ chính xác/SLA marketing của bất kỳ bên nào làm kết quả benchmark.

## 4. Nguồn pháp lý chính thức và mức đã đọc

Phần này xác định căn cứ phải kiểm tra trước vận hành; **chưa phải ý kiến pháp lý hoàn chỉnh hoặc bảng xác nhận tuân thủ**. Không dựa riêng vào thời gian “crawled/published” trong chỉ mục để suy hiệu lực. Tên, số và ngày hiệu lực được đối chiếu với trang chính thức khi đọc được.

| Mã | Nguồn | Mức truy cập / giới hạn |
| --- | --- | --- |
| L01 | [Bộ luật Lao động 45/2019/QH14 – bản ký](https://datafiles.chinhphu.vn/cpp/files/vbpq/2019/12/45.signed.pdf) | PDF 83 trang không trả text ở lượt mở. Chỉ mục chính thức có Điều 13; không tuyên bố đã rà toàn bộ bản hợp nhất hiện hành. |
| L02 | [Luật Việc làm 74/2025/QH15 – toàn văn trên cổng Chính phủ](https://xaydungchinhsach.chinhphu.vn/toan-van-luat-viec-lam-119250711173403835.htm) | Đọc được nội dung trực tiếp; dùng xác định phạm vi cần xét, không chốt phân loại hoạt động của TA.CARE. |
| L03 | [Nghị định 352/2025/NĐ-CP về dịch vụ việc làm](https://congbao.chinhphu.vn/van-ban/nghi-dinh-so-352-2025-nd-cp-468351.htm) | Metadata chính thức/chỉ mục; hiệu lực 01/01/2026. Chưa thẩm định từng điều kiện. |
| L04 | [Luật Thương mại điện tử 122/2025/QH15](https://vanban.chinhphu.vn/?classid=1&docid=216503&pageid=27160&typegroupid=3) | Metadata đọc trực tiếp, hiệu lực 01/07/2026. PDF đính kèm bị công cụ từ chối do kích thước; chưa rà toàn văn/nghị định hướng dẫn. |
| L05 | [Luật Bảo vệ dữ liệu cá nhân 91/2025/QH15](https://congbao.chinhphu.vn/van-ban/luat-so-91-2025-qh15-45578.htm) | Metadata/chỉ mục chính thức, hiệu lực 01/01/2026; chưa rà toàn bộ điều khoản cho mô hình này. |
| L06 | [Nghị định 356/2025/NĐ-CP](https://vanban.chinhphu.vn/?classid=1&docid=216387&pageid=27160&typegroupid=4) và [bản ký](https://datafiles.chinhphu.vn/cpp/files/vbpq/2026/01/356-nd.signed.pdf) | Metadata/chỉ mục đọc được; PDF 71 trang không trả text. Không suy đã hoàn tất đánh giá dữ liệu/vị trí/API. |
| L07 | [Nghị định 158/2024/NĐ-CP về hoạt động vận tải đường bộ](https://chinhphu.vn/?classid=1&docid=212082&orggroupid=2&pageid=27160) | Metadata/chỉ mục. Không dùng riêng bản 2024 để kết luận quy định hiện hành. |
| L08 | [Nghị định sửa đổi 218/2026/NĐ-CP](https://vanban.chinhphu.vn/?classid=1&docid=218537&pageid=27160) và [bản ký](https://datafiles.chinhphu.vn/cpp/files/vbpq/2026/6/218-ndcp.signed.pdf) | Metadata trực tiếp: hiệu lực 10/08/2026. PDF 39 trang không trả text; cần thẩm định nội dung và các văn bản liên quan trước mở nhánh. |

Không khẳng định danh mục văn bản ở đây bao quát mọi sửa đổi/quy định địa phương/ngành nghề. Các điều kiện chưa đọc đủ được giữ là điểm chặn hoặc việc cần thẩm định, không đánh dấu “đã đạt” chỉ vì tìm thấy văn bản.

## 5. Tài liệu và source nội bộ đã đối chiếu

- [Hướng dẫn repository](../../AGENTS.md).
- [Backend local và lịch sử QA](../backend_local.md), [mapping](../database_mapping.md), [Kho F01–F12](../kho_viec_lam_traceability.md).
- [Nghiên cứu matching ngày 17/10](matching_fields_2026-10-17.md), [form v2](recruitment_profile_forms_v2_2026-10-17.md), [triển khai gần nhất](implementation_forms_homepages_2026-10-17.md).
- [Prototype](../prototype.md): bản minh họa cũ, không dùng công thức điểm mô phỏng làm engine mới.
- `tacare_account_access/models/res_users.py`: role/host.
- `tacare_website/models/hr_job.py`, `profile.py`, `profile_details.py`, `profile_comparison.py`, `matching.py`, `privacy.py`, `connection.py`, `identity.py` và `controllers/live.py`: chủ thể, dữ liệu, quyền, đối chiếu và giới hạn hiện tại.

Các đường dẫn model/controller ở trên tương đối với `source/apps/tacare/addons/`. Không kiểm tra lại database hoặc production trong phiên này. Báo cáo không nhận các QA ngày 17/10 là kết quả chạy mới ngày 19/10.
