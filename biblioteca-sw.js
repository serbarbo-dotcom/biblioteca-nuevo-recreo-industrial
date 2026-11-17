const SHELL='nri-shell-v1',IMAGES='nri-images-v1',DATA='nri-public-data-v1';
self.addEventListener('install',e=>e.waitUntil(caches.open(SHELL).then(c=>c.addAll(['./','./IMG-20261108-WA0001.jpg'])).then(()=>self.skipWaiting())));
self.addEventListener('activate',e=>e.waitUntil(self.clients.claim()));
async function cached(req,name,networkFirst=false){const c=await caches.open(name),old=await c.match(req);if(old&&!networkFirst)return old;try{const r=await fetch(req);if(r.ok||r.type==='opaque')await c.put(req,r.clone()).catch(()=>{});return r}catch(e){if(old)return old;throw e}}
self.addEventListener('fetch',e=>{const r=e.request,u=new URL(r.url);if(r.method!=='GET')return;if(r.mode==='navigate'&&u.origin===location.origin){e.respondWith(fetch(r).then(async x=>{if(x.ok){const c=await caches.open(SHELL);await c.put('./',x.clone()).catch(()=>{})}return x}).catch(()=>caches.match('./')));return}
if(r.destination==='image'&&u.protocol==='https:'){e.respondWith(cached(r,IMAGES));return}
if(u.origin===location.origin&&u.pathname.endsWith('/noticias-auto.json')){e.respondWith(cached(r,DATA,true));return}
if(['www.gstatic.com','cdn.jsdelivr.net'].includes(u.hostname)&&r.destination==='script'){e.respondWith(cached(r,SHELL));return}
if(['openlibrary.org','es.wikipedia.org','itunes.apple.com'].includes(u.hostname)||(u.hostname==='www.googleapis.com'&&u.pathname.startsWith('/books/'))){e.respondWith(cached(r,DATA,true));}
});