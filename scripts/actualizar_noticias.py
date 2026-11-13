
#!/usr/bin/env python3
"""Actualiza titulares desde RSS público sin dependencias externas."""
import datetime as dt
import email.utils
import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

QUERIES = [
    'literatura libros premios literarios España',
    'novedades editoriales novelas escritores',
    'feria del libro presentaciones autores España',
]
HEADERS = {'User-Agent': 'BibliotecaNuevoRecreo/1.0 (lector de RSS)'}
ROOT = Path(__file__).resolve().parents[1]

def clean(s):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]*>', '', s or '')).strip()

def main():
    noticias, vistos = [], set()
    for q in QUERIES:
        url = 'https://news.google.com/rss/search?' + urllib.parse.urlencode({'q': q, 'hl': 'es', 'gl': 'ES', 'ceid': 'ES:es'})
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), timeout=20) as r:
                xml = r.read(1_500_000)
            root = ET.fromstring(xml)
            for item in root.findall('./channel/item'):
                titulo = clean(item.findtext('title'))[:180]
                enlace = (item.findtext('link') or '').strip()
                if not titulo or not enlace.startswith('https://'):
                    continue
                key = titulo.casefold()
                if key in vistos:
                    continue
                fecha_raw = item.findtext('pubDate') or ''
                try:
                    fecha = email.utils.parsedate_to_datetime(fecha_raw).astimezone(dt.timezone.utc).date().isoformat()
                except (ValueError, TypeError, OverflowError):
                    fecha = ''
                fuente = clean(item.findtext('source') or 'Google Noticias')[:80]
                vistos.add(key)
                noticias.append({'titulo': titulo, 'url': enlace, 'fuente': fuente, 'fecha': fecha})
        except Exception as e:
            print('No se pudo leer un RSS:', type(e).__name__, str(e))
    if not noticias:
        raise SystemExit('Sin resultados: se conserva el archivo anterior para evitar borrar noticias.')
    noticias.sort(key=lambda x: x['fecha'], reverse=True)
    payload = {'actualizado': dt.datetime.now(dt.timezone.utc).isoformat(timespec='minutes'), 'noticias': noticias[:18]}
    (ROOT / 'noticias-auto.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Titulares guardados:', len(payload['noticias']))

if __name__ == '__main__':
    main()
  
