# Nghiên cứu mô hình ghép nối việc thời vụ đa ngành

Ngày đọc nguồn: 22/10/2026. Theo quyết định mới của chủ dự án, TA.CARE bỏ tuyển dụng và nghiên cứu nền tảng ghép người cần việc hoàn thành với người có thể làm. Phần “áp dụng cho TA.CARE” dưới đây là đề xuất thiết kế, không phải mô tả thuật toán riêng của các hãng hoặc tính năng đã tích hợp.

## 1. Những gì có thể học từ nguồn công khai

| Nền tảng / nguồn chính thức | Bằng chứng công khai | Áp dụng cho TA.CARE |
| --- | --- | --- |
| [GrabCar](https://www.grab.com/vn/transport/car/) | Giá chuyến được trình bày cho người đặt trước chuyến | Trình bày cách tính và phạm vi giá trước khi gửi yêu cầu; không lấy giá/km làm công thức chung |
| [GrabMaps – thông cáo chính thức](https://www.grab.com/sg/press/others/grabmaps-to-power-location-based-services-for-aws-customers-in-southeast-asia/) | Phân biệt dữ liệu bản đồ, tìm địa điểm, geocoding, routing/tracking/geofencing | Bản đồ nền không tự tạo ra ghép nối; phải có dữ liệu khu vực, đường đi, lịch và quyền vị trí |
| [Green SM – trung tâm giải đáp, mục đặt chuyến](https://www.greensm.com/vn-vi/helps) | Luồng chọn điểm đón/đến, dịch vụ, giá và phương thức trả; gửi yêu cầu, chờ tài xế nhận, xem thông tin/ETA, hoàn thành và đánh giá | Mẫu trạng thái hai phía, bản tóm tắt yêu cầu, chờ phản hồi và trạng thái rõ; đổi tài xế thành người nhận làm, điểm đến thành địa điểm/đầu ra theo nghề |
| [bTaskee – quy trình đặt giúp việc theo giờ](https://www.btaskee.com/vi-VN/blog/thue-nguoi-giup-viec-nha-theo-gio-can-luu-y-gi/) | Chọn địa chỉ/dịch vụ, nhập chi tiết và lịch, xem chi phí, xác nhận | Form theo nhóm dịch vụ, có thời lượng và chuẩn bị; không dùng CV cho việc theo ca/buổi |
| [Taskrabbit – How it works](https://www.taskrabbit.com/how-it-works) và [hướng dẫn thuê Tasker](https://support.taskrabbit.com/hc/en-us/articles/46260422073755-How-Do-I-Hire-a-Tasker) | Chọn đầu việc/vị trí, xem người nhận và đơn giá, lọc lịch/giá, trao đổi và xác nhận | Thích hợp với việc đa ngành cần khách chọn người, không nhất thiết điều phối tự động người gần nhất |
| [Taskrabbit – hướng dẫn thanh toán](https://support.taskrabbit.com/hc/en-gb/articles/46260427597595-How-do-I-pay-my-Tasker) | Hóa đơn có giờ làm và chi phí đã thỏa thuận; thanh toán qua nền tảng theo chính sách của họ | Tách báo giá, phát sinh, hóa đơn và thanh toán; cần sổ giao dịch/đối soát trước khi nhận tiền thật |

Không dùng mức giá, phí hoặc thời hạn khuyến mại trong bài cũ làm chính sách hiện hành cho TA.CARE. Không có nguồn công khai được đọc ở đây cho phép khẳng định đã biết thuật toán điều phối/ML nội bộ của Grab hoặc Green SM.

**Điểm khác biệt cần làm rõ với mentor:** “đa ngành” chưa phải lợi thế độc nhất, vì Taskrabbit và bTaskee cũng cung cấp nhiều loại dịch vụ. TA.CARE có thể kiểm chứng lợi thế ở việc bao phủ cả nhu cầu gia đình và hỗ trợ kinh doanh theo ca/đầu ra, một cá nhân đổi vai thuê–nhận làm, và điều kiện minh bạch theo từng nghề. Chưa có bằng chứng để tuyên bố TA.CARE đa dạng hơn mọi đối thủ.

## 2. Mô hình đề xuất

Mô hình là marketplace hai phía với yêu cầu công việc và đề xuất người nhận làm. Không phải job board để tuyển nhân viên. Thực thể nghiệp vụ cần phân biệt:

- Nhu cầu: phạm vi, nơi làm/cách làm, lịch, khối lượng/số người, ngân sách và dụng cụ.
- Khả năng cung ứng: đầu việc, kỹ năng tự khai, lịch rảnh, khu vực, đơn giá/đơn vị và giới hạn.
- Đề nghị/lời mời: thông tin đối chiếu, người gửi/nhận, phản hồi và quyền chia sẻ.
- Đơn công việc (giai đoạn sau): báo giá đã xác nhận, lịch giữ chỗ, trạng thái thực hiện và nghiệm thu.
- Giao dịch/đối soát (giai đoạn sau): thanh toán, phí, hoàn tiền, chi trả người nhận và xử lý tranh chấp.

Giữ ba không gian Kho–Tủ–TA.CARE như các điểm vào cùng hệ thống, một tài khoản và nguồn dữ liệu dùng chung. Chọn “cần người” hay “nhận việc” là ngữ cảnh giao dịch, không tạo một tài khoản mới cho mỗi vai.

## 3. Ghép nối

Đợt local dùng đối chiếu có giải thích trên dữ liệu được phép chia sẻ, không điều phối tức thời hoặc hứa có người gần đó. Người dùng chọn và gửi đề nghị; chưa có đặt lịch giữ chỗ.

MVP tiếp theo đề xuất: lọc nghề, trạng thái nhận việc và điều kiện xung đột rõ ràng trước; sau đó xếp gợi ý theo mức độ có căn cứ. Lịch thiếu, vị trí chưa chính xác và giá khác đơn vị phải hiển thị “cần xác nhận”, không chuyển thành điểm phần trăm đáng tin hoặc mặc định đạt. Các ràng buộc không thể thiếu cho đặt việc tự động phải được bổ sung và xác nhận trước khi chuyển sang đặt lịch.

Chưa tự gán một người cho hai đơn cùng thời gian. Muốn xử lý điều đó cần lịch khả dụng, thời gian di chuyển/buffer, giữ chỗ có thời hạn, giao dịch khóa tài nguyên và thao tác xác nhận đơn. Kết nối “đồng ý trao đổi” hiện tại không được đổi nhãn thành “đã đặt thành công”.

## 4. Bản đồ

Bốn lớp cần tách: địa chỉ/geocoding; bản đồ/vùng nhận; khoảng cách đường đi/ETA; vị trí trực tiếp trong khi thực hiện. Lọc cùng tỉnh/thành hiện tại không chứng minh người làm ở gần hoặc đến trong một số phút.

Đề xuất: người cần xác nhận điểm thực hiện; người nhận khai vùng phục vụ; hiển thị vùng xấp xỉ trước kết nối, chỉ chia sẻ địa chỉ cụ thể đúng mục đích. GPS phải được chủ động cho phép, có thời điểm cập nhật/độ chính xác, giới hạn lưu và thu hồi; không lấy tọa độ nhà làm vị trí trực tiếp. Dịch vụ từ xa không cần định vị.

Chưa chọn nhà cung cấp hoặc mở API trả phí. Cần thử geocoding Việt Nam, routing, quota/giá, điều khoản và quyền dữ liệu trước khi quyết định. UI local chỉ có sơ đồ minh họa được ghi rõ; không tile map, không GPS, không km/ETA giả.

## 5. Giá và thanh toán

Không dùng giá/km cho mọi nghề. Khung đề xuất:

- Theo giờ: đơn giá × giờ đã thống nhất, nêu tối thiểu và cách làm tròn.
- Theo ca/buổi/ngày: nêu số giờ và quy tắc vượt thời lượng.
- Trọn việc/sản phẩm: nêu đầu ra, số vòng sửa và điều kiện bàn giao.
- Tách tiền công, vật tư, đi lại, phí nền tảng và các khoản khác; chỉ tính phát sinh khi có sự đồng ý.

Tỷ lệ phí, người trả phí, thuế, hoàn tiền và quy tắc hủy còn cần xác nhận. Không lấy một tỷ lệ của hãng khác làm mặc định. Bộ tính local hiện tại chỉ là đơn giá/giờ × giờ + vật tư + đi lại do người dùng nhập, ghi rõ tính thử; chưa có phí nền tảng hoặc tiền được thu.

Thanh toán thật cần giai đoạn riêng: lựa chọn cổng, checkout, callback ký/xác thực và idempotency, trạng thái giao dịch, đối soát, hoàn tiền và chi trả. Không ghi nhận “đã trả” chỉ do trình duyệt trở về trang thành công; không hứa giữ tiền/escrow khi chưa có cơ chế tương ứng.

## 6. Lộ trình và giới hạn

| Giai đoạn | Kết quả |
| --- | --- |
| Đợt hiện tại, local | Bỏ tuyển dụng; backup và dọn dữ liệu; cá nhân/doanh nghiệp đăng nhu cầu; hồ sơ nhận việc; đối chiếu và kết nối C2C; giao diện đa ngành; sơ đồ/bộ tính minh họa |
| Giai đoạn đặt việc | Chốt trạng thái đơn, lịch khả dụng/giữ chỗ, vùng phục vụ/bản đồ thật, giá xác nhận, hủy/không đến và phản hồi |
| Giai đoạn thanh toán/vận hành | Cổng thanh toán, đối soát/hoàn tiền, chất lượng/xác minh, hỗ trợ, tranh chấp và các cơ chế điều phối đã kiểm chứng |

Không vận hành vận tải hành khách chỉ vì tham khảo luồng gọi xe. Mỗi nhóm nghề có yêu cầu năng lực, công cụ, phạm vi và vận hành riêng. Không sao chép thương hiệu/giao diện của các hãng hoặc dùng số lượng người dùng/đánh giá giả để thể hiện quy mô.
