/* Lazy basemaps: existing OpenFreeMap, or configured Mapbox Standard. */
(() => {
    'use strict';
    const ASSET = '/tacare_website/static/';
    const DEFAULT = [10.7769, 106.7009];
    // Application service rectangle, not a political/national boundary polygon.
    const VIETNAM_BOUNDS = [[8, 102], [24, 110]];
    const MAPBOX_CDN = 'https://api.mapbox.com/mapbox-gl-js/v3.33.0/';
    // Area reference points, not an address geocoder or administrative catalog.
    const AREAS = [
        ['TP. Hồ Chí Minh · trung tâm', 10.7769, 106.7009], ['Bình Thạnh', 10.8106, 106.7091],
        ['Thủ Đức', 10.8494, 106.7537], ['Tân Bình', 10.8015, 106.6526],
        ['Gò Vấp', 10.8387, 106.6653], ['Bình Tân', 10.7653, 106.6034],
        ['Bình Chánh', 10.6868, 106.5939], ['Nhà Bè', 10.6953, 106.7375],
        ['Hà Nội · trung tâm', 21.0285, 105.8542], ['Cầu Giấy', 21.0362, 105.7906],
        ['Hà Đông', 20.9714, 105.7788], ['Long Biên', 21.0485, 105.8896],
        ['Đà Nẵng · trung tâm', 16.0544, 108.2022], ['Hải Phòng · trung tâm', 20.8449, 106.6881],
        ['Cần Thơ · trung tâm', 10.0452, 105.7469], ['Huế · trung tâm', 16.4637, 107.5909],
        ['Nha Trang', 12.2388, 109.1967], ['Đà Lạt', 11.9404, 108.4583],
        ['Biên Hòa', 10.9574, 106.8427], ['Vũng Tàu', 10.346, 107.0843],
    ];
    const libraryPromises = new Map();
    function leaflet(provider) {
        if (!libraryPromises.has(provider)) {
            const mapbox = provider === 'mapbox';
            for (const href of [ASSET + 'lib/leaflet/leaflet.css', mapbox ? MAPBOX_CDN + 'mapbox-gl.css' : ASSET + 'lib/maplibre/maplibre-gl.css']) {
                const css = document.createElement('link'); css.rel = 'stylesheet'; css.href = href; document.head.append(css);
            }
            const script = src => new Promise((resolve, reject) => {
                const n = document.createElement('script'); n.src = src;
                const timer = setTimeout(() => { n.remove(); reject(new Error('Thư viện bản đồ phản hồi quá lâu.')); }, 15000);
                n.onload = () => { clearTimeout(timer); resolve(); };
                n.onerror = () => { clearTimeout(timer); n.remove(); reject(new Error('Không tải được thư viện bản đồ.')); }; document.head.append(n);
            });
            libraryPromises.set(provider, (window.L ? Promise.resolve() : script(ASSET + 'lib/leaflet/leaflet.js'))
                .then(() => script(mapbox ? MAPBOX_CDN + 'mapbox-gl.js' : ASSET + 'lib/maplibre/maplibre-gl.js'))
                .then(() => mapbox ? undefined : script(ASSET + 'lib/maplibre/leaflet-maplibre-gl.js')).then(() => window.L)
                .catch(error => { libraryPromises.delete(provider); throw error; }));
        }
        return libraryPromises.get(provider);
    }
    function node(tag, text, className) {
        const n = document.createElement(tag);
        if (text !== undefined) n.textContent = text;
        if (className) n.className = className;
        return n;
    }
    async function makeMap(canvas, status, center = DEFAULT) {
        const config = canvas.closest('[data-map-provider]')?.dataset || {};
        const provider = config.mapProvider === 'mapbox' && /^pk\.[A-Za-z0-9_.-]{20,2000}$/.test(config.mapToken || '') ? 'mapbox' : 'openfreemap';
        const L = await leaflet(provider);
        const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
        const map = L.map(canvas, {scrollWheelZoom: false, minZoom: 6, maxZoom: 18,
            maxBounds: VIETNAM_BOUNDS, maxBoundsViscosity: 1, attributionControl: provider !== 'mapbox',
            fadeAnimation: !reduced, zoomAnimation: provider !== 'mapbox' && !reduced,
            markerZoomAnimation: !reduced}).setView(center, 12);
        try {
            const tiles = provider === 'mapbox' ? window.careMapboxLayer(L, {token: config.mapToken}).addTo(map) :
                L.maplibreGL({style: 'https://tiles.openfreemap.org/styles/liberty',
                    attribution: '<a href="https://openfreemap.org/" target="_blank" rel="noopener">OpenFreeMap</a> · © <a href="https://www.openmaptiles.org/" target="_blank" rel="noopener">OpenMapTiles</a> · © <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a>'}).addTo(map);
            const gl = provider === 'mapbox' ? tiles.gl : tiles.getMaplibreMap();
            map.careGL = gl;
            canvas.dataset.mapProvider = provider;
            let baseError = false;
            gl.on('style.load', () => {
                baseError = false;
                if (provider === 'openfreemap') window.careMapServices.palette(gl);
                canvas.dataset.mapPalette = provider === 'mapbox' ? 'mapbox-standard' : 'soft';
            });
            gl.on('error', () => { baseError = true; status.textContent = 'Không tải được một phần nền bản đồ. Bạn vẫn có thể nhập tọa độ hoặc xem danh sách gợi ý.'; });
            gl.on('idle', () => { if (!baseError) { status.textContent = ''; canvas.dataset.baseLoaded = '1'; } });
        } catch (_) { status.textContent = 'Trình duyệt chưa mở được nền bản đồ WebGL. Bạn vẫn có thể nhập tọa độ hoặc xem danh sách gợi ý.'; }
        new ResizeObserver(() => map.invalidateSize({pan: false})).observe(canvas);
        canvas.careMap = map;
        return map;
    }
    const ownIcon = () => window.L.divIcon({className: 'gm-own-marker', html: '<span></span>', iconSize: [24, 24], iconAnchor: [12, 12]});
    function initPicker(root) {
        const lat = root.querySelector('[name=geo_lat]'), lon = root.querySelector('[name=geo_lon]');
        const share = root.querySelector('[name=geo_share]'), status = root.querySelector('[data-geo-status]');
        const details = root.querySelector('details'), area = root.querySelector('[data-geo-area]');
        const form = root.closest('form'), address = form.querySelector('[name=flex_location]');
        const hiddenAddress = root.querySelector('[name=geo_address]');
        const manualAddress = root.querySelector('[data-geo-address-manual]');
        const addressPreview = root.querySelector('[data-geo-address-preview]');
        const urlField = root.querySelector('[data-geo-url]'), openLink = root.querySelector('[data-geo-open]');
        let map, marker, loading;
        let reverseTimer, reverseController, reverseSerial = 0, addressEdits = 0;
        let addressedPoint = [Number(lat.value), Number(lon.value)].map(v => v.toFixed(6)).join(',');
        const services = window.careMapServices;
        for (const [i, item] of AREAS.entries()) {
            const option = node('option', item[0]); option.value = String(i); area.append(option);
        }
        function point() {
            const p = [Number(lat.value), Number(lon.value)];
            return lat.value !== '' && lon.value !== '' && p.every(Number.isFinite) && p[0] >= 8 && p[0] <= 24 && p[1] >= 102 && p[1] <= 110 ? p : null;
        }
        function syncAddress(value) {
            address.value = value; hiddenAddress.value = value; manualAddress.value = value;
            addressPreview.textContent = value.trim() || 'Chưa chọn vị trí trên bản đồ';
            addressPreview.dataset.empty = value.trim() ? '0' : '1';
        }
        function place(p, move = true) {
            if (!Array.isArray(p) || !p.every(Number.isFinite) || p[0] < 8 || p[0] > 24 || p[1] < 102 || p[1] > 110) {
                status.textContent = 'Chọn vị trí trong phạm vi Việt Nam được hỗ trợ.';
                sync(false); return;
            }
            lat.value = p[0].toFixed(6); lon.value = p[1].toFixed(6);
            status.textContent = 'Đã chọn điểm. Bấm lưu để áp dụng vị trí này.';
            sync(move);
            lookup();
        }
        function updateLink() {
            const p = point(), url = p ? services.mapUrl(p) : '';
            urlField.value = url; openLink.hidden = !url; if (url) openLink.href = url;
        }
        function cancelLookup() {
            ++reverseSerial; clearTimeout(reverseTimer); reverseController?.abort(); root.dataset.reverseBusy = '0';
        }
        function lookup() {
            cancelLookup(); updateLink();
            const p = point(); if (!p) return;
            const key = p.map(v => v.toFixed(6)).join(',');
            if (key !== addressedPoint) { syncAddress(''); addressedPoint = key; }
            const generation = reverseSerial, edits = addressEdits;
            root.dataset.reverseBusy = '1';
            status.textContent = 'Đang tra địa chỉ gần ghim để điền vào ô vị trí…';
            reverseTimer = setTimeout(async () => {
                const controller = new AbortController(); reverseController = controller;
                const timer = setTimeout(() => controller.abort(), 9000);
                try {
                    const result = await services.reverse(p, controller.signal);
                    if (generation !== reverseSerial) return;
                    if (addressEdits === edits) {
                        syncAddress(result.address);
                        const region = form.elements.flex_region_id;
                        const normalized = s => s.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/đ/g, 'd')
                            .replace(/\b(thanh pho|tinh|tp)\b\.?/g, '').trim().replace(/\s+/g, ' ');
                        const names = (result.regionNames || []).map(normalized);
                        const option = region && [...region.options].find(o => o.value && names.includes(normalized(o.textContent)));
                        if (option) { region.value = option.value; region.dispatchEvent(new Event('change', {bubbles: true})); }
                    }
                    status.textContent = 'Đã lấy địa chỉ gần ghim. Kiểm tra địa chỉ đã chọn và bổ sung số nhà/hẻm nếu cần.';
                } catch (_) {
                    if (generation === reverseSerial) {
                        status.textContent = 'Chưa tra được địa chỉ. Mở phần bổ sung bên dưới để nhập số nhà/đường, phường/xã, tỉnh/thành cho ghim đã chọn.';
                        root.querySelector('.gm-address-editor').open = true;
                    }
                } finally {
                    clearTimeout(timer); if (generation === reverseSerial) root.dataset.reverseBusy = '0';
                }
            }, 700);
        }
        manualAddress.addEventListener('input', () => {
            ++addressEdits; syncAddress(manualAddress.value); cancelLookup();
            status.textContent = 'Sẽ lưu đầy đủ địa chỉ bạn nhập cùng tọa độ và liên kết vị trí.';
        });
        form.addEventListener('submit', event => {
            if (root.dataset.reverseBusy === '1' && form.elements.flex_mode?.value !== 'remote') {
                event.preventDefault(); status.textContent = 'Đang tra địa chỉ. Chờ một chút rồi lưu, hoặc nhập địa chỉ để dùng nội dung của bạn.';
                status.scrollIntoView({block: 'center'});
            } else if (point() && !address.value.trim() && form.elements.flex_mode?.value !== 'remote') {
                event.preventDefault(); root.querySelector('.gm-address-editor').open = true;
                status.textContent = 'Bổ sung địa chỉ cho ghim đã chọn trước khi lưu.'; manualAddress.focus();
            }
        });
        root.querySelector('[data-geo-reverse]').addEventListener('click', lookup);
        form.elements.flex_mode?.addEventListener('change', () => {
            updateLink(); if (form.elements.flex_mode.value === 'remote') cancelLookup();
        });
        function sync(move = true) {
            updateLink();
            const p = point();
            if (!map) return;
            if (marker) { marker.remove(); marker = null; }
            if (p) {
                marker = window.L.marker(p, {icon: ownIcon(), draggable: true, title: 'Điểm đã chọn; có thể kéo ghim hoặc nhập tọa độ'}).addTo(map);
                marker.on('dragend', () => { const v = marker.getLatLng(); place([v.lat, v.lng], false); });
                if (move) map.setView(p, 14, {animate: false});
            }
        }
        async function open() {
            if (!map && !loading) loading = makeMap(root.querySelector('[data-geo-canvas]'), root.querySelector('[data-tile-status]'), point() || DEFAULT)
                .then(m => { map = m; map.on('click', event => place([event.latlng.lat, event.latlng.lng], false)); sync(); })
                .catch(error => { status.textContent = error.message + ' Bạn vẫn có thể nhập tọa độ.'; loading = null; });
            await loading;
            if (map) map.invalidateSize();
        }
        details.addEventListener('toggle', () => { if (details.open) open(); });
        area.addEventListener('change', async () => {
            if (area.value === '') return;
            await open();
            if (map) map.setView(AREAS[Number(area.value)].slice(1), 13, {animate: false});
        });
        for (const input of [lat, lon]) input.addEventListener('change', () => {
            if (!point() && (lat.value || lon.value)) status.textContent = 'Điền đủ tọa độ hợp lệ trong Việt Nam.';
            else { status.textContent = point() ? 'Tọa độ đã nhập; bấm lưu để áp dụng.' : ''; sync(); if (point()) lookup(); else cancelLookup(); }
        });
        root.querySelector('[data-geo-clear]').addEventListener('click', () => {
            cancelLookup();
            lat.value = ''; lon.value = ''; share.checked = false;
            syncAddress(''); sync(); status.textContent = 'Đã xóa điểm; bấm lưu để áp dụng.';
        });
        root.querySelector('[data-geo-gps]').addEventListener('click', event => {
            const button = event.currentTarget;
            if (!navigator.geolocation) { status.textContent = 'Trình duyệt chưa hỗ trợ định vị. Hãy chấm bản đồ hoặc nhập tọa độ.'; return; }
            button.disabled = true; status.textContent = 'Đang xin quyền lấy vị trí…';
            navigator.geolocation.getCurrentPosition(position => {
                button.disabled = false;
                const p = [position.coords.latitude, position.coords.longitude];
                if (p[0] < 8 || p[0] > 24 || p[1] < 102 || p[1] > 110) { status.textContent = 'Bản thử chỉ hỗ trợ vị trí tại Việt Nam.'; return; }
                place(p);
                status.textContent += ' Độ chính xác thiết bị: khoảng ' + Math.round(position.coords.accuracy) + ' m.';
            }, () => { button.disabled = false; status.textContent = 'Chưa lấy được vị trí hoặc bạn chưa cấp quyền. Hãy chấm bản đồ hoặc nhập tọa độ.'; },
            {enableHighAccuracy: true, timeout: 10000, maximumAge: 60000});
        });
        root.geoPicker = {set(data) {
            lat.value = data.point ? data.point[0] : ''; lon.value = data.point ? data.point[1] : '';
            syncAddress(data.address || '');
            share.checked = !!data.shared; status.textContent = data.sample ? 'Điểm thử ngẫu nhiên. Chọn lại để xác nhận địa điểm của bạn.' : '';
            details.open = true; sync(); open();
        }};
        syncAddress(address.value); updateLink();
        if (details.open) {
            const observer = new IntersectionObserver(entries => {
                if (entries.some(entry => entry.isIntersecting)) { observer.disconnect(); open(); }
            }, {rootMargin: '150px'});
            observer.observe(root);
        }
    }
    async function initNearby(root) {
        const guest = root.dataset.guest === '1';
        const canvas = root.querySelector('[data-nearby-canvas]');
        const status = root.querySelector('[data-geo-results-status]');
        let map;
        try { map = await makeMap(canvas, root.querySelector('[data-tile-status]')); }
        catch (error) { root.querySelector('[data-tile-status]').textContent = error.message + ' Bạn vẫn xem được danh sách.'; }
        const L = window.L;
        let group = map ? L.layerGroup().addTo(map) : null;
        let view = root.dataset.role === 'candidate' ? 'receive' : 'hire', data, serial = 0;
        const select = root.querySelector('[data-geo-source]'), radius = root.querySelector('[data-geo-radius]');
        const results = root.querySelector('[data-geo-results]');
        const positions = [];
        const routeLayer = map ? L.layerGroup().addTo(map) : null;
        const routePanel = root.querySelector('[data-geo-route]');
        let routeController, routeSerial = 0, activeRoute;
        const gl = map?.careGL;
        function drawRoute() {
            if (!activeRoute?.route) return;
            if (gl && canvas.dataset.mapPalette) {
                const feature = {type: 'Feature', properties: {}, geometry: {
                    type: 'LineString', coordinates: activeRoute.route.points.map(p => [p[1], p[0]])}};
                if (!gl.getSource('tacare-route')) gl.addSource('tacare-route', {type: 'geojson', data: feature});
                else gl.getSource('tacare-route').setData(feature);
                // One-way-arrow symbols occur BEFORE bridge deck layers in
                // Liberty. Insert after every road/bridge, before text labels.
                // Full world geometry survives camera/viewport changes.
                const before = gl.getStyle().layers.find(layer => layer.type === 'symbol' && layer.layout?.['text-field'])?.id;
                const placement = canvas.dataset.mapProvider === 'mapbox' ? {slot: 'middle'} : {};
                if (!gl.getLayer('tacare-route-casing')) gl.addLayer({id: 'tacare-route-casing',
                    ...placement, type: 'line', source: 'tacare-route', layout: {'line-join': 'round', 'line-cap': 'round'},
                    paint: {'line-color': '#ffffff', 'line-width': 6, 'line-opacity': .9}}, before);
                if (!gl.getLayer('tacare-route-line')) gl.addLayer({id: 'tacare-route-line',
                    ...placement, type: 'line', source: 'tacare-route', layout: {'line-join': 'round', 'line-cap': 'round'},
                    paint: {'line-color': '#4285f4', 'line-width': 3.5}}, before);
                canvas.dataset.routeVisible = '1';
            } else if (!gl && routeLayer) {
                routeLayer.clearLayers();
                L.polyline(activeRoute.route.points, {color: '#4285f4', weight: 3.5,
                    noClip: true, interactive: false}).addTo(routeLayer);
            }
        }
        gl?.on('style.load', drawRoute);
        function clearRoute() {
            ++routeSerial; routeController?.abort(); activeRoute = null;
            routeLayer?.clearLayers(); routePanel.hidden = true; canvas.dataset.routeVisible = '0';
            routePanel.querySelector('[data-geo-route-metrics]').hidden = true;
            routePanel.querySelector('[data-geo-directions]').removeAttribute('href');
            if (gl && canvas.dataset.mapPalette) gl.getSource('tacare-route')?.setData({type: 'FeatureCollection', features: []});
        }
        root.querySelector('[data-geo-route-clear]').addEventListener('click', clearRoute);
        async function showRoute(item) {
            if (!data?.source?.point) return;
            const origin = data.source.point.slice(), destination = item.point.slice();
            if (activeRoute?.route && activeRoute.key === item.key && activeRoute.sourceId === data.source.id &&
                activeRoute.view === view && activeRoute.origin.join(',') === origin.join(',') &&
                activeRoute.destination.join(',') === destination.join(',')) {
                map?.fitBounds(activeRoute.route.points, {padding: [35, 35], animate: false}); return;
            }
            clearRoute(); const generation = routeSerial;
            activeRoute = {key: item.key, sourceId: data.source.id, view, origin, destination};
            routePanel.hidden = false;
            const routeStatus = routePanel.querySelector('[data-geo-route-status]');
            routeStatus.textContent = 'Đang tìm đường đi đến khu vực của ' + item.title + '…';
            routePanel.querySelector('[data-geo-directions]').href = window.careMapServices.mapUrl(destination, origin);
            const controller = new AbortController(); routeController = controller;
            const timer = setTimeout(() => controller.abort(), 12000);
            try {
                const route = await window.careMapServices.route(origin, destination, controller.signal);
                if (generation !== routeSerial) return;
                activeRoute.route = route; drawRoute();
                map?.fitBounds(route.points, {padding: [35, 35], animate: false});
                const distance = new Intl.NumberFormat('vi-VN', {maximumFractionDigits: route.distance < 100 ? 3 : 2}).format(route.distance / 1000) + ' km';
                const minutes = Math.max(1, Math.ceil(route.duration / 60));
                routeStatus.replaceChildren(document.createTextNode('Tuyến ô tô đến khu vực của ' + item.title + '.'),
                    node('span', ' Tổng quãng đường: ' + distance + '. Thời gian tham khảo: khoảng ' + minutes + ' phút.', 'visually-hidden'));
                routePanel.querySelector('[data-geo-route-distance]').textContent = distance;
                routePanel.querySelector('[data-geo-route-duration]').textContent = '≈ ' + minutes + ' phút';
                routePanel.querySelector('[data-geo-route-metrics]').hidden = false;
            } catch (_) {
                if (generation === routeSerial) routeStatus.textContent = 'Chưa tải được tuyến đường. Bạn có thể mở Google Maps để tìm đường tới khu vực này.';
            } finally { clearTimeout(timer); }
        }
        function fit() {
            if (!map || !positions.length) return;
            if (positions.length === 1) map.setView(positions[0], 12, {animate: false});
            else map.fitBounds(positions, {padding: [46, 46], maxZoom: 13, animate: false});
        }
        root.querySelector('[data-geo-fit]').addEventListener('click', fit);
        function card(item, compact = false) {
            const article = node('article', undefined, compact ? 'gm-result' : 'gm-result gm-result--panel');
            const category = node('p', item.category, 'gm-result-category');
            const title = node('h3', item.title), sub = node('p', item.subtitle);
            const icon = name => {
                const img = node('img'); img.src = ASSET + 'src/icons/phosphor/' + name + '.svg';
                img.alt = ''; img.width = 18; img.height = 18; return img;
            };
            if (compact) article.append(category);
            else {
                const header = node('div', undefined, 'gm-result-header'), badge = node('span', undefined, 'gm-result-icon');
                badge.append(icon(item.icon)); header.append(badge, category); article.append(header);
            }
            article.append(title, sub, node('strong', item.price), node('small', item.region + ' · Khu vực gần đúng'));
            if (item.sample) article.append(node('span', 'Vị trí thử', 'gm-sample'));
            const link = node('a', 'Xem đối chiếu & kết nối', compact ? 'gm-result-link' : 'gm-result-link gm-action gm-action-primary'); link.href = item.url;
            if (!compact) link.append(icon('arrow-right'));
            article.append(link);
            const actions = compact ? article : node('div', undefined, 'gm-result-actions');
            const directions = node('button', undefined, compact ? 'gm-text-button' : 'gm-action gm-action-secondary'); directions.type = 'button';
            if (!compact) directions.append(icon('map-pin'));
            directions.append(node('span', 'Xem đường đi'));
            directions.addEventListener('click', () => showRoute(item)); actions.append(directions);
            if (!compact && map) {
                const locate = node('button', undefined, 'gm-action gm-action-secondary'); locate.type = 'button';
                locate.append(icon('eye'), node('span', 'Hiện trên bản đồ'));
                locate.addEventListener('click', () => {
                    if (activeRoute && activeRoute.key !== item.key) clearRoute();
                    map.setView(item.point, 13, {animate: false});
                    const marker = item.mapMarker; if (marker) marker.openPopup();
                });
                actions.append(locate);
            }
            if (!compact) article.append(actions);
            return article;
        }
        function render(payload, keepView = false) {
            const target = activeRoute && payload.markers.find(item => item.key === activeRoute.key);
            if (!keepView || !target || !payload.source?.point || activeRoute.view !== payload.view ||
                activeRoute.sourceId !== payload.source.id || activeRoute.origin.join(',') !== payload.source.point.join(',') ||
                activeRoute.destination.join(',') !== target.point.join(',')) clearRoute();
            data = payload; results.replaceChildren(); positions.length = 0;
            if (group) group.clearLayers();
            select.replaceChildren();
            for (const source of data.sources) {
                const option = node('option', source.label + (source.located ? '' : ' · Chưa chọn vị trí'));
                option.value = String(source.id); option.selected = source.id === data.source?.id; select.append(option);
            }
            if (!data.sources.length) {
                const empty = node('option', 'Chưa có tin / mục nhận làm đang mở'); empty.value = '0'; select.append(empty);
            }
            const source = data.source;
            const edit = root.querySelector('[data-geo-edit]');
            edit.hidden = !source || !source.editable || source.remote;
            if (source) {
                edit.href = source.edit_url;
                edit.querySelector('.gm-action-label').textContent = view === 'hire' ? 'Chọn / sửa vị trí tại Kho Việc Làm' : 'Chọn / sửa vị trí tại Tủ Hồ Sơ';
                select.title = source.label;
            }
            root.querySelector('[data-geo-source-label]').textContent = source?.sample ? 'Vị trí thử ngẫu nhiên · hãy chọn lại khi sử dụng thật' :
                (source?.located ? source.address || 'Đã chọn điểm trên bản đồ' : 'Chưa chọn vị trí');
            if (source?.point && group) {
                L.marker(source.point, {icon: ownIcon(), title: 'Điểm của bạn'}).addTo(group);
                L.circle(source.point, {radius: data.radius * 1000, color: '#252525', weight: 1, fillOpacity: .035, interactive: false}).addTo(group);
                positions.push(source.point);
            }
            const grouped = new Map();
            for (const item of data.markers) {
                const key = item.point.join(',');
                if (!grouped.has(key)) grouped.set(key, []);
                grouped.get(key).push(item);
            }
            if (group) for (const items of grouped.values()) {
                const icon = L.divIcon({className: 'gm-profession-marker', iconSize: [48, 48], iconAnchor: [24, 24],
                    html: '<span><img alt="" src="' + ASSET + 'src/icons/phosphor/' + items[0].icon + '.svg">' + (items.length > 1 ? '<b>' + items.length + '</b>' : '') + '</span>'});
                const marker = L.marker(items[0].point, {icon, title: items.map(i => i.category).join(', ') + ' · ' + items.length + ' gợi ý trong khu vực'}).addTo(group);
                const popup = node('div', undefined, 'gm-popup');
                items.forEach(item => { popup.append(card(item, true)); item.mapMarker = marker; });
                marker.bindPopup(popup, {maxWidth: 300, maxHeight: 320}); positions.push(items[0].point);
                if (items.length === 1) marker.on('click', () => showRoute(items[0]));
                else marker.on('click', clearRoute); // Choose an explicit result in this shared-area popup.
            }
            data.markers.forEach(item => results.append(card(item)));
            status.textContent = !source ? 'Chưa có nguồn kết nối. Đăng nhu cầu hoặc cập nhật mục nhận làm để bắt đầu.' :
                source.remote ? 'Việc từ xa không hiển thị trên bản đồ. Bạn vẫn xem được gợi ý ở trang matching.' :
                !source.located ? 'Chọn vị trí cho mục này để tìm quanh khu vực của bạn.' :
                view === 'receive' && !source.shared ? 'Bật chia sẻ khu vực gần đúng để kết nối hai chiều trên bản đồ.' :
                data.markers.length ? data.markers.length + ' gợi ý phù hợp trong ' + data.radius + ' km. Bấm icon nghề hoặc xem danh sách.' :
                'Chưa có gợi ý đủ điều kiện trong ' + data.radius + ' km. Thử bán kính lớn hơn, kiểm tra vị trí và quyền chia sẻ.';
            if (!keepView) fit();
        }
        async function load(sourceId = select?.value || '0', keepView = false) {
            const current = ++serial;
            const refresh = root.querySelector('[data-geo-refresh]');
            refresh.disabled = true; refresh.setAttribute('aria-busy', 'true');
            refresh.querySelector('.gm-action-label').textContent = 'Đang cập nhật…';
            results.setAttribute('aria-busy', 'true');
            if (!keepView) clearRoute();
            status.textContent = 'Đang đối chiếu vị trí và quyền chia sẻ…';
            if (!keepView) { results.replaceChildren(); if (group) group.clearLayers(); }
            try {
                const query = new URLSearchParams({view, source_id: sourceId || '0', radius: radius.value});
                const response = await fetch('/tacare/nearby/data?' + query, {credentials: 'same-origin', cache: 'no-store', headers: {Accept: 'application/json'}});
                if (!response.ok || !response.headers.get('content-type')?.includes('application/json')) throw new Error('Phiên đăng nhập hoặc quyền truy cập đã thay đổi. Hãy đăng nhập lại hoặc cập nhật trang.');
                const payload = await response.json();
                if (current === serial) render(payload, keepView);
            } catch (error) {
                if (current === serial) {
                    clearRoute(); results.replaceChildren(); group?.clearLayers();
                    data = null; status.textContent = error.message; root.querySelector('[data-geo-edit]').hidden = true;
                }
            } finally {
                if (current === serial) {
                    refresh.disabled = false; refresh.setAttribute('aria-busy', 'false');
                    refresh.querySelector('.gm-action-label').textContent = 'Cập nhật gợi ý';
                    results.setAttribute('aria-busy', 'false');
                }
            }
        }
        root.querySelectorAll('[data-geo-view]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.geoView === view)));
        for (const button of root.querySelectorAll('[data-geo-view]')) button.addEventListener('click', () => {
            view = button.dataset.geoView;
            root.querySelectorAll('[data-geo-view]').forEach(b => b.setAttribute('aria-pressed', String(b === button)));
            if (!guest) load('0');
        });
        if (guest) return;
        select.addEventListener('change', () => load()); radius.addEventListener('change', () => load());
        root.querySelector('[data-geo-refresh]').addEventListener('click', () => load(select.value || '0', true));
        // Refresh server-side consent/state after returning to this tab, without polling GPS.
        window.addEventListener('focus', () => { if (!document.hidden) load(select.value || '0', true); });
        await load('0');
    }
    function init() {
        document.querySelectorAll('[data-geo-picker]').forEach(initPicker);
        document.querySelectorAll('[data-nearby-map]').forEach(root => {
            const canvas = root.querySelector('[data-nearby-canvas]');
            if (!canvas) return;
            // The section starts above the canvas. Watching it with a large
            // margin eagerly started WebGL/API work under the homepage hero.
            // Wait for the actual map to be visible, then yield the first paint.
            let scheduled = false;
            const observer = new IntersectionObserver(entries => {
                if (scheduled || !entries.some(e => e.isIntersecting && e.intersectionRatio >= .1)) return;
                scheduled = true;
                observer.disconnect();
                const start = () => initNearby(root);
                if (typeof window.requestIdleCallback === 'function') window.requestIdleCallback(start, {timeout: 1000});
                else setTimeout(start, 0);
            }, {rootMargin: '0px', threshold: .1});
            observer.observe(canvas);
        });
    }
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
