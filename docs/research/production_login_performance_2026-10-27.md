# Đo chậm sau đăng nhập trên production — 27/10/2026

Owner phản ánh web chậm/lag ngay sau khi đăng nhập sau full restore. Chưa có SSH trực tiếp của agent; đã yêu cầu operator cung cấp uptime/nproc/free/vmstat/systemd/process metrics, tài khoản/site bị ảnh hưởng và phần cấu hình gzip Nginx. Chưa có các kết quả đó ở thời điểm ghi chép. Không suy ra thiếu RAM hoặc cần tăng server từ cảm giác tải chậm.

## Quan sát thực tế

Đo tuần tự bằng Chrome headless, reduced motion, một context mới và một tài khoản cá nhân có nhiều hồ sơ; thêm luồng popup login TA.CARE với tài khoản business. Không chạy load test đồng thời. Credentials đọc riêng tư, không ghi vào diagnostic report; chỉ đăng nhập/đọc HTTP và thử logout, không đổi dữ liệu nghiệp vụ. Evidence riêng tư ignored `runtime/releases/login-diagnostics/performance.json` và `business-performance.json`.

| Trường hợp | TTFB HTML | DOMContentLoaded | Ghi chú |
| --- | ---: | ---: | --- |
| TA.CARE guest, lần đầu | 299 ms | 5.533 ms | Một CSS mất 4.897 ms; chưa kết luận là lỗi lặp lại |
| Tủ guest | 212 ms | 613 ms | Không có map |
| Kho guest | 653 ms | 1.091 ms | Có public matching preview |
| TA.CARE individual, cache ấm | 187 ms | 236 ms | Map ready, không long task >50ms trong cửa sổ đo |
| Tủ individual, cache ấm | 199 ms | 244 ms | Không có map |
| Kho individual, cache ấm | 223 ms | 240 ms | Không có map |
| TA.CARE business, tắt cache HTTP browser | 1.635 ms | 1.919 ms | Map ready |
| TA.CARE business, cache ấm | 740 ms | 783 ms | Map ready |

Map API individual 650 ms, business 516 ms, session-status 85 ms; HTTP 200. Login popup business authenticated và SSO hoàn tất. Các trường `elapsed` trong JSON có cộng thời gian chờ cố ý 2,2–3,5 giây của test: **không dùng** chúng làm latency đăng nhập/trang. TTFB/DOMContentLoaded lấy từ Navigation Timing. Test này chưa tái hiện lag trên thiết bị/trình duyệt của owner hoặc account admin chưa xác định.

## Điểm đã xác nhận: tài nguyên văn bản chưa nén

Browser cache-disabled nhận:

- `web.assets_frontend_lazy.min.js`: 2.185.445 bytes encoded = decoded.
- `web.assets_frontend.min.css`: 1.149.049 bytes encoded = decoded.
- Vendored `maplibre-gl.js`: 937.395 bytes encoded = decoded.
- Logo TA.CARE PNG 470.814 bytes; các TTF khoảng 137–140 KB mỗi weight.

Direct HTTPS GET với `Accept-Encoding: gzip, br` xác nhận cả ba CSS/JS HTTP 200, không có `Content-Encoding`/`Vary`, body nguyên kích thước trên. Chỉ ba file text đã khoảng 4,27 MB, chưa ảnh/font. Đây là vấn đề delivery cần xử lý tại Nginx sau khi đọc cấu hình live; không tự phát minh include paths hoặc bật directives trùng scope. Cache ấm giảm transfer của asset về 0 nhưng không giải quyết lần đầu hoặc origin khác. Chưa sửa Nginx/reload/restart server.

## Hướng kiểm tra còn lại

- So RAM/swap/load/process CPU thực tế, số core và restart trước khi điều chỉnh workers/cron hoặc đề nghị nâng máy.
- Xác định tài khoản/site và thao tác gây lag cụ thể. TA.CARE authenticated thực hiện `_home_suggestions`; admin còn `_home_admin_matches`. Có repeated consent queries trong `_current_consent` và lặp matching theo nhiều hồ sơ; có thể tối ưu sau khi đo số query/cost, nhưng không đổi eligibility, consent/organization scope hoặc dùng cache cá nhân chia sẻ giữa request/user.
- Bản đồ hiện lazy init bằng IntersectionObserver rootMargin 200px. Map/route không phải nguyên nhân được chứng minh chỉ vì nằm trên trang. Session status poll 3 giây; chưa có bằng chứng reload loop trong lần đo.
- Không xóa profiles/jobs/consents hoặc rollback data để xử lý hiệu năng chưa xác định. Full restore cũ đã committed và có thể có dữ liệu mới.

## Số liệu operator và bản tối ưu nén được chuẩn bị

Operator cung cấp live: 8 cores, load 0.16/0.11/0.09; RAM total 3.8 GiB, used 1.5 GiB, available 2.3 GiB; swap used 13 MiB nhưng vmstat si/so=0, CPU idle 87–90%, iowait=0 trong mẫu. Không thấy resource exhaustion tại thời điểm đo; không tự tăng workers, nâng máy hoặc xoá dữ liệu từ số liệu này.

`nginx -T` qua syntax, `/etc/nginx/nginx.conf` có `gzip on`, còn `gzip_vary`, `gzip_comp_level 6` và dòng MIME types đều commented. Theo [Nginx gzip module](https://nginx.org/en/docs/http/ngx_http_gzip_module.html), mặc định chỉ thêm HTML khi chưa khai báo types; gzip_types bổ sung MIME và gzip_vary thêm Accept-Encoding. Các site nằm trong sites-enabled; không phát minh include mới/đổi cấu hình TLS/proxy.

`tools/deploy/server/enable_static_gzip.py` preview mặc định, `--apply` thực hiện thay đúng các comment đã được operator cung cấp trong main config: vary on, level 4, min 1024 và types CSS/JS/SVG/TTF/OTF. Không bổ sung JSON/private-response cache policy. Giữ gzip on hiện có, server/location/proxy/TLS, route, cookies và Odoo config. Root/shared deploy lock, kiểm regular config ownership/path và pending deploy; backup vào root-owned `/var/backups/tacare-deploy/nginx-static-gzip-*`. Test config cũ, test candidate `nginx -t -c` trước atomic replacement, test live config rồi graceful `systemctl reload nginx`; kiểm active. Lỗi sau replacement khôi phục config gốc và reload. Không restart Odoo/DB. Từ chối comment khác/dòng active xung đột; cài lặp cùng bản không thay file.

Tải riêng script qua `upload_full_snapshot.py --static-gzip --upload`, server filename `~/tacare-enable-static-gzip.py`; sau preview có thể `sudo python3 ... --apply`. Không tải lại snapshot 60 MiB.

4 offline tests qua, gồm atomic file/mode và các nhánh preview/success/candidate-test-failure/live-test-failure/reload-failure có thật filesystem và simulated privileged commands. Test actual Nginx container đã chuẩn bị nhưng **chưa chạy được** do Docker daemon local đang tắt (socket không tồn tại); không báo test đó passed. Server script tự test candidate bằng Nginx đang có trước reload; chưa có xác nhận operator apply hoặc wire compression sau thay đổi. Các native authenticated timings chưa tái hiện severe lag; vẫn cần account/site/device cụ thể nếu còn chậm sau tối ưu delivery.

## Gzip đã áp dụng; tối ưu map tiếp theo

Operator xác nhận `STATIC GZIP APPLIED`, candidate/live nginx config tests qua, graceful reload thành công; backup `/var/backups/tacare-deploy/nginx-static-gzip-20261026T213038010265Z`. Direct HTTPS GET sau đó xác nhận gzip + Vary Accept-Encoding, decompress đúng kích thước gốc: CSS 1.149.049 → 179.688 bytes (−84,4%), frontend JS 2.185.445 → 549.537 (−74,9%), MapLibre 937.395 → 260.594 (−72,2%). Tổng ba file 4.271.889 → 989.819 bytes (−76,8%). Không đổi database/restart Odoo. Một lần đo business sau đó vẫn TTFB 1,17–1,97s, vì nén không thay chi phí tính matching phía server; không báo gzip đã giải quyết toàn bộ phản ánh.

Owner khoanh vùng chỉ TA.CARE chậm và nghi map. Controlled Chrome A/B (cùng business, 1366×768, DPR 2, cache disabled, reduced motion, đo tuần tự) chỉ suppress map IntersectionObserver trong control, không sửa production: không map ScriptDuration ~0,055–0,057s / TaskDuration ~0,162–0,166s / heap ~6 MB; có map ScriptDuration ~0,219–0,234s / TaskDuration ~0,435–0,457s / heap ~16–27 MB, thêm 16 resource requests và một API. TTFB vẫn khoảng 0,94–1,51s ở cả hai vì HTML matching chạy trước JS. Đây là bằng chứng map tăng chi phí client, không chứng minh nó là nguyên nhân duy nhất hoặc severe lag đã được tái hiện trên thiết bị owner.

App patch `nearby.js` chỉ đổi initializer của homepage map: observe chính `[data-nearby-canvas]`, rootMargin 0 và visible threshold 10%, sau đó yield first paint bằng requestIdleCallback (fallback timer). Guard chống schedule lặp. Bản cũ observe cả section với margin 200px nên có thể tải WebGL dưới hero hoặc khi chỉ thấy cuối section. Giữ nguyên location pickers, data endpoints, matching/rank/owner/consent, marker grouping, palette, routing và camera persistence. Version bump 19.0.17.1.0 để triển khai addon/assets.

Kiểm tra:

- `tests/nearby_lazy_check.cjs`: actual initializer trong VM, không offscreen work, canvas/threshold, idle/fallback và single schedule, thiếu canvas không lỗi: PASS.
- `tests/nearby_lazy_browser_check.cjs`: native Chrome desktop 1366 và mobile 375, DPR2, native business login/SSO; thay đúng component nearby **chỉ trong bundle của test browser**. Trước cuộn: không tải map library hoặc map API. Khi cuộn canvas: nền thật + gợi ý có quyền xuất hiện, một library load/một API, scroll away/back giữ cùng map, không overflow/JS error. Mobile dùng fallback khi idle API không có: PASS. Không deploy/source mutation server hoặc business writes.
- Node syntax và kiểm manifest/scanner/whitespace chạy local. Không chạy Odoo addon upgrade local vì Docker daemon tắt. Bản JS đang chờ code-only GitHub Actions, chưa được xác nhận triển khai production. Không chạy lại full snapshot restore vì có thể ghi đè dữ liệu mới sau cutover.
