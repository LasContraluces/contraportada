# La Contraportada

Web de noticias de cine y series de Jose (Remy Lebeau), hermana de Las Contraluces.
Se publica con GitHub Pages en https://contraportada.lascontraluces.com (rama `main`, raíz).

## Cómo está montada

- `noticias/AAAA-MM-DD-slug.json`: una noticia por archivo. Es lo único que se escribe a mano.
- `datos/taquilla.json`, `datos/estrenos.json`, `datos/criticas.json`: las cajas de la columna lateral de la portada.
- `build.py`: genera `index.html`, las páginas de sección, `noticia/<slug>.html` y `feed.xml`. Solo necesita Python 3.
- Paginación: la portada enseña la apertura, tres secundarias y 12 noticias en «Lo último» (`EN_PORTADA`). Todo lo anterior, tráilers incluidos, pasa al archivo en `pagina/2.html`, `pagina/3.html`... con 21 noticias por página (`POR_PAGINA`). Las secciones también se paginan: `cine.html`, `cine/2.html`... Ninguna noticia desaparece de la web.
- `buscar.js`: el buscador. Filtra en el navegador el índice `buscar.json`, que genera `build.py` junto con `buscar.html`.
- `estilos.css`: todo el diseño. Fondo beige, naranja vivo en cabecera y titulares de apertura. No cambiar colores ni tipografías sin que Jose lo pida.
- Los `.html`, `feed.xml` y `buscar.json` son salida generada. Nunca editarlos a mano. Se suben también al repositorio como respaldo, aunque la versión que se publica la genera GitHub en cada push (con las imágenes).

## Publicar

1. Crear o modificar archivos en `noticias/` (y `datos/` si toca).
2. `python3 build.py`
3. `git add -A && git commit -m "..." && git push origin main`

**No se publica nada sin el visto bueno de Jose.** Él revisa cada noticia antes de que salga.

## Formato de una noticia

```json
{
  "titulo": "Titular en una frase, sin punto final",
  "seccion": "cine | series | plataformas | trailers | taquilla | fichajes | industria",
  "fecha": "2026-11-16T09:00",
  "portada": 1,
  "entradilla": "Una o dos frases que resumen la noticia.",
  "resumen": "Opcional. Versión más corta para las tarjetas.",
  "cuerpo": ["Párrafo 1.", "Párrafo 2."],
  "tmdb": "movie/1567605",
  "video": "Opcional: identificador de un vídeo oficial de YouTube",
  "pie_imagen": "Imagen de «Título»",
  "fuentes": [{"nombre": "Deadline", "url": "https://..."}]
}
```

- `portada`: `1` para la noticia de apertura (solo una), `2` para las tres secundarias. Si se omite, entra por fecha en «Lo último». Al publicar una apertura nueva, quitar el `portada` de la anterior. Los tráilers normalmente van en la columna «Tráilers de la semana», pero si llevan `portada` salen en la apertura o las secundarias, con el vídeo en lugar de la foto.
- Cuando Jose pasa una noticia suelta (un enlace, una captura), va de apertura (`portada: 1`) salvo que diga que quiere mantener la apertura: entonces va de secundaria (`portada: 2`). Una apertura nueva baja la anterior a «Lo último»; una secundaria nueva sustituye a la secundaria más antigua.
- En tráilers el titular es solo el título de la película o serie entre comillas angulares.
- `fecha` en hora de Madrid.

## Fuentes

Se buscan noticias en todos estos medios y cualquiera de ellos puede ir como fuente:

- Trades: The Hollywood Reporter, Variety, Deadline, IndieWire, Collider, Entertainment Weekly, Screen Daily, TheWrap.
- Otros medios de cine y series: Gold Derby, TV Guide, TVLine, One Mann's Movies, Is My Show Cancelled, Empire, Total Film, /Film, Vulture.
- Agregadores de redes: DiscussingFilm, Culture Crave, Film Updates.
- Datos de taquilla: Box Office Mojo, The Numbers.
- Comunicados oficiales de estudios y plataformas.

Si un medio recoge una noticia que dio otro («vía», «según informa»), se enlaza también al que la dio primero cuando se encuentre. Las imágenes nunca se cogen de estos medios. No se resumen webs españolas (Espinof, SensaCine, Fotogramas...).

Temas: estrenos de cine, series y plataformas. Cada noticia lleva enlace a la fuente original.

## Redacción

- Castellano natural y directo, frases cortas. Nada de «marca un punto de inflexión», «pone de manifiesto» ni lenguaje promocional. Sin emojis.
- Contar el hecho con datos concretos (cifras, nombres, fechas) y parar. No añadir análisis ni conclusiones.
- Redacción propia: no traducir ni calcar el artículo original. Entre uno y tres párrafos breves; quien quiera más, que vaya a la fuente. Como mucho una cita textual corta por fuente.
- Títulos de películas y series entre «comillas angulares», con el título español si está confirmado.
- Si un dato no está en la fuente, no se pone. Rumores y negociaciones se cuentan como tales, diciendo quién lo publica.

## Imágenes

Salen de estos sitios, y de ninguno más:

1. **TMDB.** Cada noticia sobre una película o serie lleva el campo `tmdb` con su referencia: `"movie/1567605"` o `"tv/95480"`. Es el final de la URL de su ficha en themoviedb.org, sin el nombre. Se encuentra buscando en la web el título junto a «themoviedb.org» (las fichas no se pueden abrir con WebFetch, pero la URL del resultado basta). Comprobar que el año y el director coinciden antes de usarla.
2. **Vídeo oficial en YouTube.** En los tráilers, y en cualquier noticia que tenga un vídeo oficial (un anuncio del estudio, por ejemplo), el campo `video` lleva el identificador del vídeo (lo que va tras `v=` en la URL), siempre del canal oficial del estudio o la plataforma. La página de la noticia incrusta el vídeo, y si la noticia es la apertura, también la portada en lugar de la foto. Nunca vídeos de cuentas que solo republican (DiscussingFilm, Culture Crave...).

3. **Wikimedia Commons**, solo para noticias que no van de una película o serie concreta (estudios, plataformas, industria, taquilla, festivales) y no tienen ficha de TMDB ni vídeo oficial. Solo imágenes **sin personas**: la fachada o el logotipo de un estudio o una plataforma, un cine, la sede de un festival, una ciudad de rodaje. Solo con licencia libre (dominio público, CC0, CC BY, CC BY-SA). Se pone con `imagen` (la URL directa del archivo en upload.wikimedia.org, en una versión de unos 1280 px de ancho) y `credito_imagen` con autor y licencia: «Autor, CC BY-SA 4.0, vía Wikimedia Commons». Antes de usarla, abrir la página del archivo en Commons y comprobar autor y licencia.

`build.py` pide a TMDB la imagen de fondo de cada referencia y, si no hay, usa la miniatura del tráiler o el póster. Solo puede hacerlo donde existe la variable `TMDB_API_KEY`, que está guardada como secreto del repositorio: las imágenes aparecen cuando la web se genera en GitHub (workflow `.github/workflows/publicar.yml`), no al ejecutar `build.py` en local. Es normal que en local salga sin fotos.

- `pie_imagen` es el texto alternativo de la foto: «Imagen de «Título»».
- **No se publican noticias sin foto.** Si no hay ficha de TMDB con imágenes, ni vídeo oficial, ni una imagen sin personas que encaje en Wikimedia Commons (una negociación sindical, un fichaje para un proyecto sin ficha), se avisa a Jose en el borrador («SIN FOTO: pásame una») y la noticia no se publica hasta que él la pase. Nunca se descarta una noticia por no tener foto: se propone igual y se le pide la foto.
- Nunca fotos de los medios (Deadline, Variety...) ni de agencias.
- Fotos de personas (actores, directores...): se pueden poner cuando Jose las pasa. Van con `imagen` y `credito_imagen`, con el crédito que él indique.
- `imagen` y `credito_imagen` permiten poner a mano una foto concreta; solo si Jose la pasa o lo pide.
