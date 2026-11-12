# Bajkokredka – budowa sklepu (instrukcja dla Claude Code)

Ten plik daje się Claude Code na start: „Przeczytaj INSTRUKCJA_NEXT.md i zrób Etap 1”.

> **Aktualizacja: wersja od Fable.** Strona ma już osobne podstrony z SEO (folder `strona/`: `podglad/` = źródło, `build.py` = generator, `hosting/` = gotowe pliki .html, 42 podstrony, tytuły, opisy, okruszki, dane produktu, sitemap).
> Dlatego **nie przepisujemy wyglądu na React**. Gotowa strona zostaje jak jest, a dokładamy tylko część serwerową (płatności, PDF, maile) jako funkcje na Vercel.
> To mniej pracy i mniejsze ryzyko, że coś zacznie wyglądać inaczej. Pełny Next.js (opis niżej) zostaje jako plan B, gdyby kiedyś był potrzebny.
Każdy etap kończy się działającą stroną. Nie przechodź dalej, dopóki poprzedni etap nie działa.

---

## 0. Dlaczego Next.js, a nie WordPress

| | Next.js (polecam) | WordPress + WooCommerce |
|---|---|---|
| Wygląd | Przenosimy gotowy `index.html` 1:1 | Trzeba przerobić projekt na motyw, trudno o ten sam efekt |
| Płatności (BLIK, Przelewy24, karta) | Stripe Checkout – jedna integracja | Gotowe wtyczki (Przelewy24, Tpay, Stripe) |
| Sprzedaż PDF | Własny kod: link ważny 30 dni, limit pobrań | Wbudowane „produkty do pobrania” |
| Ceny progowe 29/25/22/19, kod WITAJ10 | Własna funkcja, ~30 linijek | Wtyczka z rabatami albo własny kod PHP |
| Bajka od zera + moderacja AI | Naturalne (API route + Claude) | Trudniejsze (formularz + własna wtyczka) |
| Kolorowanie online, karuzele | Działa jak teraz | Trzeba wstawiać jako własny kod |
| Dodawanie nowej bajki | Skrypt `finish.py` → plik → `git push` | Ręcznie w panelu (zdjęcia, PDF, opis) |
| Codzienna obsługa bez programowania | Prosty panel /admin, który zbudujemy | Gotowy panel WooCommerce |
| Utrzymanie | Mało (brak wtyczek do aktualizacji) | Aktualizacje WP i wtyczek, bezpieczeństwo |

**Wniosek:** budujesz z Claude Code, wygląd już jest gotowy, a nowe bajki i tak dodajemy skryptem. Własny kod wychodzi prościej i szybciej niż WordPress.
Teraz najprościej: **statyczna strona z `build.py` + funkcje serwerowe w folderze `api/` na Vercel** (to też Node/TypeScript, tylko bez przepisywania stron).
WordPress ma sens tylko wtedy, gdy sklep ma potem prowadzić ktoś bez dostępu do Claude Code i bez znajomości kodu.

---

## 1. Zestaw narzędzi

- **Next.js (App Router) + TypeScript**: strony bajek generowane statycznie (`/bajki/[slug]`)
- **Hosting:** Vercel (do sklepu potrzebny plan płatny, bo darmowy jest tylko do użytku niekomercyjnego) albo Netlify / Cloudflare Pages
- **Płatności:** Stripe Checkout w PLN (BLIK, Przelewy24, karta, Apple/Google Pay). Metody płatności włączasz w panelu Stripe.
- **Baza i pliki:** Supabase, czyli baza Postgres + prywatny „bucket” na pliki PDF (linki do pobrania podpisane i z terminem ważności)
- **Maile do klientów:** Resend (+ szablony `react-email`)
- **Newsletter:** MailerLite albo Brevo (double opt-in, automatyczny mail z kodem WITAJ10)
- **Faktury:** Fakturownia albo inFakt (API). Przed startem zapytaj księgową, jaką formę działalności i jakie faktury potrzebujesz.
- **Moderacja AI:** Anthropic API (szybki, tani model), wywoływane **tylko na serwerze**
- **Antyspam:** Cloudflare Turnstile w formularzach
- **Statystyki:** Plausible albo Umami (nie wymagają banera cookies)

### Konta do założenia (Etap 0, robisz sam)
1. Domena (np. bajkokredka.pl)
2. GitHub (repozytorium)
3. Vercel, z podpiętym GitHubem
4. Stripe: dane firmy, konto bankowe, włącz BLIK i Przelewy24. Najpierw pracujemy w **trybie testowym**.
5. Supabase (projekt w regionie UE, np. Frankfurt)
6. Resend: dodaj domenę i rekordy DNS (SPF, DKIM), nadawca np. `bajki@bajkokredka.pl`
7. MailerLite albo Brevo
8. Fakturownia albo inFakt
9. Anthropic Console: klucz API do moderacji
10. Cloudflare: Turnstile (klucz strony + klucz sekretny)

Klucze **nigdy** nie trafiają do kodu ani do czatu. Wpisujesz je w Vercel → Settings → Environment Variables i lokalnie w `.env.local` (plik w `.gitignore`).

---

## 2. Zmienne środowiskowe (`.env.example`)

```
NEXT_PUBLIC_SITE_URL=https://bajkokredka.pl
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=
SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=        # tylko serwer
NEXT_PUBLIC_SUPABASE_ANON_KEY=
RESEND_API_KEY=
MAIL_FROM="Bajkokredka <bajki@bajkokredka.pl>"
MAIL_ADMIN=                       # Twój adres na powiadomienia
MAILERLITE_API_KEY=
FAKTUROWNIA_DOMAIN=
FAKTUROWNIA_API_TOKEN=
ANTHROPIC_API_KEY=
TURNSTILE_SECRET_KEY=
NEXT_PUBLIC_TURNSTILE_SITE_KEY=
ADMIN_EMAILS=                     # kto może wejść na /admin
```

---

## 3. Struktura projektu

```
**Wariant obecny (strona statyczna + API):**
```
strona/podglad/               źródło (index.html, bajki.js, img, ...)
strona/build.py               generator podstron
public/                       wynik build.py (serwowany przez Vercel)
api/checkout.ts, api/stripe-webhook.ts, api/pobierz/[token].ts,
api/stworz.ts, api/kontakt.ts, api/newsletter.ts
lib/cena.ts, lib/moderacja.ts
vercel.json
```

**Plan B (pełny Next.js):**
```
app/
  page.tsx                    strona główna
  bajki/page.tsx              sklep z filtrami i sortowaniem
  bajki/[slug]/page.tsx       strona bajki (generateStaticParams z data/bajki.json)
  stworz-bajke/page.tsx       bajka od zera
  koloruj/page.tsx            kolorowanie online
  koszyk/page.tsx
  zamowienie/page.tsx         dane, faktura, zgody → przejście do Stripe
  dziekujemy/page.tsx         po płatności
  kontakt/page.tsx
  regulamin/page.tsx, polityka-prywatnosci/page.tsx
  pobierz/[token]/route.ts    pobranie PDF (sprawdza token, ważność, limit)
  api/checkout/route.ts       liczy cenę NA SERWERZE, tworzy sesję Stripe
  api/stripe-webhook/route.ts płatność opłacona → zamówienie, maile, faktura
  api/stworz/route.ts         bajka od zera: moderacja AI → zapis → płatność
  api/kontakt/route.ts, api/newsletter/route.ts
  admin/...                   panel (logowanie Supabase, tylko ADMIN_EMAILS)
  not-found.tsx               wygląd z #widok-404, kod 404
  sitemap.ts, robots.ts
components/                   Header, Footer, KartaBajki, Karuzela, Filtry, Koszyk, ...
lib/cena.ts                   progi cen + kod rabatowy (jedno źródło prawdy)
lib/moderacja.ts              prompt MODERACJA z index.html
data/bajki.json               katalog (z katalog/bajki.json)
public/img, public/kolorowanki, public/fonts, public/og.jpg
```

**Pliki PDF nie trafiają do `public/`.** Leżą w prywatnym buckecie Supabase `bajki-pdf/<id>.pdf`.

---

## 4. Baza danych (Supabase)

```sql
create table zamowienia (
  id uuid primary key default gen_random_uuid(),
  numer serial,
  email text not null, imie text, nazwisko text,
  faktura boolean default false, nip text, firma text, adres text,
  pozycje jsonb not null,          -- [{id, tytul}]
  suma_gr int not null,            -- w groszach
  rabat_kod text,
  status text default 'nowe',      -- nowe | oplacone | wyslane | zwrot
  stripe_session text unique,
  zgody jsonb not null,            -- {regulamin, natychmiastowe_dostarczenie, newsletter, czas, ip}
  faktura_url text,
  created_at timestamptz default now()
);
create table pobrania (
  token text primary key,          -- losowy, 32+ znaki
  zamowienie_id uuid references zamowienia,
  bajka_id text not null,
  wazny_do timestamptz not null,   -- +30 dni
  licznik int default 0, limit_pobran int default 10
);
create table bajki_od_zera (
  id uuid primary key default gen_random_uuid(),
  email text not null, dane jsonb not null,   -- imię, wygląd, przyjaciel, temat, liczba stron...
  moderacja jsonb,                            -- wynik AI
  status text default 'do_moderacji',         -- odrzucone | do_zaplaty | oplacone | w_produkcji | do_akceptacji | wyslane
  zamowienie_id uuid references zamowienia, pdf_path text,
  created_at timestamptz default now()
);
create table kody_uzyte (kod text, email text, primary key (kod, email));
create table kontakt (id bigserial primary key, imie text, email text, tresc text, created_at timestamptz default now());
```
Włącz RLS na wszystkich tabelach. Dostęp tylko z serwera (service role).

---

## 5. Ceny (lib/cena.ts): ta sama logika co w podglądzie

```ts
export const cenaSzt = (n: number) => n >= 4 ? 1900 : n === 3 ? 2200 : n === 2 ? 2500 : 2900; // grosze
export function policz(ids: string[], kod?: string, kodWazny = false) {
  const n = new Set(ids).size;                 // ta sama bajka liczona raz
  let suma = n * cenaSzt(n);
  if (kod?.toUpperCase() === 'WITAJ10' && kodWazny) suma = Math.round(suma * 0.9);
  return { n, cenaSzt: cenaSzt(n), suma };
}
```
Koszyk w przeglądarce tylko **pokazuje** cenę. Kwotę do Stripe zawsze liczy `api/checkout` od nowa. WITAJ10 można użyć raz na e-mail (tabela `kody_uzyte`).

---

## 6. Etapy (każdy = osobne polecenie dla Claude Code)

### Etap 1 – Strona na Vercel (bez płatności)
> Przeczytaj `strona/README.md`. Załóż repozytorium: `strona/podglad` (źródło), `strona/build.py`, a wynik `build.py` w `public/`. Skonfiguruj Vercel tak, żeby serwował `public/` (czyste adresy bez `.html` przez `vercel.json`: `cleanUrls`, 404 → `404.html`). Dodaj skrypt `npm run build`, który uruchamia `python3 build.py strona/podglad public https://bajkokredka.pl/`, albo buduj lokalnie i commituj `public/`. Strona ma wyglądać identycznie jak teraz.

Sprawdzenie: wszystkie podstrony się otwierają, menu na telefonie działa, `build.py` kończy się „Kontrola: bez uwag”.

### Etap 2 – Podmiana zapisu danych na własne API
> W `podglad/index.html` formularze (zamówienie, kontakt, newsletter, bajka od zera) zapisują dane przez `uzyj('db')`, a moderacja idzie przez `uzyj('sample')`. To działa tylko w podglądzie Claude. Dodaj warunek: w trybie strony (`data-tryb="strony"`) wysyłaj `fetch` do `/api/zamowienie`, `/api/kontakt`, `/api/newsletter`, `/api/stworz`, a w podglądzie zostaw obecne zachowanie. Na razie API tylko zapisuje dane do Supabase i odpowiada „ok”.
Dodatkowo: ikonki PNG 32/180/512 i obrazki w WebP, jeśli Lighthouse tego wymaga.

### Etap 3 – Koszyk i zamówienie
> Koszyk w localStorage (jak teraz), `lib/cena.ts`, strona `/zamowienie` z formularzem (imię, nazwisko, e-mail ×2, faktura + NIP z walidacją, zgody: regulamin, zgoda na natychmiastowe dostarczenie treści cyfrowej i utratę prawa odstąpienia, newsletter opcjonalnie). Wybór metody płatności przenosimy do Stripe.

### Etap 4 – Płatność Stripe
> `api/checkout`: walidacja (zod), cena liczona na serwerze, zapis zamówienia `status=nowe`, Stripe Checkout Session (`mode: payment`, waluta `pln`, metody z panelu Stripe, `customer_email`, `metadata.zamowienie_id`, `locale: 'pl'`). `api/stripe-webhook`: weryfikacja podpisu, `checkout.session.completed` → `status=oplacone`. Webhook musi być odporny na powtórzenia (idempotentny). Strona `/dziekujemy`.

Test: Stripe CLI (`stripe listen --forward-to localhost:3000/api/stripe-webhook`), testowa karta, testowy BLIK i P24 w trybie testowym.

### Etap 5 – Wysyłka PDF
> Po opłaceniu: dla każdej bajki token w `pobrania` (ważny 30 dni, limit 10 pobrań), mail przez Resend „Twoje bajki są gotowe” z przyciskami pobierania, kopia na MAIL_ADMIN. `/pobierz/[token]` sprawdza ważność i licznik, potem przekierowuje na podpisany link Supabase (ważny 60 s). Szablon maila w stylu strony.

Upload PDF: wgraj 30 plików do bucketu `bajki-pdf` jako `<id>.pdf`.

### Etap 6 – Faktury
> Po opłaceniu utwórz w Fakturowni/inFakt fakturę (albo rachunek, zależnie od formy działalności) z danymi z zamówienia. Gdy klient chciał fakturę z NIP, wystaw na firmę. Wyślij ją mailem z systemu faktur, a link zapisz w `faktura_url`.

### Etap 7 – Bajka od zera + moderacja + panel
> `api/stworz`: Turnstile → walidacja → moderacja AI (prompt `MODERACJA`, odpowiedź JSON ok/odrzuć + powód). Odrzucone: zapis i komunikat dla klienta, bez płatności. Zaakceptowane: płatność Stripe (cena wg liczby stron). Po opłaceniu `status=oplacone`, mail do Ciebie. Panel `/admin` (logowanie Supabase, tylko ADMIN_EMAILS): lista zamówień, kolejka bajek od zera, podgląd danych, wgranie gotowego PDF → przycisk „Wyślij klientowi” (mail z linkiem), zmiana statusu, ponowna wysyłka maila.

Każdą bajkę od zera i tak przeglądasz przed wysłaniem. AI to pierwsze sito, a nie jedyna kontrola.

### Etap 8 – Newsletter i kontakt
> Zapis do newslettera (stopka, popup, zgoda w zamówieniu) → MailerLite/Brevo z double opt-in. Po potwierdzeniu automat wysyła kod WITAJ10 i co tydzień darmową kolorowankę (ustawiasz w MailerLite). Formularz kontaktowy → tabela `kontakt` + mail do Ciebie, z Turnstile i honeypotem.

### Etap 9 – Prawo, cookies, statystyki
> Strony `/regulamin` i `/polityka-prywatnosci` (projekty w `do_budowy/`, **po sprawdzeniu przez prawnika**), dane sprzedawcy w stopce, Plausible/Umami, zdarzenia: dodanie do koszyka, start zamówienia, zakup z wartością, zapis do newslettera, formularz bajki od zera. Gdy pojawi się GA4 albo piksel reklamowy, dodaj baner zgody.

### Etap 10 – Start
- [ ] Pełny zakup testowy: BLIK, P24, karta → mail → pobranie → faktura
- [ ] Zakup z kodem WITAJ10 i drugi raz tym samym e-mailem (ma odmówić)
- [ ] Bajka od zera: treść odrzucona i zaakceptowana
- [ ] Telefon: menu, karuzele, koszyk, zamówienie
- [ ] Lighthouse ≥ 90 na telefonie
- [ ] Domena na Vercel, HTTPS, przekierowanie www → bez www
- [ ] Stripe: przełączenie na tryb live, nowe klucze i nowy webhook
- [ ] Google Search Console + zgłoszenie sitemapy
- [ ] Jedno prawdziwe zamówienie za własne pieniądze, potem zwrot

---

## 7. Dodawanie nowej bajki po starcie

1. Robisz bajkę jak dotąd (skill **bajkokredka**: Gemini → `finish.py`).
2. Claude Code: podmienia `strona/podglad/bajki.js` i obrazki w `strona/podglad/img/`, uruchamia `build.py`, wgrywa PDF do bucketu `bajki-pdf`.
3. `git push` → Vercel publikuje. Nowa bajka ma swoją podstronę, jest w sitemapie i w sklepie.

---

## 8. Co jest w paczce `strona_start`

- `strona/`: wersja od Fable z dodanym przyciskiem „Stwórz bajkę” w headerze: `podglad/` (źródło), `build.py`, `hosting/` (42 gotowe podstrony), `README.md`.
- `pdf/`: PDF-y 11 bajek z serii 2 (+ Bruno). PDF-y pozostałych 19 bajek masz z wcześniejszej paczki.
- `do_budowy/`: lista zadań, adresy bajek, robots, sitemap, projekty regulaminu i polityki prywatności.
- `katalog/bajki.json`: katalog 30 bajek.
