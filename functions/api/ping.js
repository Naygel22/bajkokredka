// Test części serwerowej: https://<adres-strony>/api/ping powinno zwrócić {"ok":true}.
// Tu w kolejnych etapach dojdą: checkout.js (płatność Stripe), stripe-webhook.js,
// newsletter.js, kontakt.js. Każdy plik w functions/api/ = jeden adres /api/...
export function onRequestGet() {
  return Response.json({ ok: true, czas: new Date().toISOString() });
}
