# Bajkokredka – strona sklepu

- `hosting/` – gotowa strona do wgrania na serwer (wgraj całą zawartość do katalogu głównego domeny).
  Każda bajka i kategoria ma własny plik .html, jest też `sitemap.xml`, `robots.txt` i `404.html`.
- `podglad/` – źródło: jeden `index.html` (adresy z #), z którego powstaje `hosting/`. Ten sam plik działa jako podgląd w Claude.
- `build.py` – buduje `hosting/` ze źródła.

## Po dodaniu nowej bajki albo zmianie tekstów

    python3 build.py podglad hosting https://bajkokredka.pl/

Wymaga: python3, playwright (chromium), beautifulsoup4, lxml. Skrypt na końcu sprawdza każdą podstronę
(własny tytuł, opis, adres kanoniczny, jeden nagłówek h1, opisy obrazków, linki) i wypisuje uwagi.

Jeśli sklep będzie pod innym adresem niż https://bajkokredka.pl/, podaj go jako trzeci argument –
trafia do adresów kanonicznych, mapy strony i danych dla wyszukiwarek.

## Po wgraniu

1. Google Search Console: dodaj domenę i zgłoś `https://bajkokredka.pl/sitemap.xml`.
2. Ustaw na serwerze `404.html` jako stronę błędu 404.
3. Strona wysyła zdarzenia sklepu (view_item, add_to_cart, begin_checkout, add_payment_info, generate_lead)
   do `window.dataLayer` – wystarczy dodać Google Tag Manager albo GA4, żeby zacząć je zbierać.
