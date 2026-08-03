const CACHE='vienna-v1',TILES='vienna-tiles-v1';
const VERSIONS=new Set([CACHE,TILES]);
self.addEventListener('install',e=>{self.skipWaiting()});
self.addEventListener('activate',e=>{
  e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>!VERSIONS.has(k)).map(k=>caches.delete(k)))));
  self.clients.claim();
});
self.addEventListener('fetch',e=>{
  const u=new URL(e.request.url);
  if(u.hostname.includes('basemaps.cartocdn.com')){
    e.respondWith(caches.open(TILES).then(c=>c.match(e.request).then(r=>{
      if(r)return r;
      return fetch(e.request).then(resp=>{
        if(resp&&resp.ok)c.put(e.request,resp.clone());
        return resp;
      }).catch(()=>new Response('',{status:204}));
    })));
    return;
  }
  e.respondWith(fetch(e.request).then(r=>{
    if(r&&r.ok){const cl=r.clone();caches.open(CACHE).then(c=>c.put(e.request,cl));}
    return r;
  }).catch(()=>caches.match(e.request)));
});
