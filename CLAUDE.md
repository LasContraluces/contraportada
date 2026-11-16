# La Contraportada

Web de noticias de cine y series de Jose (Remy Lebeau), hermana de Las Contraluces.
Se publica con GitHub Pages en https://contraportada.lascontraluces.com (rama `main`, raíz).

## Cómo está montada

- `noticias/AAAA-MM-DD-slug.json`: una noticia por archivo. Es lo único que se escribe a mano.
- `datos/taquilla.json`, `datos/estrenos.json`, `datos/criticas.json`: las cajas de la columna lateral de la portada.
- `build.py`: genera `index.html`, las páginas de sección, `noticia/<slug>.html` y `feed.xml`. Solo necesita Python 3.
- `buscar.js`: el buscador. Filtra en el navegador el índice `buscar.json`, que genera `build.py` junto con `buscar.html`.
- `estilos.css`: todo el diseño. Fondo beige, naranja vivo en cabecera y titulares de apertura. No cambiar colores ni tipografías sin que Jose lo pida.
- Los `.html`, `feed.xml` y `buscar.json` son salida generada y van al repositorio (Pages no ejecuta nada). Nunca editarlos a mano.

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
  "pie_imagen": "Imagen: descripción de la foto que iría aquí",
  "fuentes": [{"nombre": "Deadline", "url": "https://..."}]
}
```

- `portada`: `1` para la noticia de apertura (solo una), `2` para las tres secundarias. Si se omite, entra por fecha en «Lo último». Al publicar una apertura nueva, quitar el `portada` de la anterior.
- En tráilers el titular es solo el título de la película o serie entre comillas angulares.
- `fecha` en hora de Madrid.

## Fuentes

Las noticias salen de medios primarios: The Hollywood Reporter, Variety, Deadline, IndieWire, Collider, Entertainment Weekly y Screen Daily. DiscussingFilm, Culture Crave y Film Updates sirven para detectar noticias, pero se enlaza al medio que la dio primero. No se resumen webs españolas (Espinof, SensaCine, Fotogramas...).

Temas: estrenos de cine, series y plataformas. Cada noticia lleva enlace a la fuente original.

## Redacción

- Castellano natural y directo, frases cortas. Nada de «marca un punto de inflexión», «pone de manifiesto» ni lenguaje promocional. Sin emojis.
- Contar el hecho con datos concretos (cifras, nombres, fechas) y parar. No añadir análisis ni conclusiones.
- Redacción propia: no traducir ni calcar el artículo original. Entre uno y tres párrafos breves; quien quiera más, que vaya a la fuente. Como mucho una cita textual corta por fuente.
- Títulos de películas y series entre «comillas angulares», con el título español si está confirmado.
- Si un dato no está en la fuente, no se pone. Rumores y negociaciones se cuentan como tales, diciendo quién lo publica.

## Imágenes

Todavía no hay. Cada pieza lleva un hueco gris con `pie_imagen`. No añadir fotos de medios ni de agencias, ni fotos de personas, hasta que Jose decida de dónde salen. Si una noticia trae el campo `imagen`, se usa.
