# Léxico · Mazos

Catálogo público de mazos y teoría para la app [Léxico](https://github.com/CurranteAI/Lexico_Aleman).
La app lee `catalog.json` desde Ajustes → Mazos y teoría y descarga los archivos que elijas.

- `catalog.json`: lista de mazos y teoría disponibles.
- `decks/<id>.json`: un mazo. Cada palabra tiene un `id` estable; no lo cambies, porque los datos de cada usuario se asocian a ese id.
- `teoria/<id>.json`: un apartado de teoría.

Para añadir o cambiar contenido, edita estos archivos y actualiza `catalog.json`.
