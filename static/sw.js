// Churchgate HRIS Service Worker
const CACHE_NAME = 'churchgate-hris-v1';

// Assets to cache for offline use
const ASSETS_TO_CACHE = [
    '/',
    '/app.py',
    '/static/manifest.json'
];

// Install event - cache core assets
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                console.log('Service Worker: Caching files');
                return cache.addAll(ASSETS_TO_CACHE);
            })
            .then(() => self.skipWaiting())
    );
});

// Activate event - clean old caches
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cache) => {
                    if (cache !== CACHE_NAME) {
                        console.log('Service Worker: Clearing old cache:', cache);
                        return caches.delete(cache);
                    }
                })
            );
        })
    );
});

// Fetch event - serve from cache, fallback to network
self.addEventListener('fetch', (event) => {
    // Skip Supabase API calls - always go to network
    if (event.request.url.includes('supabase.co') || 
        event.request.url.includes('streamlit.app') ||
        event.request.url.includes('_stcore')) {
        return;
    }
    
    event.respondWith(
        caches.match(event.request)
            .then((response) => {
                return response || fetch(event.request).then((fetchResponse) => {
                    // Cache successful GET requests
                    if (event.request.method === 'GET' && fetchResponse.status === 200) {
                        const responseClone = fetchResponse.clone();
                        caches.open(CACHE_NAME).then((cache) => {
                            cache.put(event.request, responseClone);
                        });
                    }
                    return fetchResponse;
                });
            })
            .catch(() => {
                // Return offline page if available
                return caches.match('/');
            })
    );
});

// Push notification event
self.addEventListener('push', (event) => {
    const options = {
        body: event.data ? event.data.text() : 'New update from Churchgate HRIS',
        icon: '/churchgate-logo-192.png',
        badge: '/churchgate-logo-192.png',
        vibrate: [100, 50, 100],
        data: {
            url: '/'
        }
    };
    
    event.waitUntil(
        self.registration.showNotification('Churchgate HRIS', options)
    );
});

// Notification click event
self.addEventListener('notificationclick', (event) => {
    event.notification.close();
    event.waitUntil(
        clients.openWindow(event.notification.data.url || '/')
    );
});