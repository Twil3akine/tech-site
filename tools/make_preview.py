#!/usr/bin/env python3
"""Bundle the built site (public/) into one self-contained preview HTML.

Layout: the site's real header once as bundle chrome (taken from the
landing page itself — it uses the standard site header), then the
landing page's <main> content as section#top (in its own .lp-main
wrapper, so the two-column layout keeps its width), then each
article's <article> element as sections #axum / #hashmap / #iterator /
#fileio inside .container divs. The landing page's body scripts
(code-block panels) are carried over at the end so they keep working
in the bundle.
CSS is inlined, the icon is a base64 data URI, internal links are
rewritten to in-bundle anchors, and heading ids are prefixed per
article so the TOC jumps stay inside their own section.

Usage: zola build && python3 tools/make_preview.py [landing]

With the "landing" argument, only the landing page (its own site
header + main + its footer) is bundled — no article sections.
"""
import base64
import pathlib
import re
import sys

LANDING_ONLY = len(sys.argv) > 1 and sys.argv[1] == "landing"

ROOT = pathlib.Path(__file__).resolve().parent.parent
PUB = ROOT / "public"
OUT = pathlib.Path.home() / "workspace/your_files/noptium-site-preview.html"
BASE = "https://noptium.com"

ARTICLES = [
    ("axum", "crates/axum-http-server/index.html", "/crates/axum-http-server/"),
    ("hashmap", "std/hashmap/index.html", "/std/hashmap/"),
    ("iterator", "std/iterator/index.html", "/std/iterator/"),
    ("fileio", "std/file-io/index.html", "/std/file-io/"),
]
PATH_TO_ANCHOR = {path: prefix for prefix, _, path in ARTICLES}
PATH_TO_ANCHOR.update({"/std/": "std", "/crates/": "crates", "/errors/": "errors", "/": "top"})

css = (PUB / "css/style.css").read_text()
icon_b64 = base64.b64encode((PUB / "img/icon.png").read_bytes()).decode()
icon_uri = f"data:image/png;base64,{icon_b64}"


def body_of(html: str) -> str:
    m = re.search(r"<body>(.*?)</body>", html, re.S)
    return m.group(1) if m else ""


def rewrite_links(html: str) -> str:
    # Anchored links into bundle articles: .../path/#frag -> #prefix-frag
    def anchored(m: re.Match) -> str:
        path, frag = m.group(1), m.group(2)
        prefix = PATH_TO_ANCHOR.get(path)
        if prefix and prefix not in ("std", "crates", "errors", "top"):
            return f'href="#{prefix}-{frag}"'
        return m.group(0)

    html = re.sub(r'href="' + BASE + r'(/[^"]*?)#([^"]+)"', anchored, html)
    # Plain page links: .../path/ -> #anchor
    def plain(m: re.Match) -> str:
        anchor = PATH_TO_ANCHOR.get(m.group(1))
        return f'href="#{anchor}"' if anchor else m.group(0)

    html = re.sub(r'href="' + BASE + r'(/[^"]*?)"', plain, html)
    html = html.replace(f'src="{BASE}/img/icon.png"', f'src="{icon_uri}"')
    return html


def article_section(prefix: str, rel: str) -> str:
    html = (PUB / rel).read_text()
    m = re.search(r'(<article class="article">.*?</article>)', html, re.S)
    art = m.group(1)
    # Prefix heading ids so duplicated slugs across articles stay unique.
    art = re.sub(r'id="([^"]+)"', lambda mm: f'id="{prefix}-{mm.group(1)}"', art)
    # Same-article in-page anchors get the same prefix.
    art = re.sub(r'href="#([^"]+)"', lambda mm: f'href="#{prefix}-{mm.group(1)}"', art)
    art = rewrite_links(art)
    return f'<section id="{prefix}" class="bundle-section"><div class="container">{art}</div></section>'


landing = body_of((PUB / "index.html").read_text())
# The landing uses the standard site header, so the bundle's single
# header is taken from the landing page itself.
header = rewrite_links(re.search(r'(<header class="site-header">.*?</header>)', landing, re.S).group(1))
top_main = rewrite_links(re.search(r'<main[^>]*>(.*?)</main>', landing, re.S).group(1))
lp_footer_m = re.search(r'(<footer class="site-footer">.*?</footer>)', landing, re.S)
lp_footer = rewrite_links(lp_footer_m.group(1)) if lp_footer_m else ""
# Body scripts (code-block panels) ride along at the end.
scripts = "\n".join(re.findall(r"<script>.*?</script>", landing, re.S))

bundle_css = """
.bundle-section { border-top: 3px solid var(--border); margin-top: 3.5rem; }
.bundle-section .article { margin-top: 24px; }
"""

if LANDING_ONLY:
    out = f"""<!DOCTYPE html>
<html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Noptium プレビュー（ランディングのみ）</title>
<link rel="icon" type="image/png" href="{icon_uri}">
<style>{css}
{bundle_css}</style></head><body>
{header}
<main class="rk-wrap">{top_main}</main>
{lp_footer}
{scripts}
</body></html>"""
else:
    # The #top section is the landing page's <main> content (two
    # columns, in its own .rk-wrap wrapper; no header/footer inside).
    sections = [f'<section id="top"><main class="rk-wrap">{top_main}</main></section>']
    sections += [article_section(prefix, rel) for prefix, rel, _ in ARTICLES]
    out = f"""<!DOCTYPE html>
<html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Noptium プレビュー（全4記事）</title>
<link rel="icon" type="image/png" href="{icon_uri}">
<style>{css}
{bundle_css}</style></head><body>
{header}
{''.join(sections)}
{scripts}
</body></html>"""

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(out)
print(f"written {OUT} ({OUT.stat().st_size} bytes)")
