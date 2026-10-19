# Bộ trường tối thiểu và ví dụ điền thử việc linh hoạt

Ngày 19/10/2026. **Bản đề xuất cho chủ dự án xem trước khi triển khai thử.** Chưa sửa ứng dụng hoặc nhập dữ liệu vào database.

**Cập nhật theo trao đổi tiếp theo:** chủ dự án đề nghị tách cách làm và nơi làm để dễ matching. Xem **phần 8** về các trường cần tách. Bản 8/7 và ví dụ bên dưới giữ vai trò nhóm trình bày; không được lưu mỗi nhóm thành một chuỗi văn bản rồi coi là đã có dữ liệu đối chiếu.

**Xác nhận tiếp theo của chủ dự án về vị trí:** trước mắt dùng địa chỉ/khu vực tĩnh do người dùng khai báo. Kho ghi nơi làm, Tủ ghi khu vực nhận việc; hành trình tách điểm đầu/cuối. Giữ các thành phần địa chỉ cần thiết thành dữ liệu riêng, không gộp với cách thực hiện. Bản đồ và đánh giá khoảng cách để nghiên cứu sau; địa chỉ tĩnh không tự cung cấp khoảng cách hoặc khả năng theo dõi vị trí.

## 1. Quyết định nghiên cứu mới nhất

TA.CARE tự chọn trường phù hợp sản phẩm. Nền tảng khác giúp tìm tình huống để thử xem có bỏ sót thông tin, không quyết định cấu trúc của TA.CARE.

Tạm rút xuống **Kho Việc Làm 8 nhóm nhập, Tủ Hồ Sơ 7 nhóm nhập**. Số nhóm không phải số cột database; nhóm giá hoặc lịch có vài ô nhỏ. Chưa làm form riêng cho mọi nghề: chi tiết kỹ năng, số phòng, cây, vật tư, phương tiện, giấy phép liên quan… trước mắt có thể nằm trong mô tả có gợi ý.

Một tài khoản có thể có nhu cầu thuê và nhận việc trong thiết kế nghiên cứu. Một hồ sơ có thể có nhiều mục nhận việc, mỗi mục có giá riêng; không tự cấp quyền C2C cho tài khoản hiện tại. Bản tối thiểu này phục vụ xem và điền thử, chưa quyết định thay đổi schema/quyền.

Nguồn tham khảo đã có trong [sổ mẫu](flexible_work_form_samples_2026-10-19.md). Bốn nguồn được kiểm tra lại ở lượt rút gọn:

- [Taskrabbit — các thẻ người nhận dọn nhà](https://www.taskrabbit.com/locations/houston/house-cleaning): có phạm vi công việc, đồ nghề, số giờ tối thiểu và điều kiện nhận.
- [Airtasker — tin làm vườn](https://www.airtasker.com/au/services/gardening/sydney/): việc thay chậu có số cây, vật tư chủ cung cấp; không cần biến tất cả thành trường riêng.
- [Airtasker — tin thuê lái xe](https://www.airtasker.com/au/services/driving/sydney/): có cả thuê tài xế lái xe khách và thuê người có xe đi hành trình.
- [vLance — dự án landing page](https://www.vlance.vn/viec-freelance/can-tim-freelancer-thiet-ke-tron-goi-landing-page-dich-vu-internet): cần mô tả đầu ra và nền tảng thực hiện, thay cho lịch ca của công việc tại chỗ.

## 2. Kho Việc Làm: 8 nhóm nhập

| Mã mới | Trường người dùng thấy | Dữ liệu cần nhập | Khi nào cần |
| --- | --- | --- | --- |
| N1 | Tiêu đề việc cần người | Câu ngắn cho biết cần làm gì. | Cần có |
| N2 | Nghề / loại công việc | Một nghề chính; có lựa chọn đề xuất nghề khác. | Cần có |
| N3 | Mô tả việc và yêu cầu | Việc cụ thể, khối lượng hoặc đầu ra; kỹ năng thật sự cần; dụng cụ/vật tư ai có; phần không gồm nếu có. Gợi ý theo nghề ngay trong một ô. | Cần mô tả việc; chi tiết nào liên quan mới điền |
| N4 | Cách làm và nơi làm | Tại chỗ / từ xa / mang về làm / theo hành trình / kết hợp. Tại chỗ khai khu vực bằng chữ; hành trình khai điểm đầu–cuối; từ xa không bắt địa chỉ nhà. | Cần có; nơi làm theo cách chọn |
| N5 | Thời gian cần làm | Một lần / định kỳ / theo đợt / trước hạn; ngày, giờ, thời lượng hoặc lựa chọn linh hoạt phù hợp. | Cần có; không ép giờ vào ca cho việc theo đầu ra |
| N6 | Số người cần | Mặc định 1; đổi khi cần nhiều người. | Có mặc định hiển thị rõ |
| N7 | Tiền công / ngân sách | Số hoặc khoảng tiền; đơn vị; giá cho từng người hay cả việc/nhóm; đã gồm gì, phần chưa gồm nếu có. Cho đánh dấu có thể thương lượng. | Cần có |
| N8 | Ảnh / tài liệu mô tả | Hiện trạng hoặc mẫu mong muốn. | Tùy chọn |

Người đăng và trạng thái tin lấy từ ngữ cảnh tài khoản/hệ thống; có thao tác đóng/tạm dừng tin. Không nhập lại thông tin liên hệ vào nội dung từng bài. Kỳ trả tiền nếu muốn ghi, tạm để trong mô tả; chưa cần một mục bắt buộc riêng.

## 3. Tủ Hồ Sơ: 7 nhóm cho mỗi mục nhận việc

| Mã mới | Trường người dùng thấy | Dữ liệu cần nhập | Khi nào cần |
| --- | --- | --- | --- |
| V1 | Nghề / việc tôi nhận | Một nghề cho mục này; thêm mục khác nếu nhận nghề khác. | Cần có ít nhất một mục |
| V2 | Giới thiệu công việc tôi nhận | Tiêu đề ngắn và mô tả việc làm được; kỹ năng, giới hạn, đồ nghề, điều kiện nhận tối thiểu nếu có. | Cần mô tả phạm vi; chi tiết liên quan mới điền |
| V3 | Cách và khu vực nhận việc | Tại chỗ, từ xa, mang về làm, theo hành trình hoặc kết hợp; khu vực bằng chữ khi cần. | Cần có; khu vực theo cách chọn |
| V4 | Thời gian có thể nhận | Ngày/buổi rảnh hoặc linh hoạt cần hẹn; có thể nêu thời gian hoàn thành một gói. | Cần có |
| V5 | Tiền công mong muốn | Số/khoảng tiền theo việc này, đơn vị và phạm vi giá; số giờ tối thiểu/phí thêm nếu áp dụng có thể ghi cùng nhóm. | Cần có |
| V6 | Kinh nghiệm liên quan | Đoạn ngắn; cho phép chưa có kinh nghiệm nhận việc trả công. | Tùy chọn |
| V7 | Ảnh / sản phẩm từng làm | Ảnh/link và chú thích phần mình làm. | Tùy chọn |

Tên hiển thị và liên hệ thuộc hồ sơ chung. Trạng thái đang nhận/tạm ngừng là điều khiển quản lý hồ sơ; không bắt điền lại mỗi lần. Khu vực/lịch có thể kế thừa giữa các mục nhận việc rồi chỉnh riêng khi khác.

## 4. Cách khai giá ngắn nhưng đủ nghĩa

Trong N7/V5 có ba phần chính: **số tiền hoặc khoảng tiền → đơn vị → phạm vi giá**. Mặc định VND hiển thị rõ; chưa cần chọn tiền tệ cho mọi bài thử.

- Đơn vị thử: giờ; ca; buổi; ngày; tháng; trọn việc/gói; sản phẩm; chuyến.
- Ca/buổi/ngày phải nói gồm bao nhiêu giờ hoặc lịch cụ thể. Giá tháng cần lịch/phạm vi trong mô tả. Giá gói cần đầu ra; giá chuyến cần hành trình.
- Mặc định giá một người nếu thuê nhân công; với cả nhóm/gói/chuyến phải ghi rõ. Không để chữ “150.000đ” đứng riêng.
- Có thể thương lượng vẫn đi kèm mức hoặc khoảng tham khảo. Không tự điền số tượng trưng khi chưa có con số.
- Phí vật tư/xe/đồ ăn/phát sinh: ghi gồm/chưa gồm/trao đổi thêm theo thực tế. Không tự hiện tổng chắc chắn nếu còn khoản chưa biết.
- Lịch làm và thời điểm trả tiền khác đơn vị giá. Chưa cần thêm chức năng thanh toán để thử biểu mẫu này.

## 5. Sáu ví dụ điền thử

**Toàn bộ ví dụ sau là dữ liệu giả lập để thử form**, lấy loại tình huống từ nguồn và yêu cầu chủ dự án. Khu vực, lịch, giá VND, kinh nghiệm và hồ sơ đối ứng do nghiên cứu đặt ra; không phải bản sao tin/hồ sơ thật, không phải giá thị trường hoặc người thật sẵn sàng nhận việc. Không quy đổi giá nước ngoài sang các giá này.

Mỗi bảng điền N1–N8 và V1–V7. Chưa có ảnh là giá trị hợp lệ. Kết quả dưới bảng chỉ kiểm tra người đọc hiểu gì, chưa chạy matching hay kiểm tra năng lực người làm.

### T01 — Dọn căn hộ theo giờ

| Mục | Kho Việc Làm | Tủ Hồ Sơ |
| --- | --- | --- |
| Tiêu đề / nghề | N1: Cần người dọn căn hộ sáng thứ Bảy. N2: Dọn dẹp nhà cửa. | V1: Dọn dẹp nhà cửa. |
| Mô tả | N3: Căn hộ khoảng 60m²; lau sàn, vệ sinh bếp và một nhà tắm; không nấu ăn. Chủ có dụng cụ và hóa chất. | V2: Nhận lau dọn căn hộ, bếp và nhà tắm; không nhận vệ sinh sau xây dựng; khách chuẩn bị dụng cụ. |
| Cách / nơi | N4: Tại chỗ, khu vực Thủ Đức, TP.HCM. | V3: Nhận tại chỗ, khu vực Thủ Đức, TP.HCM. |
| Lịch | N5: Một lần, 24/10/2026, 08:00–11:00, dự kiến ba giờ. | V4: Rảnh thứ Bảy 08:00–12:00, hẹn trước một ngày. |
| Nhân lực | N6: Một người. | Người nhận làm trực tiếp; không cần nhập số người riêng. |
| Giá | N7: 60.000đ/giờ/người; dự kiến 180.000đ/ba giờ; gồm công, dụng cụ chủ có. | V5: 60.000đ/giờ; tối thiểu hai giờ/lần; khách chuẩn bị dụng cụ/hóa chất, không thu phí đi lại trong khu vực đã nêu. |
| Kinh nghiệm | Nằm trong N3 nếu có yêu cầu; ví dụ này không đòi số năm. | V6: Đã dọn căn hộ định kỳ khoảng một năm — nội dung giả lập. |
| Ảnh | N8: Chưa đính kèm. | V7: Chưa có. |

**Kiểm tra:** đọc được việc, giới hạn, đồ nghề, lịch và số tiền dự kiến. Hai giờ tối thiểu không làm đổi mức giá của việc ba giờ. Không có ảnh vẫn đủ để đăng thử.

### T02 — Nấu bữa tối định kỳ, tiền công tháng

| Mục | Kho Việc Làm | Tủ Hồ Sơ |
| --- | --- | --- |
| Tiêu đề / nghề | N1: Tìm người nấu bữa tối các ngày trong tuần. N2: Nấu ăn gia đình. | V1: Nấu ăn gia đình. |
| Mô tả | N3: Nấu cho bốn người, khoảng ba món/bữa; dọn khu bếp sau nấu; không giặt/quét nhà. Chủ mua nguyên liệu và có bếp/dụng cụ. | V2: Nhận nấu bữa gia đình bốn người, ba món và dọn bếp; không gồm đi chợ, nguyên liệu hoặc việc nhà khác. |
| Cách / nơi | N4: Tại nhà khách, khu vực Gò Vấp, TP.HCM. | V3: Nhận tại nhà khách, khu vực Gò Vấp, TP.HCM. |
| Lịch | N5: Định kỳ thứ Hai–thứ Sáu, 16:00–19:00, từ 02/11/2026; nghỉ cuối tuần. | V4: Nhận định kỳ thứ Hai–thứ Sáu, 16:00–19:00, từ tháng 11. |
| Nhân lực | N6: Một người. | Nhận làm trực tiếp. |
| Giá | N7: 5.000.000đ/tháng cho lịch và phạm vi trên; chỉ tiền công. Ghi thêm trong N3: dự kiến trả cuối tháng; ngày phát sinh trao đổi riêng. | V5: 4.800.000–5.500.000đ/tháng cho lịch và phạm vi trên; không gồm nguyên liệu, ngày làm thêm báo riêng. |
| Kinh nghiệm | Không yêu cầu chứng chỉ ở ví dụ này. | V6: Đã nấu cơm gia đình khoảng hai năm — giả lập. |
| Ảnh | N8: Chưa có. | V7: Có thể bổ sung ảnh món ăn sau, hiện để trống. |

**Kiểm tra:** giá tháng vẫn mô tả được việc bán thời gian; không cần tính lại giá giờ. Nguyên liệu và công nấu tách rõ. Chưa có ảnh không cản thử.

### T03 — Bốc hàng, cần hai người, giá một ca cho từng người

| Mục | Kho Việc Làm | Tủ Hồ Sơ |
| --- | --- | --- |
| Tiêu đề / nghề | N1: Cần hai người bốc hàng trong một buổi sáng. N2: Bốc xếp hàng hóa. | V1: Bốc xếp hàng hóa. |
| Mô tả | N3: Khoảng 40 thùng, mỗi thùng 10–15kg, chuyển từ xe tải vào kho tầng trệt; chủ có xe đẩy. Không thuê xe chở hàng. | V2: Nhận bốc thùng từ xe vào kho tầng trệt, sử dụng xe đẩy khách cung cấp; chỉ nhận phần nhân công. |
| Cách / nơi | N4: Tại chỗ, khu vực Bình Tân, TP.HCM. | V3: Tại chỗ, khu vực Bình Tân, TP.HCM. |
| Lịch | N5: Một lần, 25/10/2026, 08:00–12:00; một ca bốn giờ. | V4: Rảnh Chủ nhật 08:00–12:00, cần hẹn trước. |
| Nhân lực | N6: Hai người. | Một hồ sơ là một người; còn cần người thứ hai. |
| Giá | N7: 150.000đ/ca bốn giờ/người; hai người dự kiến 300.000đ; chỉ nhân công trong ca. | V5: 150.000đ/ca bốn giờ/người; làm quá ca phải thỏa thuận thêm. |
| Kinh nghiệm | Mô tả rõ khối lượng, không coi tên nghề là đã đủ năng lực. | V6: Đã phụ kho/bốc hàng — giả lập. |
| Ảnh | N8: Chưa có ảnh thùng hàng. | V7: Chưa có. |

**Kiểm tra:** không nhầm 150.000đ là tiền cả đội hoặc mỗi giờ. Một hồ sơ không có nghĩa đáp ứng nhu cầu hai người. Thiếu ảnh không cản mô tả khối lượng bằng chữ.

### T04 — Thay chậu cây, giá trọn đầu việc

| Mục | Kho Việc Làm | Tủ Hồ Sơ |
| --- | --- | --- |
| Tiêu đề / nghề | N1: Cần thay chậu cho 12 cây ở ban công. N2: Chăm sóc cây cảnh. | V1: Chăm sóc cây cảnh. |
| Mô tả | N3: Thay chậu 12 cây nhỏ ở ban công; chủ có chậu, đất, sỏi; gom đất thừa vào bao để tại nhà, không chở phế thải đi. | V2: Nhận thay chậu cây nhỏ và dọn chỗ làm; có dụng cụ cầm tay; không xử lý cây lớn hoặc chở phế thải. |
| Cách / nơi | N4: Tại chỗ, khu vực Phú Nhuận, TP.HCM. | V3: Nhận tại chỗ, khu vực Phú Nhuận, TP.HCM. |
| Lịch | N5: Một lần, 25/10/2026, bắt đầu khoảng 09:00; dự kiến ba giờ. | V4: Nhận Chủ nhật buổi sáng; hẹn trước. |
| Nhân lực | N6: Một người. | Một người thực hiện. |
| Giá | N7: 300.000đ/trọn việc 12 cây; tiền công; vật tư do chủ có. | V5: 300.000đ/trọn việc 12 cây nhỏ như mô tả; chưa gồm mua vật tư hoặc mang phế thải đi. |
| Kinh nghiệm | Không thêm ô số năm bắt buộc. | V6: Có chăm cây ban công tại nhà, chưa từng nhận việc trả công — giả lập. |
| Ảnh | N8: Có thể bổ sung ảnh 12 cây; hiện chưa đính kèm. | V7: Chưa có. |

**Kiểm tra:** ba giờ chỉ là dự kiến; 300.000đ là tiền trọn việc, không tự biến thành đơn giá giờ. Người mới vẫn diễn đạt được việc nhận và giới hạn. Cần trao đổi thêm nếu kích thước cây khác mô tả.

### T05 — Landing page, làm từ xa theo gói

| Mục | Kho Việc Làm | Tủ Hồ Sơ |
| --- | --- | --- |
| Tiêu đề / nghề | N1: Cần làm một landing page giới thiệu dịch vụ. N2: Thiết kế website. | V1: Thiết kế website. |
| Mô tả | N3: Một trang trên LadiPage, năm phần, dùng được trên điện thoại/máy tính, form gửi về email; khách cấp nội dung/logo; hai lượt chỉnh sửa. Không gồm quảng cáo, tên miền hoặc phí nền tảng. | V2: Nhận một landing page LadiPage năm phần, có form gửi email, hai lượt chỉnh sửa; khách cấp nội dung/logo. Không nhận chạy quảng cáo trong gói này. |
| Cách / nơi | N4: Từ xa; không khai địa chỉ nhà. | V3: Nhận từ xa. |
| Lịch | N5: Giao trước 30/10/2026; nhận đủ nội dung từ 26/10/2026; không yêu cầu giờ ca. | V4: Có thể bắt đầu 26/10/2026; hoàn thành trong bốn ngày sau khi nhận đủ nội dung, cần thống nhất hạn chốt bản cuối. |
| Nhân lực | N6: Một người. | Nhận trực tiếp. |
| Giá | N7: 2.000.000đ/gói cho đầu ra nêu trên; không gồm tên miền/phí nền tảng. | V5: 1.800.000–2.200.000đ/gói theo phạm vi trên; chốt giá sau khi xem nội dung. |
| Kinh nghiệm | Yêu cầu làm được LadiPage viết ngay N3; không mở bảng kỹ năng riêng. | V6: Đã làm vài trang giới thiệu dịch vụ — giả lập. |
| Ảnh | N8: Chưa có mẫu tham khảo. | V7: Chưa đính kèm link sản phẩm; có thể bổ sung sau. |

**Kiểm tra:** không cần ép điền nơi làm tại chỗ hoặc giờ/ngày. Đủ mô tả đầu ra, hạn giao, giá gói và phạm vi sửa. Khoảng giá chưa phải báo giá đã chốt.

### T06 — Xe kèm tài xế, theo chuyến

| Mục | Kho Việc Làm | Tủ Hồ Sơ |
| --- | --- | --- |
| Tiêu đề / nghề | N1: Cần xe kèm tài xế đưa gia đình đi một chiều. N2: Chở khách theo chuyến. | V1: Chở khách theo chuyến. |
| Mô tả | N3: Bốn hành khách, bốn vali nhỏ; yêu cầu xe 7 chỗ; TP.HCM đến Đà Lạt, không quay về cùng chuyến; không có điểm đón thêm; cần có cả xe và tài xế. Giấy tờ/điều kiện dịch vụ phải được làm rõ ở bước tiếp theo. | V2: Nhận xe 7 chỗ kèm tài xế, tối đa bốn hành khách và hành lý như mô tả; nhận một chiều/khứ hồi báo giá riêng; chưa xác minh giấy tờ trong dữ liệu thử. |
| Cách / nơi | N4: Theo hành trình; đón tại khu vực Thủ Đức, TP.HCM; trả tại khu vực trung tâm Đà Lạt. | V3: Nhận hành trình TP.HCM–Đà Lạt; cần chốt điểm cụ thể để báo giá. |
| Lịch | N5: Một lần; đón 24/10/2026 lúc 07:00; một chiều, cần thống nhất giờ đến dự kiến. | V4: Có thể nhận sáng 24/10/2026, cần hẹn trước. |
| Nhân lực | N6: Một tài xế; bốn hành khách ghi trong N3, không nhập thành bốn người cần thuê. | Một tài xế kèm xe. |
| Giá | N7: Ngân sách 1.200.000đ/chuyến một chiều, mong gồm xe/tài xế/nhiên liệu/cầu đường; cần báo rõ nếu chưa đủ. | V5: 1.500.000–1.800.000đ/chuyến một chiều cho hành trình dự kiến, gồm xe/tài xế/nhiên liệu/cầu đường; chốt sau điểm đón/trả. |
| Kinh nghiệm | Điều kiện nghề chưa được giải quyết bằng một dòng tự khai. | V6: Để trống ở ví dụ này. |
| Ảnh | N8: Chưa có. | V7: Chưa có ảnh xe. |

**Kiểm tra:** form thể hiện được xe+tài xế, một chiều, hành khách, hành lý và hai mức giá khác nhau. Hai bên **chưa thống nhất giá**; không gọi đây là giao dịch có thể nhận ngay. Đây là thử mô tả dữ liệu, chưa kết luận điều kiện vận hành vận tải.

## 6. Kiểm tra sau khi điền thử

| Câu kiểm tra | Kết quả trên sáu ví dụ |
| --- | --- |
| Việc theo giờ, ca, tháng, trọn việc/gói và chuyến có chỗ khai không? | Có; không cần đổi toàn bộ form theo đơn vị giá. |
| Có phân biệt một người/hai người và giá từng người/cả việc không? | Có; T03 thể hiện hai người, giá một ca cho từng người. |
| Có đủ chỗ ghi kỹ năng/khối lượng/vật tư/giới hạn không? | Có trong N3/V2; chưa cần ép thành nhiều ô bắt buộc. |
| Việc từ xa có bị bắt nhập địa chỉ nhà/ca làm không? | Không; T05 dùng hình thức từ xa và hạn giao. |
| Giá gói có bị biến thành giá giờ từ thời lượng dự kiến không? | Không; T04 giữ giá trọn việc dù có ước lượng thời gian. |
| Người mới/không ảnh có thể đăng thử không? | Có; V6/V7 tùy chọn, T04 thể hiện người chưa nhận việc trả công. |
| Có giữ được khác biệt chưa thống nhất thay vì làm dữ liệu cho đẹp không? | Có; T06 còn lệch giá, T03 còn thiếu người thứ hai; T05 còn chốt phạm vi/giá. |
| Có kết luận form đã được thử trên phần mềm hoặc với người dùng không? | Chưa; đây là điền và đọc lại thủ công trong tài liệu. |

**Đề xuất tiếp theo:** dùng 8/7 nhóm này làm bản thử đầu tiên. Dọn nhà, nấu ăn, bốc xếp, chăm cây và việc số đủ để thử nhiều kiểu khai; tình huống chuyến xe giữ làm ca nghiên cứu biểu mẫu. Trường riêng chỉ tách thêm khi điền thực tế thấy mô tả chung khó dùng, cần kiểm tra bắt buộc hoặc có yêu cầu sản phẩm mới.

## 7. Đối chiếu tài liệu trước

Đây là **bản rút gọn mới nhất để xem và thử**, theo yêu cầu sau khi đọc [bộ trường đầy đủ](flexible_work_forms_2026-10-19.md). Mã N/V chỉ dùng trong tài liệu này, không đổi mã K/H/P/C cũ hay model/field của Odoo.

Những điều kiện còn cần nghiên cứu không cản việc dựng ví dụ và thử cấu trúc dữ liệu. Triển khai ứng dụng sẽ là bước riêng sau khi chủ dự án xem bản này; không tự sửa luồng tuyển dụng, map, matching hoặc database trong lượt nghiên cứu.

## 8. Điều chỉnh: tách trường để có dữ liệu đối chiếu rõ

Đây là đề xuất cấu trúc dữ liệu nghiệp vụ, chưa triển khai thuật toán hoặc đổi schema. Số nhóm trình bày không quyết định số trường lưu. Các trường độc lập vẫn có thể nằm cùng hàng/khối trên giao diện, không phải mỗi trường một màn hình hoặc một đoạn mô tả nhập lại.

### 8.1. Những phần nên tách ở cả hai phía

| Thành phần | Kho Việc Làm | Tủ Hồ Sơ | Quy tắc đề xuất |
| --- | --- | --- | --- |
| Nghề chính | Nghề/dịch vụ cần thuê | Nghề của mục nhận việc | Một nghề chính cho từng tin/mục nhận; không suy mọi năng lực từ nhãn nghề. |
| Kỹ năng / đầu việc cụ thể | Chọn các mục cần, ví dụ lau sàn, vệ sinh bếp, nấu ăn; thêm công cụ chuyên môn nếu liên quan | Chọn khả năng thực hiện của mục nhận việc | Chọn từ danh mục chung có thể mở rộng, không ép đủ số thẻ hoặc khai số năm từng thẻ. Phân biệt tác vụ và công cụ trong danh mục; không coi chúng đồng nghĩa. Mô tả tự do vẫn bổ sung phạm vi. |
| Mức cần thiết của yêu cầu | Đánh dấu bắt buộc hoặc ưu tiên trên từng yêu cầu đã chọn | Khai khả năng và giới hạn thực tế; có thể chưa khai | Không tạo hai danh sách nhập lặp. Nhiều yêu cầu bắt buộc mặc định cần đủ; nếu chấp nhận một trong các mục thay thế phải nêu rõ, không tự hiểu dấu phẩy là “hoặc”. Chưa khai khác xác nhận không làm được. |
| Cách thực hiện | Trực tiếp / từ xa / kết hợp | Các cách chấp nhận nhận việc | Không dùng cách thực hiện để suy ra nơi làm hoặc giờ làm. “Mang về làm” có thể ghi điều kiện bàn giao riêng khi liên quan. |
| Nơi thực hiện / khu vực nhận | Khu vực công việc bằng chữ; công việc hành trình có điểm đầu và điểm cuối riêng | Các khu vực nhận việc bằng chữ; hành trình có các tuyến/phạm vi nhận phù hợp | Từ xa thuần túy không bắt địa chỉ nhà. Khu vực nhận không phải nơi ở. Chưa tích hợp map/bán kính. |
| Kiểu lịch | Một lần / định kỳ / theo đợt | Các kiểu lịch chấp nhận | Một lần vẫn có thể là việc theo đầu ra. “Giao trước hạn” là mốc thời gian, không thay cho mọi kiểu lịch. |
| Ngày và giờ cụ thể | Ngày bắt đầu/kết thúc, thứ/ngày lặp và giờ bắt đầu/kết thúc theo từng lịch; hoặc hạn bàn giao với việc theo đầu ra | Ngày/buổi/khung giờ có thể nhận, ngày sớm nhất, ngoại lệ khi có | Gắn đúng khung giờ với đúng ngày, không ghép mọi giờ với mọi thứ. Cho chọn linh hoạt/cần hẹn; giá trị chưa rõ không bị suy thành luôn rảnh. |
| Thời lượng | Số giờ/phút dự kiến; nếu tính ca/buổi/ngày thì nêu độ dài đơn vị | Thời gian nhận tối thiểu nếu có; thời gian hoàn thành dự kiến cho gói nếu biết | Tách dự kiến với giới hạn bắt buộc. Không coi khung rảnh bốn giờ là cam kết nhận tối thiểu bốn giờ. |
| Số tiền | Một số hoặc từ–đến, tiền tệ mặc định VND hiển thị rõ | Một số hoặc từ–đến theo mục nhận việc | Không ép khai thêm giá sàn riêng tư. Khoảng giá và mức cố định cần phân biệt. |
| Đơn vị giá | Giờ / ca / buổi / ngày / tháng / gói / sản phẩm / chuyến | Cùng bộ đơn vị | Không lưu tất cả trong chuỗi “150k/ca”. Không so giá khác đơn vị khi chưa có cơ sở. |
| Giá cho ai / phạm vi giá | Mỗi người / cả nhóm / cả đầu việc-gói-chuyến | Giá của cá nhân / đội thực hiện / gói dịch vụ như đã mô tả | Số người cần là trường riêng; không lấy số hành khách làm số người thuê. Giá gói/chuyến không tự thành giá cho mỗi người. |
| Khoản bao gồm và khả năng thương lượng | Các khoản đã gồm/chưa gồm/chưa rõ; ngân sách cố định hay có thể trao đổi | Các khoản đã gồm/chưa gồm/chưa rõ, điều kiện phụ thu; có thể thương lượng | Không tự tính tổng chắc chắn khi còn khoản chưa biết; không tự thêm phụ phí. |

Kỹ năng/đầu việc nên là trường chọn riêng ngay trong bản thử, thay cho việc chỉ nằm ở N3/V2. Với việc không cần yêu cầu chuyên môn riêng, cho khai nhận người mới/được hướng dẫn; không buộc bịa kỹ năng hoặc sao chép toàn bộ mô tả thành thẻ.

### 8.2. Chỉ tách thêm khi có yêu cầu thật

| Nội dung | Khi nào mở thành dữ liệu riêng | Cách giữ form gọn |
| --- | --- | --- |
| Dụng cụ, vật tư hoặc phương tiện | Việc quyết định bên nào chuẩn bị; ví dụ cần xe chở, máy cắt cỏ, dụng cụ vệ sinh | Chọn chủ chuẩn bị/người làm mang/mỗi bên một phần/cần trao đổi; chỉ hỏi danh sách vật dụng thực sự cần, có thể đánh dấu món bắt buộc. |
| Xe+tài xế hay chỉ tài xế | Tin thuê lái xe/hành trình | Loại dịch vụ riêng; nếu có xe mới hỏi sức chở, số hành khách/hành lý và đặc điểm cần. Không dùng mỗi nhãn “lái xe”. |
| Giấy phép/chứng nhận | Nghề hoặc người thuê có yêu cầu liên quan cụ thể | Loại giấy tờ/phạm vi/thời hạn khi cần; trạng thái tự khai và đã kiểm tra tách biệt. Không mặc định yêu cầu bản chụp công khai. |
| Kinh nghiệm | Có yêu cầu thực sự cần đối chiếu | Số tháng/năm liên quan hoặc mô tả loại việc đã làm theo yêu cầu; không bắt mọi người khai số năm và không coi thiếu dữ liệu là 0. |
| Khối lượng/đầu ra | Giá theo sản phẩm/khối lượng hoặc khả năng thực hiện phụ thuộc quy mô | Số lượng và đơn vị phù hợp: 12 cây, 40 thùng, một trang web…; không bắt mọi nghề điền đồng thời phòng, m², cân nặng, số cây. |

Các yêu cầu riêng nếu được dùng để kết luận đủ điều kiện phải được khai rõ theo loại dữ liệu phù hợp. Nếu còn nằm trong mô tả và chưa được xác nhận, để ở trạng thái cần trao đổi; không giả định máy đã hiểu toàn bộ văn bản.

### 8.3. Áp lại vào sáu tình huống đã điền

| Ví dụ | Dữ liệu nên tách từ nội dung đã có | Điều kiểm tra được bằng việc đọc dữ liệu |
| --- | --- | --- |
| T01 Dọn nhà | Cách: trực tiếp; nơi: Thủ Đức; việc: lau sàn/vệ sinh bếp/nhà tắm; lịch: một lần, 24/10/2026 08–11; giá: 60.000, VND, giờ, mỗi người; tối thiểu phía nhận: hai giờ | Nếu thêm yêu cầu nấu ăn, phải hỏi năng lực nấu; cùng nghề dọn nhà chưa đủ. |
| T02 Nấu ăn | Việc: nấu bữa gia đình/dọn bếp; lịch: định kỳ thứ Hai–thứ Sáu 16–19; tiền: 5.000.000, VND, tháng; chủ mua nguyên liệu | Giá tháng không khiến việc trở thành toàn thời gian; kỳ trả cuối tháng không thay đơn vị giá. |
| T03 Bốc xếp | Trực tiếp; Bình Tân; một ca bốn giờ; số người: hai; giá: 150.000, VND, ca, mỗi người; xe đẩy do chủ có | Nhận một người còn thiếu người thứ hai; không nhầm giá mỗi người với cả nhóm. |
| T04 Chăm cây | Đầu việc: thay chậu; số lượng: 12 cây nhỏ; trực tiếp; giá: 300.000, VND, trọn việc; không gồm mang phế thải đi | Ba giờ dự kiến không đổi giá thành 100.000đ/giờ; cây lớn hoặc tăng số lượng cần xem lại phạm vi. |
| T05 Website | Cách: từ xa; chuyên môn/công cụ: thiết kế landing page/LadiPage; đầu ra: một trang, năm phần; hạn: 30/10; giá: gói | Cùng nghề website nhưng chưa khai LadiPage vẫn là chưa biết; không bắt nơi ở/giờ vào ca. |
| T06 Xe theo chuyến | Cách: trực tiếp; loại dịch vụ: xe+tài xế; điểm đầu/cuối: Thủ Đức/trung tâm Đà Lạt; một chiều; xe 7 chỗ; bốn hành khách; giá: chuyến | Người chỉ nhận lái xe khách chưa đáp ứng nhu cầu có xe; giá hai phía vẫn chưa thống nhất. |

Đây vẫn là kiểm tra dữ liệu và đọc tình huống thủ công. Chưa chạy matching. Đề xuất ưu tiên tách **cách/nơi, nghề/kỹ năng, lịch và giá**, sau đó mở các mục điều kiện theo nghề. Tiêu đề, mô tả chi tiết, kinh nghiệm kể chuyện và ảnh vẫn có vai trò giải thích, không cần chuẩn hóa mọi câu thành một trường.
