const CACHE='vienna-v1', TILES='vienna-tiles-v1';
const ASSETS=[
  './',
  'vienna-tutti-luoghi.html',
  'padova-e-venezia.html',
  'vienna-itinerario.html',
  'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js',
  'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css'
];
self.addEventListener('install',e=>{
  e.waitUntil(caches.open(CACHE).then(c=>c.addAll(ASSETS)));
  self.skipWaiting();
});
self.addEventListener('activate',e=>{
  e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==CACHE&&k!==TILES).map(k=>caches.delete(k)))));
  self.clients.claim();
});
self.addEventListener('fetch',e=>{
  const u=new URL(e.request.url);
  if(u.hostname.includes('basemaps.cartocdn.com')){
    e.respondWith(caches.open(TILES).then(c=>c.match(e.request).then(r=>{
      if(r)return r;
      return fetch(e.request).then(resp=>{
        if(resp.ok)c.put(e.request,resp.clone());
        return resp;
      }).catch(()=>new Response('',{status:204}));
    })));
    return;
  }
  if(u.hostname.includes('cdnjs.cloudflare.com')){
    e.respondWith(caches.match(e.request).then(r=>r||fetch(e.request)));
    return;
  }
  e.respondWith(fetch(e.request).then(r=>{
    const cl=r.clone();
    caches.open(CACHE).then(c=>c.put(e.request,cl));
    return r;
  }).catch(()=>caches.match(e.request)));
});
