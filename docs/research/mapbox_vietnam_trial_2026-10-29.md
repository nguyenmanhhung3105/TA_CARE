# Thử Mapbox và giới hạn vùng bản đồ — 29/10/2026

Owner yêu cầu thử công cụ thứ ba trong nghiên cứu Figma: Figma Make + Mapbox, sau đó giới hạn phạm vi bản đồ Việt Nam. Website thực tế là Odoo, nên tích hợp trực tiếp Mapbox GL JS, không thay application bằng một prototype Figma Make. Chưa kết nối tài khoản Figma/Mapbox, tạo token, phát sinh yêu cầu bản đồ có tính phí, push hoặc triển khai production.

## Cách bật thử

Sau khi cập nhật addon `tacare_website` phiên bản `19.0.17.2.0`, admin hệ thống mở **Cài đặt → Website → Bản đồ TA.CARE**. Chọn **Mapbox Standard**, nhập **public access token** của tài khoản Mapbox và lưu. Áp dụng cho homepage TA.CARE và picker trong Kho/Tủ. Quay về **OpenFreeMap (hiện tại)** để dùng nền cũ. Không thay database/filestore bằng full restore để triển khai thay đổi này.

Các system parameters là `tacare.map_provider` và `tacare.mapbox_public_token`. Chỉ admin hệ thống sửa qua settings. Không đặt token thật trong source/git hoặc gửi secret token `sk.` xuống frontend. `_care_map_config()` chỉ chiếu provider và token công khai `pk.` hợp lệ; thiếu/sai cấu hình dùng OpenFreeMap, không đưa secret/token hỏng xuống HTML. Public token được thiết kế để xuất hiện trong browser, cần quyền đọc tối thiểu và URL restrictions cho domain local/production sẽ dùng. Không dùng token ví dụ từ tài khoản của người khác.

Tạo token tại [Mapbox Console](https://console.mapbox.com/account/access-tokens/), tham khảo [Access tokens](https://docs.mapbox.com/help/dive-deeper/access-tokens/). Với local cần cho phép origin thực tế `http://tacare.localhost:8069`, `http://khovieclam.localhost:8069`, `http://tuhoso.localhost:8069`; production dùng các domain hiện tại. Quản lý hạn mức/chi phí ở tài khoản Mapbox. Không cần mua Figma chỉ để hiển thị Mapbox trên Odoo.

## Triển khai

- SDK chính thức được tải từ CDN, ghim GL JS `3.33.0`, chỉ sau lazy initializer hiện có. Khi chọn Mapbox không tải MapLibre/OpenFreeMap. Mặc định chưa có token vẫn dùng OpenFreeMap.
- `mapbox_layer.js` là cầu nối Leaflet nhỏ, chỉ dùng public API. Leaflet tiếp tục quản lý ghim, popup, circle, thao tác chọn điểm và keyboard; GL theo camera bằng `jumpTo`/`resize`. Zoom GL bằng zoom Leaflet trừ một để khớp tile size 512/256. Tắt zoom animation của Leaflet ở chế độ Mapbox để tránh hai renderer lệch khung.
- Nền `mapbox://styles/mapbox/standard`, ánh sáng ban ngày, tiếng Việt khi nguồn hỗ trợ, Mercator, camera phẳng, không world copies, không vật thể 3D; giữ logo/attribution Mapbox. Không quảng cáo đây là Apple Maps hoặc đã sao chép chính xác file Figma chưa truy cập được. Không ép palette Liberty lên các lớp Mapbox.
- Route GeoJSON vẫn do OSRM, Google Maps action vẫn dùng hai đầu đã chọn; route ở slot `middle` của Standard (trên đường, dưới chữ/POI). OpenFreeMap tiếp tục cách chèn dưới lớp chữ đầu tiên. Không tải lại OSRM khi pan/zoom. Không thay matching/consent/rank, coarse counterpart coordinates, source ownership hoặc việc lưu địa chỉ.
- Vùng dịch vụ hiện có `[8,102]–[24,110]` theo thứ tự lat/lon; Leaflet `maxBounds`, `maxBoundsViscosity:1`, min zoom 6; GL dùng cùng rectangle đổi sang lon/lat. Chặn ghim click/drag ngoài rectangle trước khi thay form. Các kiểm tra server hiện có vẫn giữ.

**Giới hạn phạm vi:** rectangle giới hạn camera quanh Việt Nam, không phải polygon biên giới quốc gia và không bao trọn mọi vùng biển/đảo. Mép màn hình có thể thấy một phần nước láng giềng; kiểm tọa độ hiện có cũng không chứng minh một điểm thuộc lãnh thổ Việt Nam. Photon chỉ nhận kết quả quốc gia VN như trước; chưa thêm bộ dữ liệu địa giới hoặc suy diễn chủ quyền. Nếu yêu cầu che sạch toàn bộ ngoài biên giới hoặc kiểm chọn điểm sát biên chính xác, cần nguồn polygon được chọn/kiểm chứng riêng. Không tuyên bố đã triển khai giới hạn polygon.

## Kiểm tra và trạng thái

Backup local trước upgrade: ignored `backups/mapbox_trial_20261029/`, dump PG custom format đã đọc danh mục bằng `pg_restore -l`, kèm filestore. Addon upgrade và restart riêng Odoo local thành công; không đổi account/password/job/profile/consent trong triển khai.

- Python/XML parse, JS syntax, scanner credential và whitespace: qua.
- `test_map_config.py`: chỉ xuất public token khi bật rõ ràng, không xuất secret/malformed token: qua.
- `mapbox_layer_check.cjs`: bridge thật với GL mô phỏng, đổi tọa độ/zoom, Việt Nam rectangle, cấu hình phẳng, attribution, move/resize/remove: qua. Đây **không** là test Mapbox live.
- `nearby_lazy_check.cjs`: canvas visible/idle/fallback/single-init: qua.
- `dev_map_settings_check.py`: Odoo ORM local, admin fields, public allowlist, secret-token rejection, view tồn tại; token/provider thử nghiệm rollback: qua.
- `map_provider_browser_check.cjs`: Chrome native login đúng website của tài khoản (business tại Kho, individual tại Tủ), chờ browser SSO sang TA.CARE; nền OpenFreeMap thật, desktop 1366/mobile 375, không tải SDK Mapbox khi chưa bật, matching list, giới hạn camera, không overflow/JS error; mở owner edit form Kho/Tủ và kiểm picker/địa chỉ canonical/CSRF, không submit; HTTP ba homepage có marker đúng: qua. Các lần thử ban đầu đếm CSRF toàn trang thay vì đúng work form và chưa chờ đúng luồng SSO gây lỗi kiểm thử; đã sửa test, không sửa authentication hay mật khẩu.
- `dev_nearby_check.py`: ORM rollback, matching hai chiều/winning offer, radius/coarse projection, consent theo purpose/organization/revoke/expiry, private/hidden/disabled, guest/foreign-owner denial và protected exact fields: qua.

**Chưa có token Mapbox được owner cung cấp:** chưa bật Mapbox trong DB local, chưa tải/đánh giá Standard thật, chưa kiểm cầu/tên đường trên Mapbox thật hoặc benchmark tải Mapbox so với OpenFreeMap. Không báo Mapbox đã hoạt động hoặc nhẹ hơn từ các test mô phỏng. Production chưa thay đổi; config provider trên server vẫn do admin/operator bật sau khi code được triển khai và token đã được giới hạn domain.

Nguồn kỹ thuật: [Mapbox GL JS](https://docs.mapbox.com/mapbox-gl-js/guides/get-started/), [Standard config](https://docs.mapbox.com/map-styles/reference/standard/), [slots và layer order](https://docs.mapbox.com/mapbox-gl-js/guides/styles/work-with-layers/), [restrict bounds](https://docs.mapbox.com/mapbox-gl-js/example/restrict-bounds/), [Figma connector](https://docs.mapbox.com/location-ai/mcp-servers/figma-mcp-server/).
