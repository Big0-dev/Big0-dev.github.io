// Cloudflare Pages Function middleware
// Returns HTTP 410 (Gone) for permanently removed URLs.
// Cloudflare _redirects does NOT support 410 status codes — this middleware fills that gap.

// Live service slugs that must pass through (everything else under /services/ is 410)
const LIVE_SERVICE_SLUGS = new Set([
  'ai-powered-applications',
  'custom-software-development',
  'startup-engineering',
]);

// Exact paths that return 410
const EXACT_410 = new Set([
  '/blog', '/blog.html',
  '/industries', '/industries.html',
  '/products', '/products.html',
  '/partners', '/partners.html',
  '/policy',
  '/case.html',
  '/gallery.html.html',
  '/blogs/ai-transformation-2024',
  '/blogs/cloud-migration-best-practices',
  '/blogs/cloud-migration-best-practices.html',
]);

// Prefix patterns — anything starting with these is 410
const PREFIX_410 = [
  '/blog/',
  '/industries/',
  '/services/locations/',
  '/cgi-bin/',
  '/_next/',
  '/cdn-cgi/',
  '/insights/',
];

function isGoneServicePath(path) {
  if (path === '/services' || path === '/services.html') return false;
  if (!path.startsWith('/services/')) return false;

  let slug = path.slice('/services/'.length);
  if (slug.endsWith('.html')) slug = slug.slice(0, -5);
  if (slug.endsWith('/')) slug = slug.slice(0, -1);
  if (slug === '') return false;

  // Subpaths (e.g. /services/locations/foo) — gone
  if (slug.includes('/')) return true;

  // If it's a live service, pass through
  if (LIVE_SERVICE_SLUGS.has(slug)) return false;

  // Everything else under /services/ is gone
  return true;
}

function shouldReturn410(path) {
  if (EXACT_410.has(path)) return true;

  for (const prefix of PREFIX_410) {
    if (path.startsWith(prefix)) return true;
  }

  if (path.startsWith('/services')) {
    return isGoneServicePath(path);
  }

  return false;
}

export async function onRequest(context) {
  const { pathname } = new URL(context.request.url);

  if (!shouldReturn410(pathname)) {
    return context.next();
  }

  try {
    const page = await context.env.ASSETS.fetch(
      new URL('/404.html', context.request.url)
    );
    return new Response(page.body, {
      status: 410,
      headers: {
        'Content-Type': 'text/html; charset=utf-8',
        'X-Robots-Tag': 'noindex',
        'Cache-Control': 'public, max-age=86400',
      },
    });
  } catch {
    return new Response('<!DOCTYPE html><html><head><title>410 Gone</title></head><body><h1>410 Gone</h1><p>This page has been permanently removed.</p></body></html>', {
      status: 410,
      headers: {
        'Content-Type': 'text/html; charset=utf-8',
        'X-Robots-Tag': 'noindex',
      },
    });
  }
}
