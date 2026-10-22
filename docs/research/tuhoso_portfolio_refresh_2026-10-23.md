# Thiết kế Tủ Hồ Sơ theo năng lực và việc nhận làm

Ngày 23/10/2026. Chủ dự án yêu cầu tìm thiết kế phù hợp và bắt mắt hơn cho Tủ Hồ Sơ. Yêu cầu mới cho phép đổi bố cục Tủ, thay quyết định giữ nguyên homepage Tủ trước đó. Kho và TA.CARE giữ nguyên. Tông xanh đậm/kem hiện tại được giữ.

## Tham chiếu và lựa chọn trước triển khai

- [Contra — Get discovered](https://contra.com/features/get-discovered): đã đọc trang và xem Chrome/screenshot. Cách ghép portfolio, dịch vụ và thông tin người nhận làm là tham chiếu cho thẻ hồ sơ có ảnh lớn, tiêu đề mạnh và CTA rõ. Không sử dụng ảnh người, đánh giá hoặc số liệu của Contra.
- [Contra — portfolio](https://contra.com/blog/creating-a-portfolio-for-your-freelance-career): đọc nội dung về đưa sản phẩm/dịch vụ vào cùng một nơi giới thiệu. Áp dụng cho ngôn ngữ bố cục, không thêm chức năng portfolio upload chưa có.
- [Airtasker — What should I put in my profile?](https://support.airtasker.com/hc/en-au/articles/360020588332-What-should-I-put-in-my-profile): đã đọc hướng dẫn chính thức về giới thiệu, kỹ năng và ảnh công việc. Trang marketing qua Chrome trả 403/Just a moment, không dùng làm bằng chứng thị giác hoặc vượt kiểm tra.
- [Taskrabbit — New to Tasking](https://www.taskrabbit.com/blog/new-to-tasking-we-have-all-the-info-you-need/): đọc phần mô tả từng kỹ năng, mức tiền và ảnh công việc. Tham khảo cách kể đầu việc cụ thể; không thêm booking, earned metrics hay xác minh giả.

Đánh giá thiết kế của người triển khai: chọn hướng **tủ trưng bày kỹ năng**, thay cho banner dịch vụ toàn chiều ngang và thẻ hồ sơ giống danh sách. Hero có nhịp chữ và ảnh lệch trục, gallery nghề thành một phần của câu chuyện; thư viện là các bìa hồ sơ có ảnh công việc, nội dung và thao tác rõ. Khách thấy cách giới thiệu năng lực; người đăng nhập thấy tủ của mình và phạm vi quản lý thật.

Skill ui-ux-pro-max được áp dụng. Kết quả design-system mặc định gợi ý brutalism/font khác không phù hợp nên không dùng. Tra cứu style có Editorial Grid phù hợp về lưới ảnh/bố cục, chỉ dùng nhịp ảnh và chữ; giữ Be Vietnam Pro, token xanh đậm, không dùng parallax/hiệu ứng VHS hoặc đổi palette. Các quyết định là đề xuất thiết kế, chưa phải kết quả nghiên cứu người dùng.

## Giới hạn

Giữ nguyên controller/domain/ACL/consent, explicit profile_id và multi-profile. Gallery Tủ vẫn mặc định dừng, dùng bộ ảnh cooking/garden/pets khác Kho và đứng trước thư viện. Ảnh thật đã có nguồn trong assets; luôn ghi rõ là ảnh minh họa. Không gắn ảnh minh họa thành chân dung chủ hồ sơ; không tạo đánh giá, huy hiệu, số liệu hay hồ sơ giả. Khối mẫu có nhãn Mẫu minh họa rõ. Chỉ dùng các bản ghi đã được controller cấp quyền; admin all và owner mine giữ nguyên. Không schema/data seed/commit/push/deploy.

Bằng chứng kiểm tra sẽ được bổ sung sau triển khai.


## Làm rõ cấu trúc trong lúc triển khai

Chủ dự án chỉ ra bản mở đầu hai cột và lưới thẻ còn giống các trang khác. Bản triển khai cuối thay thành **thư viện**: một mục lục kỹ năng dọc và mặt trưng bày ảnh nhiều ô cho khách; workspace có sidebar phạm vi hồ sơ, nội dung dạng ngăn hồ sơ ngang và carousel cảm hứng gọn nằm trước thư viện. Không dùng hero hai cột chữ/ảnh hoặc grid thẻ hồ sơ đồng đều. Trên mobile, sidebar thành thanh mục lục cuộn trong vùng riêng, ngăn hồ sơ xếp dọc. Mẫu giới thiệu nằm trong khối mở rộng, không tạo hồ sơ mẫu công khai.

## Quyết định cuối: tổng quan ở trang chủ, thư viện ở route riêng

Chủ dự án yêu cầu bỏ khối ảnh trượt trong “Hồ sơ của tôi”, giữ phần còn lại; trang chủ cần chung và tổng quan. Vì vậy homepage Tủ không dùng sidebar hoặc hồ sơ riêng, kể cả sau đăng nhập. `controllers/main.py` bỏ nhánh chuyển root sang `profile_library(_home=True)`; các route quản lý có role/owner/admin/consent giữ nguyên. Homepage dùng nội dung giới thiệu chức năng, cách chuẩn bị hồ sơ, nhóm nghề và quyền riêng tư; gallery chỉ là minh họa nghề trên homepage. `/tuhoso/profiles` giữ sidebar, ngăn hồ sơ ngang, tìm kiếm, scope và thao tác; bỏ carousel trong template workspace (cả mine/all).

Quyết định này thay các mô tả gallery đứng trước thư viện và homepage như thư viện trong phần lịch sử bên trên.

## Kiểm chứng bản cuối

- Backup trước đợt thay template: ignored `backups/tuhoso_portfolio_20261023/tacare_local.dump`, quyền thư mục 700/tệp 600, pg_restore list PASS. Không đổi schema.
- Update `tacare_website --stop-after-init` cho từng lần chỉnh template, exit 0; restart Odoo local. Python/XML parse và manifest asset cuối PASS. CSS chỉ scope `.tc-live.tc-profiles`.
- Chrome `/tmp/tuhoso-portfolio-browser-check.cjs` bản cuối PASS: guest + signed-in overview có nội dung chung, không có sidebar/thẻ dữ liệu riêng; homepage sau đăng nhập vẫn active Trang chủ. Thư viện có sidebar/ngăn ngang và **không có carousel**, tab Hồ sơ của tôi active.
- Hai hồ sơ hư cấu của cùng một account hiện đúng và tách biệt; tìm kiếm/không kết quả, admin all/mine, nút sửa/xóa theo quyền, từ chối scope all cho cá nhân (403) và URL hồ sơ người khác (404). Các đường dẫn sửa, chia sẻ và tạo giữ profile_id rõ, tên gợi ý từ danh mục được giữ. Không submit tạo/sửa/chia sẻ trong browser check.
- Gallery homepage mặc định dừng, nút/keyboard hoạt động, reduced motion tắt autoplay; focus hiển thị, ảnh đang hiển thị tải được, không lỗi JS/static asset. Các ảnh lazy trong slide ẩn không bị coi là ảnh lỗi; carousel được chuyển qua các slide trong phần kiểm tra tương tác.
- Viewport 320/375/768/1100/1440/1920 không tràn ngang. Cả ba marker homepage và màu Kho/TA.CARE giữ nguyên.
- Ảnh bản cuối trong `docs/screenshots/tuhoso-overview-20261023/`; đã xem homepage sau đăng nhập và thư viện không có banner ảnh. Các thư mục screenshot portfolio/library trước đó là bản trong quá trình điều chỉnh, không phải trạng thái cuối.
- Security scan 285 text files và `git diff --check` PASS. Chỉ local; không commit/push/deploy.

Đã dọn 2 account, 2 hồ sơ, 3 offer QA theo đúng ID và xóa tệp credentials private; không cấp consent hoặc đổi hồ sơ gốc.
