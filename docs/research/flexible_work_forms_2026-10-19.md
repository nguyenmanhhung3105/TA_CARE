# Trường Kho Việc Làm và Tủ Hồ Sơ cho việc linh hoạt — bản nghiên cứu

Ngày: **19/10/2026**. Trạng thái: **đề xuất nghiệp vụ để tiếp tục nghiên cứu, chưa duyệt triển khai**.

Tài liệu này tập trung trường nhập và nội dung hiển thị của **phần tìm việc linh hoạt**, theo yêu cầu mới nhất. Không nghiên cứu map, bán kính, cách tính matching, thanh toán hoặc thay đổi phần tuyển dụng đã có. Địa điểm vẫn cần dưới dạng khu vực bằng chữ để người đọc hiểu công việc; đây không phải tích hợp bản đồ.

Đề xuất dựa trên [40 mẫu tin/hồ sơ công khai và bảng kiểm tra từng mẫu](flexible_work_form_samples_2026-10-19.md). Không sửa code, model, database, cấu hình hoặc dữ liệu ứng dụng.

## 1. Kết luận để thiết kế biểu mẫu

Nên có **phần chung ngắn + chi tiết mở theo công việc**. Người đăng việc mô tả nhu cầu; người nhận việc mô tả khả năng và điều kiện nhận. Một cá nhân có thể có cả hai nhu cầu; không bắt họ tạo tài khoản mới theo từng nghề.

Tủ Hồ Sơ nên cho giới thiệu **nhiều mục “Công việc tôi nhận” trong cùng hồ sơ**. Mỗi mục có phạm vi và giá riêng; lịch và khu vực có thể kế thừa thông tin chung, sửa riêng khi khác. Đây là cấu trúc nghiệp vụ đề xuất, chưa quyết định model hoặc sửa ràng buộc hồ sơ hiện tại.

Ba thông tin phải tách:

- **Đơn vị tính giá:** giờ, ca, ngày, buổi, tháng, đầu việc/gói, sản phẩm hoặc chuyến.
- **Lịch thực hiện:** một lần, lặp theo tuần, theo đợt hoặc hoàn thành trước hạn.
- **Kỳ trả tiền:** sau mỗi lần, tuần, tháng hoặc theo mốc; có thể chưa chốt khi đăng.

Ví dụ tự dựng để giải thích: 60.000đ/giờ × ba giờ mỗi buổi, thứ Hai/Tư/Sáu, trả cuối tháng. Giá giờ không đổi thành giá tháng chỉ vì trả cuối tháng. Ví dụ không phải báo giá thị trường.

Nguồn nghiệp vụ nền: [Airtasker hướng dẫn mô tả việc, thời điểm, ngân sách và ảnh](https://support.airtasker.com/hc/en-au/articles/202427844-How-do-I-post-a-task); [Taskrabbit hướng dẫn chọn dịch vụ, lịch, người làm và vật dụng](https://support.taskrabbit.com/hc/en-us/articles/46260422073755-How-Do-I-Hire-a-Tasker). Các tài liệu hướng dẫn không được đếm vào 40 mẫu nội dung thực tế.

## 2. Quy ước trường

- **B:** đề xuất cần có trước khi công khai; lưu nháp không bắt hoàn tất.
- **ĐK:** chỉ cần khi nhánh việc, lịch hoặc giá tương ứng được chọn.
- **T:** tùy chọn; có gợi ý để người dùng biết khi nào hữu ích.
- **S:** hệ thống lấy từ tài khoản/ngữ cảnh hoặc tự sinh; không hỏi nhập lặp.

Một hàng là một mục nghiệp vụ, có thể gồm vài ô nhỏ. Không gọi bảng này là số ô thực tế của giao diện hoặc tên cột database. Điều kiện “chưa rõ” phải hiện đúng như vậy; không thay bằng số 0 hoặc giá trị tự đoán.

## 3. Kho Việc Làm — người cần thuê đăng nhu cầu

| Mã | Nhãn đề xuất | Nội dung / cách nhập | Mức | Vì sao cần; mẫu đối chứng |
| --- | --- | --- | --- | --- |
| K01 | **Bạn cần người làm việc gì?** | Tiêu đề ngắn, diễn đạt công việc và điểm chính. | B | Người xem hiểu tin trước khi đọc chi tiết; D01–D21. |
| K02 | **Loại công việc** | Chọn một nghề/dịch vụ chính; tìm kiếm trong danh mục. Chưa có thì nhập đề xuất để rà soát. | B | Không suy nghề chỉ từ tiêu đề; D04 thuộc dạy kỹ năng dù nằm trang nấu ăn. |
| K03 | **Việc cần làm cụ thể** | Ô mô tả: tác vụ, khối lượng/sản phẩm, phần gồm và không gồm; câu gợi ý đổi theo nghề. | B | Tên “giúp việc” hay “sửa nhà” quá rộng; D01, D10–D12. |
| K04 | **Cần bao nhiêu người?** | Số nguyên, mặc định 1 hiển thị rõ; cho chọn “cần đội/nhóm, trao đổi số người”. Tách người chủ đã có hỗ trợ. | B, có mặc định | Hai người hỗ trợ sẵn không có nghĩa cần thuê thêm hai; D11. |
| K05 | **Cách thực hiện** | Tại nơi làm; từ xa; mang đồ/thiết bị đi làm rồi giao lại; di chuyển theo hành trình; kết hợp. | B | Việc kỹ thuật không luôn làm tại nhà khách; D12, D14–D16. |
| K06 | **Làm một lần hay định kỳ?** | Một lần; lặp lại; theo đợt; giao sản phẩm trước hạn. | B | Lịch thực hiện khác loại giá; D02, D14, D17. |
| K07 | **Khi nào cần làm?** | Nhánh một lần: ngày/khung giờ hoặc “linh hoạt, trao đổi”. Nhánh định kỳ: ngày trong tuần/tần suất, giờ nếu cố định, ngày bắt đầu/kết thúc nếu có. Nhánh đầu ra: hạn bàn giao hoặc thời gian linh hoạt. | B; chi tiết ĐK | Không bắt việc giao trước hạn khai giờ vào ca; D03, D13–D19. |
| K08 | **Mỗi lần khoảng bao lâu?** | Giờ/phút hoặc ước lượng; có “chưa ước lượng”. Nếu giá theo ca/ngày/buổi, phải giải thích độ dài và phạm vi đơn vị đó. | ĐK | Giá một buổi không đủ nếu chưa biết buổi 50 hay 90 phút; S14–S15. |
| K09 | **Ngân sách / tiền công dự kiến** | Số tiền hoặc khoảng tiền, đơn vị tính, cho một người hay cả nhóm/gói, cố định hay còn thương lượng; chi tiết P01–P04. | B | Đáp ứng yêu cầu có tiền đi kèm; D15–D17, D20. |
| K10 | **Yêu cầu người nhận việc** | Tùy chọn: kinh nghiệm hoặc khả năng thật sự cần; thẻ kỹ năng gợi ý, không ép chọn đủ số lượng. Giấy tờ theo nghề mở riêng. | T / ĐK với nghề cần | Người mới vẫn có thể nhận việc phù hợp; D14 có yêu cầu chuyên môn cụ thể. |
| K11 | **Dụng cụ, vật tư và điều kiện làm việc** | Ai chuẩn bị gì; chủ cung cấp, người làm mang, mỗi bên một phần hoặc cần trao đổi. Ghi lối vào/cầu thang, phế thải nếu liên quan. | ĐK | Không dùng một nút “có dụng cụ” cho mọi vật tư; D06–D11. |
| K12 | **Ảnh / tài liệu mô tả việc** | Ảnh hiện trạng, ảnh mẫu đầu ra hoặc brief; không bắt buộc. Hướng dẫn che thông tin riêng tư. | T | Hỗ trợ hiểu phạm vi; không đồng nghĩa người đăng sở hữu mọi ảnh. |
| K13 | **Dự kiến thanh toán khi nào?** | Sau mỗi lần, tuần, tháng, theo mốc, chưa chốt; nội dung thỏa thuận, chưa xây luồng tiền. | T | Không nhập chung với đơn vị giá; X02. |
| K14 | **Khu vực / nơi thực hiện** | Với việc tại chỗ: khu vực hành chính bằng chữ; với hành trình: điểm đầu/cuối; với từ xa thuần túy không bắt địa chỉ nhà. Địa chỉ chi tiết và quyền chia sẻ là phần riêng. | ĐK | Biết nơi làm mà chưa cần map; D06, D14–D16. |
| K15 | **Người đăng, thời điểm và trạng thái tin** | Tài khoản/ngữ cảnh cá nhân hoặc tổ chức hợp lệ, thời điểm, nháp/đang tìm/đã đủ người/tạm dừng/đóng. | S; người dùng có thể cập nhật trạng thái | Không nhập lại họ tên/điện thoại trong mọi tin; không tự coi cá nhân là C2C đã được cấp quyền. |

**Cách gom trên màn hình:** (1) Việc cần làm K01–K04; (2) Nơi và cách làm K05/K14; (3) Lịch K06–K08; (4) Tiền công K09; (5) Yêu cầu/chuẩn bị K10–K11; (6) Ảnh và nội dung thêm K12–K13. K15 thuộc ngữ cảnh và quản lý tin. Các mục tùy chọn được mở khi cần.

Không bắt mọi người nhập công ty, cấp bậc, bằng cấp, CV, số năm từng kỹ năng hoặc lịch ca dạng bảng. Việc đơn giản có thể viết “lau nhà, vệ sinh bếp; không nấu ăn” ngay trong K03, không phải điền từng thao tác vào nhiều ô.

## 4. Tủ Hồ Sơ — người muốn nhận việc

Tên hiển thị, ảnh đại diện và thông tin liên hệ thuộc hồ sơ chung; có thể kế thừa từ tài khoản, kiểm tra lại và chọn phạm vi hiển thị. **Ảnh đại diện khác ảnh việc đã làm; hai loại đều không phải bằng chứng tự động về tay nghề.**

| Mã | Nhãn đề xuất | Nội dung / cách nhập | Mức | Căn cứ và giới hạn |
| --- | --- | --- | --- | --- |
| H01 | **Công việc tôi nhận** | Thêm một hoặc nhiều mục nhận việc; mỗi mục có nghề chính và tiêu đề dễ hiểu. | B: ít nhất một mục | Một người có thể nhận dọn nhà và nấu ăn với điều kiện khác nhau. |
| H02 | **Tôi làm được những gì?** | Mô tả ngắn theo từng mục; kỹ năng/thẻ nghề có thể gợi ý thêm, không bắt khai trùng. | B | Năng lực diễn đạt bằng việc cụ thể, không chỉ chức danh; S01–S17. |
| H03 | **Phạm vi nhận việc** | Loại tác vụ, đầu ra, loại khách/thiết bị/đối tượng phù hợp; phần không nhận nếu có. | B: cần mô tả phạm vi; phần loại trừ T | Có thể nằm cùng ô H02; S01, S05, S12–S15. |
| H04 | **Kinh nghiệm liên quan** | Đoạn ngắn, thời gian nếu người dùng biết; cho nói chưa từng nhận việc trả công hoặc đã làm cho gia đình. | T | Không ép kinh nghiệm tuyển dụng chính thức; S09, S16. |
| H05 | **Cách tôi nhận làm** | Tại chỗ, từ xa, mang về làm, di chuyển hoặc kết hợp; có thể chọn nhiều. | B | Phù hợp bản chất dịch vụ; chưa phải lịch đặt việc. |
| H06 | **Khu vực tôi nhận việc** | Danh sách khu vực bằng chữ, ghi chú nếu cần. Việc từ xa thuần túy không bắt địa chỉ nhà. | ĐK | Không công khai nơi ở để thay khu vực nhận việc. |
| H07 | **Thời gian có thể nhận** | Ngày/buổi rảnh, tần suất hay số giờ/tuần nếu muốn; ngày sớm nhất, ngày không nhận nếu có; cho “linh hoạt, cần hẹn trước”. | B: mô tả hoặc lựa chọn hợp lệ | Không buộc khai lịch từng nửa giờ; thiếu lịch không suy ra luôn rảnh; S01, S16, S18–S19. |
| H08 | **Tiền công tham khảo** | Số hoặc khoảng tiền theo mục nhận việc, đơn vị, giá cá nhân/nhóm/gói, có thể thương lượng; P01–P04. | B theo đề xuất nhánh này | Không ép đồng thời khai giá sàn riêng tư và giá mong muốn. |
| H09 | **Điều kiện tính thêm / nhận tối thiểu** | Số giờ/giá trị tối thiểu, phí vật tư/đi lại, người hỗ trợ; chỉ khai khoản áp dụng và điều kiện phát sinh. | ĐK nếu có áp dụng; không có thì bỏ qua | Không tự thêm phụ phí không khai; S03–S06. |
| H10 | **Dụng cụ / phương tiện / phần mềm tôi có** | Theo nghề; có, không có, có một phần, mô tả cụ thể. | ĐK / T | Chưa có xe tải vẫn có thể chỉ nhận bốc đồ; S07–S08. |
| H11 | **Chứng chỉ / giấy phép liên quan** | Tên loại, phạm vi, thời hạn nếu liên quan; tách tự khai với kiểm tra. Không mặc định phải công khai bản chụp giấy tờ. | ĐK với nghề có yêu cầu; ngoài ra T | Là phần bổ sung riêng, chưa kết luận quy trình hay điều kiện pháp lý. |
| H12 | **Việc tôi đã làm / sản phẩm minh họa** | Ảnh, link hoặc mô tả; chú thích việc gì, phần mình làm, thời gian gần đúng nếu có. | T | Cho bỏ qua hoàn toàn; không có ảnh vẫn đăng được hồ sơ. |
| H13 | **Tình trạng nhận việc** | Đang nhận; nhận từ ngày…; tạm ngừng. Cho chỉnh nhanh, không buộc xóa hồ sơ. | B, có lựa chọn mặc định để xác nhận | Có hồ sơ không đồng nghĩa còn rảnh; S14–S15. |
| H14 | **Thông tin nào được hiển thị?** | Xem trước nội dung công khai; ảnh/tài liệu và liên hệ có phạm vi riêng; kế thừa cơ chế quyền phù hợp khi triển khai. | ĐK trước công khai | Không đồng nhất đăng hồ sơ với công khai điện thoại/địa chỉ. |

**Cách gom trên màn hình:** (1) Tôi nhận làm H01–H03; (2) Cách làm/khu vực H05–H06; (3) Thời gian/trạng thái H07/H13; (4) Tiền công H08–H09; (5) Kinh nghiệm/điều kiện H04/H10/H11; (6) Minh họa H12 và xem trước quyền chia sẻ H14.

H02 và H03 có thể là một ô “Việc tôi nhận và giới hạn”. H05–H07 có thể dùng chung cho nhiều công việc trong hồ sơ; chỉ sửa riêng nơi khác nhau. Không tạo một form hoàn toàn lặp lại cho từng dịch vụ.

**Điều chỉnh so với bản nghiên cứu trước:** ở giai đoạn này không bắt khai “tối thiểu chấp nhận” cùng “mong muốn”; không bắt tọa độ/bán kính hoặc lịch chi tiết để hoàn thành hồ sơ. Trường H02/H03/H04 cũ trong báo cáo tổng quan được cụ thể hóa theo bảng mới này; đây là thay đổi khuyến nghị nghiên cứu, chưa phải thay đổi sản phẩm.

## 5. Giá: nhóm trường dùng nhất quán ở hai phía

| Mã | Trường | Đề xuất |
| --- | --- | --- |
| P01 | Số tiền và tiền tệ | Một số hoặc từ–đến; số dương, khoảng hợp lệ. Mặc định VND cho bối cảnh Việt Nam và hiển thị rõ; chưa đề xuất quy đổi ngoại tệ. |
| P02 | Đơn vị tính | Giờ; ca; ngày; buổi; tháng; đầu việc/gói; sản phẩm; chuyến ở nhánh đang nghiên cứu. Chỉ hiện đơn vị liên quan. |
| P03 | Đơn vị gồm những gì? | Ca/ngày/buổi: độ dài hoặc lịch cụ thể; đầu việc/gói/sản phẩm: đầu ra; tháng: lịch và khối lượng đã mô tả. Có mức tối thiểu thì ghi riêng. |
| P04 | Giá cho ai, gồm gì, có thương lượng? | Một người/cả nhóm/cả gói; tiền công thuần hay kèm vật tư/xe/phí khác; ngân sách dự kiến hay mức giới hạn. Khoản chưa rõ phải nói chưa rõ. |
| P05 | Lịch thanh toán | Tùy chọn, tách đơn giá; có thể chưa chốt. Chưa đề xuất thu, giữ hay chuyển tiền trên hệ thống. |

Đối với việc trả công công khai, đề xuất có **con số tham khảo có ý nghĩa cùng đơn vị** để đáp ứng ý định của chủ dự án. Không để “thỏa thuận” là thông tin giá duy nhất, không dùng giá 0/1 để lấp chỗ. Khi cần khảo sát, có thể nêu khoảng dự kiến và điều kiện; chưa có cơ sở cho con số thì lưu nháp để bổ sung. Đây là lựa chọn sản phẩm đề xuất, không phải khẳng định mọi nền tảng đều làm vậy.

Không cộng hoặc quy đổi máy móc giá giờ, gói và tháng. Một mức theo gói đi kèm thời lượng ước tính không trở thành giá giờ; một mức “từ…” không phải tổng trọn gói. Chỉ hiển thị tổng dự kiến khi biết đủ số lượng, đơn vị và các khoản liên quan; các khoản còn chưa biết phải hiện cạnh giá.

Nếu có nhiều ca khác giá, dùng **các dòng lựa chọn ca–giá**; không ép một khoảng thấp–cao che mất giá thuộc ca nào. Đối với người nhận nhiều nghề, mỗi mục nhận việc có thể có giá riêng hoặc các gói phạm vi rõ; không áp một giá cho cả hồ sơ.

Phát hiện cần giữ khi làm form sau này: D20 gắn nhầm giờ/ca; D05 ghi hai lượng sản phẩm; D13 số tiền đầu bài và mô tả khác cơ sở. Đây là phản ví dụ về chất lượng dữ liệu, không phải dữ liệu sạch để điền tự động.

## 6. Chi tiết theo nghề — mở vừa đủ

Các mục dưới đây là **gợi ý hỏi và dữ liệu có thể cần**, không phải tất cả đều là ô bắt buộc. Với việc đơn giản, ưu tiên câu gợi ý trong mô tả. Chỉ tách thành ô khi người dùng cần chọn rõ hoặc khi đơn vị giá sẽ mơ hồ nếu thiếu.

| Mã / nhóm | Kho Việc Làm cần làm rõ | Tủ Hồ Sơ nên giới thiệu | Độ chắc của căn cứ |
| --- | --- | --- | --- |
| C01 Dọn dẹp | Dọn thường/tổng vệ sinh/sau xây dựng; khu vực cần làm; quy mô gần đúng hoặc số phòng; dụng cụ ai có; việc không gồm. Không bắt đồng thời đủ diện tích và mọi số phòng. | Loại vệ sinh nhận; có nấu/giặt kèm không; dụng cụ; mức tối thiểu nếu có. | D01–D02, S01–S03; có hai phía. |
| C02 Nấu ăn / phụ bếp | Nấu hay phục vụ/rửa dọn; số người/bữa; nơi nấu; nguyên liệu ai mua, tiền nguyên liệu có gồm; hạn chế thực phẩm cần biết, trao đổi riêng chi tiết nhạy cảm. | Món/kiểu bữa nhận; có đi chợ/chuẩn bị/dọn không; nhận tại nhà khách hay nơi khác. | D03/D05, S10–S11; cần thêm mẫu bữa gia đình. |
| C03 Bốc / chuyển hàng | Chỉ nhân công hay kèm xe; loại/số lượng/kích thước hoặc trọng lượng ước lượng của đồ nặng; cầu thang/thang máy; điểm lấy/giao nếu có chuyển; ai hỗ trợ. | Một người/đội; có xe đẩy/xe chở không; loại đồ/phần việc nhận và giới hạn. | D06–D07/D20, S07–S09; có hai phía. |
| C04 Chăm cây / vườn | Tác vụ, loại cây/diện tích hoặc số chậu; dụng cụ/vật tư ai có; có gom và chở phế thải không. | Việc nhận, dụng cụ, phần không nhận, phí phế thải nếu có. | D08–D09, S04–S06; có hai phía. |
| C05 Nông nghiệp / chăn nuôi | Loại cây/con, số lượng/quy mô gần đúng; cho ăn/vệ sinh/cắt cỏ/thu hoạch…; thời gian, máy móc, ăn ở nếu cần. | Kinh nghiệm với loại cây/con và công việc; có ở lại/theo đợt không; biết dùng máy gì. | D21 chỉ là đối chứng lâu dài; **chưa đủ dữ liệu phía người làm để chốt**. |
| C06 Sửa / lắp / IT | Đồ hoặc thiết bị, tình trạng/lỗi, việc mong muốn; tại chỗ/mang đi; ai mua vật tư; có phí kiểm tra không; giới hạn thao tác; cách xác nhận xong việc. | Loại thiết bị/việc nhận; đồ nghề; có nhận chẩn đoán không, khoản kiểm tra nếu có. | D10–D12; thiếu hồ sơ thợ trong tập chính, cần bổ sung. |
| C07 Dạy học / kỹ năng | Môn/kỹ năng, cấp độ và mục tiêu, số học viên; trực tiếp/từ xa; thời lượng buổi và tần suất. Không cần tên/ngày sinh học viên trên tin công khai. | Môn/cấp độ nhận dạy, phương pháp, độ dài buổi, học phí, minh họa/chứng nhận tùy trường hợp. | D04/D13–D14, S14–S15; có hai phía. |
| C08 Sáng tạo / việc số / dịch thuật | Sản phẩm bàn giao, số lượng/định dạng/thời hạn; nguyên liệu khách cung cấp; số lượt sửa nếu áp dụng. Dịch: ngôn ngữ nguồn–đích, lĩnh vực, khối lượng và định dạng. | Dịch vụ cụ thể, chuyên ngành/công cụ, sản phẩm được phép giới thiệu, cách báo giá theo phạm vi. | D19, S16–S17; khác loại dịch vụ, còn thiếu tin thuê dịch thuật. |
| C09 Lái xe / chuyến | Chỉ tài xế hay xe+tài xế; đón/trả bằng chữ; ngày giờ; một chiều/khứ hồi; chờ/điểm dừng nếu có; số người/hành lý khi kèm xe; phí gì đã gồm. | Nhận lái xe khách hay có xe; loại xe/sức chở nếu kèm xe; lịch và vùng nhận bằng chữ; căn cứ báo giá. | D15–D16 chứng minh hai nhu cầu khác nhau; **chưa chốt bộ hồ sơ/điều kiện khai thác**. |
| C10 Chăm thú cưng | Loài/số lượng; ghé chăm hay ở lại/nhận giữ; ngày bắt đầu/kết thúc; số lượt, cho ăn/dắt đi; bên nào chuẩn bị đồ. | Loài và kiểu chăm nhận; kinh nghiệm, giới hạn số thú; giá theo lượt/ngày/đêm/toàn kỳ phải rõ. | D17–D18, S12–S13; có hai phía. |

Gom thành mười mẫu hỏi không có nghĩa mười mã nghề cố định. Một mẫu C08 dùng cho nhiều nghề nhưng đổi câu gợi ý. Không mở tất cả mẫu cho một người; không tự ép nghề ngoài danh mục vào nghề gần nhất. Nghiên cứu bổ sung khi xuất hiện nghề mới.

## 7. Ảnh và minh họa: tùy chọn đúng nghĩa

- Tủ Hồ Sơ: cho đăng ảnh/link việc từng làm hoặc sản phẩm; chú thích ngắn “đây là việc gì, mình làm phần nào”. Nếu có ảnh trước/sau thì có thể nhóm cùng một việc.
- Kho Việc Làm: ảnh hiện trạng hoặc mẫu đầu ra; chức năng khác ảnh chứng minh năng lực của người nhận.
- Không có ảnh vẫn tạo/công khai hồ sơ được nếu đủ mục cốt lõi; không yêu cầu người mới làm giả dự án cũ.
- Nhãn ban đầu là **người dùng cung cấp**. Đã nhận việc, có ảnh và đã được kiểm tra là các tình trạng khác nhau; chưa đề xuất điểm chất lượng hay số ảnh tối thiểu.
- Không yêu cầu công khai CCCD, bằng lái có số giấy tờ, người tham chiếu, tài khoản ngân hàng hoặc thông tin nhà khách trong ảnh.

[Fiverr phân biệt tác phẩm tự thêm và sản phẩm từ giao dịch](https://help.fiverr.com/hc/en-us/articles/4413134063633-Using-your-Fiverr-Portfolio); TA.CARE có thể tham khảo cách ghi nguồn, chưa có nghĩa đã tích hợp upload/xác minh. Việc xử lý file khi triển khai cần đặc tả riêng.

## 8. Rà lại các trường hợp dễ sai

Đây là rà soát thủ công ở mức nghiệp vụ, không phải test code hoặc đo thành công thực tế.

| Trường hợp | Kết quả kiểm tra bộ trường |
| --- | --- |
| Việc 2 giờ, một lần | Có ngày/khung giờ hoặc linh hoạt, giá giờ và thời lượng; không cần bảng lịch tuần. |
| Việc 3 buổi/tuần, trả cuối tháng | Lịch ở K06–K08; giá ở P01–P03; kỳ trả P05; không nhầm ba khái niệm. |
| Một buổi 50 phút | P03 giữ độ dài buổi; không gọi là một giờ. |
| Giá ngày nhưng chưa biết ngày mấy giờ | Hỏi rõ định nghĩa trước công khai mức giá có thể gây hiểu nhầm. |
| Cần hai người, giá cho cả đội | K04 tách số người; P04 ghi cả nhóm, không hiểu là mỗi người. |
| Có hai người chủ hỗ trợ sẵn | K03 ghi hỗ trợ; không cộng vào số người đang tìm ở K04. |
| Chỉ bốc đồ, không thuê xe | C03 không bắt có xe; H10 cho không có; vẫn mô tả được việc. |
| Thuê xe+tài xế / chỉ thuê tài xế | C09 tách hai nhánh; chỉ nhánh kèm xe hỏi sức chở/phương tiện. |
| Một hồ sơ nhận dọn và nấu với giá khác | H01 có nhiều mục, H08 giá từng mục; khu vực/lịch kế thừa khi giống. |
| Có dụng cụ nhưng không có hóa chất/vật tư | K11/H10 cho mỗi bên một phần; không suy đủ mọi thứ. |
| Cần khảo sát trước báo tổng | Giữ ngân sách/khoảng tham khảo có điều kiện; không hiện tổng chắc chắn hoặc điền giá tượng trưng. |
| Người mới, không có ảnh/kinh nghiệm trả công | H04/H12 tùy chọn; không cản công khai chỉ vì thiếu hai mục này. |
| Còn hồ sơ nhưng ngừng nhận | H13 tạm dừng; không phải xóa lịch sử hoặc sửa mọi mô tả. |
| Thiếu thời lượng hoặc thông tin chuyên môn | Giữ “chưa biết/cần trao đổi” nơi được phép; không tự suy từ nghề hoặc bằng cấp. |
| Tiêu đề, giá hoặc khối lượng tự mâu thuẫn | Yêu cầu người đăng làm rõ; không dùng thuật toán đoán đáp án đúng. |
| Tin trong danh mục cá nhân nhưng cần người lâu dài | Không tự xem là part-time; đọc lịch, phạm vi và ý định công việc, như D21. |

## 9. Những gì chưa chốt và bước kiểm chứng tiếp

**Có cơ sở để dùng làm bản nháp form:** nội dung công việc; lịch; nơi/cách làm; giá có đơn vị; vật tư; giới hạn nhận; nhiều mục nhận việc trên một hồ sơ; ảnh tùy chọn. Mẫu dọn dẹp, chuyển đồ, làm vườn, dạy học và chăm thú cho thấy thông tin tương ứng ở cả hai phía.

**Còn yếu:** hồ sơ lao động phổ thông nhận việc theo giờ tại Việt Nam, chăn nuôi/nghề nông ngắn hạn, hồ sơ thợ sửa chữa, người lái xe kèm phương tiện; tính dễ hiểu của từ “ca/ngày/buổi” đối với người dùng thực. Các nghề này vẫn có đề xuất trường ban đầu nhưng chưa đóng đặc tả. Không biến nghiên cứu nước ngoài thành bằng chứng về hành vi người dùng Việt Nam.

Trước khi chốt giao diện, nên cho hai phía thử nhập và đọc chéo các trường hợp thật được phép sử dụng: họ có diễn đạt đủ việc không, hiểu cùng đơn vị giá không, biết những gì cần hỏi thêm không, mục nào bị hỏi lặp/không biết trả lời. Lấy riêng các trường hợp chưa dùng khi soạn bảng này. Chưa tiến hành hoạt động đó trong phiên này.

Không thể từ 40 mẫu chọn thủ công suy ra xác suất khả thi trên 80%. Kết quả hiện tại là **bộ trường có truy vết và đã rà phản ví dụ**, có nêu rõ nhánh còn thiếu bằng chứng; chưa phải xác nhận toàn bộ hệ thống có thể triển khai hoàn toàn.

## 10. Quan hệ với tài liệu cũ

- [Phạm vi dự án](../project_scope.md) vẫn giữ hai phần: tuyển dụng và việc linh hoạt đang nghiên cứu.
- [Báo cáo tổng quan C2C](flexible_work_c2c_2026-10-19.md) giữ bối cảnh rộng. Riêng khuyến nghị form và mức chi tiết bắt buộc, ưu tiên bản nghiên cứu tập trung này.
- [Form tuyển dụng trước đó](recruitment_profile_forms_v2_2026-10-17.md) là phần khác, không tự đổi theo bảng K/H ở đây.
- Các mã K/H/P/C là mã phân tích trong tài liệu, **không phải field/model/XML ID mới**, không chứng minh tính năng tồn tại trong database hoặc code.
