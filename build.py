#!/usr/bin/env python3
"""Genera La Contraportada a partir de noticias/*.json y datos/*.json.

Uso: python3 build.py
Salida: index.html, una página por sección, noticia/<slug>.html, feed.xml y el buscador (buscar.html, buscar.json).
No necesita nada más que Python 3.
"""
import json
import os
import re
import shutil
import urllib.request
from datetime import datetime
from html import escape as e
from pathlib import Path

RAIZ = Path(__file__).parent
URL = "https://contraportada.lascontraluces.com"

SECCIONES = {  # clave: (nombre en la barra, etiqueta en las piezas)
    "cine": ("Cine", "Cine"),
    "series": ("Series", "Series"),
    "plataformas": ("Plataformas", "Plataformas"),
    "trailers": ("Tráilers", "Tráiler"),
    "taquilla": ("Taquilla", "Taquilla"),
    "fichajes": ("Fichajes", "Fichajes"),
    "industria": ("Industria", "Industria"),
}
MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
MESES_LARGO = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
               "septiembre", "octubre", "noviembre", "diciembre"]
DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]


def cargar_noticias():
    noticias = []
    for ruta in sorted((RAIZ / "noticias").glob("*.json")):
        n = json.loads(ruta.read_text(encoding="utf-8"))
        n["slug"] = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", ruta.stem)
        n["dt"] = datetime.fromisoformat(n["fecha"])
        if n["seccion"] not in SECCIONES:
            raise SystemExit(f"{ruta.name}: sección desconocida «{n['seccion']}»")
        noticias.append(n)
    noticias.sort(key=lambda n: n["dt"], reverse=True)
    return noticias


def dato(nombre):
    ruta = RAIZ / "datos" / f"{nombre}.json"
    return json.loads(ruta.read_text(encoding="utf-8")) if ruta.exists() else None


def fecha_corta(dt):
    return f"{dt.day} {MESES[dt.month - 1]}"


def fecha_larga(dt):
    return f"{DIAS[dt.weekday()]}, {dt.day} de {MESES_LARGO[dt.month - 1]} de {dt.year}"


def enlace(n):
    return f"/noticia/{n['slug']}.html"


def etiqueta(n):
    return f'<a class="etiqueta {n["seccion"]}" href="/{n["seccion"]}.html">{e(SECCIONES[n["seccion"]][1])}</a>'


def nombres_fuentes(n):
    return ", ".join(f["nombre"] for f in n.get("fuentes", []))


TMDB_KEY = os.environ.get("TMDB_API_KEY", "").strip()
_tmdb = {}


def tmdb(ref):
    """Devuelve (fondo, poster) de TMDB para una referencia tipo movie/123 o tv/456."""
    if ref in _tmdb:
        return _tmdb[ref]
    resultado = (None, None)
    if TMDB_KEY and re.fullmatch(r"(movie|tv)/\d+", ref or ""):
        try:
            url = f"https://api.themoviedb.org/3/{ref}?api_key={TMDB_KEY}&language=es-ES"
            with urllib.request.urlopen(url, timeout=15) as r:
                d = json.load(r)
            resultado = (d.get("backdrop_path"), d.get("poster_path"))
        except Exception as error:  # una imagen que falla no debe tumbar la publicación
            print(f"TMDB {ref}: {error}")
    _tmdb[ref] = resultado
    return resultado


def imagen_de(n):
    """Elige la imagen de una noticia: la indicada a mano, la de TMDB o la miniatura del tráiler."""
    if n.get("imagen"):
        return n["imagen"], n.get("credito_imagen", "")
    fondo, poster = tmdb(n.get("tmdb"))
    if fondo:
        return f"https://image.tmdb.org/t/p/w1280{fondo}", "TMDB"
    if n.get("video"):
        return f"https://i.ytimg.com/vi/{n['video']}/hqdefault.jpg", "YouTube"
    if poster:
        return f"https://image.tmdb.org/t/p/w780{poster}", "TMDB"
    return None, ""


def video(n):
    return (f'<div class="video"><iframe src="https://www.youtube-nocookie.com/embed/{e(n["video"])}" '
            f'title="Vídeo: {e(n["titulo"])}" loading="lazy" '
            f'allow="encrypted-media; picture-in-picture; fullscreen" allowfullscreen></iframe></div>')


def foto(n, enlazar=True):
    url, _ = imagen_de(n)
    if not url:
        return ""
    img = f'<img src="{e(url)}" alt="{e(n.get("pie_imagen", ""))}" loading="lazy">'
    if enlazar:
        return f'<a class="foto" href="{enlace(n)}" tabindex="-1" aria-hidden="true">{img}</a>'
    return f'<div class="foto">{img}</div>'


def pagina(titulo, descripcion, cuerpo, activa="", ruta="/", hoy=None):
    barra = [f'<a href="/" class="{"activa" if activa == "portada" else ""}">Portada</a>']
    for clave in ["cine", "series", "plataformas", "trailers", "taquilla", "fichajes"]:
        clases = " ".join(c for c in [clave if clave in ("cine", "series") else "", "activa" if activa == clave else ""] if c)
        barra.append(f'<a href="/{clave}.html" class="{clases}">{SECCIONES[clave][0]}</a>')
    barra.append('<a href="https://lascontraluces.com/">Críticas</a>')
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{e(titulo)}</title>
<meta name="description" content="{e(descripcion)}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="La Contraportada">
<meta property="og:title" content="{e(titulo)}">
<meta property="og:description" content="{e(descripcion)}">
<link rel="canonical" href="{URL}{ruta}">
<link rel="alternate" type="application/rss+xml" title="La Contraportada" href="{URL}/feed.xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,500;0,9..144,600;1,9..144,500&family=IBM+Plex+Sans:wght@400;500;600&display=swap">
<link rel="stylesheet" href="/estilos.css">
</head>
<body>
<div class="franja"><div class="ancho">
<span>{e(fecha_larga(hoy))}</span>
<nav aria-label="Otras webs"><a href="https://lascontraluces.com/">Archivo de reseñas</a><a href="https://lascontraluces.com/podcasts.html">Podcasts</a><a href="https://linktr.ee/lacontraludica">La Contralúdica ↗</a></nav>
</div></div>
<header class="cabecera"><div class="ancho">
<div class="marca-grupo">
<a class="marca" href="/">La Contraportada</a>
<span class="submarca">las noticias de <a href="https://lascontraluces.com/">Las Contraluces</a></span>
</div>
<form class="buscador" action="/buscar.html" method="get" role="search">
<label for="buscar">Buscar noticias</label>
<div class="buscador-fila"><input id="buscar" name="q" type="search" placeholder="Título, actor, plataforma" autocomplete="off"><button type="submit">Buscar</button></div>
</form>
</div></header>
<nav class="secciones" aria-label="Secciones"><div class="ancho">
{chr(10).join(barra)}
</div></nav>
<main class="ancho">
{cuerpo}
</main>
<footer class="pie"><div class="ancho">
<span class="lema">Cine, series, libros y juegos, mirados a contraluz.</span>
<span>Cada noticia enlaza a su fuente original. <a href="/feed.xml">RSS</a></span>
<span class="aviso">Imágenes de películas y series: <a href="https://www.themoviedb.org/">TMDB</a>. Este sitio usa la API de TMDB, pero no está avalado ni certificado por TMDB.</span>
</div></footer>
</body>
</html>
"""


def tarjeta(n):
    return f"""<article class="tarjeta">
{foto(n)}
<div class="meta">{etiqueta(n)}<span>{fecha_corta(n["dt"])} · {e(nombres_fuentes(n))}</span></div>
<h3><a href="{enlace(n)}">{e(n["titulo"])}</a></h3>
<p>{e(n.get("resumen") or n["entradilla"])}</p>
</article>"""


def fila(n):
    return f"""<article class="fila">
{foto(n)}
<div class="texto">
<h3><a href="{enlace(n)}">{e(n["titulo"])}</a></h3>
<p>{e(n.get("resumen") or n["entradilla"])}</p>
<p class="fuente">{fecha_corta(n["dt"])} · {e(nombres_fuentes(n))}</p>
</div>
</article>"""


def cajas_laterales():
    partes = []
    taq = dato("taquilla")
    if taq:
        filas = "".join(
            f'<li><span class="puesto">{i}</span><span class="nombre">{e(p["titulo"])}</span><span class="cifra">{e(p["cifra"])}</span></li>'
            for i, p in enumerate(taq["lista"], 1))
        partes.append(f'<div class="caja"><h2>Taquilla de EE. UU.</h2><p class="nota">{e(taq["periodo"])}</p><ol>{filas}</ol><p class="nota">Fuente: {e(taq["fuente"])}</p></div>')
    est = dato("estrenos")
    if est:
        filas = "".join(
            f'<li><span class="dia {"cines" if p["donde"] == "cines" else ""}">{e(p["dia"])}</span><span class="nombre">{e(p["titulo"])} <span class="donde">· {e(p["donde"])}</span></span></li>'
            for p in est["lista"])
        partes.append(f'<div class="caja"><h2>Llega esta semana</h2><p class="nota">{e(est["nota"])}</p><ul>{filas}</ul></div>')
    cri = dato("criticas")
    if cri:
        filas = "".join(
            f'<li class="critica"><a href="{e(p["url"])}">{e(p["titulo"])}</a><span>{e(p["frase"])}</span></li>'
            for p in cri["lista"])
        partes.append(f'<div class="caja"><h2>Últimas críticas</h2><ul>{filas}</ul><a class="mas" href="https://lascontraluces.com/">Ir al archivo de reseñas</a></div>')
    return "\n".join(partes)


def portada(noticias, hoy):
    sin_trailers = [n for n in noticias if n["seccion"] != "trailers"]
    principal = next((n for n in sin_trailers if n.get("portada") == 1), None) or (sin_trailers[0] if sin_trailers else None)
    if not principal:
        return pagina("La Contraportada — Noticias de cine y series", "Noticias de cine y series.", '<p class="vacio">Todavía no hay noticias.</p>', "portada", "/", hoy)
    resto = [n for n in sin_trailers if n is not principal]
    secundarias = [n for n in resto if n.get("portada") == 2][:3]
    for n in resto:
        if len(secundarias) >= 3:
            break
        if n not in secundarias:
            secundarias.append(n)
    ultimas = [n for n in resto if n not in secundarias][:6]
    trailers = [n for n in noticias if n["seccion"] == "trailers"][:4]

    sec = "".join(f"""<article>
<div class="meta">{etiqueta(n)}<span>{fecha_corta(n["dt"])}</span></div>
<h2><a href="{enlace(n)}">{e(n["titulo"])}</a></h2>
<p>{e(n.get("resumen") or n["entradilla"])}</p>
<p class="fuente">Fuente: {e(nombres_fuentes(n))}</p>
</article>""" for n in secundarias)

    cuerpo = f"""<section class="apertura">
<article class="principal">
{video(principal) if principal.get("video") else foto(principal)}
<div class="meta">{etiqueta(principal)}<span>{fecha_corta(principal["dt"])}</span></div>
<h1><a href="{enlace(principal)}">{e(principal["titulo"])}</a></h1>
<p class="entradilla">{e(principal["entradilla"])}</p>
<p class="fuente">Fuente: {e(nombres_fuentes(principal))}</p>
</article>
<div class="secundarias">{sec}</div>
</section>"""
    if ultimas:
        cuerpo += f"""
<section class="bloque">
<div class="titulo-seccion"><h2>Lo último</h2></div>
<div class="rejilla">{"".join(tarjeta(n) for n in ultimas)}</div>
</section>"""
    lateral = cajas_laterales()
    if trailers or lateral:
        columna = ""
        if trailers:
            columna = f'<div class="columna"><div class="titulo-seccion"><h2>Tráilers de la semana</h2><a href="/trailers.html">Ver todos</a></div>{"".join(fila(n) for n in trailers)}</div>'
        cuerpo += f'\n<section class="dos-columnas">{columna}<aside class="lateral">{lateral}</aside></section>'
    return pagina("La Contraportada — Noticias de cine y series",
                  "Noticias de cine y series de Las Contraluces: estrenos, taquilla, fichajes, renovaciones y tráilers, con enlace a la fuente original.",
                  cuerpo, "portada", "/", hoy)


def pagina_seccion(clave, noticias, hoy):
    nombre = SECCIONES[clave][0]
    propias = [n for n in noticias if n["seccion"] == clave]
    lista = f'<div class="rejilla">{"".join(tarjeta(n) for n in propias)}</div>' if propias else '<p class="vacio">Todavía no hay noticias en esta sección.</p>'
    cuerpo = f'<section class="bloque"><div class="cabecera-seccion"><h1>{e(nombre)}</h1></div>{lista}</section>'
    return pagina(f"{nombre} — La Contraportada", f"Noticias de {nombre.lower()} en La Contraportada.", cuerpo, clave, f"/{clave}.html", hoy)


def pagina_noticia(n, noticias, hoy):
    parrafos = "".join(f"<p>{e(p)}</p>" for p in n.get("cuerpo", []))
    fuentes = ", ".join(f'<a href="{e(f["url"])}" rel="noopener">{e(f["nombre"])}</a>' for f in n.get("fuentes", []))
    otras = [o for o in noticias if o is not n][:3]
    if n.get("video"):
        medio = video(n)
    else:
        _, credito = imagen_de(n)
        medio = foto(n, enlazar=False)
        if medio and credito:
            medio += f'<p class="credito">Imagen: {e(credito)}</p>'
    cuerpo = f"""<article class="noticia">
<div class="meta">{etiqueta(n)}<span>{e(fecha_larga(n["dt"]))}</span></div>
<h1>{e(n["titulo"])}</h1>
<p class="entradilla">{e(n["entradilla"])}</p>
{medio}
<div class="cuerpo">{parrafos}</div>
<p class="fuentes">Fuente original: {fuentes}</p>
</article>
<section class="bloque">
<div class="titulo-seccion"><h2>Más noticias</h2><a href="/">Volver a la portada</a></div>
<div class="rejilla">{"".join(tarjeta(o) for o in otras)}</div>
</section>"""
    return pagina(f"{n['titulo']} — La Contraportada", n["entradilla"], cuerpo, n["seccion"], enlace(n), hoy)


def pagina_buscar(hoy):
    cuerpo = """<section class="bloque">
<div class="cabecera-seccion"><h1>Buscar</h1></div>
<p id="estado" class="vacio" aria-live="polite">Escribe arriba lo que buscas: un título, un actor, una plataforma.</p>
<div id="resultados" class="rejilla"></div>
</section>
<script src="/buscar.js"></script>"""
    return pagina("Buscar — La Contraportada", "Busca entre las noticias de La Contraportada.", cuerpo, "", "/buscar.html", hoy)


def indice(noticias):
    return json.dumps([{
        "t": n["titulo"], "e": n.get("resumen") or n["entradilla"],
        "x": " ".join([n["entradilla"]] + n.get("cuerpo", [])),
        "s": n["seccion"], "n": SECCIONES[n["seccion"]][1], "f": fecha_corta(n["dt"]),
        "u": enlace(n), "o": nombres_fuentes(n),
    } for n in noticias], ensure_ascii=False)


def feed(noticias):
    items = "".join(f"""<item><title>{e(n["titulo"])}</title><link>{URL}{enlace(n)}</link><guid>{URL}{enlace(n)}</guid>
<pubDate>{n["dt"].strftime("%a, %d %b %Y %H:%M:%S +0100")}</pubDate><description>{e(n["entradilla"])}</description></item>
""" for n in noticias[:30])
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel>
<title>La Contraportada</title><link>{URL}/</link>
<description>Noticias de cine y series de Las Contraluces</description><language>es</language>
{items}</channel></rss>
"""


def main():
    noticias = cargar_noticias()
    hoy = noticias[0]["dt"] if noticias else datetime.now()
    (RAIZ / "index.html").write_text(portada(noticias, hoy), encoding="utf-8")
    for clave in SECCIONES:
        (RAIZ / f"{clave}.html").write_text(pagina_seccion(clave, noticias, hoy), encoding="utf-8")
    salida = RAIZ / "noticia"
    if salida.exists():
        shutil.rmtree(salida)
    salida.mkdir()
    for n in noticias:
        (salida / f"{n['slug']}.html").write_text(pagina_noticia(n, noticias, hoy), encoding="utf-8")
    (RAIZ / "feed.xml").write_text(feed(noticias), encoding="utf-8")
    (RAIZ / "buscar.html").write_text(pagina_buscar(hoy), encoding="utf-8")
    (RAIZ / "buscar.json").write_text(indice(noticias), encoding="utf-8")
    print(f"{len(noticias)} noticias, {len(SECCIONES)} secciones")


if __name__ == "__main__":
    main()
