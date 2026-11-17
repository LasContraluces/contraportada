#!/usr/bin/env python3
"""Publica en Bluesky, de una en una, las noticias nuevas de La Contraportada.

Lo ejecuta cada media hora el workflow .github/workflows/bluesky.yml.
En cada pasada publica como mucho UNA noticia: la más antigua que aún no esté en Bluesky.
Si la última publicación de la cuenta es de hace menos de 25 minutos, no hace nada.

Para saber qué noticias ya están publicadas no guarda nada: mira los enlaces de los
últimos posts de la cuenta. Solo tiene en cuenta noticias con fecha desde INICIO y de
los últimos DIAS_ATRAS días, para no volcar el archivo entero.

Necesita los secretos BLUESKY_HANDLE y BLUESKY_APP_PASSWORD (una contraseña de aplicación).
Solo usa la biblioteca estándar de Python.
"""
import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timedelta, timezone
from html import unescape
from pathlib import Path
from zoneinfo import ZoneInfo

RAIZ = Path(__file__).parent
URL = "https://contraportada.lascontraluces.com"
SERVIDOR = "https://bsky.social/xrpc"
MADRID = ZoneInfo("Europe/Madrid")
INICIO = datetime(2026, 11, 18, 0, 0, tzinfo=MADRID)  # noticias anteriores no se publican
DIAS_ATRAS = 2
MINUTOS_ENTRE_POSTS = 25   # margen por si GitHub retrasa la pasada de cada media hora
MAX_IMAGEN = 950_000       # Bluesky no acepta miniaturas de más de ~1 MB
AGENTE = "LaContraportada-Bluesky/1.0"


def peticion(metodo, ruta, token=None, datos=None, tipo="application/json", crudo=False):
    url = ruta if ruta.startswith("http") else f"{SERVIDOR}/{metodo}{ruta}"
    cabeceras = {"User-Agent": AGENTE}
    if token:
        cabeceras["Authorization"] = f"Bearer {token}"
    cuerpo = None
    if datos is not None:
        cuerpo = datos if isinstance(datos, bytes) else json.dumps(datos).encode()
        cabeceras["Content-Type"] = tipo
    with urllib.request.urlopen(urllib.request.Request(url, cuerpo, cabeceras), timeout=30) as r:
        contenido = r.read()
    return contenido if crudo else json.loads(contenido)


def descargar(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": AGENTE}), timeout=30) as r:
        return r.read(), r.headers.get("Content-Type", "image/jpeg").split(";")[0]


def pendientes():
    ahora = datetime.now(MADRID)
    lista = []
    for ruta in (RAIZ / "noticias").glob("*.json"):
        n = json.loads(ruta.read_text(encoding="utf-8"))
        dt = datetime.fromisoformat(n["fecha"]).replace(tzinfo=MADRID)
        if dt < INICIO or dt < ahora - timedelta(days=DIAS_ATRAS) or dt > ahora:
            continue
        slug = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", ruta.stem)
        lista.append((dt, f"{URL}/noticia/{slug}.html", n))
    return sorted(lista, key=lambda x: x[0])


def meta(html, nombre):
    m = re.search(rf'<meta (?:property|name)="{re.escape(nombre)}" content="([^"]*)"', html)
    return unescape(m.group(1)) if m else ""


def miniatura(token, url_imagen):
    candidatas = [url_imagen]
    if "image.tmdb.org" in url_imagen:  # si pesa demasiado, una versión más pequeña
        candidatas += [re.sub(r"/w\d+/", "/w780/", url_imagen), re.sub(r"/w\d+/", "/w500/", url_imagen)]
    for url in candidatas:
        try:
            datos, tipo = descargar(url)
        except Exception as error:
            print(f"No se pudo bajar la imagen {url}: {error}")
            continue
        if len(datos) <= MAX_IMAGEN:
            return peticion("com.atproto.repo.uploadBlob", "", token, datos, tipo)["blob"]
    print("Sin miniatura: la imagen pesa demasiado.")
    return None


def main():
    usuario, clave = os.environ.get("BLUESKY_HANDLE"), os.environ.get("BLUESKY_APP_PASSWORD")
    if not usuario or not clave:
        print("Faltan BLUESKY_HANDLE o BLUESKY_APP_PASSWORD: no se publica nada.")
        return

    sesion = peticion("com.atproto.server.createSession", "", datos={"identifier": usuario, "password": clave})
    token, did = sesion["accessJwt"], sesion["did"]

    feed = peticion("app.bsky.feed.getAuthorFeed", f"?actor={did}&limit=100&filter=posts_no_replies", token)["feed"]
    propios = [p["post"] for p in feed if p["post"]["author"]["did"] == did]
    ya = {p["record"].get("embed", {}).get("external", {}).get("uri") for p in propios}

    if propios:
        ultimo = max(datetime.fromisoformat(p["record"]["createdAt"].replace("Z", "+00:00")) for p in propios)
        if datetime.now(timezone.utc) - ultimo < timedelta(minutes=MINUTOS_ENTRE_POSTS):
            print(f"El último post es de {ultimo:%H:%M} UTC: toca esperar.")
            return

    cola = [(dt, url, n) for dt, url, n in pendientes() if url not in ya]
    if not cola:
        print("Nada pendiente.")
        return

    dt, url, n = cola[0]
    try:  # la página tiene que estar ya en la web; si no, se intenta en la siguiente pasada
        html = descargar(url)[0].decode("utf-8")
    except Exception as error:
        print(f"{url} todavía no está publicada ({error}).")
        return

    tarjeta = {"uri": url, "title": n["titulo"],
               "description": meta(html, "og:description") or n["entradilla"]}
    imagen = meta(html, "og:image")
    if imagen:
        blob = miniatura(token, imagen)
        if blob:
            tarjeta["thumb"] = blob

    texto = n["titulo"]
    registro = {
        "$type": "app.bsky.feed.post",
        "text": texto,
        "langs": ["es"],
        "createdAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "embed": {"$type": "app.bsky.embed.external", "external": tarjeta},
    }
    peticion("com.atproto.repo.createRecord", "", token, {"repo": did, "collection": "app.bsky.feed.post", "record": registro})
    print(f"Publicada: {texto} ({len(cola) - 1} en cola)")


if __name__ == "__main__":
    try:
        main()
    except urllib.error.HTTPError as error:
        print(f"Error de Bluesky {error.code}: {error.read().decode(errors='replace')[:500]}")
        sys.exit(1)
