// Część serwerowa sklepu. Obsługuje tylko adresy /api/...; resztę strony Cloudflare podaje z folderu public/.
// W kolejnych etapach dojdą: /api/checkout (płatność Stripe), /api/stripe-webhook, /api/newsletter, /api/kontakt.

const json = (dane, status = 200) => Response.json(dane, { status });

const trasy = {
  // test: https://<adres-strony>/api/ping powinno zwrócić {"ok":true}
  'GET /api/ping': () => json({ ok: true, czas: new Date().toISOString() }),
};

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const obsluga = trasy[`${request.method} ${url.pathname}`];
    if (obsluga) return obsluga(request, env, ctx);
    if (url.pathname.startsWith('/api/')) return json({ ok: false, blad: 'Nie ma takiego adresu' }, 404);
    return env.ASSETS.fetch(request);
  },
};
