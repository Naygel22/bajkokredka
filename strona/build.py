#!/usr/bin/env python3
"""Buduje wersję sklepu Bajkokredka na hosting: osobny, gotowy plik .html dla każdej podstrony.

  python3 build.py <katalog-zrodlowy> <katalog-wynikowy> [https://adres-sklepu.pl/]

Adresy podstron są bez końcówki .html (np. /kontakt); hosting (Cloudflare Pages) sam dobiera plik kontakt.html.

Źródło: index.html (jeden plik, adresy z #), bajki.js, img/, kolorowanki/, fonts/, og.jpg.
Wynik:  index.html, strona każdej bajki i kategorii, style/app z odciskiem w nazwie,
        sitemap.xml, robots.txt, 404.html.
Wymaga: python3, playwright (chromium), beautifulsoup4.
"""
import sys, os, re, json, shutil, hashlib, threading, datetime, functools
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

SRC, OUT = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
BASE = (sys.argv[3] if len(sys.argv) > 3 else 'https://bajkokredka.pl/').rstrip('/') + '/'
PORT = 8765

# 1. pliki statyczne
if os.path.exists(OUT): shutil.rmtree(OUT)
os.makedirs(OUT)
for d in ['img', 'kolorowanki', 'fonts']:
    shutil.copytree(os.path.join(SRC, d), os.path.join(OUT, d))
for f in ['og.jpg', 'bajki.js']:
    shutil.copy(os.path.join(SRC, f), os.path.join(OUT, f))

# 2. szablon: CSS i JS do osobnych plików (przeglądarka pobiera je raz dla wszystkich podstron)
html = open(os.path.join(SRC, 'index.html'), encoding='utf-8').read()
css = re.search(r'<style>\n(.*?)</style>', html, re.S)
js = re.search(r'<script src="bajki\.js"></script>\n<script>\n(.*?)</script>\n</body>', html, re.S)
assert css and js, 'Nie znaleziono <style> albo głównego <script> w index.html'
h = lambda t: hashlib.sha256(t.encode()).hexdigest()[:8]
css_name, js_name = f'style.{h(css.group(1))}.css', f'app.{h(js.group(1))}.js'
open(os.path.join(OUT, css_name), 'w', encoding='utf-8').write(css.group(1))
open(os.path.join(OUT, js_name), 'w', encoding='utf-8').write(js.group(1))
bajki_v = h(open(os.path.join(SRC, 'bajki.js'), encoding='utf-8').read())
tpl = html.replace(css.group(0), f'<link rel="stylesheet" href="{css_name}">')
tpl = tpl.replace(js.group(0), f'<script src="bajki.js?v={bajki_v}"></script>\n<script src="{js_name}"></script>\n</body>')
tpl = tpl.replace('<html lang="pl">', f'<html lang="pl" data-tryb="strony" data-baza="{BASE}">', 1)
assert 'data-tryb="strony"' in tpl
open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(tpl)

# 3. lokalny serwer + przeglądarka: każdą podstronę otwieramy i zapisujemy już wyrenderowaną
class Cichy(SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = ThreadingHTTPServer(('127.0.0.1', PORT), functools.partial(Cichy, directory=OUT))
threading.Thread(target=srv.serve_forever, daemon=True).start()

ZRZUT = """() => {
  document.querySelectorAll('main > [id^=widok-][hidden]').forEach(v => {
    v.querySelectorAll('#lista,#karuzela,#p-podobne,#p-inne,#k-polecane,#p-male,#p-postacie-lista,#strony,#wybor,#obrazki,#paleta,#k-lista,#z-lista,#s-opis,#g-lista').forEach(x => x.innerHTML = '');
    const t = document.createElement('template'); t.setAttribute('data-widok', ''); v.replaceWith(t); t.content.appendChild(v);
  });
  document.body.classList.remove('kup-widac');
  return '<!DOCTYPE html>\\n' + document.documentElement.outerHTML + '\\n';
}"""
strony, bledy = [], []
with sync_playwright() as p:
    br = p.chromium.launch(executable_path=os.environ.get('CHROME') or None); pg = br.new_page(viewport={'width': 1280, 'height': 900})
    pg.on('pageerror', lambda e: bledy.append(str(e)))
    pg.on('console', lambda m: bledy.append(m.text) if m.type == 'error' else None)
    pg.goto(f'http://127.0.0.1:{PORT}/index.html'); pg.wait_for_load_state('networkidle')
    info = pg.evaluate("""() => ({bajki: BAJKI.map(b => [b.id, plikBajki(b)]), pliki: PLIKI, landingi: Object.keys(LANDINGI)})""")
    # (plik, czy w mapie strony, priorytet, id bajki)
    strony.append(('index', True, '1.0', None))
    strony.append((info['pliki']['sklep'], True, '0.9', None))
    strony += [(k, True, '0.9', None) for k in info['landingi']]
    strony += [(info['pliki'][k], True, '0.7', None) for k in ['stworz', 'koloruj']]
    strony.append((info['pliki']['kontakt'], True, '0.3', None))
    strony += [(plik, True, '0.8', bid) for bid, plik in info['bajki']]
    strony += [(info['pliki']['koszyk'], False, None, None), ('404', False, None, None)]
    for plik, *_ in strony:
        sciezka = os.path.join(OUT, plik + '.html')
        if plik != 'index': open(sciezka, 'w', encoding='utf-8').write(tpl)
        pg.goto(f'http://127.0.0.1:{PORT}/{plik}.html'); pg.wait_for_load_state('networkidle')
        open(sciezka, 'w', encoding='utf-8').write(pg.evaluate(ZRZUT))
    br.close()
srv.shutdown()
# zamówienie zależy od koszyka klienta, więc zostaje zwykłym szablonem
open(os.path.join(OUT, info['pliki']['zamowienie'] + '.html'), 'w', encoding='utf-8').write(tpl)
assert not bledy, 'Błędy w przeglądarce:\n' + '\n'.join(bledy)

# 4. mapa strony i robots.txt
dzis = datetime.date.today().isoformat()
url = lambda plik: BASE + ('' if plik == 'index' else plik)
x = ['<?xml version="1.0" encoding="UTF-8"?>',
     '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">']
for plik, wmapie, prio, bid in strony:
    if not wmapie: continue
    obr = ''.join(f'<image:image><image:loc>{BASE}img/{bid}-{k}.jpg</image:loc></image:image>' for k in ['okladka', 's2', 's4', 's10', 's12']) if bid else ''
    x.append(f'  <url><loc>{url(plik)}</loc><lastmod>{dzis}</lastmod><priority>{prio}</priority>{obr}</url>')
x.append('</urlset>')
open(os.path.join(OUT, 'sitemap.xml'), 'w', encoding='utf-8').write('\n'.join(x) + '\n')
open(os.path.join(OUT, 'robots.txt'), 'w', encoding='utf-8').write(f'User-agent: *\nAllow: /\n\nSitemap: {BASE}sitemap.xml\n')

# 5. kontrola: każda podstrona ma własny tytuł, opis, adres kanoniczny, jeden nagłówek h1 i poprawne dane strukturalne
tytuly, opisy, problemy = {}, {}, []
for plik, wmapie, _, bid in strony:
    d = BeautifulSoup(open(os.path.join(OUT, plik + '.html'), encoding='utf-8').read(), 'lxml')
    for t in d.find_all('template'): t.decompose()
    tyt = d.title.string; op = d.find('meta', attrs={'name': 'description'})['content']
    kan = d.find('link', rel='canonical'); h1 = d.find_all('h1'); ld = d.find('script', id='dane-ld')
    if wmapie:
        if tyt in tytuly: problemy.append(f'{plik}: tytuł jak w {tytuly[tyt]}')
        if op in opisy: problemy.append(f'{plik}: opis jak w {opisy[op]}')
        tytuly[tyt] = plik; opisy[op] = plik
        if not kan or kan['href'] != url(plik): problemy.append(f'{plik}: zły adres kanoniczny {kan and kan["href"]}')
        if len(op) > 165: problemy.append(f'{plik}: opis ma {len(op)} znaków')
        if 'noindex' in d.find('meta', attrs={'name': 'robots'})['content']: problemy.append(f'{plik}: noindex')
    if len(h1) != 1: problemy.append(f'{plik}: liczba h1 = {len(h1)}')
    typy = [g['@type'] for g in json.loads(ld.string)['@graph']]
    if bid and 'Product' not in typy: problemy.append(f'{plik}: brak danych produktu')
    # obrazki w przyciskach (przycisk ma własną etykietę) i w ukrytych blokach mogą mieć pusty alt
    if any(not i.get('alt') for i in d.select('main img') if not i.find_parent('button') and not i.find_parent(hidden=True)): problemy.append(f'{plik}: obrazek bez opisu alt')
    for a in d.select('a[href]'):
        hr = a['href']
        if hr == '#glowna': continue
        if hr.startswith('#'): problemy.append(f'{plik}: link z # ({hr})')
        elif not re.match(r'^(https?:|mailto:|tel:|data:|\./)', hr) and '.' not in hr.split('/')[-1] and not os.path.exists(os.path.join(OUT, hr.split('#')[0] + '.html')): problemy.append(f'{plik}: link donikąd ({hr})')
print(f'Gotowe: {len(strony) + 1} plików .html w {OUT} (adres: {BASE})')
print('Kontrola:', 'bez uwag' if not problemy else '\n  ' + '\n  '.join(problemy))
sys.exit(1 if problemy else 0)
