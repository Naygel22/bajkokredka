# Bajkokredka – sklep z bajkami do kolorowania

Hosting: **Cloudflare Pages** (strona statyczna + funkcje serwerowe).

## Co gdzie jest

| Folder | Co to jest |
|---|---|
| `public/` | Gotowa strona, którą widzą klienci (42 podstrony, obrazki, sitemap). **Nie edytuj ręcznie**, powstaje z `build.py`. |
| `strona/podglad/` | Źródło strony: jeden `index.html` + `bajki.js` + obrazki. Tu wprowadza się zmiany. |
| `strona/build.py` | Generator: z `podglad/` robi `public/`. |
| `functions/api/` | Część serwerowa (płatności, maile, newsletter). Każdy plik = jeden adres `/api/...`. |
| `docs/` | Instrukcja budowy, lista zadań, projekty regulaminu i polityki prywatności, katalog bajek. |

## Po zmianie strony albo dodaniu bajki

```
cd strona
python3 build.py podglad ../public https://bajkokredka.pl/
```

Skrypt na końcu musi wypisać `Kontrola: bez uwag`. Potem `git push`, a Cloudflare sam opublikuje nową wersję.

Wymaga: python3, playwright (`pip install playwright beautifulsoup4 lxml` i `playwright install chromium`).

## Ustawienia w Cloudflare Pages

- Framework preset: **None**
- Build command: *(puste)*
- Build output directory: **public**

Adresy podstron są bez `.html` (np. `/kontakt`), a nieistniejące adresy pokazują `404.html` z kodem 404.

## Zasady

- **Pliki PDF nigdy nie trafiają do repozytorium** (pilnuje tego `.gitignore`). Leżą w prywatnym magazynie plików, a klient dostaje link po zapłacie.
- **Klucze (Stripe, maile itd.) nigdy nie trafiają do kodu.** Wpisuje się je w Cloudflare: projekt → Settings → Variables and Secrets.
