# Phạm vi sản phẩm TA.CARE

> **Cập nhật 20/10/2026:** chủ dự án yêu cầu nhiều hồ sơ/một ứng viên và làm lại Tủ Hồ Sơ. Đã chuyển yêu cầu này thành [demo local](research/implementation_profile_refresh_2026-10-20.md); quyết định giữ một hồ sơ/user trong tài liệu cũ không còn áp dụng. Map và matching việc linh hoạt vẫn để sau.

Cập nhật theo yêu cầu chủ dự án ngày **19/10/2026**. Chủ dự án đã cho phép chuyển một phần nghiên cứu thành **demo local có code và dữ liệu giả lập**. Xem [bản triển khai demo ngày 19/10](research/implementation_flexible_demo_2026-10-19.md) để phân biệt phần đã chạy và phần tiếp tục nghiên cứu.

## Hai phần của dự án

1. **Tuyển dụng:** phần đã triển khai, tạm ổn theo xác nhận của chủ dự án. Giữ nghiệp vụ hiện tại làm đường cơ sở; việc nghiên cứu phần mở rộng không tự cho phép sửa luồng này.
2. **Tìm việc và tìm người làm việc linh hoạt:** phần mở rộng **đã có demo local cho biểu mẫu, danh sách và quản lý dữ liệu; nghiệp vụ kết nối tiếp tục nghiên cứu**, gồm doanh nghiệp–cá nhân và cá nhân–cá nhân. Người có nhu cầu đăng việc ở Kho Việc Làm; người nhận việc giới thiệu khả năng, điều kiện nhận việc ở Tủ Hồ Sơ; TA.CARE thực hiện matching và kết nối.

Trong ngôn ngữ sản phẩm dùng B2C/C2C theo yêu cầu chủ dự án. Chiều mua bán dịch vụ có thể được gọi khác trong tài liệu kinh doanh; không dùng nhãn B2C/C2C làm quy tắc quyền truy cập hay thuật toán matching.

## Yêu cầu đã được chủ dự án nêu

- Cá nhân có thể có nhu cầu thuê người làm một việc; cá nhân có thời gian rảnh có thể đăng năng lực để nhận việc, kể cả khi chưa có việc cố định.
- Hướng tới nhiều nghề và cách hợp tác, không chỉ tuyển nhân viên. Cần nghiên cứu đơn giá theo giờ, ngày, tháng, công việc, sản phẩm hoặc chuyến tùy tình huống.
- Các ví dụ dọn nhà, nấu ăn, bốc vác, chăm cây, công việc nông nghiệp và xe 7 chỗ là **đầu bài khảo sát**, chưa phải danh mục được duyệt vận hành. Các mức 30–40 nghìn/giờ, 1,2 triệu/chuyến, 1–2 triệu là ví dụ, không phải bảng giá.
- Matching phải phù hợp về nội dung việc, thời gian, giá và vị trí; việc tại chỗ không được gợi ý người ở quá xa khi họ không nhận khu vực đó.
- Nghiên cứu ảnh công việc/minh chứng **tùy chọn** trong hồ sơ để hỗ trợ tạo niềm tin.
- **Matching chính đặt ở TA.CARE**, đồng thời Kho Việc Làm cần có một số gợi ý phù hợp và hiển thị tiền công/ngân sách để thu hút người xem. Hai nơi phải dùng cùng nguồn dữ liệu và cùng quy tắc.
- Vị trí giai đoạn hiện tại dùng **địa chỉ/khu vực tĩnh do người dùng khai báo**, tách riêng cách thực hiện và nơi thực hiện. Kho ghi nơi làm; Tủ ghi khu vực nhận việc; việc theo hành trình có điểm đầu/cuối riêng. Bản đồ, bán kính và đánh giá khoảng cách để nghiên cứu sau.
- Giai đoạn hiện tại: **được phép sửa code, schema local và tạo dữ liệu demo**. Đã thêm lựa chọn “Tuyển dụng” / “Việc linh hoạt”, bộ lọc riêng, form nhu cầu và công việc nhận làm, ảnh tùy chọn. Tủ chỉ hiện dữ liệu của chủ tài khoản; admin thấy tất cả. Chưa triển khai maps/matching cho nhánh mới; chưa đưa lên production.

## Đề xuất nghiên cứu, chưa phải quyết định đã duyệt

- Tách người đăng nhu cầu, người nhận việc và người được tổ chức ủy quyền; một cá nhân có thể có cả nhu cầu thuê và năng lực nhận việc. Quyền mỗi hành động vẫn phụ thuộc chủ bản ghi và ngữ cảnh.
- Một hồ sơ cá nhân có thể giới thiệu nhiều dịch vụ, mỗi dịch vụ có giá, lịch và vùng nhận việc riêng; không tự tạo nhiều tài khoản hoặc nhiều hồ sơ trái ràng buộc hiện hành.
- Dùng phần chung và phần bổ sung theo loại việc: tại một địa điểm; theo ca; theo đầu ra; theo hành trình. Không dùng một form dài cho tất cả nghề.
- Lọc điều kiện bắt buộc trước, sau đó mới sắp xếp gợi ý. Thiếu dữ liệu là chưa biết; ảnh tự đăng không tự chứng minh tay nghề; không hiển thị phần trăm phù hợp ở Kho.
- Khởi đầu bằng kết nối có giải thích; đặt lịch, giữ chỗ, thanh toán, bảo hiểm và điều phối tức thời cần phạm vi và kiểm chứng riêng.
- Chưa mở vận tải hành khách trả tiền chỉ dựa vào việc có xe hoặc có giấy phép lái xe. Nhánh này cần hoàn tất nghiên cứu nghiệp vụ, giấy tờ, trách nhiệm và điều kiện vận hành.
- Các bán kính, số lượng gợi ý và ngưỡng kiểm nghiệm trong báo cáo là giả thuyết thử nghiệm, không phải chuẩn ngành hoặc cấu hình đã phê duyệt.

## Tài liệu nối tiếp

- [Triển khai demo việc linh hoạt ngày 19/10/2026](research/implementation_flexible_demo_2026-10-19.md): trạng thái hiện hành, dữ liệu demo, quyền truy cập và kiểm thử.

- [Bộ trường tối thiểu và sáu ví dụ điền thử](research/flexible_work_minimum_trial_2026-10-19.md): phần 8 cập nhật các trường cần tách để đối chiếu; 8/7 là nhóm trình bày, không phải số trường lưu.
- [Nghiên cứu trường Kho Việc Làm và Tủ Hồ Sơ cho việc linh hoạt](research/flexible_work_forms_2026-10-19.md): tài liệu nghiên cứu gốc; phần được chọn đưa vào demo ghi ở báo cáo triển khai, map/matching để sau.
- [40 mẫu tin/hồ sơ dùng kiểm tra trường và giới hạn bằng chứng](research/flexible_work_form_samples_2026-10-19.md).
- [Báo cáo nghiên cứu phần tìm việc linh hoạt, C2C và matching](research/flexible_work_c2c_2026-10-19.md).
- [Danh mục nguồn, mức truy cập và giới hạn bằng chứng](research/flexible_work_sources_2026-10-19.md).
- [Trạng thái triển khai gần nhất trước nghiên cứu](research/implementation_forms_homepages_2026-10-17.md).
- [Mapping và các xung đột schema hiện hành](database_mapping.md).

Nếu tiếp tục triển khai, đọc báo cáo và mapping trước khi chọn model, mở quyền cá nhân, tích hợp API hoặc thay đổi consent. Phạm vi mới không bãi bỏ các quy tắc bảo mật và triển khai trong `AGENTS.md`.
