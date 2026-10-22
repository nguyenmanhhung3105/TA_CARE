# Phạm vi sản phẩm TA.CARE

**Quyết định chủ dự án ngày 22/10/2026, sau trao đổi với mentor:** TA.CARE là nền tảng ghép nối việc thời vụ đa ngành. Tuyển dụng nhân sự, CV ứng tuyển và vị trí nhân viên dài hạn đã được loại khỏi phạm vi. Quyết định này thay thế phân chia “tuyển dụng + việc linh hoạt” trong các tài liệu ngày 19–21/10; tài liệu cũ chỉ là lịch sử.

## Mục tiêu và ba không gian

Kết nối người cần hoàn thành một công việc với người có thể thực hiện theo giờ, ca, buổi hoặc đầu việc/sản phẩm. Cá nhân và doanh nghiệp đều có thể đăng nhu cầu. Người nhận việc giới thiệu khả năng, lịch, khu vực và đơn giá. Không dùng quan hệ nhà tuyển dụng–ứng viên làm mô hình trung tâm.

| Không gian | Vai trò |
| --- | --- |
| Kho Việc Làm | Đăng, khám phá, lọc và quản lý nhu cầu thời vụ |
| Tủ Hồ Sơ | Quản lý hồ sơ nhận việc và nhiều mục công việc nhận làm |
| TA.CARE | Đối chiếu điều kiện, lời mời/đề nghị và kết nối hai phía |

Một tài khoản cá nhân có thể vừa cần thuê vừa nhận việc. Cá nhân được dùng cả Kho, Tủ và TA.CARE. Doanh nghiệp dùng Kho + TA.CARE để đăng nhu cầu/tìm người; việc tổ chức cung ứng dịch vụ bằng hồ sơ doanh nghiệp chưa được mở rộng trong đợt này. Admin dùng cả ba trong phạm vi công ty được phép. Giữ tên kỹ thuật role `candidate` cho tương thích nhưng nhãn sản phẩm là “Cá nhân”, không còn “Ứng viên”.

Tài khoản, model và XML ID hiện có được giữ. SSO mở các site được phép tương ứng; không tạo ba database hay ba bộ tài khoản. Mọi ghi dữ liệu vẫn kiểm vai trò, owner/công ty, trường cho phép và trạng thái. Mọi cập nhật hồ sơ/mục nhận làm dùng profile_id cụ thể.

## Luồng hiện tại

1. Người cần làm việc khai đầu việc, nghề, khu vực/cách làm, lịch, số người và ngân sách.
2. Người nhận làm khai dịch vụ/công việc có thể làm, lịch, khu vực, tiền công và điều kiện.
3. TA.CARE đối chiếu thông tin được đồng ý chia sẻ: cùng nghề, cách thực hiện, tỉnh/thành, lịch và cách tính giá. Xung đột đã khai được loại; dữ liệu thiếu là chưa biết, không phải điểm phần trăm hoặc xác nhận đủ điều kiện.
4. Hai bên gửi và phản hồi đề nghị/lời mời. Chấp nhận kết nối mới là đồng ý trao đổi, chưa phải lịch đặt việc hay một giao dịch đã thanh toán.
5. Chủ hồ sơ quyết định cấp/thu hồi liên hệ cho đúng bên thuê sau khi chấp nhận. Quyền này không tự cấp bởi admin hoặc chuyển đổi phạm vi.

Nhóm nghề hiện có trải rộng việc nhà, chăm cây/nông nghiệp, kho/bốc xếp, sửa chữa/lắp ráp, dạy kèm, dịch vụ số và chăm thú cưng. Không tự mở vận tải hành khách do lấy cảm hứng từ nền tảng gọi xe.

## Triển khai local trong đợt này

- Sao lưu DB và filestore private trước xóa; đã bỏ 5 tin tuyển dụng và 3 hồ sơ tuyển dụng không có ràng buộc, giữ toàn bộ tài khoản, 15 việc thời vụ, 3 hồ sơ nhận việc, 12 mục nhận làm.
- Bỏ lựa chọn/tab/form tuyển dụng khỏi ba website. Các đường dẫn tuyển dụng cũ và việc tạo/đổi loại dữ liệu tuyển dụng được chặn ở server; gói import cũ có nội dung tuyển dụng cũng bị từ chối.
- Cá nhân được đăng và quản lý nhu cầu thời vụ; luồng C2C kiểm đúng người gửi, người nhận, chủ tin và quyền liên hệ theo bên thuê cụ thể.
- Giao diện hai ý định “Tôi cần người làm” / “Tôi muốn nhận việc”, danh mục đa ngành, ảnh công việc, lịch và tiền công. Kho và Tủ có bộ carousel khác nhau; TA.CARE dùng bố cục mạng kết nối, không có carousel.
- Bản đồ ở trang cách hoạt động là sơ đồ minh họa, không phải GPS/vị trí người dùng hoặc khoảng cách thật. Bộ tính chi phí chỉ tính thử số người dùng nhập, không tạo đơn hay thu tiền.

## Phần nghiên cứu để phát triển tiếp

Xem [nghiên cứu Grab, Green SM, bTaskee, Taskrabbit](research/seasonal_platform_benchmark_2026-10-22.md). Học mô hình yêu cầu–người nhận–xác nhận–thực hiện–hoàn thành; điều chỉnh theo đa ngành, không sao chép công thức tính tiền theo km hoặc giả định thuật toán nội bộ của các hãng.

- Bản đồ thật: nhà cung cấp bản đồ/geocoding/routing, quyền vị trí chủ động, vùng nhận việc, bảo vệ địa chỉ và thời hạn lưu vị trí.
- Đặt lịch: đơn công việc, giữ chỗ, tránh nhận trùng lịch, sửa lịch, hủy/không đến và kiểm tra hoàn thành.
- Thanh toán: báo giá/version/phát sinh được chấp thuận, cổng thanh toán, đối soát, hoàn tiền và tranh chấp. Chưa chốt tỷ lệ phí nền tảng hoặc nhà cung cấp; không tích hợp thanh toán thật ở đợt này.
- Xác minh, đánh giá sau công việc, hỗ trợ và quản lý rủi ro theo từng nhóm nghề.

Không báo cáo GPS trực tiếp, tối ưu điều phối như Grab, thanh toán, OCR/CV upload, worker/outbox hoặc snapshot matching là đã vận hành nếu chưa có tích hợp và kiểm thử tương ứng. Dữ liệu mẫu là hư cấu, không phải quy mô người dùng thực tế. Đợt này là local; chưa push/deploy hoặc chuyển dữ liệu production.
