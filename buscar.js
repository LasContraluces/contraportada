// Buscador de La Contraportada: filtra buscar.json en el navegador.
(function () {
  var estado = document.getElementById('estado');
  var caja = document.getElementById('resultados');
  var campo = document.getElementById('buscar');
  var q = (new URLSearchParams(location.search).get('q') || '').trim();
  if (campo) campo.value = q;
  if (!q) return;

  function plano(t) {
    return t.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
  }
  function crear(etiqueta, clase, texto) {
    var el = document.createElement(etiqueta);
    if (clase) el.className = clase;
    if (texto) el.textContent = texto;
    return el;
  }

  estado.textContent = 'Buscando…';
  fetch('/buscar.json')
    .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
    .then(function (noticias) {
      var palabras = plano(q).split(/\s+/).filter(Boolean);
      var hallazgos = noticias.map(function (n) {
        var titulo = plano(n.t), resto = plano(n.x + ' ' + n.n + ' ' + n.o);
        var puntos = 0;
        for (var i = 0; i < palabras.length; i++) {
          if (titulo.indexOf(palabras[i]) !== -1) puntos += 3;
          else if (resto.indexOf(palabras[i]) !== -1) puntos += 1;
          else return null;
        }
        return { n: n, puntos: puntos };
      }).filter(Boolean).sort(function (a, b) { return b.puntos - a.puntos; });

      if (!hallazgos.length) {
        estado.textContent = 'No hay ninguna noticia con «' + q + '». Prueba con menos palabras o con otro nombre.';
        return;
      }
      estado.textContent = hallazgos.length + (hallazgos.length === 1 ? ' noticia con «' : ' noticias con «') + q + '»';
      hallazgos.forEach(function (h) {
        var n = h.n;
        var art = crear('article', 'tarjeta');
        var meta = crear('div', 'meta');
        var et = crear('a', 'etiqueta ' + n.s, n.n);
        et.href = '/' + n.s + '.html';
        meta.appendChild(et);
        meta.appendChild(crear('span', '', n.f + ' · ' + n.o));
        var h3 = crear('h3');
        var a = crear('a', '', n.t);
        a.href = n.u;
        h3.appendChild(a);
        art.appendChild(meta);
        art.appendChild(h3);
        art.appendChild(crear('p', '', n.e));
        caja.appendChild(art);
      });
    })
    .catch(function () {
      estado.textContent = 'No se ha podido cargar el buscador. Recarga la página para volver a intentarlo.';
    });
})();
