#!/usr/bin/env python3
"""Build the site from _src/.

    python3 _src/build.py          # rebuild every page and the feed
    python3 _src/build.py --og     # also re-render the link-preview images (needs Playwright)

To add a card: add an entry to _src/cards.json and rebuild.
Folders that start with "_" are not published by GitHub Pages, so _src/ stays private.
"""
import datetime
import html
import json
import os
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "_src"

# ── Change the site's name (and anything else site-wide) here. ──
SITE = {
    "name": "Monk’s Path",
    "author": "Jasper Palmer",
    "base": "https://jaspalmer.github.io",
    "email": "jaspalmer@proton.me",
    "substack": "https://jaspalmer.substack.com",
    "description": "Epiphany engines. Film, sound, prose.",
    "updated": datetime.date(2026, 11, 1),
}

# Quotation marks in each language's own reckoning.
MARKS = {"en": ("“", "”"), "de": ("„", "“"), "it": ("«", "»")}

e = html.escape


def long_date(d):
    return f"{d.day} {d.strftime('%B %Y')}"


def quoted(text, lang):
    o, c = MARKS.get(lang, MARKS["en"])
    return f"{o}{text}{c}"


def sort_key(card):
    t = card["title"].lower()
    for article in ("the ", "a ", "an "):
        if t.startswith(article):
            t = t[len(article):]
    return t


def attribution(card):
    parts = [e(card["maker"]) + (f", {e(card['year'])}" if card.get("year") else "")]
    if card.get("note"):
        parts.append(e(card["note"]))
    return " &middot; ".join(parts)


GLYPH = '<div class="glyph" aria-hidden="true"><i></i><i></i><i></i><i></i><i></i></div>'


def placard(card, link_title=False):
    lang = card.get("lang", "en")
    title = e(card["title"])
    if link_title:
        title = f'<a href="/circa/{card["slug"]}/">{title}</a>'
    out = [
        '<article class="card">',
        '  <div class="label">From the concordance</div>',
        f'  <h1 class="card-title">{title}</h1>',
        f'  <div class="card-attr">{attribution(card)}</div>',
        f'  <p class="face" lang="{lang}">{e(quoted(card["door"], lang))}</p>',
    ]
    if card.get("door_gloss"):
        out.append(f'  <p class="gloss">{e(card["door_gloss"])}</p>')
    if card.get("exit"):
        out.append("  " + GLYPH)
        out.append(f'  <p class="face face--exit" lang="{lang}">{e(quoted(card["exit"], lang))}</p>')
        if card.get("exit_gloss"):
            out.append(f'  <p class="gloss">{e(card["exit_gloss"])}</p>')
    out.append("</article>")
    return "\n".join(out)


def draw_script(cards):
    slugs = json.dumps([c["slug"] for c in cards])
    return (
        "<script>(function(){var C=" + slugs + ";"
        "document.querySelectorAll('[data-draw]').forEach(function(a){a.addEventListener('click',function(ev){"
        "ev.preventDefault();var s,here=location.pathname;"
        "do{s=C[Math.floor(Math.random()*C.length)]}while(C.length>1&&here.indexOf('/'+s+'/')>-1);"
        "location.href='/circa/'+s+'/';});});})();</script>"
    )


NAV = [("/circa/", "Concordance"), ("/workshop/", "Workshop"), ("/resume.pdf", "R&eacute;sum&eacute;"), ("/#about", "About")]


def page(*, path, title, description, body, colophon, og_image, cards, og_type="website"):
    nav = "\n      ".join(
        f'<a href="{href}"{" aria-current=\"page\"" if href == path else ""}>{label}</a>' for href, label in NAV
    )
    url = SITE["base"] + path
    full_title = title if path == "/" else f"{title} — {SITE['name']}"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{e(full_title)}</title>
<meta name="description" content="{e(description)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="{e(SITE['name'])}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(description)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE['base']}/og/{og_image}.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="alternate" type="application/rss+xml" title="{e(SITE['name'])}" href="/feed.xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;0,600;1,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/site.css">
</head>
<body>
<div class="wrap">

  <header class="masthead">
    <a class="sitename" href="/">{e(SITE['name'])}</a>
    <nav>
      {nav}
    </nav>
  </header>

{body}

  <footer class="colophon">
    <p class="colophon-text">{colophon}</p>
    <div class="colophon-meta">
      <span class="label">Updated {long_date(SITE['updated'])}</span>
      <span class="label">Set in EB Garamond</span>
    </div>
  </footer>

</div>
{draw_script(cards)}
</body>
</html>
"""


WORKSHOP_LINK = ' <a href="/workshop/">How I work with AI</a>'


def build_home(cards):
    featured = next((c for c in cards if c.get("featured")), cards[0])
    n = len(cards)
    body = f"""{placard(featured, link_title=True)}
  <div class="after-card">
    <a class="draw" href="/circa/" data-draw>Draw another card</a>
    <a href="/circa/">All {n} cards</a>
  </div>

  <p class="stance">Amidst derision, a vision. <em>Epiphany engines</em> &mdash; in film, in sound, in prose.</p>
  <p class="byline">Jasper Palmer, Northern Virginia. &nbsp;<a href="mailto:{SITE['email']}">Write to me</a> &middot; <a href="/resume.pdf">R&eacute;sum&eacute;</a></p>

  <section class="section" id="rooms">
    <div class="section-head"><span class="label">Rooms</span></div>
    <a class="entry" href="/circa/">
      <div class="entry-title">The Concordance</div>
      <div class="entry-meta">{n} cards &middot; a work&rsquo;s title and the lines lifted from it</div>
    </a>
    <a class="entry" href="/workshop/">
      <div class="entry-title">How I work with AI</div>
      <div class="entry-meta">The workshop &middot; what the machine touched, and what it didn&rsquo;t</div>
    </a>
    <a class="entry" href="{SITE['substack']}">
      <div class="entry-title">Letters</div>
      <div class="entry-meta">By email, on Substack</div>
    </a>
  </section>

  <section class="section" id="about">
    <div class="section-head"><span class="label">About</span></div>
    <p>I make things out of what other people left behind &mdash; public-domain film, forgotten text, the archive&rsquo;s discard pile &mdash; and arrange them so something turns over in the person receiving them.</p>
    <p>A <a href="/circa/">concordance</a> of 159 cards is underway. Essays and films when they&rsquo;re finished.</p>
  </section>"""
    return page(
        path="/",
        title=f"{SITE['name']} — {SITE['author']}",
        description=SITE["description"],
        body=body,
        colophon="Site built with Claude (Anthropic)." + WORKSHOP_LINK,
        og_image="home",
        cards=cards,
    )


def build_index(cards):
    rows = []
    for c in sorted(cards, key=sort_key):
        meta = e(c["maker"]) + (f" &middot; {e(c['year'])}" if c.get("year") else "")
        rows.append(
            f'    <a class="entry" href="/circa/{c["slug"]}/">\n'
            f'      <div class="entry-title">{e(c["title"])}</div>\n'
            f'      <div class="entry-meta">{meta}</div>\n'
            f"    </a>"
        )
    body = f"""  <div class="prose">
  <h1 class="page-title">The Concordance</h1>
  <p class="lede">Each card is a work&rsquo;s real title and a line or two lifted from it, exactly as written: a door, and where there is one, an exit.</p>
  <p>Quotation marks follow each language&rsquo;s own custom. Cards are listed by title. {len(cards)} so far.</p>
  </div>
  <div class="after-card" style="margin-top:22px">
    <a class="draw" href="/circa/" data-draw>Draw a card</a>
  </div>

  <section class="section">
{chr(10).join(rows)}
  </section>"""
    return page(
        path="/circa/",
        title="The Concordance",
        description=f"{len(cards)} cards: a work’s title and the lines lifted from it.",
        body=body,
        colophon="Works chosen and lines lifted by Jasper Palmer. Pages built with Claude (Anthropic)." + WORKSHOP_LINK,
        og_image="circa",
        cards=cards,
    )


def build_card(card, cards):
    lang = card.get("lang", "en")
    desc = quoted(card["door"], lang) + (f" … {quoted(card['exit'], lang)}" if card.get("exit") else "")
    body = f"""{placard(card)}
  <div class="after-card">
    <a class="draw" href="/circa/" data-draw>Draw another card</a>
    <a href="/circa/">All cards</a>
  </div>"""
    colophon = "Work chosen and lines lifted by Jasper Palmer. Page built with Claude (Anthropic)."
    if card.get("door_gloss") or card.get("exit_gloss"):
        colophon += " English glosses are working translations."
    return page(
        path=f"/circa/{card['slug']}/",
        title=card["title"],
        description=f"{card['maker']}. {desc}",
        body=body,
        colophon=colophon + WORKSHOP_LINK,
        og_image=card["slug"],
        cards=cards,
        og_type="article",
    )


def build_workshop(cards):
    body = '  <div class="prose">\n' + (SRC / "workshop.html").read_text(encoding="utf-8") + "  </div>"
    return page(
        path="/workshop/",
        title="How I work with AI",
        description="Where a language model touched the work on this site, line by line.",
        body=body,
        colophon="Drafted by Claude (Anthropic) at Jasper Palmer’s request, from his notes on colophons, November 2026.",
        og_image="workshop",
        cards=cards,
    )


def rfc822(iso):
    d = datetime.date.fromisoformat(iso)
    return datetime.datetime(d.year, d.month, d.day, 12, tzinfo=datetime.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")


def build_feed(cards):
    items = []
    entries = [
        {
            "title": c["title"],
            "link": f"{SITE['base']}/circa/{c['slug']}/",
            "date": c["added"],
            "text": f"{c['maker']}. " + quoted(c["door"], c.get("lang", "en"))
            + (f" … {quoted(c['exit'], c.get('lang', 'en'))}" if c.get("exit") else ""),
        }
        for c in cards
    ]
    entries.append({
        "title": "How I work with AI",
        "link": f"{SITE['base']}/workshop/",
        "date": SITE["updated"].isoformat(),
        "text": "Where a language model touched the work on this site, line by line.",
    })
    entries.sort(key=lambda x: (x["date"], x["title"]), reverse=True)
    for x in entries:
        items.append(
            f"""  <item>
    <title>{e(x['title'])}</title>
    <link>{x['link']}</link>
    <guid>{x['link']}</guid>
    <pubDate>{rfc822(x['date'])}</pubDate>
    <description>{e(x['text'])}</description>
  </item>"""
        )
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
  <title>{e(SITE['name'])}</title>
  <link>{SITE['base']}/</link>
  <description>{e(SITE['description'])}</description>
  <language>en</language>
{chr(10).join(items)}
</channel>
</rss>
"""


def write(rel, text):
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


# ── Link-preview images: the placard, 1200 × 630 ──
OG_CSS = """
@font-face{font-family:'EBG';src:url('FONTDIR/eb-garamond-latin-400-normal.woff2')}
@font-face{font-family:'EBG';font-style:italic;src:url('FONTDIR/eb-garamond-latin-400-italic.woff2')}
@font-face{font-family:'EBG';font-weight:500;src:url('FONTDIR/eb-garamond-latin-500-normal.woff2')}
*{margin:0;padding:0;box-sizing:border-box}
body{width:1200px;height:630px;background:#16150f;color:#ddd8ca;font-family:'EBG',Georgia,serif;
  padding:74px 92px;display:flex;flex-direction:column;justify-content:center}
.label{font-family:-apple-system,'Helvetica Neue',Arial,sans-serif;font-size:17px;font-weight:600;
  letter-spacing:.2em;text-transform:uppercase;color:#6d675a}
h1{font-weight:500;font-size:58px;line-height:1.12;margin:22px 0 8px;letter-spacing:-.01em}
.attr{font-style:italic;font-size:27px;color:#8b8577;margin-bottom:38px}
.face{font-style:italic;font-size:38px;line-height:1.35}
.glyph{display:flex;gap:8px;align-items:flex-end;height:24px;margin-top:40px}
.glyph i{display:block;width:2.5px;background:#8b2f24;height:17px}
.glyph i:nth-child(2){height:24px}.glyph i:nth-child(3){height:14px}
.glyph i:nth-child(4){height:22px}.glyph i:nth-child(5){height:16px}
.paper{background:#eae7de;color:#191713}
.paper .label{color:#7d7768}
.paper .face{font-style:normal;color:#191713}
.paper em{color:#8b2f24}
"""


def og_html(inner, paper=False):
    # OG_FONTS = a folder holding the EB Garamond .woff2 files (from @fontsource/eb-garamond).
    import base64
    import re

    fontdir = pathlib.Path(os.environ.get("OG_FONTS", ""))

    def embed(m):
        f = fontdir / m.group(1)
        if not f.is_file():
            return "url('missing')"
        return "url(data:font/woff2;base64," + base64.b64encode(f.read_bytes()).decode() + ")"

    css = re.sub(r"url\('FONTDIR/([^']+)'\)", embed, OG_CSS)
    return f"<!DOCTYPE html><html><head><meta charset='utf-8'><style>{css}</style></head><body class='{'paper' if paper else ''}'>{inner}</body></html>"


def og_pages(cards):
    glyph = "<div class='glyph'><i></i><i></i><i></i><i></i><i></i></div>"
    name = e(SITE["name"])
    pages = {}
    for c in cards:
        attr = e(c["maker"]) + (f", {e(c['year'])}" if c.get("year") else "")
        door = e(quoted(c["door"], c.get("lang", "en")))
        pages[c["slug"]] = og_html(
            f"<div class='label'>{name} &middot; The Concordance</div><h1>{e(c['title'])}</h1>"
            f"<div class='attr'>{attr}</div><p class='face'>{door}</p>{glyph}"
        )
    pages["circa"] = og_html(
        f"<div class='label'>{name}</div><h1>The Concordance</h1>"
        f"<div class='attr'>{len(cards)} cards</div><p class='face'>A work&rsquo;s title and the lines lifted from it.</p>{glyph}"
    )
    pages["workshop"] = og_html(
        f"<div class='label'>{name} &middot; The Workshop</div><h1>How I work with AI</h1>"
        f"<div class='attr'>Jasper Palmer</div><p class='face'>Witnessed &middot; Made by hand &middot; Generated &middot; Checked</p>{glyph}"
    )
    pages["home"] = og_html(
        f"<div class='label'>{name}</div><h1>Jasper Palmer</h1>"
        f"<p class='face' style='margin-top:26px'>Amidst derision, a vision. <em>Epiphany engines</em> &mdash; in film, in sound, in prose.</p>{glyph}",
        paper=True,
    )
    return pages


def render_og(cards):
    from playwright.sync_api import sync_playwright

    out = ROOT / "og"
    out.mkdir(exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        pg = browser.new_page(viewport={"width": 1200, "height": 630})
        for slug, doc in og_pages(cards).items():
            pg.set_content(doc)
            pg.evaluate("document.fonts.ready")
            pg.wait_for_timeout(150)
            pg.screenshot(path=str(out / f"{slug}.png"))
        browser.close()


def main():
    cards = json.loads((SRC / "cards.json").read_text(encoding="utf-8"))
    slugs = [c["slug"] for c in cards]
    assert len(slugs) == len(set(slugs)), "two cards share a slug"
    write("index.html", build_home(cards))
    write("circa/index.html", build_index(cards))
    for c in cards:
        write(f"circa/{c['slug']}/index.html", build_card(c, cards))
    write("workshop/index.html", build_workshop(cards))
    write("feed.xml", build_feed(cards))
    if "--og" in sys.argv:
        render_og(cards)
    print(f"Built {len(cards)} cards, the index, the workshop, home and feed.")


if __name__ == "__main__":
    main()
