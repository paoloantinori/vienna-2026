const CACHE='vienna-v1',TILES='vienna-tiles-v1';
const VERSIONS=new Set([CACHE,TILES]);
self.addEventListener('install',()=>self.skipWaiting());
self.addEventListener('activate',e=>{
  e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>!VERSIONS.has(k)).map(k=>caches.delete(k)))));
  self.clients.claim();
});
self.addEventListener('fetch',e=>{
  const u=new URL(e.request.url);
  if(u.hostname.includes('basemaps.cartocdn.com')){
    // For tile images: try cache first, then fetch+cache
    e.respondWith(caches.open(TILES).then(c=>c.match(e.request,{ignoreSearch:true,ignoreVary:true})).then(r=>{
      if(r)return r;
      return fetch(e.request).then(resp=>{
        if(resp){c.put(e.request,resp.clone());}
        return resp;
      }).catch(()=>fetch(e.request));
    }));
    return;
  }
  e.respondWith(
    caches.match(e.request).then(r=>{
      if(r)return r;
      return fetch(e.request).then(resp=>{
        if(resp&&resp.ok){caches.open(CACHE).then(c=>c.put(e.request,resp.clone()));}
        return resp;
      });
    })
  );
});
