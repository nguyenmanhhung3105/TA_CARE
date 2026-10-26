/* Exercise the real initializer without loading a browser or provider network. */
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const source=fs.readFileSync('source/apps/tacare/addons/tacare_website/static/src/js/nearby.js','utf8');
for(const mode of ['idle','timer','missing-canvas']){
 const queued=[],assets=[],observers=[];const canvas={};
 const root={dataset:{guest:'0',role:'business'},querySelector:selector=>selector==='[data-nearby-canvas]'?(mode==='missing-canvas'?null:canvas):{textContent:''}};
 const document={readyState:'complete',querySelectorAll:selector=>selector==='[data-nearby-map]'?[root]:[],
  createElement:tag=>({tag}),head:{append:node=>assets.push(node)}};
 class Observer{constructor(callback,options){this.callback=callback;this.options=options;observers.push(this);}observe(target){this.target=target;}disconnect(){this.disconnected=true;}}
 const window={};if(mode==='idle')window.requestIdleCallback=(fn,options)=>queued.push({fn,kind:'idle',options});
 vm.runInNewContext(source,{window,document,IntersectionObserver:Observer,setTimeout:(fn,delay)=>queued.push({fn,kind:'timer',delay})});
 if(mode==='missing-canvas'){assert.equal(observers.length,0);assert.equal(assets.length,0);continue;}
 assert.equal(observers.length,1);const observer=observers[0];
 assert.equal(observer.target,canvas);assert.equal(observer.options.rootMargin,'0px');
 observer.callback([{isIntersecting:false,intersectionRatio:0}]);
 observer.callback([{isIntersecting:true,intersectionRatio:.05}]);
 assert.equal(queued.length,0);assert.equal(assets.length,0);
 observer.callback([{isIntersecting:true,intersectionRatio:.2}]);
 observer.callback([{isIntersecting:true,intersectionRatio:.3}]);
 assert.equal(queued.length,1);assert(observer.disconnected);assert.equal(assets.length,0);
 assert.equal(queued[0].kind,mode==='idle'?'idle':'timer');
 queued[0].fn();assert.equal(assets.length,3,'Map libraries begin only after visible/idle callback');
}
console.log('PASS actual nearby initializer: observe canvas, no offscreen work, threshold, idle/fallback, single initialization, missing-canvas guard');
