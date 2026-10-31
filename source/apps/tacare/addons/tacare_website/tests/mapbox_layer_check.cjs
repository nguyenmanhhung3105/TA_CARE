/* Real bridge, simulated GL: exercise coordinate order, camera and cleanup. */
const fs = require('node:fs'), vm = require('node:vm'), assert = require('node:assert/strict');
let options, moves = [], resized = 0, removed = 0, position;
const container = {style: {}, remove() {this.removed = true;}};
const L = {
    Layer: {extend: definition => class {constructor() {Object.assign(this, definition);}}},
    DomUtil: {create: () => container, setPosition: (_, p) => {position = p;}},
};
const window = {mapboxgl: {Map: class {
    constructor(value) {options = value;}
    jumpTo(value) {moves.push(value);}
    resize() {resized++;}
    remove() {removed++;}
}}};
vm.runInNewContext(fs.readFileSync('source/apps/tacare/addons/tacare_website/static/src/js/mapbox_layer.js', 'utf8'), {window});
let center = {lat: 10.7769, lng: 106.7009}, zoom = 12;
const host = {getSize: () => ({x: 800, y: 500}), getPane: () => ({append: node => assert.equal(node, container)}),
    getCenter: () => center, getZoom: () => zoom, containerPointToLayerPoint: () => ({x: 10, y: 20})};
const layer = window.careMapboxLayer(L, {token: 'PUBLIC_TEST_PLACEHOLDER'});
layer.onAdd(host);
const plain = value => JSON.parse(JSON.stringify(value));
assert.deepEqual(plain(options.center), [106.7009, 10.7769]);
assert.equal(options.zoom, 11); // Leaflet's 256px vs GL's 512px zoom convention.
assert.equal(options.style, 'mapbox://styles/mapbox/standard');
assert.deepEqual(plain(options.maxBounds), [[102, 8], [110, 24]]);
assert.equal(options.renderWorldCopies, false);
assert.equal(options.config.basemap.show3dObjects, false);
assert.equal(options.language, 'vi');
assert.equal(options.attributionControl, true);
assert.equal(options.logoPosition, 'bottom-left');
assert.equal(options.performanceMetricsCollection, false);
assert.equal(container.style.width, '800px');
center = {lat: 21.0285, lng: 105.8542}; zoom = 15;
layer.getEvents().move.call(layer);
assert.deepEqual(plain(moves.at(-1)), {center: [105.8542, 21.0285], zoom: 14});
assert.deepEqual(position, {x: 10, y: 20});
layer.resize(); assert.equal(resized, 1);
assert.equal(moves.length, 2);
layer.onRemove(); assert.equal(removed, 1); assert(container.removed);
assert.equal(layer.gl, null);
console.log('PASS Mapbox bridge: public API, Vietnam rectangle, flat Standard, attribution, camera/resize, cleanup');
