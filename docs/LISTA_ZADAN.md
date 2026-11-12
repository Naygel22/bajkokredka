# Bajkokredka – lista zadań na start budowy (Claude Code)

Punkt wyjścia: `index.html` + `bajki.js` + `img/`, `kolorowanki/`, `fonts/` z podglądu (artefakt), katalog `katalog/bajki.json`, skrypty w głównym folderze.

## 1. Bez tego nie startujemy (prawo)
- [ ] Regulamin – projekt w `regulamin_projekt.md`. **Sprawdzić z prawnikiem**, uzupełnić dane firmy.
- [ ] Polityka prywatności – projekt w `polityka_prywatnosci_projekt.md`. **Sprawdzić z prawnikiem.**
- [ ] Baner zgody na cookies (Consent Mode v2), jeśli będą statystyki/marketing. Bez zgody – tylko niezbędne.
- [ ] Dane sprzedawcy w stopce i w regulaminie (nazwa, adres, NIP, e-mail).
- [ ] Rejestr zgód: newsletter (double opt-in), zgoda „14 dni” przy zakupie treści cyfrowych – zapisywać datę i treść zgody.

## 2. Sklep (funkcje)
- [ ] Prawdziwe adresy podstron zamiast `#...`: `/`, `/bajki`, `/bajki/<slug>` (gotowe slugi w `adresy_bajek.json`), `/stworz-bajke`, `/kontakt`, `/koszyk`, `/zamowienie`, `/regulamin`, `/polityka-prywatnosci`.
  Najprościej: framework z generowaniem stron statycznych (np. Astro / Next.js) – każda bajka = osobna strona HTML.
- [ ] Płatności: Przelewy24 / Tpay / Stripe (BLIK, przelew, karta). Webhook „opłacone” → wysyłka.
- [ ] Wysyłka PDF: po opłaceniu mail z linkami do pobrania (link ważny np. 30 dni, limit pobrań). Pliki PDF poza publicznym folderem.
- [ ] Koszyk i progi cen liczone **na serwerze** (1=29, 2=25/szt, 3=22/szt, 4+=19/szt; kod WITAJ10 = −10%, jednorazowy na adres e-mail).
- [ ] Faktury: automatycznie (np. Fakturownia / inFakt) po płatności; z NIP-em gdy klient zaznaczył fakturę.
- [ ] Bajka od zera: zamówienie → **moderacja AI na serwerze** (prompt jest w index.html: `MODERACJA`) → płatność → kolejka do produkcji → Twoja akceptacja → mail z PDF.
- [ ] Newsletter: MailerLite / Brevo, double opt-in, automatyczny mail z kodem WITAJ10 po potwierdzeniu, cotygodniowa kolorowanka.
- [ ] Formularz kontaktowy → mail do kontakt@bajkokredka.pl (+ antyspam: honeypot/Turnstile).

## 3. SEO i udostępnianie
- [ ] `<title>` i `<meta name="description">` na każdej stronie – teksty są już w index.html (obiekt `OPISY`, dla bajek: tytuł + opis z katalogu).
- [ ] Open Graph: `og.jpg` (1200×630, w tym folderze) dla stron ogólnych; dla bajek – okładka bajki jako `og:image`. Adresy w `og:*` muszą być **pełne** (https://bajkokredka.pl/...).
- [ ] `robots.txt` i `sitemap.xml` – gotowe w tym folderze (domena bajkokredka.pl – zmienić, jeśli inna). Sitemap generować automatycznie przy dodaniu bajki.
- [ ] Dane strukturalne `Product` (cena, dostępność) na stronach bajek – szansa na cenę w wynikach Google.
- [ ] Prawdziwa strona 404 (wygląd jest w index.html: `#widok-404`) zwracająca kod HTTP 404.
- [ ] Ikonki: favicon SVG jest w index.html; dodać PNG 32×32, 180×180 (Apple) i 512×512 (manifest).

## 4. Szybkość i dostępność
- [ ] Obrazki w WebP/AVIF, kilka rozmiarów (`srcset`), `loading="lazy"` poza pierwszym ekranem.
- [ ] Okładki w kartach jako `<img alt="Okładka bajki …">` (teraz tło + `role="img"`).
- [ ] Test Lighthouse ≥ 90 (wydajność, dostępność, SEO) na telefonie.

## 5. Statystyki
- [ ] Google Analytics 4 albo Plausible/Umami (Plausible/Umami nie wymagają banera cookies).
- [ ] Zdarzenia: dodanie do koszyka, rozpoczęcie zamówienia, zakup (z wartością), zapis do newslettera, wysłanie formularza bajki od zera.
- [ ] Google Search Console – zgłosić sitemap.

## 6. Treści do dorobienia
- [x] Nowe okładki Igora i Michasia.
- [ ] Darmowa próbka (3 strony do pobrania za e-mail) – dobry magnes na newsletter.
- [x] Zdjęcia „na żywo” (4 sztuki w sekcji „Tak wygląda bajka w domu”).
