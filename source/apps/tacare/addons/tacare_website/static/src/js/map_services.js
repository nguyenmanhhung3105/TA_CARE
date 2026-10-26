/* Local trial integrations; requests are triggered by a location/route action. */
(() => {
    'use strict';
    const reverseCache = new Map(), routeCache = new Map();
    let reverseLast = 0, routeLast = 0;
    const delay = ms => new Promise(resolve => setTimeout(resolve, ms));
    const valid = p => Array.isArray(p) && p.length === 2 && p.every(Number.isFinite) && p[0] >= 8 && p[0] <= 24 && p[1] >= 102 && p[1] <= 110;
    function address(properties) {
        const p = properties || {};
        const street = [p.housenumber, p.street].filter(v => typeof v === 'string' && v.trim()).join(' ');
        const parts = [street || p.name, p.locality, p.district, p.city, p.county, p.state, p.postcode,
            p.countrycode?.toUpperCase() === 'VN' ? 'Việt Nam' : p.country];
        const seen = new Set();
        return parts.filter(v => {
            if (typeof v !== 'string' || !v.trim()) return false;
            const key = v.trim().toLocaleLowerCase('vi');
            if (seen.has(key)) return false;
            seen.add(key); return true;
        }).map(v => v.trim()).join(', ');
    }
    function directionsUrl(point, origin) {
        if (!valid(point)) return '';
        const params = new URLSearchParams({api: '1', destination: point.join(','), travelmode: 'driving'});
        // Omit origin for a device-location/choose-origin launch in Google Maps.
        if (origin && valid(origin)) params.set('origin', origin.join(','));
        return 'https://www.google.com/maps/dir/?' + params;
    }
    function mapUrl(point, origin) {
        if (!valid(point)) return '';
        const params = new URLSearchParams({api: '1'});
        if (origin && valid(origin)) {
            return directionsUrl(point, origin);
        }
        params.set('query', point.join(','));
        return 'https://www.google.com/maps/search/?' + params;
    }
    async function reverse(point, signal) {
        if (!valid(point)) throw new Error('Chọn tọa độ hợp lệ trong Việt Nam.');
        const key = point.map(v => v.toFixed(6)).join(',');
        if (reverseCache.has(key)) return reverseCache.get(key);
        const now = Date.now(), wait = Math.max(0, reverseLast + 1500 - now);
        reverseLast = now + wait; if (wait) await delay(wait);
        if (signal?.aborted) throw new DOMException('Aborted', 'AbortError');
        const query = new URLSearchParams({lat: point[0], lon: point[1], limit: '1', radius: '.5'});
        query.append('layer', 'house'); query.append('layer', 'street');
        const response = await fetch('https://photon.komoot.io/reverse?' + query, {signal, credentials: 'omit',
            headers: {'Accept-Language': 'vi'}, referrerPolicy: 'strict-origin-when-cross-origin'});
        if (!response.ok) throw new Error('Dịch vụ tra địa chỉ chưa phản hồi.');
        const p = (await response.json()).features?.[0]?.properties;
        if (!p || p.countrycode?.toUpperCase() !== 'VN') throw new Error('Chưa tìm thấy địa chỉ đường/nhà tại điểm này.');
        const label = address(p);
        if (!label) throw new Error('Bản đồ chưa có địa chỉ chi tiết tại điểm này.');
        const value = {address: label, completeStreet: !!(p.street || p.type === 'street'), regionNames: [p.state, p.city].filter(Boolean)};
        if (reverseCache.size >= 40) reverseCache.delete(reverseCache.keys().next().value);
        reverseCache.set(key, value); return value;
    }
    async function route(origin, target, signal) {
        if (!valid(origin) || !valid(target)) throw new Error('Chưa có đủ vị trí để tìm đường.');
        const key = origin.join(',') + ':' + target.join(',');
        if (routeCache.has(key)) return routeCache.get(key);
        const now = Date.now(), wait = Math.max(0, routeLast + 1500 - now);
        routeLast = now + wait; if (wait) await delay(wait);
        if (signal?.aborted) throw new DOMException('Aborted', 'AbortError');
        const coordinates = origin.slice().reverse().join(',') + ';' + target.slice().reverse().join(',');
        const response = await fetch('https://router.project-osrm.org/route/v1/driving/' + coordinates + '?overview=simplified&geometries=geojson&steps=false&generate_hints=false',
            {signal, credentials: 'omit', referrerPolicy: 'strict-origin-when-cross-origin'});
        if (!response.ok) throw new Error('Dịch vụ đường đi chưa phản hồi.');
        const data = await response.json(), r = data.routes?.[0];
        if (data.code !== 'Ok' || !r || !Array.isArray(r.geometry?.coordinates) || r.geometry.coordinates.length < 2 ||
            !Number.isFinite(r.distance) || !Number.isFinite(r.duration) ||
            r.geometry.coordinates.some(p => !Array.isArray(p) || p.length < 2 || !p.slice(0, 2).every(Number.isFinite))) throw new Error('Chưa tìm được tuyến đường tại khu vực này.');
        const value = {points: r.geometry.coordinates.map(p => [p[1], p[0]]), distance: r.distance, duration: r.duration};
        if (routeCache.size >= 20) routeCache.delete(routeCache.keys().next().value);
        routeCache.set(key, value); return value;
    }
    function palette(gl) {
        const layers = gl.getStyle().layers;
        const roads = layers.filter(l => l.type === 'line' && l['source-layer'] === 'transportation' && !/rail|casing/.test(l.id));
        const streetWidths = roads.filter(l => l.id.startsWith('road_'));
        const byId = new Map(roads.map(l => [l.id, l]));
        function widthAt(value, zoom) {
            if (typeof value === 'number') return value;
            if (!Array.isArray(value) || value[0] !== 'interpolate' || value[2]?.[0] !== 'zoom') return 0;
            if (zoom <= value[3]) return Number(value[4]) || 0;
            for (let i = 5; i < value.length; i += 2) if (zoom <= value[i]) {
                const start = value[i - 2], span = value[i] - start, base = value[1][1] || 1;
                const weight = base === 1 ? (zoom - start) / span : (base ** (zoom - start) - 1) / (base ** span - 1);
                return Number(value[i - 1]) + (Number(value[i + 1]) - Number(value[i - 1])) * weight;
            }
            return Number(value[value.length - 1]) || 0;
        }
        function roadColor(layer) {
            const casing = layer.id.endsWith('_casing');
            const fillId = layer.id.replace(/_casing$/, '');
            const fill = byId.get(fillId) || byId.get(fillId.replace(/_street$/, '_minor')) || layer;
            const expression = ['interpolate', ['linear'], ['zoom']];
            for (let zoom = 3; zoom <= 20; zoom += .5) {
                const width = widthAt(fill.paint?.['line-width'], zoom);
                const largest = Math.max(1, ...streetWidths.map(l => widthAt(l.paint?.['line-width'], zoom)));
                // Dark gray is reserved for conspicuously wide roads. Ordinary
                // streets stay pale even when several road classes are visible.
                const veryWide = width >= 4.5 && width >= largest * .94;
                const color = casing ? (veryWide ? '#a8bbc4' : '#cbd5d4') :
                    veryWide ? '#b9c9d0' : width >= 3 ? '#d8e0de' : '#e5e9e4';
                expression.push(zoom, color);
            }
            return expression;
        }
        for (const layer of layers) {
            const id = layer.id, type = layer.type, source = layer['source-layer'];
            const set = (name, value) => gl.setPaintProperty(id, name, value);
            if (type === 'background') set('background-color', '#f3f0e7');
            if (type === 'fill') {
                if (source === 'water') set('fill-color', '#98d8e8');
                else if (id === 'landuse_residential') set('fill-color', '#f1eee4');
                else if (source === 'park' || /wood|grass|cemetery|pitch/.test(id)) {
                    const green = /wood/.test(id) ? '#bfe8ce' : /grass/.test(id) ? '#d3f3df' : '#c9f2d8';
                    set('fill-color', green); set('fill-outline-color', green);
                }
                else if (id === 'building') { set('fill-color', '#eeeade'); set('fill-outline-color', '#deded4'); }
                else if (source === 'aeroway') set('fill-color', '#e7ecf8');
                else if (/hospital/.test(id)) set('fill-color', '#f9e7e7');
                else if (/school/.test(id)) set('fill-color', '#eeebdc');
                else if (/sand|track/.test(id)) set('fill-color', '#f3e9c8');
            }
            if (type === 'line') {
                if (source === 'waterway') set('line-color', '#98d8e8');
                else if (source === 'transportation' && !/rail/.test(id)) {
                    set('line-color', roadColor(layer));
                } else if (source === 'aeroway') set('line-color', '#d4def0');
                else if (source === 'boundary') set('line-color', '#bdc8c7');
                else if (source === 'park') set('line-color', '#b4e6c9');
            }
            if (type === 'symbol' && layer.layout?.['text-field']) {
                const color = /water/.test(id) ? '#527f8b' : source === 'poi' ? '#557887' : '#53636c';
                set('text-color', color);
                set('text-halo-color', '#ffffff'); set('text-halo-width', 1.4);
                if (['place', 'water_name', 'waterway', 'poi'].includes(source) || source === 'transportation_name' && id.startsWith('highway-name')) {
                    gl.setLayoutProperty(id, 'text-field', ['coalesce', ['get', 'name:vi'], ['get', 'name:latin'], ['get', 'name'], ['get', 'name:en']]);
                }
            }
        }
        // Liberty omits farmland although it is present in the vector data.
        // Show actual agricultural polygons below cities, water and roads.
        const cover = layers.find(layer => layer['source-layer'] === 'landcover');
        if (cover && !gl.getLayer('tacare-landcover-farmland')) gl.addLayer({
            id: 'tacare-landcover-farmland', type: 'fill', source: cover.source, 'source-layer': 'landcover',
            filter: ['==', ['get', 'class'], 'farmland'],
            paint: {'fill-color': ['match', ['get', 'subclass'],
                ['orchard', 'vineyard', 'plant_nursery'], '#ccebd5', '#d5f4e0'], 'fill-opacity': .95},
        }, layers.find(layer => layer.type === 'fill')?.id);
    }
    window.careMapServices = {address, mapUrl, directionsUrl, reverse, route, palette};
})();
