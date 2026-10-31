/* Public-API-only Leaflet bridge. No private Mapbox transform/canvas fields. */
(() => {
    'use strict';
    window.careMapboxLayer = (L, options) => {
        const Layer = L.Layer.extend({
            onAdd(map) {
                this.host = map;
                this.container = L.DomUtil.create('div', 'gm-mapbox-layer');
                map.getPane('tilePane').append(this.container);
                this.size();
                const center = map.getCenter();
                this.gl = new window.mapboxgl.Map({
                    container: this.container, accessToken: options.token,
                    style: 'mapbox://styles/mapbox/standard',
                    config: {basemap: {lightPreset: 'day', show3dObjects: false,
                        showTransitLabels: false, showPointOfInterestLabels: true}},
                    center: [center.lng, center.lat], zoom: map.getZoom() - 1,
                    projection: 'mercator', pitch: 0, bearing: 0,
                    maxBounds: [[102, 8], [110, 24]], renderWorldCopies: false,
                    interactive: false, attributionControl: true,
                    logoPosition: 'bottom-left', language: 'vi',
                    performanceMetricsCollection: false,
                    trackResize: false,
                });
            },
            getEvents() { return {move: this.sync, resize: this.resize}; },
            size() {
                const size = this.host.getSize();
                this.container.style.width = size.x + 'px';
                this.container.style.height = size.y + 'px';
            },
            sync() {
                if (!this.gl) return;
                L.DomUtil.setPosition(this.container, this.host.containerPointToLayerPoint([0, 0]));
                const center = this.host.getCenter();
                this.gl.jumpTo({center: [center.lng, center.lat], zoom: this.host.getZoom() - 1});
            },
            resize() { this.size(); this.gl?.resize(); this.sync(); },
            onRemove() { this.gl?.remove(); this.gl = null; this.container.remove(); },
        });
        return new Layer();
    };
})();
