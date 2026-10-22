# Nghiên cứu trước khi thiết kế lại Kho Việc Làm và Tủ Hồ Sơ

Ngày: 22/10/2026. Yêu cầu: xây lại cấu trúc giao diện, tìm nhiều tham chiếu trong/ngoài nước, ảnh và icon đa nghề. Nghiên cứu và quyết định bên dưới được lập trước khi sửa template mới. Phạm vi nghiệp vụ thời vụ, quyền và dữ liệu giữ theo `docs/project_scope.md`.

## Nguồn đã xem

| Nguồn | Quan sát và phần có ích cho TA.CARE |
| --- | --- |
| [Refero Styles](https://styles.refero.design/) | Thư viện style/tokens; xem cả trang và bản mô tả Wise/Figma. Dùng để chọn nhịp chữ, mảng màu và khoảng trắng, không xem một DESIGN.md là quy định sản phẩm. |
| [bTaskee](https://www.btaskee.com/vi-VN/giup-viec-nha-theo-gio/) | Đã mở Chrome: ảnh người đang làm việc, màu ấm, dịch vụ và lợi ích cụ thể. Học cách đưa tình huống đời sống lên đầu; TA.CARE cần thêm nhiều nghề. |
| [Giúp Việc Nhà Việt](https://giupviecnhaviet.com/) | Xem trang và Chrome: danh mục dịch vụ gia đình/văn phòng và lối tư vấn. TA.CARE cần thao tác khám phá trực tiếp hơn, giảm mật độ hotline/văn bản quảng bá. |
| [Việc Làm Tốt](https://www.vieclamtot.com/viec-lam-giup-viec-tp-ho-chi-minh-sdjt35) | Đọc được danh mục, bộ lọc và nội dung giúp việc; trang vẫn định vị là tuyển dụng. Chỉ tham khảo cách tìm theo vùng/điều kiện, không dùng bố cục tin tuyển làm mẫu. |
| [JupViec](https://jupviec.vn/) | Đã mở Chrome: banner theo tình huống, danh mục giúp việc theo giờ/định kỳ/tổng vệ sinh. Học cách dùng ảnh có ngữ cảnh và một hành động chính. Không dùng lại claim đào tạo/bảo hành của họ. |
| [Green SM](https://www.greensm.com/vn-vi/green-subscription) | Đã mở Chrome: cách chia thành nhóm lợi ích, icon và banner rõ ngữ cảnh. Đây là trang hội viên, không phải mẫu luồng ghép việc; không thêm gói/khuyến mại/thanh toán giả. |
| [Grab Việt Nam](https://www.grab.com/vn/) | Đã mở Chrome: thông điệp đời sống, hệ dịch vụ và phía đối tác. Tham khảo tổ chức hệ sinh thái, không dùng hình tài xế/nhận diện Grab làm hình TA.CARE. |
| [Taskrabbit, Mỹ](https://www.taskrabbit.com/) | Đã mở Chrome: tìm theo đầu việc, dải icon, nhóm tác vụ và ảnh đang thực hiện. Đây là tham chiếu chính cho khám phá nghề, không phải tìm nhân viên. |
| [Airtasker, Úc](https://www.airtasker.com/au/) | Đọc trang bằng web tool: hai phía đăng đầu việc/nhận làm, danh mục nhiều nghề. Chrome gặp trang kiểm tra truy cập nên không khẳng định đã xem đủ giao diện thực. Học cấu trúc ý định từ nội dung đọc được. |
| [Urban Company](https://www.urbancompany.com/) | Đã mở Chrome: lựa chọn địa điểm, dịch vụ và phạm vi/giá. Học cách đưa điều kiện sử dụng vào ngữ cảnh. Không sao chép lời đảm bảo chất lượng của họ. |
| [Helpling, Đức](https://www.helpling.de/) | Đã mở Chrome: lối vào theo địa điểm và lịch, so sánh hồ sơ/giá; hai phía người thuê/người cung ứng. TA.CARE hiện chỉ đối chiếu và kết nối, chưa có booking như họ. |

Đã thử thêm [Thumbtack](https://www.thumbtack.com/) và [Yoojo](https://www.yoojo.fr/), nhưng tool gặp trang kiểm tra truy cập/lỗi tải. Không dùng làm bằng chứng thị giác, không vượt qua kiểm tra của các trang.

Ảnh chụp tham khảo để phân tích được giữ trong ignored `runtime/design-references-20261022/`, không đưa screenshot/ảnh thương hiệu đối thủ vào sản phẩm. Các nhận xét thiết kế là đánh giá của người triển khai từ phiên xem, không phải kết quả thử nghiệm người dùng.

## Ba hướng đã cân nhắc

1. Bảng tin/cổng nghề nghiệp: rất thuận cho tìm tin, nhưng nhấn vào hồ sơ, vị trí, danh sách và thu nhập khiến người dùng tiếp tục hiểu đây là tuyển dụng. Không chọn làm ngôn ngữ trang chủ.
2. Landing giúp việc chuyên biệt: thân thiện và rõ dịch vụ nhưng dễ làm TA.CARE bị hiểu chỉ có dọn nhà. Không chọn làm toàn bộ hệ thống.
3. **Khám phá dịch vụ đời thường đa nghề**: lấy đầu việc và tình huống làm trung tâm, kết hợp ảnh thực, icon, lựa chọn nghề và hai phía giao dịch. Chọn hướng này.

## Hướng được chọn và lý do

Tên mô tả nội bộ: **Everyday services**. Đây là chỉ dẫn thiết kế, không đổi tên sản phẩm.

- Kho mở bằng tiêu đề ở giữa, tìm theo đầu việc và dải ảnh nhiều nghề có nhịp cao/thấp. Người dùng nhận ra sửa chữa, nấu ăn, chăm cây, thiết kế và hỗ trợ kinh doanh ngay từ đầu.
- Danh mục dùng cùng bộ icon hai tông, mỗi nghề một nền màu nhạt và nhãn chữ. Icon không thay thế tên nghề; không dùng emoji trộn nhiều kiểu.
- Phần khám phá chia theo tình huống ở nhà, hỗ trợ cửa hàng và làm từ xa. Các nút đi vào bộ lọc hoặc form thật. Tin đang mở là nội dung tiếp theo, không chiếm vai trò hero.
- Tủ dùng phong cách bàn làm việc sáng, ảnh nghề khác Kho, nhấn mạnh người dùng biết làm gì và muốn nhận vào lúc nào. Sau đăng nhập là thư viện dịch vụ/hồ sơ riêng và công cụ chỉnh sửa, không là danh sách CV.
- Hai trang chung kiểu chữ, nút, bo góc, icon, thanh điều hướng và quy tắc ảnh; khác bố cục và mục đích. Giữ logo gốc và liên kết TA.CARE.
- Tham khảo Refero: [Wise](https://styles.refero.design/style/367c0c6e-73a7-441c-a8ff-91d139ac60dc) gợi nhịp chữ lớn, tương phản mảng màu; [Figma](https://styles.refero.design/style/5fd3b3b4-02ab-456a-87aa-e4395636b671) gợi cách để nội dung thị giác có khoảng thở. Màu, bố cục, copy và component cụ thể được tự xây cho TA.CARE.

Không dùng claim “đã xác minh”, sao đánh giá, số người nhận việc, khoảng cách GPS hoặc bảo hiểm khi hệ thống chưa có dữ liệu/cơ chế tương ứng. Chỉ hiển thị số liệu DB được phép đọc; ảnh stock ghi rõ minh họa, không gắn thành minh chứng hoặc danh tính hồ sơ.

## Hình ảnh và icon

Ảnh chụp mới lấy từ các trang Unsplash miễn phí cụ thể, không dùng Unsplash+, AI hoặc ảnh của đối thủ. Tự host WebP sau khi kiểm tra nội dung và nguồn. Danh mục nguồn ở `static/src/img/services/SOURCES.md`.

Icon dùng [Phosphor](https://phosphoricons.com/), tài nguyên SVG từ [repo chính thức](https://github.com/phosphor-icons/core) theo giấy phép MIT, giữ LICENSE. Cùng một icon nghề được dùng ở Kho và Tủ. Danh sách lựa chọn và token ở [design system](../design-system/everyday-services.md).

## Tiêu chí nghiệm thu

Trang chủ có cấu trúc khác bản trước; không còn hero hai cột văn bản–một ảnh và dãy ba thẻ tin làm trục chính. Ảnh đa nghề có con người/hoạt động, không họp văn phòng hoặc tập CV. Test 320/375/768/1440 px; keyboard/focus, ảnh lỗi, giảm chuyển động, bộ lọc, đường dẫn CTA, đăng nhập và luồng chủ hồ sơ/admin. Giữ ba marker HTTP và quyền sở hữu/consent. Không đổi schema, seed, mật khẩu, push hoặc deploy trong công việc thiết kế này.
