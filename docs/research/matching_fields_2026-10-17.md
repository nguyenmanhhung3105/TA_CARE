# Nghiên cứu cấu trúc tuyển dụng và hồ sơ phục vụ matching TA.CARE

Ngày khảo sát: **17/10/2026**. Trạng thái: **đề xuất nghiệp vụ để thảo luận**, chưa phải đặc tả triển khai hoặc danh mục đã phê duyệt.

> **Điều chỉnh sau phản hồi về công sức nhập liệu:** xem [phương án form và hồ sơ v2](recruitment_profile_forms_v2_2026-10-17.md). V2 thay thế khuyến nghị về số mục nhập, cách nhập yêu cầu và phạm vi matching ban đầu trong bản này. Danh mục bảy lĩnh vực và các tình huống đối chiếu bên dưới tiếp tục là tài liệu tham khảo, không phải danh sách ô bắt người dùng điền.

## 1. Kết luận định hướng

Nên thiết kế Kho Việc Làm theo **phần chung + mẫu yêu cầu theo nghề/vị trí**, sau đó thiết kế Tủ Hồ Sơ để cung cấp dữ liệu đối ứng. Không gom tất cả yêu cầu của bảy lĩnh vực vào một biểu mẫu; không dùng một ô “ngành nghề”, một con số “kinh nghiệm” và một danh sách từ khóa để đại diện toàn bộ năng lực.

Cấu trúc đề xuất có sáu phần:

1. Nghề và chuyên môn thực hiện công việc.
2. Bối cảnh: sản phẩm, ngành hàng, khách hàng, lĩnh vực hoạt động.
3. Nhiệm vụ và đầu ra của vị trí.
4. Yêu cầu năng lực: nghiệp vụ, công cụ, kinh nghiệm liên quan, ngoại ngữ, học vấn và giấy phép khi cần.
5. Điều kiện hợp tác hai chiều: địa điểm, cách làm việc, lịch, thu nhập và ngày bắt đầu.
6. Minh chứng, nguồn khai báo, tình trạng kiểm chứng và quyền sử dụng dữ liệu.

Mọi yêu cầu phải có ý nghĩa đối chiếu được: **cần điều gì → hồ sơ trả lời bằng dữ liệu nào → so sánh thế nào → thiếu dữ liệu thì giải thích gì**. Trường chỉ để giới thiệu doanh nghiệp hoặc vận hành tin không tự trở thành tiêu chí matching.

## 2. Bối cảnh dự án và giới hạn nghiên cứu

Không có toàn bộ hội thoại session trước trong ngữ cảnh hiện tại. Bối cảnh triển khai được đọc từ [prototype.md](../prototype.md), [prototype_assumptions.md](../prototype_assumptions.md), [database_mapping.md](../database_mapping.md), [kho_viec_lam_traceability.md](../kho_viec_lam_traceability.md), [backend_local.md](../backend_local.md) và lịch sử commit gần nhất.

Những điều giữ làm ranh giới sản phẩm: phân biệt tổ chức với tài khoản; thiếu dữ liệu là chưa biết; chỉ matching khi có quyền và đồng ý đúng mục đích; email chỉ mở theo đồng ý riêng cho đúng tổ chức sau kết nối được chấp nhận; Kho không hiển thị điểm matching phần trăm. Các trường đang tồn tại không được dùng làm giới hạn cho đề xuất này.

Đây là khảo sát định tính có chủ đích trên **10 nền tảng**: danh mục nghề, bộ lọc, hướng dẫn nhà tuyển dụng, tin cụ thể và hướng dẫn hồ sơ. Không phải khảo sát thống kê đại diện thị trường. Không thể suy ra tần suất yêu cầu, mức lương chuẩn hoặc chất lượng thuật toán riêng của các nền tảng từ mẫu này.

Các tin đã hết hạn vẫn có ích để tìm cấu trúc dữ liệu. Ngày hiển thị, số ngày còn lại và bản được công cụ tìm kiếm lưu có thể lệch nhau; báo cáo không xác nhận tin còn tuyển. Không đăng nhập, ứng tuyển, lấy CV cá nhân hoặc sao chép dữ liệu ứng viên. Các ví dụ đối chiếu trong phần đề xuất là tình huống giả định.

## 3. Mười nền tảng và điều rút ra từ nguồn đọc được

| Nền tảng / nguồn chính | Đã quan sát | Hệ quả đề xuất cho TA.CARE | Giới hạn |
| --- | --- | --- | --- |
| 1. [TopCV – hướng dẫn đăng tin](https://tuyendung.topcv.vn/help/huong-dan-su-dung/dang-tin-tuyen-dung-mien-phi/) | Phân loại nhóm nghề → nghề → chuyên môn; có thông tin bổ sung theo chuyên môn, kỹ năng cần/nên có, lịch và cấu phần thu nhập cho sales. | Chọn vị trí trước; phần chuyên môn thay đổi theo lựa chọn; tách bắt buộc và ưu tiên. | Đọc tài liệu công khai, không thao tác form sau đăng nhập. |
| 2. [CareerViet – tin kinh doanh B2B](https://careerviet.vn/vi/tim-viec-lam/nhan-vien-kinh-doanh-b2b-ha-noi.35C8A7AE.html) | Kinh nghiệm bán B2B trong dịch vụ; trải nghiệm tuyển dụng là ưu tiên; có nhiệm vụ tìm khách, đề xuất giải pháp và đàm phán. | Tách loại khách hàng, nghiệp vụ bán hàng và lĩnh vực dịch vụ. | Một tin không đại diện tất cả việc sales. |
| 3. [CareerLink – danh mục nghề](https://www.careerlink.vn/tim-viec-lam-nhanh) | Phần mềm, phần cứng/mạng, y tế, vận chuyển/kho, xuất nhập khẩu, thu mua và thiết kế xuất hiện thành các nhóm riêng. | Không gộp mọi nghề cùng doanh nghiệp vào một ngành; kho, vận tải, thu mua cần phân nhánh. | Một số liên kết tin chi tiết không tải được. |
| 4. [JobsGO – danh sách vận hành sàn](https://jobsgo.vn/viec-lam-nhan-vien-van-hanh-san-thuong-mai-dien-tu.html) | Có bộ lọc kinh nghiệm/học vấn, cả lựa chọn không yêu cầu; tin phân biệt vận hành sàn, affiliate, tăng trưởng và kinh doanh dịch vụ sàn. | TMĐT gồm nhiều nghề; không mặc định mọi vị trí đều cần học vấn hoặc kinh nghiệm. | Không dùng số lượng tin làm số liệu thị trường. |
| 5. [Glints – Inbound Marketing Consultant](https://glints.com/sg/opportunities/jobs/inbound-marketing-consultant/99cb14e9-a45c-425d-8ccb-0124aefb48a6) | Phần yêu cầu, kỹ năng, quyền lợi, nhiệm vụ; mô tả phân biệt năng lực cần có và điểm cộng. | Kỹ năng dùng để làm nhiệm vụ nào cần rõ; quyền lợi là một phần độc lập. | Tin tại Singapore đã đóng; chỉ tham khảo cấu trúc. Danh mục và một số tin Việt Nam chỉ đọc được bản chỉ mục. |
| 6. [ITviec – tìm việc](https://itviec.com/it-jobs) | Chuyên môn, cấp độ, mô hình làm việc, job domain và lĩnh vực công ty là các chiều riêng. | Nghề, lĩnh vực doanh nghiệp và bối cảnh công việc phải tách. | Không suy ra cách nền tảng chấm matching. |
| 7. [TopDev – trang tìm kiếm](https://topdev.vn/jobs/search) | Tìm bằng vị trí/kỹ năng; có kinh nghiệm, loại công việc và phúc lợi. Các trang được đọc mang nhãn Saramin. | Chuẩn hóa kỹ năng và vị trí; giữ riêng thông tin thu hút ứng viên. | Ghi nhận nội dung tại URL khảo sát; không kết luận lịch sử chuyển đổi thương hiệu. |
| 8. [LinkedIn – bộ lọc việc làm](https://www.linkedin.com/help/linkedin/answer/a507441) | Địa điểm, doanh nghiệp, cấp độ kinh nghiệm và loại việc làm được lọc riêng. | Dùng dữ liệu cấu trúc cho tìm kiếm; ngày đăng và cách ứng tuyển không phải năng lực. | Tài liệu bộ lọc, không kiểm tra form nhà tuyển dụng. |
| 9. [Indeed – thư viện mô tả công việc](https://www.indeed.com/hire/how-to-write-a-job-description) | Có mẫu theo từng nghề, gồm thiết kế, y tế, kinh doanh và logistics. | Mẫu theo vị trí giúp hướng dẫn nhập liệu thay vì chỉ tăng số ô nhập. | Nguồn quốc tế; một số liên kết chuyển tới bản Ấn Độ, không dùng làm quy định nghề tại Việt Nam. |
| 10. [JobOKO – danh mục ngành nghề](https://vn.joboko.com/viec-lam-theo-nganh-nghe) | Có nhóm logistics/xuất nhập khẩu/mua hàng/kho và các nhánh nghề; tin trưởng nhóm kho phân biệt kinh nghiệm nghiệp vụ với kinh nghiệm dẫn nhóm. | Tách phạm vi quản lý khỏi trình độ chuyên môn; danh mục có thể mở rộng. | Danh mục nền tảng là tham khảo, không phải danh mục chính thức của TA.CARE. |

Đã thử thêm VietnamWorks và Việc Làm 24h nhưng các trang trực tiếp cần dùng trả lỗi truy cập/403; không tính hai trang này vào mười nguồn nghiên cứu chính và không dùng bản đăng lại để khẳng định cấu trúc form của họ.

## 4. Phân biệt các khái niệm trước khi đặt trường

| Khái niệm | Ý nghĩa | Ví dụ |
| --- | --- | --- |
| Lĩnh vực doanh nghiệp | Tổ chức kinh doanh hoặc cung cấp dịch vụ gì. Có thể nhiều lĩnh vực. | Bệnh viện; dịch vụ vận chuyển; bán lẻ. |
| Nhóm nghề | Nhánh điều hướng lớn theo công việc. | CNTT; marketing; y tế. |
| Nghề | Loại công việc tương đối ổn định, dùng danh mục chuẩn chung. | Phát triển phần mềm; điều dưỡng; quản lý kho. |
| Chuyên môn / vị trí chuẩn | Nhánh nghề cụ thể dùng để tìm và đối chiếu. | Backend Developer; điều dưỡng nhi; chuyên viên chứng từ hàng nhập. |
| Chức danh tin | Tên doanh nghiệp muốn hiển thị. Có thể chứa cấp bậc, bộ phận. | Chuyên viên Backend Python – nền tảng bán hàng. |
| Bối cảnh công việc | Sản phẩm, thị trường, khách hàng hoặc môi trường áp dụng nghề. | B2B; SaaS; thời trang; kho lạnh; phòng xét nghiệm. |
| Cấp độ chuyên môn | Mức tự chủ và độ phức tạp công việc. | Mới vào nghề; làm độc lập; chuyên sâu. |
| Phạm vi quản lý | Trách nhiệm với con người, ngân sách hoặc vận hành. | Không quản lý trực tiếp; dẫn nhóm; phụ trách bộ phận. |
| Chuyên ngành đào tạo | Nội dung đã học hoặc nhà tuyển dụng yêu cầu. | Điều dưỡng; thiết kế đồ họa; khoa học máy tính. |

Ví dụ: một doanh nghiệp y tế tuyển chuyên viên vận hành TikTok Shop có **lĩnh vực doanh nghiệp: y tế**, **nghề: vận hành TMĐT**, **nền tảng: TikTok Shop**, **ngành hàng: sản phẩm sức khỏe**. Không tự yêu cầu giấy phép lâm sàng vì doanh nghiệp thuộc y tế.

Bảy lĩnh vực người dùng yêu cầu nên là bảy **cửa vào khám phá**. Marketing và thiết kế là chức năng nghề; TMĐT đồng thời có thể là kênh kinh doanh; y tế có thể là lĩnh vực tổ chức hoặc nghề lâm sàng. Không ép tất cả thành một cây ngành kinh tế duy nhất.

Mỗi vị trí có một mã chuẩn. Một vị trí UI/UX có thể được tìm từ cả thiết kế và CNTT nhưng không tạo hai nghề khác nhau. Tin có vị trí chính và chuyên môn phụ khi thực sự kiêm nhiệm; hai công việc có yêu cầu hoặc điều kiện khác hẳn nên đăng hai tin.

## 5. Danh mục đề xuất cho bảy lĩnh vực

Các bảng sau là **danh mục tổng hợp đề xuất**, không phải bản sao taxonomy của một website. Danh mục nguồn và các tin mẫu là căn cứ để mở rộng thành nhóm hợp lý; không khẳng định đã đọc tin riêng cho từng chức danh dưới đây. “Trường đặc thù” là thông tin có thể cần hỏi theo vị trí, không phải tất cả đều bắt buộc.

### 5.1. Công nghệ thông tin

Căn cứ: [chuyên môn trên ITviec](https://itviec.com/it-jobs), [tin Backend Python](https://topdev.vn/detail-jobs/backend-developer-mid-level-globaltech-2136294), [tin kiểm thử tự động](https://topdev.vn/detail-jobs/associate-quality-engineer-automation-cong-ty-tnhh-capgemini-viet-nam-2137416).

| Nhánh nghề | Vị trí tiêu biểu | Trường đặc thù bên tuyển dụng | Dữ liệu đối ứng trong hồ sơ |
| --- | --- | --- | --- |
| Phát triển phần mềm | Frontend, Backend, Fullstack, Mobile Developer | Loại sản phẩm; ngôn ngữ/framework; nhiệm vụ kỹ thuật; kinh nghiệm stack liên quan. | Dự án, vai trò, công nghệ đã dùng và giai đoạn sử dụng. |
| Kiểm thử và chất lượng | Manual Tester, Automation QA | Web/mobile/API; kiểm thử thủ công/tự động; công cụ; kinh nghiệm từng loại. | Dự án kiểm thử, phạm vi, bộ kiểm thử và công cụ sử dụng. |
| Dữ liệu và AI | Data Analyst, Data Engineer, ML Engineer | Bài toán; dữ liệu; xử lý/phân tích/mô hình; công cụ. | Dự án, đóng góp, quy mô dữ liệu có thể chia sẻ và kết quả. |
| Hạ tầng và vận hành | System/Network Engineer, DevOps, Cloud Engineer | Môi trường triển khai; cloud; CI/CD; trực hệ thống. | Hệ thống từng phụ trách, nhiệm vụ, lịch trực chấp nhận. |
| An toàn thông tin | SOC Analyst, Pentester, Security Engineer | Phòng thủ/kiểm thử; hệ thống mục tiêu; quy trình; chứng nhận nếu yêu cầu. | Phạm vi kinh nghiệm, báo cáo đã ẩn dữ liệu, chứng nhận. |
| Phân tích và sản phẩm | Business Analyst, Product Owner, IT Project Manager | Phân tích nghiệp vụ/quản lý sản phẩm/dự án; lĩnh vực sản phẩm; bên liên quan. | Dự án, trách nhiệm, tài liệu và kết quả bàn giao. |

Không suy “biết Python” thành “làm AI”, hoặc “SQL” thành “có kinh nghiệm Data Engineer”. Công cụ và năng lực làm việc phải liên kết với nhiệm vụ thực tế.

### 5.2. Thương mại điện tử

Căn cứ: [danh mục JobsGO](https://jobsgo.vn/viec-lam-nhan-vien-van-hanh-san-thuong-mai-dien-tu.html), [vận hành TikTok Shop tại BIUBIUSHOP](https://jobsgo.vn/viec-lam/chuyen-vien-van-hanh-san-tmdt-29042819516.html), [vận hành TikTok Shop tại Ladomax](https://jobsgo.vn/viec-lam/nhan-vien-van-hanh-san-tiktok-shop-luong-cung-10-16-trieu-thang-29002897256.html).

| Nhánh nghề | Vị trí tiêu biểu | Trường đặc thù bên tuyển dụng | Dữ liệu đối ứng trong hồ sơ |
| --- | --- | --- | --- |
| Vận hành gian hàng | Marketplace Executive, Shop Operator | Sàn; thị trường; ngành hàng; tác vụ quản trị; thời gian trực tiếp vận hành. | Gian hàng/dự án mô tả được, nền tảng, vai trò và thời gian. |
| Ngành hàng và sản phẩm | Category Executive, Online Merchandiser | Danh mục hàng; định giá; khuyến mại; dự báo bán hàng. | Nhóm sản phẩm từng phụ trách; nghiệp vụ và kết quả. |
| Tăng trưởng và quảng cáo sàn | E-commerce Growth, Marketplace Ads Specialist | Công cụ quảng cáo; mục tiêu; phạm vi ngân sách; phân tích chuyển đổi. | Chiến dịch, ngân sách theo khoảng, thời gian, chỉ số có bối cảnh. |
| Affiliate và livestream | Affiliate Executive, Livestream Operator/Host | Kết nối đối tác hay vận hành/đứng hình; nền tảng; lịch; sản phẩm. | Vai trò thực tế, chương trình, sản phẩm nội dung và lịch sẵn sàng. |
| Đơn hàng và dịch vụ khách hàng | Order Processing, E-commerce Customer Service | Quản lý đơn; hoàn/hủy; đối soát; hệ thống; ca. | Nghiệp vụ đã làm, hệ thống, khối lượng theo khoảng và ca nhận được. |
| Website và phân tích thương mại | D2C Operations, E-commerce Analyst | Nền tảng website; báo cáo; hành trình mua; kết nối vận hành. | Dự án website/báo cáo, công cụ và phần việc trực tiếp. |

Kênh sàn, ngành hàng và nghiệp vụ là ba chiều khác nhau. Kinh nghiệm Shopee không tự đáp ứng yêu cầu TikTok Shop; có thể là kinh nghiệm liên quan nếu nhà tuyển dụng chấp nhận chuyển đổi.

### 5.3. Marketing

Căn cứ: [Trade Marketing trên CareerViet](https://careerviet.vn/vi/tim-viec-lam/trade-marketing-executive.35C8AC68.html), [Inbound Marketing trên Glints](https://glints.com/sg/opportunities/jobs/inbound-marketing-consultant/99cb14e9-a45c-425d-8ccb-0124aefb48a6), [nhánh nghề trên JobsGO](https://jobsgo.vn/viec-lam-nhan-vien-van-hanh-san-thuong-mai-dien-tu.html).

| Nhánh nghề | Vị trí tiêu biểu | Trường đặc thù bên tuyển dụng | Dữ liệu đối ứng trong hồ sơ |
| --- | --- | --- | --- |
| Nội dung | Content Marketer, Copywriter, Social Content | Kênh; định dạng; ngôn ngữ; đối tượng; đầu ra. | Bài/video/kịch bản, vai trò, mục tiêu và quyền chia sẻ. |
| Quảng cáo hiệu suất | Performance Marketer, Paid Media Specialist | Kênh quảng cáo; đo lường; mục tiêu; phạm vi ngân sách. | Chiến dịch, trách nhiệm, công cụ, ngân sách và kết quả theo kỳ. |
| Tìm kiếm | SEO Specialist, SEO Content | Kỹ thuật/nội dung; loại website; công cụ; thị trường. | Website/dự án, hạng mục thực hiện và thay đổi theo thời gian. |
| Thương hiệu và sản phẩm | Brand Executive, Product Marketing | Định vị; nghiên cứu; ra mắt sản phẩm; phân khúc. | Dự án thương hiệu/sản phẩm và phần đóng góp. |
| Trade, sự kiện và quan hệ công chúng | Trade Marketing, Event Executive, PR Executive | Điểm bán/kênh phân phối/sự kiện; khu vực; đi thị trường; ngân sách. | Chương trình từng triển khai, vai trò, địa bàn và đầu ra. |
| CRM và nghiên cứu | CRM/Lifecycle Specialist, Market Researcher | Phân khúc; tự động hóa; khảo sát/phân tích; hệ thống. | Luồng chăm sóc hoặc nghiên cứu, phương pháp, công cụ, kết quả. |

Không đặt ROAS, lượt xem hoặc số follower thành yêu cầu mặc định cho toàn marketing. Số liệu của một chiến dịch cần mục tiêu, nền tảng, kỳ đo và phần đóng góp trước khi được người tuyển dụng diễn giải.

### 5.4. Kinh doanh và bán hàng

Căn cứ: [tin B2B trên CareerViet](https://careerviet.vn/vi/tim-viec-lam/nhan-vien-kinh-doanh-b2b-ha-noi.35C8A7AE.html), [phân nhánh nghề JobsGO](https://jobsgo.vn/viec-lam-nhan-vien-van-hanh-san-thuong-mai-dien-tu.html), [hướng dẫn cấu phần thu nhập TopCV](https://tuyendung.topcv.vn/help/huong-dan-su-dung/dang-tin-tuyen-dung-mien-phi/).

| Nhánh nghề | Vị trí tiêu biểu | Trường đặc thù bên tuyển dụng | Dữ liệu đối ứng trong hồ sơ |
| --- | --- | --- | --- |
| Bán hàng doanh nghiệp | B2B Sales Executive, Account Executive | Khách hàng; sản phẩm/dịch vụ; tìm khách hay chốt; chu kỳ bán. | Phân khúc từng bán, nhiệm vụ, kinh nghiệm và thành tích có kỳ đo. |
| Bán hàng cá nhân | B2C Consultant, Telesales, Online Sales | Kênh tư vấn; nguồn khách; sản phẩm; ca; cơ cấu thu nhập. | Kênh đã làm, công việc, lịch và ưu tiên thu nhập. |
| Phát triển thị trường | Business Development, Partnership Executive | Thị trường/địa bàn; phát triển khách/đối tác; yêu cầu di chuyển. | Dự án phát triển, địa bàn, đối tác theo loại và vai trò. |
| Quản lý khách hàng | Key Account Manager, Customer Success | Chăm sóc/tái ký/mở rộng; loại khách; sản phẩm; hệ thống CRM. | Danh mục theo phân khúc, nghiệp vụ, chỉ số giữ khách có ngữ cảnh. |
| Phân phối và bán lẻ | Channel Sales, Sales Representative, Store Supervisor | Đại lý/điểm bán; địa bàn; lịch thị trường; quản lý ca/nhóm. | Kênh, tuyến, nhiệm vụ và kinh nghiệm dẫn nhóm. |
| Bán hàng kỹ thuật và hỗ trợ | Sales Engineer, Pre-sales, Sales Admin | Kiến thức giải pháp; demo/báo giá/đấu thầu; xử lý hợp đồng/đơn. | Sản phẩm/giải pháp đã làm và phần việc trực tiếp. |

Kinh doanh logistics thuộc nghề bán hàng với bối cảnh logistics; không mặc định đòi nghiệp vụ khai báo hải quan như một nhân viên chứng từ. Mức thu nhập gồm hoa hồng không đồng nghĩa lương cứng được bảo đảm.

### 5.5. Y tế và chăm sóc sức khỏe

Căn cứ: [danh mục y tế CareerLink](https://www.careerlink.vn/viec-lam/cham-soc-suc-khoe-y-te/14), [hướng dẫn trình bày hồ sơ điều dưỡng](https://www.careerlink.vn/cam-nang-viec-lam/goc-ky-nang/cach-viet-cv-dieu-duong), [tin kỹ thuật viên xét nghiệm trên Glints – bản chỉ mục](https://glints.com/vn/en/opportunities/jobs/ky-thuat-vien-xet-nghiem/d157560b-87e7-43a7-b314-6b4102e21e4c), [thư viện nghề Indeed](https://www.indeed.com/hire/how-to-write-a-job-description).

| Nhánh nghề | Vị trí tiêu biểu | Trường đặc thù bên tuyển dụng | Dữ liệu đối ứng trong hồ sơ |
| --- | --- | --- | --- |
| Khám chữa bệnh | Bác sĩ nội khoa, Bác sĩ răng hàm mặt | Chuyên khoa; phạm vi nhiệm vụ; loại giấy phép cần có; lịch. | Đào tạo; giấy phép/phạm vi; kinh nghiệm chuyên khoa và lịch. |
| Điều dưỡng và hộ sinh | Điều dưỡng nội trú, Điều dưỡng nhi, Hộ sinh | Khoa; nghiệp vụ; loại nhân sự thực hành/độc lập; ca; giấy phép khi cần. | Khoa đã làm, nhiệm vụ, đào tạo/giấy phép và ca nhận được. |
| Xét nghiệm | Kỹ thuật viên xét nghiệm, Nhân sự lấy mẫu | Nhánh xét nghiệm; quy trình; thiết bị; mức giám sát; yêu cầu chuyên môn. | Đào tạo; kỹ thuật từng thực hiện; thiết bị và phạm vi công việc. |
| Chẩn đoán và phục hồi | Kỹ thuật viên hình ảnh, Kỹ thuật viên phục hồi chức năng | Loại kỹ thuật; nhóm thiết bị; môi trường; yêu cầu đào tạo/phạm vi. | Kỹ thuật, thiết bị, lịch sử thực hành và giấy tờ tương ứng. |
| Dược | Dược sĩ nhà thuốc, Dược sĩ bệnh viện | Loại cơ sở; nghiệp vụ; nhiệm vụ; giấy phép nếu vị trí cần. | Bằng cấp, giấy phép, kinh nghiệm đúng loại cơ sở/nghiệp vụ. |
| Thiết bị và vận hành dịch vụ y tế | Kỹ sư thiết bị y tế, Điều phối dịch vụ khám | Thiết bị hay điều phối; quy trình; người sử dụng; ca/di chuyển. | Kinh nghiệm kỹ thuật/dịch vụ, hệ thống và nghiệp vụ liên quan. |

Không sử dụng blog tuyển dụng để quyết định quy định pháp lý về hành nghề. Danh mục giấy phép, phạm vi, giá trị chuyển tiếp và cách kiểm chứng cần nguồn chuyên ngành có thẩm quyền khi viết đặc tả. Báo cáo này chỉ đề xuất cấu trúc lưu yêu cầu và dữ kiện. Không mặc định mọi vị trí y tế có cùng yêu cầu giấy phép; không tự suy năng lực lâm sàng từ tên bằng cấp.

### 5.6. Logistics và chuỗi cung ứng

Căn cứ: [danh mục CareerLink](https://www.careerlink.vn/tim-viec-lam-nhanh), [nhân viên chứng từ hàng nhập](https://jobsgo.vn/viec-lam/nhan-vien-chung-tu-hang-nhap-27114248462.html), [trưởng nhóm kho trên JobOKO](https://vn.joboko.com/viec-lam-truong-nhom-kho-xvi6774321).

| Nhánh nghề | Vị trí tiêu biểu | Trường đặc thù bên tuyển dụng | Dữ liệu đối ứng trong hồ sơ |
| --- | --- | --- | --- |
| Giao nhận quốc tế và chứng từ | Import Documentation, Freight Forwarding Operations | Hàng nhập/xuất; biển/hàng không; chứng từ; nghiệp vụ và ngoại ngữ. | Loại lô hàng, chứng từ/quy trình đã xử lý và thời gian. |
| Hải quan | Customs Declaration, Customs Operations | Loại hình hàng; tác vụ khai báo; hệ thống; kiến thức cần dùng. | Nghiệp vụ thực tế, hệ thống và chuyên môn được khai báo rõ. |
| Kho và hoàn tất đơn | Warehouse Staff, Inventory Controller, Warehouse Lead | Loại kho/hàng; nhập-xuất-kiểm kê; WMS; ca; dẫn nhóm nếu có. | Loại kho, nghiệp vụ, hệ thống, lịch và trách nhiệm quản lý. |
| Vận tải và giao nhận | Transport Coordinator, Delivery Driver | Tuyến; loại phương tiện; lịch; di chuyển; giấy phép tương ứng khi cần. | Kinh nghiệm tuyến/xe, giấy phép, khả năng nhận ca. |
| Thu mua | Purchasing Executive, Sourcing Specialist | Nhóm vật tư; nhà cung cấp; trong nước/quốc tế; đàm phán; hệ thống. | Nhóm hàng từng mua, nghiệp vụ, thị trường và vai trò. |
| Hoạch định chuỗi cung ứng | Demand Planner, Supply Planner | Dự báo; kế hoạch tồn kho/cung ứng; công cụ; bối cảnh sản xuất/bán lẻ. | Dự án kế hoạch, hệ thống, phạm vi và kết quả có kỳ đo. |

Không dùng “biết logistics” làm một kỹ năng duy nhất. Thủ kho, điều phối xe, nhân viên chứng từ và chuyên viên thu mua cần các tập nghiệp vụ khác nhau.

### 5.7. Thiết kế và sáng tạo

Căn cứ: [Graphic Designer trên TopCV](https://www.topcv.vn/viec-lam/graphic-designer-thu-nhap-hap-dan-lam-tai-hcm-marketing-agency/2211518.html), [UI/UX tại MISA – bản chỉ mục](https://www.topcv.vn/viec-lam/ui-ux-designer-toi-thieu-2-nam-kinh-nghiem/2248725.html), [mẫu Graphic Designer của Indeed](https://in.indeed.com/hire/job-description/graphic-designer), [danh mục thiết kế trên JobOKO](https://vn.joboko.com/viec-lam-theo-nganh-nghe).

| Nhánh nghề | Vị trí tiêu biểu | Trường đặc thù bên tuyển dụng | Dữ liệu đối ứng trong hồ sơ |
| --- | --- | --- | --- |
| Đồ họa và nhận diện | Graphic Designer, Brand Designer | Đầu ra; kênh; công cụ; giai đoạn sáng tạo; portfolio. | Sản phẩm, vai trò, công cụ, bối cảnh và quyền chia sẻ. |
| Sản phẩm số và trải nghiệm | UI Designer, UX Designer, Product Designer | Web/app; nghiên cứu/thiết kế; prototype; design system; case study. | Case study thể hiện vấn đề, quy trình, đóng góp và đầu ra. |
| Chuyển động và video | Motion Designer, Video Editor | Dựng hay diễn hoạt; 2D/3D; định dạng; công cụ; showreel. | Video/showreel, phần việc, công cụ và quy trình. |
| Minh họa và game | Illustrator, Concept Artist, 3D/Game Artist | Loại asset; phong cách phù hợp dự án; 2D/3D; công cụ. | Bộ tác phẩm, vai trò và loại sản phẩm đã làm. |
| Không gian | Interior Designer, Exhibition Designer | Loại không gian; thiết kế/triển khai; bản vẽ; vật liệu; công cụ. | Dự án, giai đoạn phụ trách, bản vẽ và ảnh được phép chia sẻ. |
| Sản phẩm vật lý | Industrial Designer, Packaging Designer | Loại sản phẩm; vật liệu; mô hình; khả năng sản xuất; đầu ra. | Dự án, vai trò, công cụ, mẫu và kết quả bàn giao. |

Portfolio là **vật mang minh chứng**, không phải một kỹ năng. Có liên kết không chứng minh chất lượng; không có liên kết công khai cũng không chứng minh thiếu năng lực vì có dự án bị hạn chế chia sẻ.

## 6. Bộ trường chung của Kho Việc Làm

Quy ước: **B** = cần trả lời khi đăng; **ĐK** = bắt buộc khi tình huống tương ứng phát sinh; **T** = tùy chọn. Đây là quy tắc đề xuất, không mô tả validation hiện tại. Dữ liệu đã biết của tổ chức nên tự điền; lưu nháp không đòi đủ các trường đăng.

| Mã | Nhóm trường | Cách biểu diễn / số lượng | Mức | Vai trò |
| --- | --- | --- | --- | --- |
| J01 | Tổ chức, đơn vị tuyển | Một tổ chức; đơn vị/chi nhánh khi có. | B | Xác định bên tuyển và quyền quản lý; không chấm năng lực. |
| J02 | Tiêu đề tin | Văn bản dễ đọc. | B | Hiển thị/tìm kiếm; không dùng title chứa từ khóa để kết luận phù hợp. |
| J03 | Vị trí chuẩn | Một vị trí chính; chuyên môn phụ theo danh mục. | B | Tạo tập công việc liên quan; không buộc title trùng nguyên văn. |
| J04 | Lĩnh vực/bối cảnh | Lĩnh vực lấy từ tổ chức; ngành hàng, sản phẩm, khách hàng gắn riêng với tin. | T/ĐK | Đối chiếu khi tin thực sự yêu cầu trải nghiệm bối cảnh. |
| J05 | Cấp độ và quản lý | Cấp chuyên môn; có/không quản lý; phạm vi nếu cần. | B/ĐK | Hai chiều riêng, không suy từ số năm. |
| J06 | Mục tiêu, nhiệm vụ | Mô tả ngắn; các nhiệm vụ chính; đầu ra mong đợi. | B | Người dùng hiểu việc; chỉ nhiệm vụ đã chuẩn hóa và xác nhận mới dùng đối chiếu tự động. |
| J07 | Quan hệ hợp tác | Tuyển nhân sự, thực tập, cộng tác dịch vụ/dự án; thời hạn và điều kiện hợp tác khi có. | B/ĐK | Tương thích loại cơ hội. Không dùng thay cho lịch làm việc hoặc tự suy loại hợp đồng pháp lý từ nhãn thực tập. |
| J08 | Thời lượng làm việc | Toàn thời gian/bán thời gian hoặc số giờ dự kiến; khoảng thời gian cộng tác khi có. | B/ĐK | So với khả năng và mong muốn nhận việc. |
| J09 | Cách làm việc | Tại nơi làm việc/từ xa/kết hợp; yêu cầu hiện diện nếu kết hợp. | B/ĐK | So với khả năng hiện diện, không chỉ một nhãn remote. |
| J10 | Địa điểm/phạm vi | Danh sách địa điểm; chọn một hay phải đi nhiều nơi; vùng tuyển từ xa nếu có giới hạn. | B/ĐK | Địa lý, chuyển chỗ ở, di chuyển. Không cần địa chỉ nhà ứng viên. |
| J11 | Lịch và ca | Kiểu lịch; thứ/ngày; khung giờ; múi giờ; ca cố định/xoay; cuối tuần/trực khi có. | B/ĐK | So sánh giao nhau và ràng buộc lịch. Lịch linh hoạt phải được khai báo rõ. |
| J12 | Thu nhập | Công khai khoảng/từ/đến/thỏa thuận; tiền tệ; đơn vị; gross/net/chưa xác định; cơ cấu. | B/ĐK | Ưu tiên hai chiều; chỉ so số khi cùng cơ sở. |
| J13 | Lương cố định/biến đổi | Phần cố định, có phụ thuộc KPI không; hoa hồng/thưởng và điều kiện. | ĐK | Cho sales và vị trí tương tự; không cộng thu nhập tối đa vào lương bảo đảm. |
| J14 | Kỹ năng nghiệp vụ | Các yêu cầu theo mã kỹ năng, gắn với việc cần làm. | T/ĐK | Đối chiếu năng lực; cho phép vị trí được đào tạo từ đầu. |
| J15 | Công cụ/nền tảng/thiết bị | Các yêu cầu riêng, có thể gắn với nghiệp vụ. | T/ĐK | Biết công cụ và biết nghiệp vụ là hai dữ kiện. |
| J16 | Kinh nghiệm liên quan | Không yêu cầu, hoặc số tháng tối thiểu theo nghề/kỹ năng/bối cảnh. | B/ĐK | Không chỉ hỏi tổng số năm đi làm. |
| J17 | Học vấn/chuyên ngành | Không yêu cầu, hoặc bậc/ngành được chấp nhận; cho phép năng lực tương đương nếu bên tuyển chấp nhận. | B/ĐK | Không bắt mọi ứng viên có đại học hoặc đúng một chuyên ngành. |
| J18 | Ngoại ngữ | Ngôn ngữ, công việc cần sử dụng, năng lực/điểm chuẩn khi có. | T/ĐK | Ví dụ đọc chứng từ khác giao tiếp hoặc thuyết trình. |
| J19 | Giấy phép/chứng nhận | Loại, phạm vi, thời điểm cần đáp ứng, yêu cầu kiểm chứng. | ĐK | Điều kiện riêng của vị trí; không suy từ lĩnh vực. |
| J20 | Minh chứng/câu hỏi thêm | Loại minh chứng; kỹ năng/nhiệm vụ cần chứng minh; câu hỏi còn thiếu. | T/ĐK | Đánh giá bổ sung; không bắt tất cả nghề nộp portfolio. |
| J21 | Ngày có thể bắt đầu | Ngày muộn nhất hoặc khoảng; có linh hoạt không. | T | Đối chiếu thời điểm sẵn sàng. |
| J22 | Số lượng, hạn, trạng thái | Số người; hạn nhận; trạng thái tuyển. | B | Vận hành và điều kiện đưa tin vào matching, không chấm năng lực. |
| J23 | Quyền lợi và quy trình | Phúc lợi, đào tạo, các bước tuyển, người phụ trách nội bộ. | T | Giúp lựa chọn; không dùng tuổi/giới/ngôn từ quảng cáo làm suy luận năng lực. |

Một dòng trong bảng là **nhóm dữ liệu**, không phải một ô duy nhất. Ví dụ “thu nhập” có nhiều thuộc tính nhưng chỉ mở chi tiết khi người đăng chọn có số tiền hoặc có hoa hồng.

Các trường J16/J17 bắt buộc **trả lời chính sách**; câu “không yêu cầu” là hợp lệ. Không ép tin phải có một kỹ năng bắt buộc hoặc một bằng cấp chỉ để qua bước đăng.

### 6.1. Địa điểm và thời gian

Địa điểm nên dùng mã danh mục có phiên bản, tên hiện hành và tên cũ phục vụ tìm kiếm. Không hard-code quận/huyện bắt buộc; không suy các địa danh giống tên là cùng địa điểm. Một tin tuyển tại ba chi nhánh phải phân biệt “được chọn một” với “phải luân chuyển cả ba”.

Lịch có phần cấu trúc đủ so sánh và ghi chú ngoại lệ. “Thứ bảy cách tuần” không thể biểu diễn đúng bằng một số ngày/tuần; cần chu kỳ hoặc ghi rõ phần chưa thể tính tự động. Ca qua nửa đêm phải có ngày kết thúc phù hợp. Việc từ xa vẫn có thể đòi cư trú trong vùng hoặc giờ làm trùng nhau.

### 6.2. Thu nhập

Không đặt “12–25 triệu” vào một chuỗi duy nhất nếu cần đối chiếu. Cần biết đó là lương cố định hay tổng kỳ vọng, theo giờ/tháng/dự án, tiền tệ và gross/net. “Thỏa thuận” là chưa có căn cứ số, không phải mức bằng 0.

Không tự đổi lương giờ sang tháng khi chưa biết số giờ; không tự đổi net sang gross khi chưa đủ giả định; không tự coi mức lương hiện tại là kỳ vọng ứng viên. Mức tối thiểu ứng viên chấp nhận cần phân biệt với mức mong muốn, và có thể để riêng tư.

## 7. Cấu trúc một yêu cầu dùng cho matching

Đây là đối tượng nghiệp vụ đề xuất, chưa ánh xạ sang model hoặc tên trường code.

| Thuộc tính | Ý nghĩa / ví dụ |
| --- | --- |
| Loại | Nghiệp vụ; công cụ; kinh nghiệm; học vấn; ngoại ngữ; giấy phép; lịch; địa điểm; thu nhập. |
| Đối tượng chuẩn | Mã kỹ năng/nghề/công cụ/chứng nhận; tên hiển thị Việt/Anh và bí danh. |
| Nội dung cần đáp ứng | Ví dụ tự xử lý kiểm kê, dùng WMS, vận hành TikTok Shop. |
| Mức cần đạt | Mô tả hành vi hoặc chuẩn chuyên ngành; không dùng chung “4/5” cho mọi nghề. |
| Phép so sánh | Có; thuộc một trong; ít nhất; trong khoảng; còn hiệu lực; trùng lịch. |
| Giá trị và đơn vị | 18 tháng; một trong các công cụ; 2 ca/tuần; mã địa điểm. |
| Bối cảnh áp dụng | Nghề, khách hàng, ngành hàng, loại hệ thống/kho/khoa. |
| Mức cần thiết | Bắt buộc hoặc ưu tiên; nhà tuyển dụng phải xác nhận. |
| Nhóm lựa chọn | Cần tất cả (AND) hoặc ít nhất một (OR). Ví dụ Java **hoặc** TypeScript. |
| Chấp nhận tương đương | Có/không; danh mục hoặc mô tả được xác nhận, không do thuật toán tự đoán. |
| Thời điểm | Cần khi ứng tuyển, khi bắt đầu hay trước khi đảm nhận nhiệm vụ cụ thể. |
| Yêu cầu minh chứng | Chỉ khai báo; cần bổ sung; cần kiểm chứng theo quy trình phù hợp. |
| Nguồn và phiên bản | Ai nhập/xác nhận, thời điểm, phần mô tả gốc nếu được trích xuất. |

Ví dụ rõ nghĩa: **nghiệp vụ vận hành TikTok Shop, ít nhất 24 tháng trực tiếp phụ trách, bắt buộc; kinh nghiệm ngành gia dụng là ưu tiên**. Hai dòng này không nên bị gộp thành “TMĐT: 2 năm”.

Thang năng lực gợi ý cho nhiệm vụ: đã học/tiếp cận → làm với hướng dẫn → làm độc lập → xử lý tình huống phức tạp/hướng dẫn người khác. Đây là thang tham khảo theo hành vi; cần mô tả riêng theo nghề. Kỹ năng tự khai và kỹ năng đã có minh chứng vẫn phải phân biệt.

Không biến mọi yêu cầu ghi trong đoạn mô tả thành điều kiện loại. Với dữ liệu trích xuất sau này, máy chỉ đề xuất các dòng; người đăng phải xác nhận ý nghĩa, mức bắt buộc/ưu tiên và quan hệ AND/OR.

Khoảng kinh nghiệm mong muốn khác với ngưỡng tối thiểu. “Ưu tiên 2–4 năm” không tự trở thành điều kiện loại người có 5 năm. Một năng lực xuất hiện trong cả nhiệm vụ, công cụ và mô tả không được đếm thành ba căn cứ độc lập.

## 8. Mẫu chuyên môn nên thử trước

Mỗi mẫu chỉ gợi ý những trường liên quan. Những con số dưới đây là ví dụ cách đặt câu hỏi, không phải chuẩn tuyển dụng do TA.CARE áp đặt.

| Vị trí mẫu | Câu hỏi chuyên môn nên xuất hiện | Minh chứng hợp lý | Không tự yêu cầu |
| --- | --- | --- | --- |
| Backend Developer | Stack nào? Cần làm API/hệ thống/dữ liệu gì? Kinh nghiệm liên quan? | Dự án, vai trò và phần kỹ thuật có thể chia sẻ. | GitHub công khai, đại học, chứng chỉ cloud cho mọi tin. |
| Automation QA | Web/mobile/API? Tự động hóa bao lâu? Ngôn ngữ nào có thể thay thế nhau? | Dự án kiểm thử, test strategy/case đã ẩn dữ liệu. | Thành thạo toàn bộ công cụ liệt kê trong stack của công ty. |
| Vận hành sàn | Sàn và thị trường nào? Tự phụ trách tác vụ nào? Ngành hàng? | Case vận hành với giai đoạn và phần đóng góp. | Biết mọi sàn, hoặc coi xem TikTok là vận hành shop. |
| Affiliate/Livestream Operations | Tuyển tìm đối tác, vận hành hay host? Nền tảng và lịch? | Chương trình, kịch bản, quy trình hoặc video theo vai trò. | Ngoại hình/follower cho nhân sự vận hành hậu trường. |
| Performance Marketing | Kênh? Mục tiêu? Đo lường? Phạm vi ngân sách? | Chiến dịch với kỳ đo, ngân sách và kết quả có bối cảnh. | ROAS tuyệt đối dùng chung cho mọi sản phẩm. |
| Trade Marketing | Kênh phân phối? Điểm bán? Địa bàn? Đi thị trường? | Chương trình triển khai và vai trò. | Google Ads như kỹ năng bắt buộc mặc định. |
| B2B Sales | Loại khách? Giải pháp? Tự tìm hay nhận lead? Chu kỳ bán? | Case bán hàng đã ẩn tên khách, vai trò và kết quả. | Danh sách khách hàng thật hoặc doanh số không kèm kỳ đo. |
| Sales Engineer | Sản phẩm kỹ thuật? Mức tư vấn/demo? Ngoại ngữ? | Giải pháp hoặc dự án từng tư vấn và phần việc. | Có kỹ năng kỹ thuật đồng nghĩa biết bán hàng. |
| Điều dưỡng | Khoa? Nhiệm vụ và mức giám sát? Lịch trực? Hồ sơ chuyên môn cần đối chiếu? | Đào tạo, quá trình làm việc và giấy tờ qua quyền truy cập phù hợp. | Dữ liệu người bệnh hoặc một loại giấy phép mặc định cho mọi vai trò. |
| Kỹ thuật viên xét nghiệm | Nhánh xét nghiệm? Nhiệm vụ? Thiết bị? Đào tạo cần có? | Kinh nghiệm quy trình và giấy tờ chuyên môn phù hợp. | Đăng kết quả xét nghiệm thật hoặc coi chứng nhận ngắn hạn thay bằng chuyên môn. |
| Nhân viên chứng từ | Hàng nhập/xuất? Phương thức vận tải? Chứng từ/nghiệp vụ? Ngoại ngữ? | Mô tả quy trình và trách nhiệm; tài liệu minh họa đã ẩn dữ liệu khi được phép. | Năng lực lái xe hoặc quản lý kho. |
| Trưởng nhóm kho | Loại kho? Nghiệp vụ? WMS? Thời gian làm kho và dẫn nhóm? Ca? | Quá trình làm việc, phạm vi dẫn nhóm và case cải tiến. | Chức danh quản lý đồng nghĩa có nhiều năm dẫn nhóm. |
| Graphic Designer | Loại ấn phẩm? Kênh? Công cụ? Vai trò concept/triển khai? | Tác phẩm với brief, vai trò và quyền chia sẻ. | Biết Figma hoặc viết code cho mọi tin đồ họa. |
| UI/UX Designer | Web/app? Nghiên cứu hay UI? Design system? Handoff? | Case study về vấn đề, quá trình, vai trò và giải pháp. | Biết Figma đồng nghĩa biết nghiên cứu UX. |

Các mẫu kiểm thử tự động, vận hành sàn, trade, B2B, chứng từ, trưởng nhóm kho và graphic được đối chiếu với tin đọc trực tiếp ở phần 11. Mẫu điều dưỡng dựa thêm trên hướng dẫn hồ sơ; xét nghiệm và UI/UX có nguồn Việt Nam đọc được ở bản chỉ mục. Các mẫu còn lại là mở rộng đề xuất từ nhóm nghề và cần đối chiếu tin riêng khi chốt danh mục.

## 9. Từ yêu cầu tuyển dụng suy ra cấu trúc Tủ Hồ Sơ

Tủ Hồ Sơ nên lưu **sự kiện và trải nghiệm có thể dùng lại**, thay vì bắt người dùng điền một bộ câu trả lời mới cho từng nghề. Một người có thể quan tâm nhiều vị trí; một kinh nghiệm có thể chứng minh nhiều năng lực.

| Nhóm dữ liệu hồ sơ | Nội dung tối thiểu hợp lý | Đáp ứng yêu cầu tuyển dụng |
| --- | --- | --- |
| Giới thiệu | Tên hiển thị, tiêu đề nghề, tóm tắt năng lực; thông tin liên hệ lưu riêng. | Hiển thị và hiểu hồ sơ; tên không dùng xếp hạng. |
| Nghề quan tâm | Nhiều vị trí chuẩn; mức độ mong muốn; có nhận nghề gần không. | J03; giúp ứng viên chuyển nghề mà không bị khóa vào công việc cũ. |
| Mong muốn theo loại cơ hội | Vị trí/nhóm cơ hội, hình thức hợp tác, cách làm, vùng, lịch và thu nhập tương ứng. | J07–J13; không gộp lương theo dự án với lương nhân viên. |
| Sẵn sàng làm việc | Ngày bắt đầu, giờ/ca có thể nhận, múi giờ, di chuyển/chuyển nơi ở. | J08–J11, J21; phân biệt mong muốn với khả năng thực tế. |
| Kinh nghiệm làm việc | Tổ chức hoặc mô tả tổ chức, vai trò chuẩn và chức danh, thời gian, nhiệm vụ, bối cảnh, công cụ. | J04–J06, J14–J16; ghi riêng việc làm, thực tập, dự án. |
| Dự án và thực hành | Vấn đề, thời gian, vai trò, nhiệm vụ, công cụ, đầu ra. | Nguồn chứng minh cho người mới và người đổi nghề. Không tự tính như thời gian làm nhân viên. |
| Năng lực nghiệp vụ | Mã kỹ năng, hành vi có thể thực hiện, mức tự khai, trải nghiệm liên kết. | J14; không chỉ một ô “kỹ năng mềm”. |
| Công cụ/nền tảng/thiết bị | Mã, mức sử dụng thực tế, tác vụ, kinh nghiệm/dự án liên quan, lần dùng gần nhất nếu biết. | J15; không tự suy năng lực nghề từ việc biết công cụ. |
| Học vấn | Nhiều quá trình, bậc, chuyên ngành, trạng thái đang học/hoàn tất, thời gian. | J17; không bắt công khai trường hoặc GPA để matching cơ bản. |
| Ngoại ngữ | Ngôn ngữ, tác vụ dùng được, chuẩn/điểm và ngày đánh giá nếu có. | J18; tự khai và chứng chỉ được đánh dấu riêng. |
| Giấy phép/chứng nhận | Loại, cơ quan cấp, phạm vi, ngày cấp, hết hạn nếu có, tình trạng khai báo/kiểm chứng. | J19; giấy phép, bằng cấp và khóa học không thay thế tùy tiện. |
| Minh chứng/kết quả | Loại, tiêu đề, vai trò, năng lực liên quan, thời gian, ngữ cảnh; link/file khi có chức năng phù hợp. | J20; một minh chứng liên kết được nhiều kỹ năng. |
| Quyền chia sẻ và cập nhật | Phạm vi từng dữ liệu, đồng ý tìm kiếm/matching/liên hệ, thời điểm xác nhận gần nhất. | Điều kiện được xử lý và hiển thị; không phải điểm cộng năng lực. |

Không bắt nhập toàn bộ các nhóm để tạo hồ sơ. Hồ sơ ban đầu có thể gồm nghề muốn làm, khu vực/cách làm, khả năng nhận lịch và một nguồn năng lực như kinh nghiệm, dự án, học vấn hoặc kỹ năng. Thông tin còn thiếu được hỏi khi một cơ hội cần, và người dùng có thể chưa cung cấp.

### 9.1. Kinh nghiệm và kết quả không chỉ là một con số

Kinh nghiệm nên có khoảng thời gian và liên kết tới nghề/nhiệm vụ/công cụ. Tính tháng liên quan từ các khoảng có căn cứ, gộp khoảng trùng; không cộng hai công việc đồng thời thành hai lần thời gian. Nếu không biết giai đoạn dùng một kỹ năng trong công việc dài, số tháng của riêng kỹ năng là chưa xác định, không tự lấy cả thời gian làm việc.

Phân biệt mức làm toàn/bán thời gian, thực tập, thực hành và dự án. Khi đối chiếu cần nói rõ nhà tuyển dụng có chấp nhận từng loại không; không tự quy đổi “ba dự án” thành “hai năm”.

Một kết quả định lượng nên có: tên chỉ số, giá trị/đơn vị, kỳ đo, bối cảnh/quy mô, phần đóng góp, nguồn và quyền chia sẻ. Chỉ hỏi khi có ích. Doanh số, lượt xem, tốc độ xử lý và số lượng người phục vụ không so trực tiếp giữa các môi trường khác nhau.

Trạng thái minh chứng: tự khai → có tài liệu tham chiếu → đã được người có thẩm quyền kiểm tra → cần cập nhật/không còn hiệu lực, tùy loại. Có URL hoặc file không tự chuyển thành đã xác minh. Không ép tải dữ liệu khách hàng, bệnh nhân hoặc tài liệu mật để chứng minh thành tích.

## 10. Cách dữ liệu này hỗ trợ matching

### 10.1. Trình tự đề xuất

1. **Kiểm tra quyền và hiệu lực:** tin đang nhận kết nối, hồ sơ được phép dùng cho mục đích matching, đúng phạm vi dữ liệu và người xem.
2. **Tìm cơ hội có liên quan:** vị trí chuẩn, nghề gần có quan hệ được duyệt, nhiệm vụ và mong muốn của ứng viên. Không lọc cứng theo lĩnh vực công ty cũ hoặc tên chức danh cũ.
3. **Đối chiếu điều kiện hai bên:** các yêu cầu bắt buộc được xác nhận, khả năng hiện diện, lịch, ngày bắt đầu và điều kiện ứng viên không thể nhận.
4. **Đối chiếu chuyên môn và ưu tiên:** nghiệp vụ, công cụ, kinh nghiệm liên quan, bối cảnh và minh chứng được phép dùng.
5. **Giải thích và hỏi phần thiếu:** hiện căn cứ đã có, điều kiện mâu thuẫn, thông tin cần xác nhận và ưu tiên bổ sung.

### 10.2. Trạng thái từng tiêu chí

| Trạng thái | Khi nào | Ví dụ lời giải thích |
| --- | --- | --- |
| Đáp ứng theo dữ liệu đã khai | Có dữ liệu đủ để so sánh, đạt yêu cầu; kèm trạng thái kiểm chứng. | “Đã khai 26 tháng trực tiếp vận hành TikTok Shop.” |
| Có mâu thuẫn được xác nhận | Dữ kiện rõ ràng trái điều kiện thực sự bắt buộc. | “Vị trí cần ca tối; bạn chỉ nhận ca sáng.” |
| Chưa đủ thông tin | Không có dữ liệu, bị giới hạn chia sẻ hoặc dữ liệu chưa đủ chi tiết. | “Chưa có thông tin về phạm vi giấy phép cần đối chiếu.” |
| Cần đánh giá chuyên môn | Dữ liệu có nhưng chất lượng/tương đương cần người đánh giá. | “Đã có case study UX; cần xem phần đóng góp.” |
| Không áp dụng | Tin không đặt yêu cầu đó. | “Vị trí này không yêu cầu bằng cấp.” |

Ưu tiên không phải điều kiện loại. Một điều kiện bắt buộc mâu thuẫn không được bù bằng nhiều kỹ năng phụ. “Chưa đủ thông tin” không bị đổi thành “không đạt”; nếu đó là điều kiện quan trọng thì kết quả là **chờ xác nhận**, không kết luận đủ điều kiện.

Với nhóm OR, một lựa chọn đáp ứng là đủ; chỉ kết luận không đáp ứng khi mọi lựa chọn đều có dữ liệu xác nhận không đáp ứng. Với nhóm AND, một mâu thuẫn bắt buộc đã xác nhận là đủ để nêu điều kiện chưa phù hợp. Nếu chưa có mâu thuẫn nhưng còn dữ liệu thiếu, trạng thái của nhóm vẫn là chưa đủ thông tin.

Giải thích chỉ dùng dữ liệu người xem được phép biết. Không tiết lộ sự tồn tại, tên hoặc nội dung một minh chứng riêng tư qua câu “hồ sơ có tài liệu nhưng chưa chia sẻ”. Khi không có dữ liệu được phép dùng, chỉ nói chưa có đủ thông tin cho tiêu chí đó.

Kết quả tổng hợp ban đầu nên là: **có căn cứ phù hợp**, **cần bổ sung/xác nhận**, hoặc **có điều kiện bắt buộc chưa phù hợp**, cùng lý do cụ thể. Không hiển thị “đã xác minh đủ điều kiện hành nghề” khi chỉ có tự khai. Mọi kết luận còn phụ thuộc tính đúng và phạm vi của dữ liệu đầu vào.

### 10.3. Các trường hợp cần thiết kế đúng

| Tình huống giả định | Xử lý đề xuất |
| --- | --- |
| Một ứng viên làm backend ở bệnh viện, ứng tuyển backend tại công ty bán lẻ. | Đối chiếu chuyên môn; bối cảnh bệnh viện không khóa ứng viên vào y tế. |
| Tin ghi Java hoặc TypeScript; ứng viên đáp ứng một lựa chọn. | Đánh giá đúng nhóm OR, không báo thiếu lựa chọn còn lại. |
| Có 5 năm đi làm, chỉ 8 tháng làm chứng từ hàng nhập; tin cần 12 tháng liên quan. | Nêu 8 tháng liên quan theo khai báo; không lấy 5 năm tổng. |
| Ứng viên khai Shopee; tin bắt buộc kinh nghiệm TikTok Shop. | Không tự coi tương đương. Nếu chưa hỏi TikTok thì đánh dấu chưa biết; nếu xác nhận chưa có thì nêu khoảng thiếu. |
| Tin y tế cần giấy phép đúng phạm vi; hồ sơ chỉ có bằng chuyên môn. | Chưa có dữ liệu giấy phép để kết luận; bằng cấp không tự thay giấy phép. |
| Tin yêu cầu giấy phép còn hiệu lực tại ngày bắt đầu; giấy tờ đã xác nhận hết hiệu lực trước ngày đó. | Nêu mâu thuẫn tại đúng thời điểm; không bù bằng kinh nghiệm. |
| Biết Figma, chưa có dữ kiện làm nghiên cứu người dùng. | Đáp ứng phần công cụ; năng lực nghiên cứu vẫn cần thông tin. |
| Công việc kho bắt buộc ca đêm; ứng viên xác nhận không nhận đêm. | Có mâu thuẫn lịch; cùng thành phố và đủ nghiệp vụ không xóa mâu thuẫn. |
| Tin lương cứng 9 triệu, tổng kỳ vọng 20 triệu; ứng viên cần lương cứng tối thiểu 15 triệu. | So 9 với 15, không lấy 20 so với 15. |
| Ứng viên muốn 18 triệu net, tin 20 triệu gross. | Chưa cùng cơ sở; yêu cầu làm rõ, không kết luận hơn/kém bằng phép so số thô. |
| Một tin có ba địa điểm được chọn một; ứng viên nhận một địa điểm. | Đủ điều kiện địa điểm; không bắt cả ba. |
| Người mới chưa có việc làm nhưng có dự án phù hợp; tin chấp nhận người mới. | Dùng dự án để đối chiếu năng lực, không loại vì kinh nghiệm làm việc rỗng. |
| Portfolio không công khai do hạn chế dự án. | Cho mô tả/đánh giá qua luồng được phép; không đánh dấu thiếu năng lực. |
| Ứng viên thu hồi đồng ý matching hoặc quyền xem một minh chứng. | Ngừng dùng dữ liệu tương ứng; kết quả cũ không tạo quyền đọc tiếp. |

Chưa đề xuất trọng số hoặc ngưỡng xếp hạng chung cho bảy lĩnh vực. Cần có bộ cặp việc–hồ sơ giả định/được phép sử dụng, người tuyển đánh giá và kiểm tra lỗi loại nhầm trước khi chốt. Độ đầy đủ hồ sơ, mức tự tin kết luận và mức phù hợp là ba khái niệm riêng.

## 11. Sổ căn cứ từ tin và tài liệu bổ sung

Các ghi nhận dưới đây chỉ lấy phần cần cho thiết kế dữ liệu; không sao chép toàn bộ mô tả. “Trực tiếp” nghĩa là công cụ đọc được nội dung trang, không nghĩa là đã thực hiện quy trình tuyển dụng.

| Nguồn | Mức đọc | Ghi nhận cụ thể | Quyết định thiết kế liên quan |
| --- | --- | --- | --- |
| [Backend Python – TopDev](https://topdev.vn/detail-jobs/backend-developer-mid-level-globaltech-2136294) | Trực tiếp | Phân biệt kinh nghiệm backend Python và các kinh nghiệm hệ thống là điểm cộng. | Kinh nghiệm có ngữ cảnh; bắt buộc/ưu tiên riêng. |
| [Automation QA – TopDev](https://topdev.vn/detail-jobs/associate-quality-engineer-automation-cong-ty-tnhh-capgemini-viet-nam-2137416) | Trực tiếp | Kinh nghiệm kiểm thử và tự động hóa có ngưỡng riêng; ngôn ngữ có lựa chọn thay thế. | Nhiều dòng kinh nghiệm; nhóm OR. |
| [Vận hành sàn – BIUBIUSHOP/JobsGO](https://jobsgo.vn/viec-lam/chuyen-vien-van-hanh-san-tmdt-29042819516.html) | Trực tiếp | Nêu TikTok Shop, trách nhiệm doanh số, phân tích hiệu quả và case từng triển khai. | Nền tảng, tác vụ, trách nhiệm và minh chứng tách nhau. |
| [Vận hành sàn – Ladomax/JobsGO](https://jobsgo.vn/viec-lam/nhan-vien-van-hanh-san-tiktok-shop-luong-cung-10-16-trieu-thang-29002897256.html) | Trực tiếp | Có Seller Center; ngành gia dụng là ưu tiên; lương cứng khác phần doanh số. | Bối cảnh ưu tiên; cấu phần thu nhập. |
| [Vận hành/phân tích dữ liệu TMĐT – JobsGO](https://jobsgo.vn/viec-lam/chuyen-vien-van-hanh-va-phan-tich-du-lieu-thuong-mai-dien-tu-27952806028.html) | Bản chỉ mục; mở trực tiếp lỗi | Không yêu cầu kinh nghiệm nhưng có công cụ báo cáo/truy vấn; vai trò giao giữa TMĐT và dữ liệu. | Không suy yêu cầu số năm từ danh sách công cụ; nghề giao nhau. |
| [Trade Marketing – CareerViet](https://careerviet.vn/vi/tim-viec-lam/trade-marketing-executive.35C8AC68.html) | Trực tiếp | Công việc tại điểm bán, phối hợp sales, ngân sách, thị trường; thông tin học vấn trong các phần không hoàn toàn đồng nhất. | Cần trường nghiệp vụ và bối cảnh; cần kiểm tra mâu thuẫn dữ liệu trước khi dùng. |
| [Inbound Marketing – Glints](https://glints.com/sg/opportunities/jobs/inbound-marketing-consultant/99cb14e9-a45c-425d-8ccb-0124aefb48a6) | Trực tiếp, Singapore | Giao tiếp với khách, quản lý công việc và công cụ marketing; các năng lực cần/ưu tiên được tách. | Một vị trí có nhiều nhóm năng lực; không sao chép điều kiện quốc gia vào Việt Nam. |
| [B2B Sales – CareerViet](https://careerviet.vn/vi/tim-viec-lam/nhan-vien-kinh-doanh-b2b-ha-noi.35C8A7AE.html) | Trực tiếp | Kinh nghiệm B2B dịch vụ và kinh nghiệm ngành tuyển dụng có mức cần thiết khác nhau. | Khách hàng và lĩnh vực sản phẩm là hai chiều. |
| [Danh sách y tế – CareerLink](https://www.careerlink.vn/viec-lam/cham-soc-suc-khoe-y-te/14) | Trực tiếp danh sách; một số tin chi tiết lỗi | Có điều dưỡng nhi, bác sĩ nội khoa, răng hàm mặt; cùng danh sách còn có vai trò phần mềm/dịch vụ. | Không dùng nhãn y tế thay cho nghề cụ thể. |
| [Hồ sơ điều dưỡng – CareerLink](https://www.careerlink.vn/cam-nang-viec-lam/goc-ky-nang/cach-viet-cv-dieu-duong) | Trực tiếp, bài hướng dẫn | Đề cập khoa, quá trình làm việc, kỹ thuật, giấy tờ và ngoại ngữ. | Tủ Hồ Sơ cần khoa/chuyên môn và giấy tờ riêng; không lấy các khẳng định pháp luật trong bài làm quy tắc hệ thống. |
| [Kỹ thuật viên xét nghiệm – Glints](https://glints.com/vn/en/opportunities/jobs/ky-thuat-vien-xet-nghiem/d157560b-87e7-43a7-b314-6b4102e21e4c) | Bản chỉ mục; mở trực tiếp lỗi | Nêu đào tạo xét nghiệm, công việc theo quy trình và thời gian làm việc. | Trường đào tạo chuyên môn, nghiệp vụ và lịch riêng. |
| [Chứng từ hàng nhập – JobsGO](https://jobsgo.vn/viec-lam/nhan-vien-chung-tu-hang-nhap-27114248462.html) | Trực tiếp | Nội dung yêu cầu kinh nghiệm 6 tháng; nhãn tóm tắt ghi 1–3 năm. Có nghiệp vụ hàng nhập và ngoại ngữ. | Phải xác nhận mâu thuẫn, không tự chọn một ngưỡng; lưu yêu cầu theo ngữ cảnh. |
| [Trưởng nhóm kho – JobOKO](https://vn.joboko.com/viec-lam-truong-nhom-kho-xvi6774321) | Trực tiếp | Thời gian nghiệp vụ và dẫn nhóm khác nhau; Excel là yêu cầu, ERP/WMS là ưu tiên. | Tách hai loại kinh nghiệm; tránh biến toàn bộ công cụ thành bắt buộc. |
| [Graphic Designer – TopCV](https://www.topcv.vn/viec-lam/graphic-designer-thu-nhap-hap-dan-lam-tai-hcm-marketing-agency/2211518.html) | Trực tiếp | Nhiều dạng ấn phẩm, công cụ và portfolio; chức danh và mô tả có khác biệt cấp bậc. | Cần đầu ra/vai trò thực tế; không tự suy cấp độ chỉ từ title. |
| [UI/UX Designer – MISA/TopCV](https://www.topcv.vn/viec-lam/ui-ux-designer-toi-thieu-2-nam-kinh-nghiem/2248725.html) | Bản chỉ mục | Phân biệt công cụ, nghiên cứu trải nghiệm và bối cảnh sản phẩm. | Tách kỹ năng UX khỏi công cụ thiết kế. |
| [Graphic Designer – Indeed](https://in.indeed.com/hire/job-description/graphic-designer) | Trực tiếp, mẫu quốc tế | Mẫu nghề đề cập phát triển ý tưởng, phối hợp và chỉnh sửa thiết kế. | Đầu ra và quy trình nghề giúp viết mẫu câu hỏi. |

Đọc bổ sung [ESCO – nghề nghiệp](https://esco.ec.europa.eu/en/classification/occupation_main) và [O*NET – các nhóm kỹ năng](https://www.onetonline.org/find/descriptor/browse/2.A) để đối chiếu cách tách nghề, kỹ năng, kiến thức và bối cảnh. Đây là tài liệu tham khảo cấu trúc, không tính vào 10 website tuyển dụng; chưa nhập hay ánh xạ toàn bộ danh mục, chưa quyết định dùng chuẩn nào cho TA.CARE.

## 12. Hình dung biểu mẫu gọn hơn

### Kho Việc Làm

1. **Tuyển ai:** chức danh, vị trí chuẩn, cấp độ, số lượng; thông tin tổ chức tự điền.
2. **Làm việc gì:** mục tiêu và nhiệm vụ chính; bối cảnh cần thiết.
3. **Cần năng lực gì:** mẫu theo vị trí; từng yêu cầu có bắt buộc/ưu tiên; phần học vấn, kinh nghiệm và giấy phép mở theo câu trả lời.
4. **Làm ở đâu, khi nào, thu nhập ra sao:** hợp tác, thời lượng, cách làm, địa điểm, lịch, thu nhập và quyền lợi.
5. **Xem trước và đăng:** hạn tuyển; kiểm tra trường thiếu, yêu cầu mâu thuẫn và tóm tắt dữ liệu sẽ dùng matching.

Không buộc người đăng chọn lại ba tầng danh mục nếu gõ được vị trí: tìm một lần, chọn kết quả, hệ thống suy ra nhánh. Nếu chưa có vị trí, cho mô tả để đề xuất danh mục; không tự biến tên nhập tự do thành một nghề chuẩn ngay lập tức.

Form cần cho phép sửa mẫu; mẫu là gợi ý, không phải rào cản. Không tự thêm “đại học”, “2 năm kinh nghiệm” hoặc “có chứng chỉ” chỉ vì đã chọn lĩnh vực. Dữ liệu không liên quan được ẩn; nếu đổi vị trí, giữ bản nháp và yêu cầu rà lại điều kiện cũ trước khi đưa vào matching.

### Tủ Hồ Sơ

Khởi đầu bằng **muốn làm gì + có thể làm ở đâu/khi nào + đã làm/học/thực hành gì**. Khi chọn nghề, gợi ý đúng nhóm năng lực và minh chứng. Các lần bổ sung làm giàu cùng hồ sơ; không tạo một hồ sơ độc lập cho mỗi tin. Tách phần thông tin liên hệ và quyền chia sẻ khỏi phần năng lực.

Với một cơ hội cụ thể, hỏi phần còn thiếu dưới dạng câu dễ trả lời: “Bạn đã trực tiếp xử lý chứng từ hàng nhập chưa?”, “Bạn nhận được ca 22:00–06:00 không?”. Trả lời chưa cung cấp khác với không có/không nhận. Câu trả lời cần lưu ngữ cảnh và thời điểm, chỉ tái dùng khi đúng nghĩa và đúng quyền.

## 13. Điều cần kiểm chứng trước khi chuyển sang đặc tả

Đề xuất hiện tại đủ để soát lại cách đặt trường, nhưng chưa phải bộ danh mục hoàn chỉnh cho mọi ngành. Các bước nghiệp vụ tiếp theo nên là:

1. Chọn các vị trí ưu tiên trong 14 mẫu; bổ sung tin chi tiết đọc trực tiếp cho các nhánh hiện mới có danh mục/bản chỉ mục, nhất là y tế.
2. Cho người tuyển dụng và người tìm việc thử mô tả một công việc/hồ sơ bằng bộ trường; kiểm tra ô nào khó hiểu, trùng nghĩa hoặc không dùng được.
3. Chuẩn hóa tên nghề, kỹ năng và bí danh Việt/Anh; phân biệt đồng nghĩa với năng lực liên quan. Ví dụ “JS” có thể là bí danh JavaScript; React và JavaScript là hai khái niệm liên quan, không phải một.
4. Chốt yêu cầu nào được coi là bắt buộc, ai xác nhận tương đương và khi nào cần người đánh giá. Giấy phép theo nghề cần nguồn chuyên ngành riêng.
5. Đánh giá bằng các tình huống phần 10, ghi nhận lỗi loại nhầm và trường còn thiếu trước khi bàn trọng số hay mô hình AI.
6. Sau khi chốt nghiệp vụ mới lập bảng ánh xạ vào mô hình dự án, phương án thay form, tương thích dữ liệu và kiểm tra quyền. Báo cáo này chưa quyết định đổi tên model hoặc migration.

Không chỉnh sửa code ứng dụng, form đang chạy, database, Docker hoặc production trong nghiên cứu này. Không chạy kiểm thử Python/XML/HTTP vì không có thay đổi ứng dụng; chỉ kiểm tra cấu trúc và liên kết của tài liệu cục bộ. Chưa có OCR, thuật toán mới, xác minh giấy tờ, tải CV hay lưu snapshot matching nào được triển khai từ báo cáo này.
