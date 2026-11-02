# jaspalmer.github.io

The site is built from `_src/` (GitHub Pages doesn't publish folders that start with `_`).

- **Add a card:** add an entry to `_src/cards.json`, then run `python3 _src/build.py --og`.
- **Change the site's name:** edit `SITE["name"]` at the top of `_src/build.py` and rebuild.
- **Edit the workshop page:** `_src/workshop.html`.
- **Colors and type:** `assets/site.css`.

`--og` re-renders the link-preview images in `og/`. It needs Playwright and the EB Garamond `.woff2` files (set `OG_FONTS` to their folder).
