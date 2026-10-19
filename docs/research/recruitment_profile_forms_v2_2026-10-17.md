# Form tuyển dụng và hồ sơ ứng viên: phương án v2

Ngày nghiên cứu: **17/10/2026**. Đây là đề xuất nghiệp vụ, chưa triển khai form, thuật toán, tải CV hoặc đọc CV tự động.

V2 điều chỉnh [bản nghiên cứu đầu](matching_fields_2026-10-17.md): giữ danh mục nhiều ngành để tìm kiếm và gợi ý, nhưng giảm công sức nhập. Cấu trúc lưu trữ chi tiết không đồng nghĩa phải đưa từng thuộc tính thành một ô trên form.

## 1. Quyết định từ góc nhìn người tuyển dụng và người đăng tin

Nếu được giao đăng nhiều vị trí, tôi cần nhận một bản mô tả đã thống nhất với người phụ trách tuyển dụng, dán các phần có sẵn, chọn vài thông tin để tìm ứng viên và kiểm tra trước khi đăng. Tôi không muốn phân loại từng câu thành một dòng điều kiện, nhập đơn vị đo, mức thành thạo và nguồn minh chứng cho mọi kỹ năng.

Ở vòng xem hồ sơ ban đầu, tôi cần biết:

1. Ứng viên muốn làm vị trí này hoặc một vị trí gần không?
2. Có chuyên môn chính để làm việc, hoặc phù hợp diện được đào tạo không?
3. Có đủ kinh nghiệm liên quan với mức tự chủ công việc cần không?
4. Có thể nhận địa điểm, cách làm và thời lượng công việc không?
5. Thu nhập hai bên có cơ sở để trao đổi không?
6. Nếu công việc có điều kiện riêng: có đáp ứng giấy phép, ngoại ngữ hoặc lịch bắt buộc không?

Tác phong, khả năng xử lý tình huống và chất lượng sản phẩm vẫn cần người tuyển đánh giá. Không biến mọi câu như “chịu áp lực tốt”, “chủ động” thành trường chọn hoặc tiêu chí máy tự kết luận.

**Đề xuất chốt để thử:** 16 mục đăng tin thông thường; 7 nhóm dữ liệu matching cơ bản; tối đa 6 nhóm bổ sung được mở theo nhu cầu thực tế. Phần nội dung giữ ba ô quen thuộc: **Mô tả công việc – Yêu cầu ứng viên – Quyền lợi**.

## 2. Form các website có nhiều trường không?

### 2.1. Cách khảo sát và cách đếm

Ưu tiên hướng dẫn của chính nền tảng về thao tác tạo tin, không lấy danh sách thông tin trên trang chi tiết công việc để suy ra người đăng phải nhập bao nhiêu ô. Không đăng nhập hoặc tạo tin thử trên tài khoản bên ngoài. Các nguồn dưới đây chứng minh được cách tổ chức nhập liệu; không cho phép xác định đầy đủ mọi biến thể giao diện sau đăng nhập.

Một **mục nghiệp vụ** có thể có nhiều **ô điều khiển**. Ví dụ “Mức lương” gồm lựa chọn thỏa thuận/khoảng, hai số tiền và cơ sở lương. Không so 16 mục đề xuất với 37 ô hiện tại rồi kết luận đã giảm theo một tỷ lệ chính xác.

| Nền tảng và nguồn chính thức | Nhập theo cách nào? | Có thể nói gì về số lượng? | Điều áp dụng |
| --- | --- | --- | --- |
| [TopCV – hướng dẫn đăng tin](https://tuyendung.topcv.vn/help/huong-dan-su-dung/dang-tin-tuyen-dung-mien-phi/) | Các mục chọn vị trí/kinh nghiệm/cấp bậc; nội dung mô tả, yêu cầu, quyền lợi; lương, địa điểm, thời gian; mục bổ sung. | Đếm được **22 dòng tên mục** trong các bảng hướng dẫn, gồm cả thông tin bổ sung, người nhận và dịch vụ. Không phải 22 ô bắt buộc. | Có thể giữ form vừa phải; không cần ép mọi yêu cầu thành dòng cấu trúc. |
| [Glints – hướng dẫn đăng tin tại Việt Nam](https://glints.com/vn/blog/dang-tin-tuyen-dung-tren-glints/) | Liệt kê 10 mục cơ bản; hướng dẫn sao chép JD có sẵn vào mô tả; hồ sơ công ty tạo riêng. | **10 mục cơ bản được bài viết liệt kê**, chưa gồm mọi mục công ty/thông báo. Đọc được bản chỉ mục; trang trực tiếp lỗi 500. | Cho nhập nội dung dài có sẵn và dùng mẫu để giảm công soạn. |
| [CareerLink – hướng dẫn 1-Click Job Post](https://www.careerlink.vn/cam-nang-tuyen-dung/bi-quyet-tuyen-dung/1-click-job-post-dang-tin-bang-ai) | Với doanh nghiệp đã được kích hoạt, nhận JD từ URL/file/văn bản, tạo nháp để kiểm tra và bổ sung. | Không đủ căn cứ đếm tổng số ô của form thủ công. | Bản JD nên được tái sử dụng; tự động hóa là tiện ích có thể làm sau. |
| [LinkedIn – đăng việc miễn phí](https://www.linkedin.com/help/linkedin/answer/a521598) | Bắt đầu từ chức danh, mô tả; thêm thiết lập nhận đơn và câu hỏi sàng lọc. Tài liệu nói mục kỹ năng có thể khác theo tài khoản/thử nghiệm. | Không công bố một tổng số ô cố định cho mọi người dùng. | Giữ mô tả chung; chỉ tách điều kiện có ý nghĩa sàng lọc. |
| [Indeed – hướng dẫn tạo tin](https://www.indeed.com/hire/resources/howtohub/how-to-post-a-job-on-indeed) | Nhập thông tin việc, địa điểm/cách làm, thu nhập; thêm mô tả và yêu cầu; có câu hỏi sàng lọc. | Hướng dẫn không đủ để xác nhận tổng số ô hoặc số bắt buộc mọi thị trường. | Thông tin chung có cấu trúc kết hợp nội dung tự do. |
| [JobsGO – form Việc Nhanh](https://employer.jobsgo.vn/viec-nhanh) | Chọn vị trí, sửa tiêu đề, số người, thời lượng, lương, địa điểm và mô tả mẫu; thêm câu hỏi có sẵn khi cần. | Đọc được nội dung form trong bản chỉ mục; chưa thao tác giao diện trực tiếp. Đây là luồng lao động phổ thông, không đại diện form chuyên môn của JobsGO. | Gợi ý theo nghề và chỉ hỏi thêm điều kiện thực sự quan trọng. |

**Kết luận trong phạm vi mẫu:** có nền tảng cung cấp khá nhiều mục, nên không cần rút TA.CARE xuống một form cực ngắn. Điểm cần sửa là các mục trùng ý, yêu cầu nhập lặp và mức chi tiết bắt buộc. Không có căn cứ để khẳng định mọi nền tảng chỉ có 10 ô, hoặc mọi nhà tuyển dụng đều chấp nhận form dài.

### 2.2. Đối chiếu với form của dự án

Đọc định nghĩa template [kvl_pages.xml](../../source/apps/tacare/addons/tacare_website/views/kvl_pages.xml) và xác nhận controller đang render `kvl_job_form`. Không chạy ứng dụng để đo số ô hiển thị theo từng tài khoản.

Trong template có **37 định nghĩa điều khiển không ẩn**, gồm 36 trong phần nội dung và 1 checkbox xác nhận đăng. Có ô chỉ xuất hiện theo quyền/số tổ chức; ba ô của dòng yêu cầu lặp theo số điều kiện; các ô đặc thù có thể được ẩn theo ngành. Đây không phải kết luận mọi nhà tuyển dụng đều thấy đúng 37 ô.

| Phần hiện tại | Số định nghĩa ô | Điểm tạo công nhập |
| --- | ---: | --- |
| Thông tin tuyển dụng | 8 | Tiêu đề, vị trí và ngành đều phải tự điền/chọn; tài khoản/tổ chức chỉ cần trong tình huống riêng. |
| Mô tả và nhiệm vụ | 2 | “Đầu ra mong đợi” có thể viết cùng mô tả. |
| Yêu cầu và ưu tiên | 6 | Hai ô kỹ năng cộng bảng nhóm–điều kiện–mức độ; dễ lặp ý và tăng thao tác. |
| Địa điểm và thời gian | 13 | Ngày/tuần, ca và lịch chi tiết rời nhau; bốn checkbox chuyên ngành được đặt cùng phần này. |
| Thu nhập và bật matching | 7 | Có thể nhóm lương và dùng giá trị mặc định có hiển thị, mở chi tiết khi cần. |
| Xác nhận đăng | 1 | Là thao tác công bố, không phải dữ liệu tuyển ứng viên. |

## 3. Mười sáu mục tuyển dụng đề xuất

**B** = cần trả lời trước khi đăng; **T** = tùy chọn; **M** = dữ liệu dùng cho matching cơ bản. Lưu nháp chỉ cần tiêu đề. Giá trị mặc định không được che giấu; người đăng phải thấy và sửa được.

| Mã | Tên mục hiển thị | Nhập/chọn chính xác gì? | Bắt buộc? | Matching ban đầu |
| --- | --- | --- | --- | --- |
| F01 | **Tiêu đề tin tuyển dụng** | Một ô văn bản. Ví dụ “Nhân viên vận hành TikTok Shop”. | B | Tìm kiếm/hiển thị; không kết luận năng lực từ title. |
| F02 | **Nghề/vị trí tuyển dụng** | Tìm và chọn một vị trí chính trong danh mục. Hệ thống biết nhóm nghề tương ứng; không yêu cầu chọn lại ngành ở ô khác. | B | M: tìm hồ sơ đúng nghề hoặc nghề gần được chấp nhận. |
| F03 | **Cấp bậc tuyển dụng** | Nhân viên/chuyên viên; chuyên viên cao cấp; trưởng nhóm; trưởng bộ phận; quản lý cấp cao; hoặc chưa xác định. | T | Hiển thị/lọc tìm kiếm; không tự loại ứng viên vì cấp bậc cũ khác tên. |
| F04 | **Số lượng cần tuyển** | Số nguyên từ 1; mặc định 1. | B, tự điền | Không xếp hạng ứng viên. |
| F05 | **Loại cơ hội** | Tuyển nhân sự; thực tập; cộng tác/dự án. Mặc định tuyển nhân sự. | B, có mặc định | M: đối chiếu loại cơ hội ứng viên nhận. |
| F06 | **Thời lượng làm việc** | Toàn thời gian; bán thời gian; theo khối lượng công việc. Không dùng nhãn “thực tập” thay cho thời lượng. | B | M: cùng F05 là một nhóm điều kiện nhận việc. |
| F07 | **Cách làm việc** | Tại nơi làm việc; từ xa; kết hợp. | B | M: so khả năng hiện diện. |
| F08 | **Địa điểm làm việc** | Tỉnh/thành hoặc vùng tuyển từ xa; địa chỉ làm việc nhập trong cùng mục. Nếu nhiều địa điểm, khai được chọn một hay phải di chuyển giữa các nơi. | B theo cách làm | M: vùng có thể nhận việc. Remote không mặc định mọi quốc gia. |
| F09 | **Mức lương/thu nhập** | Thỏa thuận/khoảng/từ/đến; số tiền nếu có; **lương cố định** hay **tổng thu nhập có phần biến đổi**. Hiển thị tiền tệ/kỳ trả và gross/net/chưa xác định, cho sửa khi cần. | B, thỏa thuận hợp lệ | M có điều kiện: chỉ so phần thu nhập cùng cơ sở; thỏa thuận là chưa có số. |
| F10 | **Kinh nghiệm tối thiểu với vị trí này** | Không yêu cầu; 6 tháng; 1, 2, 3, 5 năm; hoặc nhập số tháng khác. Không hỏi riêng số năm từng công cụ trên form thường. | B, không yêu cầu hợp lệ | M: so kinh nghiệm nghề liên quan được ứng viên xác nhận. |
| F11 | **Chuyên môn/kỹ năng chính** | Một ô tìm–chọn thẻ, gồm nghiệp vụ và công cụ. Gợi ý chọn khoảng 3–7 mục thực sự quan trọng; không bắt đủ số. Có thể đánh dấu riêng thẻ nào là bắt buộc. | B: chọn mục liên quan hoặc xác nhận được đào tạo từ đầu | M: các năng lực chính; thẻ không đánh dấu bắt buộc chỉ là căn cứ liên quan. |
| F12 | **Mô tả công việc** | Một ô nội dung dài: nhiệm vụ, trách nhiệm, đầu ra. Cho dán và giữ gạch đầu dòng. | B | Người tuyển đọc; chưa mặc định dùng toàn bộ để matching. |
| F13 | **Yêu cầu ứng viên** | Một ô nội dung dài: yêu cầu chi tiết, kinh nghiệm ngành, điều ưu tiên, kỹ năng giao tiếp… | B; có thể nêu nhận người mới/đào tạo | Người tuyển đọc. Điều kiện muốn máy đối chiếu phải nằm trong F10/F11 hoặc phần riêng được bật. |
| F14 | **Quyền lợi** | Một ô nội dung dài: thưởng, phụ cấp, bảo hiểm, đào tạo và quyền lợi khác. | T | Hiển thị; không tự biến thành tiêu chí năng lực. |
| F15 | **Thời gian làm việc** | Một ô mô tả: ví dụ “Thứ 2–6, 08:30–17:30” hoặc “xoay ca, trao đổi khi phỏng vấn”. Cần lịch bắt buộc thì mở cấu trúc U04 ngay trong mục này. | B; lịch linh hoạt là câu trả lời hợp lệ | M khi U04 được khai rõ; văn bản thường chỉ hiển thị. |
| F16 | **Hạn nhận hồ sơ** | Ngày kết thúc nhận hồ sơ; có thể gợi ý sẵn ngày để sửa/xác nhận. | B | Quyết định tin còn được gợi ý; không xếp hạng năng lực. |

**Không thêm các ô “số năm kỹ năng”, “mức công cụ”, “ngân sách từng làm”, “KPI”, “nguồn minh chứng” cho mọi tin.** Các thông tin này có thể xuất hiện trong F12/F13 hoặc được hỏi khi tuyển dụng sâu hơn.

Danh mục nghề làm công việc phân loại phía sau. Người đăng chỉ cần chọn “Backend Developer”, không phải nghĩ xem nghề nằm dưới nhóm nào rồi chọn lại ba lần. Nếu chưa có vị trí đúng, cho đề xuất tên để quản trị rà soát; không tự biến mọi tên nhập thành nghề chuẩn.

Ở F11, thẻ thông thường dùng tìm mức liên quan. Các thẻ được đánh dấu bắt buộc mặc định là cần đủ tất cả. Nếu có lựa chọn thay thế, người đăng có thể gom các thẻ đó thành một nhóm **Chấp nhận một trong các mục này**; ví dụ Java hoặc TypeScript. Đây là tùy chọn thao tác trên các thẻ đã chọn, không phải bảng điều kiện cần nhập cho từng kỹ năng. Một lựa chọn đáp ứng là đủ cho nhóm; thiếu dữ liệu chưa được hiểu là không biết kỹ năng đó.

### 3.1. Dự kiến bao nhiêu ô thực tế?

Với một tin thông thường, một địa điểm, lương theo khoảng VND/tháng: 16 mục có thể tương ứng khoảng **20 ô dữ liệu** — F08 có tỉnh/thành và địa chỉ; F09 có cách công bố, hai số tiền và cơ sở thu nhập; các mục còn lại một ô mỗi mục. Chưa tính tùy chọn mở rộng, danh sách địa điểm lặp và thao tác xác nhận công bố/quyền matching.

Đây là ước tính cho thiết kế, chưa phải số đo giao diện đã triển khai. Các giá trị như số người, loại cơ hội, tiền tệ và kỳ lương có thể tự điền có hiển thị. “Gross/net” ban đầu để chưa xác định nếu chưa được bên tuyển xác nhận, không tự mặc định rồi so sai.

## 4. Những mục gộp và những mục phải giữ riêng

| Thông tin | Cách xử lý v2 | Lý do |
| --- | --- | --- |
| Mô tả, trách nhiệm, nhiệm vụ, đầu ra mong đợi | Gộp vào **Mô tả công việc**. | Người đăng thường đã có cùng một đoạn JD. |
| Kỹ năng nghiệp vụ, phần mềm, công cụ, nền tảng | Gộp vào **Chuyên môn/kỹ năng chính** dưới dạng thẻ. Danh mục giữ loại của thẻ phía sau. | Người đăng không cần phân loại công cụ hay nghiệp vụ để thêm thẻ. |
| Kỹ năng quan trọng và ưu tiên | Một bộ thẻ; chỉ đánh dấu bắt buộc với mục quyết định. | Bỏ hai ô nhập danh sách và bảng tiêu chí trùng nhau. |
| Số ngày/tuần, ca, giờ và lịch chi tiết | Gộp thành **Thời gian làm việc**, có phần cấu trúc khi cần. | Tránh phải diễn đạt một lịch thành ba câu trả lời. |
| Lương thấp/cao, đơn vị, kỳ trả và cấu phần | Một mục **Mức lương/thu nhập**, giữ các giá trị con đủ nghĩa. | Gộp cách trình bày nhưng vẫn so sánh được khi dữ liệu đủ. |
| Phúc lợi, thưởng, phụ cấp, đào tạo | Gộp **Quyền lợi**; phần lương cần so nằm ở F09. | Không yêu cầu khai từng quyền lợi để matching. |
| Chi tiết ngành hàng, thị trường, khách hàng | Mặc định viết trong mô tả/yêu cầu. Nếu là năng lực quyết định, chọn thẻ chuyên môn tương ứng hoặc hỏi riêng khi tuyển. | Không bắt mọi tin khai đủ mọi bối cảnh. |
| Nghề, kinh nghiệm tối thiểu, kỹ năng chính | Giữ các mục riêng F02/F10/F11. | Ba căn cứ chuyên môn trọng tâm cần chuẩn hóa. |
| Địa điểm, thời lượng và cách làm việc | Giữ riêng trong cùng nhóm điều kiện. | Toàn thời gian không có nghĩa tại văn phòng; từ xa không có nghĩa giờ linh hoạt. |
| Giấy phép, ngoại ngữ, học vấn thực sự bắt buộc | Mở đúng mục riêng theo nhu cầu. | Không để điều kiện quyết định chỉ nằm trong một đoạn văn rồi kết luận hồ sơ đủ điều kiện. |

## 5. Chỉ mở thêm khi vị trí cần

Mặc định các nhóm sau thu gọn dưới lựa chọn **Bổ sung điều kiện cần đối chiếu**. Mở nhóm không đồng nghĩa tự coi là bắt buộc; người tuyển xác nhận mức cần thiết. Không dùng bảng trống “Nhóm – Điều kiện – Phép so sánh – Giá trị – Đơn vị” cho mọi yêu cầu.

| Mã | Mục bổ sung | Nhập rõ những gì? | Khi dùng cho matching |
| --- | --- | --- | --- |
| U01 | **Học vấn yêu cầu** | Bậc tối thiểu; chuyên ngành được chấp nhận nếu cần; có chấp nhận kinh nghiệm/năng lực tương đương không. | Khi người tuyển bật yêu cầu học vấn; không mặc định đại học cho mọi nghề. |
| U02 | **Ngoại ngữ yêu cầu** | Ngôn ngữ; việc cần dùng như đọc tài liệu/giao tiếp; mức yêu cầu hoặc chuẩn/điểm nếu có. | Chỉ ngôn ngữ được khai rõ. Không tự quy đổi “giao tiếp tốt” thành một điểm chứng chỉ. |
| U03 | **Giấy phép/chứng nhận bắt buộc** | Loại giấy tờ; phạm vi liên quan nếu cần; phải có lúc ứng tuyển hay trước ngày làm. | Các vị trí hành nghề/lái xe hoặc công việc có điều kiện tương ứng; kiểm chứng là trạng thái riêng. |
| U04 | **Lịch/ca bắt buộc** | Ngày hoặc kiểu ca cần nhận; khung giờ nếu cố định; ca xoay và yêu cầu trùng giờ khi cần. Ghi chú ngoại lệ. | Mở ngay trong F15, dùng dữ liệu cấu trúc thay cho nhập lại lịch bằng văn bản. |
| U05 | **Yêu cầu đi công tác/di chuyển** | Không có/đôi khi/thường xuyên; phạm vi nếu cần. | Chỉ khi khả năng di chuyển ảnh hưởng việc nhận công việc. |
| U06 | **Thời điểm bắt đầu cần đáp ứng** | Ngày cần bắt đầu; có linh hoạt/trao đổi được không. | Chỉ khi có giới hạn thời gian rõ. |

Portfolio không trở thành checkbox “có/không” để tự loại. Yêu cầu portfolio hoặc bài làm được viết rõ ở F13; hồ sơ có thể gắn dự án/đường dẫn, người tuyển xem chất lượng và phần đóng góp. Một URL công khai không chứng minh ứng viên đạt chuyên môn.

Mọi điều kiện bắt buộc trong văn bản nhưng chưa được chuẩn hóa phải được người tuyển đọc/xác nhận. Khi chưa có dữ liệu để máy kiểm tra, hệ thống chỉ nêu **chưa đối chiếu điều kiện này**, không nói ứng viên đã đáp ứng mọi yêu cầu.

## 6. Đã khảo sát gì về hồ sơ ứng viên?

Bản trước chủ yếu mở rộng danh mục dữ liệu từ tin tuyển dụng; chưa đối chiếu đủ cách tạo hồ sơ. Lần này khảo sát cấu trúc hồ sơ, mẫu CV và hướng dẫn quản lý mong muốn việc làm từ nguồn chính thức. Không truy cập CV hoặc hồ sơ thật của người tìm việc; không đồng nhất trang hướng dẫn với form đã thao tác sau đăng nhập.

| Nguồn | Cấu trúc hoặc cách làm quan sát được | Điều nên áp dụng |
| --- | --- | --- |
| [TopCV – mẫu CV và hướng dẫn các phần](https://www.topcv.vn/mau-cv) | Nội dung CV gồm phần giới thiệu, học vấn, kinh nghiệm, kỹ năng và chứng chỉ; có hướng dẫn theo nghề. | Dùng cấu trúc CV quen thuộc; không yêu cầu phân tích từng kỹ năng thành bảng phức tạp. |
| [ITviec – hướng dẫn CV theo góc nhìn người tuyển](https://itviec.com/blog/huong-dan-viet-mau-cv-an-tuong-cho-it/) | Nhấn mạnh vai trò gần đây, kỹ năng liên quan, tóm tắt và quá trình làm việc; dự án giúp giải thích phần việc. | Đọc kinh nghiệm có ngữ cảnh, không chỉ nhìn danh sách công cụ hoặc tổng số năm. Không áp chuẩn IT cho mọi ngành. |
| [LinkedIn – các phần hồ sơ](https://www.linkedin.com/help/linkedin/answer/a540837/adding-sections-to-your-profile) | Có phần cốt lõi, phần khuyến nghị và phần bổ sung; người dùng thêm dần học vấn, công việc, kỹ năng, dự án và chứng nhận. | Không bắt hoàn thiện mọi mục để tạo hồ sơ. |
| [LinkedIn – Open to Work](https://www.linkedin.com/help/linkedin/answer/a507508/let-recruiters-know-you-re-open-to-work?lang=en) | Mong muốn việc có chức danh, cách làm, địa điểm, thời điểm bắt đầu, loại việc và quyền hiển thị. | Mong muốn công việc là thông tin riêng với lịch sử làm việc. |
| [Indeed – hồ sơ và mong muốn tìm việc](https://www.indeed.com/help/job-seekers/articles/32603395892109-adding-or-editing-job-search-preferences?co=GB&hl=en) | Phân biệt mong muốn công việc với dữ liệu năng lực; có nghề, thời lượng/lịch, mức lương cố định tối thiểu, cách làm, kinh nghiệm, kỹ năng, học vấn và giấy tờ. | Matching hai chiều: làm được việc và nhận được điều kiện việc. |
| [Glints – tài liệu mô tả hồ sơ](https://assets.glints.com/docs/operation-regulation-vn.pdf) | Tài liệu năm 2021, mục Hồ sơ Glints, đề cập CV, lịch sử việc/học, liên hệ, kỳ vọng lương và vị trí ưa thích. | Tham khảo sự tách biệt hồ sơ nghề nghiệp với mong muốn; không dùng tài liệu cũ để khẳng định form hiện tại hoặc chính sách chia sẻ của TA.CARE. |

Các nguồn này ủng hộ một hồ sơ có thể bổ sung dần. Chúng không chứng minh mọi ứng viên sẵn sàng nhập bất kỳ số trường nào, cũng không chứng minh tải CV là đủ để hệ thống có dữ liệu chuẩn mà không cần xác nhận.

## 7. Chín mục hồ sơ đề xuất

Đây là các mục nội dung có thể mở/sửa dần, không phải chín trang bắt buộc. Tạo bản nháp hồ sơ chỉ cần tên hiển thị từ tài khoản. Khi muốn nhận gợi ý, hỏi trước **nghề muốn làm, điều kiện nhận việc, kinh nghiệm liên quan và kỹ năng chính**; có lựa chọn chưa cung cấp và chưa có kinh nghiệm.

| Mã | Tên mục | Các trường cụ thể | Mức cần thiết / matching |
| --- | --- | --- | --- |
| P01 | **Giới thiệu và liên hệ** | Tên hiển thị; tiêu đề nghề; giới thiệu ngắn. Email/số điện thoại lấy từ thông tin tài khoản khi có, quản lý riêng. | Tên để hiển thị; tóm tắt hỗ trợ người tuyển đọc. Liên hệ không dùng xếp hạng và không tự công khai. |
| P02 | **Công việc mong muốn** | Nghề/vị trí muốn làm; loại cơ hội; thời lượng chấp nhận; cách làm chấp nhận; tỉnh/thành/vùng nhận việc. Lương cố định tối thiểu chấp nhận và kỳ vọng có thể bổ sung; ngày sẵn sàng nhận việc khi cần. | Nguồn đối ứng cho F02, F05–F09 và U06. Có thể chọn nhiều lựa chọn chấp nhận, không ép một giá trị. |
| P03 | **Kinh nghiệm với nghề muốn làm** | Nghề đã chọn trong P02 và số tháng kinh nghiệm liên quan do ứng viên xác nhận; có lựa chọn chưa có/chưa cung cấp. Nếu chọn nhiều nghề, mỗi nghề có giá trị riêng khi bổ sung. | Đối ứng F10. Khởi đầu chỉ hỏi nghề chính; không lấy một con số tổng áp cho mọi nghề. |
| P04 | **Chuyên môn/kỹ năng chính** | Một ô chọn thẻ cho nghiệp vụ, công cụ, nền tảng. Gợi ý theo nghề, sửa được; không bắt điền số năm, điểm thành thạo và tài liệu cho mỗi thẻ. | Đối ứng F11; thông tin tự khai. Không có thẻ khác với xác nhận không biết. |
| P05 | **Kinh nghiệm làm việc** | Tên tổ chức; chức danh; tháng/năm bắt đầu và kết thúc hoặc đang làm; một ô mô tả công việc và kết quả. Mỗi công việc một mục. | Người tuyển kiểm tra bối cảnh; có thể dùng xác nhận lại P03. Không cộng tự động toàn bộ thời gian công việc vào một kỹ năng. |
| P06 | **Học vấn** | Trường/cơ sở; bậc đào tạo; chuyên ngành; trạng thái đang học/hoàn thành và thời gian phù hợp. Mỗi quá trình một mục. | Bổ sung khi có; matching khi U01 của tin được bật. |
| P07 | **Ngoại ngữ** | Ngôn ngữ; khả năng sử dụng cho đọc/viết/giao tiếp; chuẩn/điểm nếu có. | Bổ sung khi cần; matching khi U02 được bật. |
| P08 | **Giấy phép và chứng nhận** | Loại/tên giấy tờ; đơn vị cấp; ngày cấp/hết hạn nếu có; phạm vi khi liên quan. | Bổ sung theo nghề. Dùng cho U03; trạng thái kiểm chứng do quy trình có thẩm quyền quản lý. |
| P09 | **Dự án, sản phẩm và minh chứng** | Tên dự án/tác phẩm; vai trò, phần việc và kết quả trong một ô; đường dẫn hoặc tài liệu được phép chia sẻ khi chức năng có sẵn. | Tùy chọn; hữu ích cho thiết kế, IT, marketing, người mới. Người tuyển xem chất lượng, không tự cộng điểm vì có nhiều link. |

Khả năng nhận ca/đi công tác chỉ hỏi thêm khi người dùng muốn khai hoặc cơ hội đang xem cần U04/U05. Không bắt mọi người thiết lập lịch tuần chi tiết, bán kính đi lại và giờ từng ngày khi tạo hồ sơ.

### 7.1. Tránh yêu cầu ứng viên nhập lại cả CV

P03 là **xác nhận ngắn để đối chiếu kinh nghiệm nghề**, không phải yêu cầu tính số năm cho từng kỹ năng. Ví dụ nghề chính là “Nhân viên chứng từ”, ứng viên khai 18 tháng kinh nghiệm liên quan; các việc từng làm vẫn mô tả bình thường ở P05.

Nếu sau này có đọc CV tự động, dữ liệu đề xuất phải để ứng viên sửa/xác nhận, đánh dấu nguồn và phần chưa chắc. Nếu chưa có chức năng đó, vẫn dùng được form ngắn và các phần CV tự nhập; không coi việc tải file là đã có dữ liệu matching. Việc bổ sung upload/đọc CV là giai đoạn triển khai riêng, chưa có trong nghiên cứu này.

Một kinh nghiệm của ứng viên có thể được trình bày bằng đoạn văn; không yêu cầu họ gắn từng câu với từng dòng yêu cầu tuyển dụng. Những kết quả định lượng, KPI hay case chi tiết để trong mô tả/dự án khi có ích; không đặt thành điều kiện tạo hồ sơ cho mọi ngành.

### 7.2. Dữ liệu tự khai và dữ liệu kiểm chứng

P03/P04 là tự khai cho tới khi có căn cứ kiểm chứng. Nếu kinh nghiệm tự khai và lịch sử làm việc không khớp, báo cần làm rõ; không tự lấy giá trị cao hơn. Tháng làm việc chồng nhau không cộng hai lần; thời gian dùng một công cụ không suy ra từ toàn bộ thời gian làm công ty.

Người mới có thể khai kinh nghiệm bằng 0 nhưng có kỹ năng từ học tập/dự án. Tin nhận người mới hoặc đào tạo từ đầu vẫn có thể gợi ý. Thiếu lịch sử làm việc không phải lý do loại chung cho mọi cơ hội.

## 8. Matching chỉ dùng những gì phục vụ quyết định ban đầu

Quyền truy cập, consent đúng mục đích và hiệu lực tin/hồ sơ là **điều kiện được xử lý**, không phải điểm cộng. Kho không hiển thị điểm phần trăm. Kết quả là gợi ý để xem xét và các căn cứ cần kiểm tra, không phải quyết định tuyển dụng tự động.

### 8.1. Bảy nhóm dữ liệu cơ bản

| Nhóm | Bên tuyển | Bên ứng viên | Cách dùng |
| --- | --- | --- | --- |
| M01. Nghề/vị trí | F02 | P02 | Tìm đúng nghề hoặc nghề gần mà hai bên chấp nhận; không bắt chức danh trùng nguyên văn. |
| M02. Chuyên môn/kỹ năng chính | F11 | P04 và phần mô tả được phép dùng để làm rõ | Các thẻ chính tạo căn cứ liên quan. Chỉ tiêu chí được người tuyển đánh dấu bắt buộc mới xét như điều kiện bắt buộc. |
| M03. Kinh nghiệm liên quan | F10 | P03 | So số tháng cùng nghề/ngữ cảnh đã xác nhận. Chưa khai là chưa biết. Không dùng tổng năm đi làm cho mọi vị trí. |
| M04. Địa điểm nhận việc | F08 | P02 | So vùng làm việc/vùng tuyển từ xa và khả năng đến nơi. Địa chỉ công ty không cần trùng nơi ở. |
| M05. Loại cơ hội và thời lượng | F05/F06 | P02 | Ví dụ thực tập toàn thời gian khác việc nhân viên bán thời gian. |
| M06. Cách làm việc | F07 | P02 | Tại nơi làm việc/từ xa/kết hợp; nếu cần số ngày hiện diện cụ thể thì hỏi thêm. |
| M07. Thu nhập | F09 | P02 | Chỉ đối chiếu khi có số và cùng tiền tệ/kỳ/cơ sở. Lương ứng viên mong muốn là ưu tiên; mức tối thiểu xác nhận không thể nhận thấp hơn mới tạo ràng buộc. |

Không bắt tin/hồ sơ phải có đủ dữ liệu số cho cả bảy nhóm. Tin lương thỏa thuận vẫn được gợi ý, kèm “chưa đối chiếu thu nhập”. Trạng thái chưa đủ dữ liệu khác với có mâu thuẫn đã xác nhận.

Việc nêu bảy nhóm không có nghĩa chia đều trọng số. Trong góc nhìn người tuyển, nghề, chuyên môn và kinh nghiệm là căn cứ năng lực; các điều kiện còn lại giúp tránh giới thiệu việc mà ứng viên không nhận được. Chưa chốt công thức xếp hạng khi chưa thử với bộ cặp việc–hồ sơ.

### 8.2. Điều kiện riêng chỉ dùng khi tin bật

U01 ↔ P06; U02 ↔ P07; U03 ↔ P08. U04/U05 hỏi khả năng nhận lịch/di chuyển của ứng viên khi cần; U06 đối chiếu ngày sẵn sàng trong P02.

Ví dụ tin yêu cầu giấy phép đúng phạm vi thì đây là căn cứ cần xác nhận trước khi kết luận đủ điều kiện. Tin sales trong công ty y tế không tự có điều kiện giấy phép lâm sàng. Nội dung và quy tắc giấy phép theo nghề cần nguồn chuyên ngành có thẩm quyền khi chốt đặc tả; báo cáo không đặt chuẩn pháp lý từ blog tuyển dụng.

### 8.3. Những dữ liệu không dùng để xếp hạng ban đầu

- Tên, email, số điện thoại, ảnh và hình thức trình bày CV.
- Số lượng cần tuyển, người phụ trách, phúc lợi, số link hoặc số trang CV.
- Điểm tự chấm 5 sao, tuổi/giới hoặc các cụm chung như chăm chỉ/chịu áp lực.
- Toàn bộ đoạn mô tả/yêu cầu/quyền lợi chưa được chuẩn hóa và xác nhận.
- Mức lương hiện tại, tên trường/công ty cũ như một thước đo năng lực mặc định.

Nội dung văn bản vẫn hiển thị cho người có quyền đọc và hữu ích khi tuyển dụng. Chưa dùng tự động không có nghĩa được bỏ qua điều kiện thực tế viết trong JD; hệ thống phải thể hiện phạm vi đã đối chiếu.

## 9. Áp dụng cho bảy lĩnh vực mà không thêm bảy form dài

Các ví dụ sau là tin giả định để thử thiết kế. Số tháng, kỹ năng và điều kiện không phải chuẩn tuyển dụng áp đặt cho toàn ngành.

| Tin ví dụ | Một đoạn yêu cầu người tuyển có thể dán vào F13 | Thẻ chính nên xác nhận ở F11 | Mục riêng nên mở nếu đó là điều kiện thực tế |
| --- | --- | --- | --- |
| Backend Developer | “Có kinh nghiệm xây API bằng Python, làm việc với PostgreSQL; từng triển khai hệ thống thực tế là lợi thế.” | Python; PostgreSQL; phát triển API. | U02 nếu công việc bắt buộc dùng ngoại ngữ. |
| Vận hành sàn TMĐT | “Đã trực tiếp vận hành TikTok Shop, quản lý sản phẩm và chương trình bán hàng. Ưu tiên từng làm ngành gia dụng.” | TikTok Shop; vận hành gian hàng; quản lý sản phẩm. | U04 nếu bắt buộc nhận lịch livestream/ca cụ thể. |
| Performance Marketing | “Đã chạy Meta Ads, Google Ads và đọc báo cáo hiệu quả chiến dịch; gửi ví dụ công việc nếu có thể chia sẻ.” | Meta Ads; Google Ads; phân tích hiệu quả quảng cáo. | U02 chỉ khi ngoại ngữ là yêu cầu làm việc. |
| Nhân viên kinh doanh B2B | “Có kinh nghiệm tìm khách doanh nghiệp, tư vấn dịch vụ và đàm phán; ưu tiên đã bán giải pháp phần mềm.” | Bán hàng B2B; tìm khách; đàm phán. | U05 nếu thường xuyên đi gặp khách; không mở giấy phép chỉ vì thuộc sales. |
| Điều dưỡng | “Có đào tạo phù hợp, kinh nghiệm công việc tại khoa và đáp ứng hồ sơ chuyên môn theo nhiệm vụ được giao; nhận lịch trực đã thông báo.” | Nghiệp vụ điều dưỡng; các kỹ thuật đúng công việc. | U01/U03/U04 theo yêu cầu cụ thể; không mặc định giấy tờ cho mọi vai trò. |
| Nhân viên chứng từ hàng nhập | “Đã xử lý chứng từ hàng nhập, hiểu quy trình giao nhận và đọc được chứng từ tiếng Anh.” | Chứng từ hàng nhập; nghiệp vụ giao nhận. | U02 cho tiếng Anh; U01 nếu người tuyển đặt học vấn cụ thể. |
| Graphic Designer | “Dùng Photoshop/Illustrator để thiết kế ấn phẩm; có sản phẩm đã làm và mô tả phần đóng góp.” | Thiết kế đồ họa; Photoshop; Illustrator. | Portfolio ghi ở F13 và xem P09; không tự loại vì thiếu link công khai. |

Trong mọi ví dụ, người đăng dùng cùng form 16 mục. Mẫu nghề chỉ gợi ý thẻ/câu chữ; không tự thêm một danh sách điều kiện bắt buộc khi đổi ngành.

Ví dụ Graphic Designer: tiêu đề và phần mô tả có thể dán từ JD; người đăng chọn nghề, kinh nghiệm tối thiểu, vài thẻ chính, điều kiện làm việc và lương. Họ không cần khai số năm từng phần mềm, loại hình từng dự án hoặc mức độ từng thao tác để đăng tin. Khi xem hồ sơ, người tuyển vẫn đọc sản phẩm và trao đổi chuyên môn.

## 10. Luồng thao tác đề xuất cho người đăng nhiều tin

1. **Thông tin việc:** tiêu đề, vị trí, số người; cấp bậc nếu muốn. Thông tin tổ chức lấy từ tài khoản, chỉ chọn khi có nhiều tổ chức được phép quản lý.
2. **Nội dung:** dán mô tả, yêu cầu và quyền lợi vào ba ô. Nếu có mẫu tin cùng nghề của chính tổ chức, sao chép bản nháp và sửa.
3. **Điều kiện nhận việc:** loại cơ hội, thời lượng, cách làm, nơi làm, thời gian, lương và hạn nhận hồ sơ.
4. **Thông tin để gợi ý hồ sơ:** xác nhận nghề đã chọn, kinh nghiệm tối thiểu và thẻ chính; mở thêm ngoại ngữ/giấy phép/lịch khi cần. Không nhập lại thông tin đã có ở phần trước.
5. **Xem trước:** hiện tin công khai và bản tóm tắt những tiêu chí thực sự được dùng để đối chiếu. Người có quyền đăng kiểm tra nội dung và xác nhận công bố.

Bản nháp nên lưu được khi thiếu mục đăng, giữ nội dung khi lỗi, có thể xem trước. Người kỹ thuật được giao nhập tin không phải tự quyết định chuyên môn bắt buộc; bản tóm tắt giúp chuyển người phụ trách tuyển rà lại những lựa chọn đó.

Không bắt buộc phụ thuộc AI để có form gọn. Dán văn bản, gợi ý thẻ theo danh mục, dùng lại tổ chức và sao chép tin nháp đã giảm thao tác. Nhập một JD rồi tự tách/điền là tiện ích nghiên cứu sau; chưa coi có chức năng này trong dự án.

## 11. Tình huống cần đạt khi chuyển sang triển khai

Các dòng sau là tiêu chí đánh giá thiết kế, **chưa phải các bài kiểm thử ứng dụng đã chạy**.

| Tình huống | Kết quả mong muốn |
| --- | --- |
| Tin nhận người mới, được đào tạo | Đăng được khi kinh nghiệm là không yêu cầu; không ép nhập một kỹ năng bắt buộc giả. |
| Có JD dài | Dán được vào ba ô; không buộc tách từng gạch đầu dòng. |
| Chỉ một tổ chức | Không bắt chọn lại tên công ty hoặc người phụ trách mỗi lần. |
| Thẻ “Python” chỉ là chuyên môn liên quan | Không mặc định mọi người thiếu thẻ đều bị loại; chỉ có dấu bắt buộc mới xét điều kiện bắt buộc. |
| Tin cần Java hoặc TypeScript | Người đăng chọn hai thẻ và nhóm “Chấp nhận một trong các mục này”; hồ sơ có một lựa chọn thì đáp ứng nhóm. Nếu chưa cấu trúc được nhóm, không tự áp điều kiện phải biết cả hai. |
| Lương tổng kỳ vọng 25 triệu, lương cố định 10 triệu | Không đối chiếu 25 triệu với yêu cầu lương cố định tối thiểu 18 triệu. |
| Ứng viên có nhiều nghề quan tâm | Kinh nghiệm nghề A không tự áp sang nghề B. Chưa khai nghề B thì nêu chưa đủ thông tin. |
| Có điều kiện giấy phép nhưng hồ sơ chưa khai | Nêu cần bổ sung/xác nhận; không báo không có hoặc đã đủ điều kiện. |
| Lịch chỉ ghi “xoay ca” | Hiển thị để trao đổi, không tự kết luận trùng giờ. Nếu ca bắt buộc, cần U04 rõ nghĩa. |
| Thiếu portfolio công khai | Chưa có minh chứng để đánh giá; không kết luận thiếu năng lực. |
| Thu hồi quyền dùng hồ sơ/minh chứng | Ngừng dùng dữ liệu tương ứng; không lộ sự tồn tại hoặc tên minh chứng riêng tư qua giải thích. |

## 12. Phạm vi hoàn thành và giới hạn

Đã đọc nguồn công khai về nhập tin và hồ sơ, rà template hiện tại ở chế độ chỉ đọc, lập bộ trường v2 và phạm vi matching hẹp hơn. Chỉ thêm/cập nhật tài liệu nghiên cứu, không thay ứng dụng hoặc DB, không đăng tin bên ngoài.

Đã kiểm tra tài liệu cục bộ: đủ 16 mục F, 6 nhóm U, 9 mục P và 7 nhóm M; liên kết tệp cục bộ; cấu trúc bảng; khoảng trắng. Số ô giao diện v2 là ước tính để thử, chưa đo trên form chạy hoặc với người dùng. Không có kiểm thử Odoo/Python/XML/HTTP vì không có thay đổi ứng dụng.

Trước khi chốt triển khai, cho người đăng thử vài JD thuộc các lĩnh vực khác nhau và người tìm việc thử hoàn thiện hồ sơ. Cần ghi nhận thời gian, chỗ phải đọc lại, mục bỏ trống và yêu cầu bị hiểu sai. Khi chưa có phép thử này, không cam kết số phút nhập hoặc tỷ lệ giảm công sức.
