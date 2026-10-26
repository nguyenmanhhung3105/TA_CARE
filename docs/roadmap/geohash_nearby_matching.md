# Ghép nối theo khu vực bằng geohash — ghi nhận 26/10/2026

**Trạng thái cập nhật cuối 26/10/2026: đã có bản thử local geohash/radius và map hai chiều, theo yêu cầu mới của chủ dự án.** Xem [triển khai, cách dùng và kiểm thử](../research/nearby_map_trial_2026-10-26.md). Chọn/lưu vị trí tại Kho/Tủ; TA.CARE chỉ hiển thị matching. Chưa có định vị liên tục, dispatch, ETA hoặc tự nhận ca theo người chấp nhận đầu tiên. Các hướng dưới đây là ghi chú khảo sát trước bản thử; không còn mô tả đầy đủ trạng thái hiện tại.

Hướng cần khảo sát khi bắt đầu:

- Người dùng chủ động chọn vị trí/vùng nhận làm và bán kính; thiết kế quyền đồng ý, thời hạn, thu hồi, độ chính xác công khai và phạm vi bên được xem. Giữ nguyên kiểm account, company, ownership, trạng thái, matching và purpose-specific consent; vị trí không tự cấp quyền xem hồ sơ/liên hệ.
- Geohash dùng để lấy ứng viên theo ô và các ô lân cận. Ranh giới ô có thể tách hai điểm gần nhau; cần lọc lại khoảng cách thực từ tọa độ, xử lý trùng và kiểm biên bán kính. Cùng tiền tố geohash không đồng nghĩa chắc chắn nằm trong bán kính. [Tài liệu geoqueries của Firebase](https://firebase.google.com/docs/firestore/solutions/geoqueries) là tham khảo nguyên lý, chưa chọn Firebase hoặc chuyển database.
- Sau bộ lọc khu vực, vẫn áp dụng thuật toán matching hiện hành và trả căn cứ, không thay nghề/lịch/giá bằng khoảng cách. Chưa suy ra đường đi, ETA, lịch trống hoặc nhận việc tự động.
- [mapcn-react-native](https://mapcn-rn.dev/) là tham khảo giao diện map, marker, clustering và vùng phục vụ, xây trên MapLibre/Mapbox cho Expo/React Native. Website hiện dùng Odoo/QWeb; cần chọn phương án web tương thích nếu làm web trước, hoặc đánh giá thư viện này cho app riêng. Chưa cài thư viện hay chọn nhà cung cấp/API key.
- Trước triển khai, chốt lưu vị trí nào, độ chính xác nào, khi nào cập nhật/xóa, ngân sách map/geocoding, giới hạn truy vấn và quy mô dữ liệu. Cần kiểm thử biên ô/bán kính, dữ liệu cũ/thiếu, revoke consent, truy cập chéo tổ chức và hiệu năng.

Giao diện hiện tại chỉ đối chiếu tỉnh/thành và dữ liệu tự khai; không quảng bá đã có tìm người gần đây hoặc định vị trực tiếp.
