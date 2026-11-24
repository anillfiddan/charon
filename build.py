#!/usr/bin/env python3
"""Charon sitesi derleyici: src/pages/*.html + ortak şablon -> site/

Kullanım:  python3 build.py
Her sayfanın ilk satırı JSON yorumudur:
<!--{"title": "...", "description": "...", "path": "/kurumsal/", "nav": "kurumsal"}-->
Sayfa içinde {{icon:ad}} ile ikon eklenir.
"""
import json, re, shutil, datetime
from pathlib import Path

SITE_URL = "https://anillfiddan.github.io/charon"  # alan adı gelince değiştir (sonunda / yok)
BASE_PATH = "/charon"   # GitHub Pages alt klasörü; kendi alan adında "" yap
NOINDEX = True          # önizleme yayını: Google'a kapalı. Gerçek yayında False yap
APP_LOGIN = "https://charon.twinlikee.com/tr/login"

ROOT = Path(__file__).parent
SRC, OUT = ROOT / "src", ROOT / "site"

NAV = [
    ("nasil-calisir", "/nasil-calisir/", "Nasıl çalışır"),
    ("kurumsal", "/kurumsal/", "Kurumsal"),
    ("startup", "/startup/", "Startup"),
    ("avantajlar", "/avantajlar/", "Avantajlar"),
    ("hakkimizda", "/hakkimizda/", "Hakkımızda"),
]

ICONS = {
    "check": '<path d="M5 12.5l4.5 4.5L19 7.5"/>',
    "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "plus": '<path d="M12 5v14M5 12h14"/>',
    "flask": '<path d="M9 3h6M10 3v6l-5 9a2 2 0 0 0 1.7 3h10.6a2 2 0 0 0 1.7-3l-5-9V3"/>',
    "cart": '<path d="M3 4h2l2.4 11h11.2L21 7H6.2"/><circle cx="9" cy="20" r="1.2"/><circle cx="18" cy="20" r="1.2"/>',
    "doc": '<path d="M6 3h9l4 4v14H6z"/><path d="M14 3v5h5M9 13h7M9 17h5"/>',
    "chat": '<path d="M4 5h16v11H9l-5 4z"/>',
    "calendar": '<rect x="3.5" y="5" width="17" height="15" rx="2"/><path d="M3.5 10h17M8 3v4M16 3v4"/>',
    "handshake": '<path d="M8 12l3 3 5-6"/><rect x="3.5" y="3.5" width="17" height="17" rx="3"/>',
    "shield": '<path d="M12 3l7 3v6c0 4.5-3 7.5-7 9-4-1.5-7-4.5-7-9V6z"/><path d="M9 12l2 2 4-4"/>',
    "lock": '<rect x="5" y="10.5" width="14" height="10" rx="2"/><path d="M8 10.5V8a4 4 0 0 1 8 0v2.5"/>',
    "list": '<path d="M9 6h11M9 12h11M9 18h11"/><circle cx="4.5" cy="6" r="1"/><circle cx="4.5" cy="12" r="1"/><circle cx="4.5" cy="18" r="1"/>',
    "target": '<circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="4"/><circle cx="12" cy="12" r=".8"/>',
    "user": '<circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 3.6-6.5 8-6.5s8 2.5 8 6.5"/>',
    "building": '<path d="M4 21V5l8-2v18M12 8h8v13M8 8h.01M8 12h.01M8 16h.01M16 12h.01M16 16h.01M2 21h20"/>',
    "tag": '<path d="M3 12V4h8l10 10-8 8z"/><circle cx="7.5" cy="8" r="1.2"/>',
    "inbox": '<path d="M3 13l3-8h12l3 8v6H3z"/><path d="M3 13h5l1 2h6l1-2h5"/>',
    "eye": '<path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
}

def icon(name):
    return ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" '
            'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + ICONS[name] + "</svg>")

def header(active):
    cur = ' aria-current="page"'
    links = "".join(
        '<li><a href="%s"%s>%s</a></li>' % (href, cur if key == active else "", label)
        for key, href, label in NAV)
    mlinks = "".join(f'<a href="{href}">{label}</a>' for _, href, label in NAV)
    return f'''<header class="site-header">
  <div class="wrap nav">
    <a class="brand" href="/" aria-label="Charon ana sayfa"><img src="/assets/logo-black.png" alt="Charon" width="84" height="24"></a>
    <nav aria-label="Ana menü"><ul class="nav-links">{links}</ul></nav>
    <div class="nav-actions">
      <a class="signin" href="{APP_LOGIN}">Giriş yap</a>
      <a class="btn btn-primary" href="/basvuru/">Başvur</a>
      <button class="menu-toggle" type="button" aria-label="Menüyü aç" aria-expanded="false" aria-controls="mobile-nav">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M4 8h16M4 16h16"/></svg>
      </button>
    </div>
  </div>
  <nav class="mobile-nav" id="mobile-nav" aria-label="Mobil menü">{mlinks}<a href="/sss/">SSS</a><a href="/iletisim/">İletişim</a><a href="{APP_LOGIN}">Giriş yap</a><a class="btn btn-primary" href="/basvuru/">Başvur</a></nav>
</header>'''

FOOTER = f'''<footer class="site-footer">
  <div class="wrap">
    <div class="foot-grid">
      <div class="foot-brand">
        <img src="/assets/logo-black.png" alt="Charon" width="77" height="22">
        <p>Kurumsal şirketlerle startup'ları ilan, teklif ve görüşme akışıyla buluşturan B2B pazar yeri.</p>
      </div>
      <div class="foot-col"><b>Ürün</b>
        <a href="/nasil-calisir/">Nasıl çalışır</a><a href="/kurumsal/">Kurumsal</a><a href="/startup/">Startup</a><a href="/avantajlar/">Avantajlar</a>
      </div>
      <div class="foot-col"><b>Şirket</b>
        <a href="/hakkimizda/">Hakkımızda</a><a href="/sss/">SSS</a><a href="/iletisim/">İletişim</a><a href="/basvuru/">Başvuru</a>
      </div>
      <div class="foot-col"><b>Yasal</b>
        <a href="/kvkk/">KVKK Aydınlatma Metni</a><a href="/gizlilik/">Gizlilik Politikası</a><a href="/cerez-politikasi/">Çerez Politikası</a><a href="/kullanim-kosullari/">Kullanım Koşulları</a>
      </div>
    </div>
    <div class="foot-bottom"><span>© <span data-year>{datetime.date.today().year}</span> Charon. Tüm hakları saklıdır.</span><span>Türkiye</span></div>
  </div>
</footer>'''

def layout(meta, body):
    path = meta["path"]
    url = SITE_URL + (path if path != "/404" else "/")
    title = meta["title"]
    full_title = title if meta.get("raw_title") else f"{title} · Charon"
    desc = meta["description"]
    robots = '<meta name="robots" content="noindex">' if (meta.get("noindex") or NOINDEX) else ""
    ld = ""
    if path == "/":
        ld = ('<script type="application/ld+json">' + json.dumps({
            "@context": "https://schema.org", "@type": "Organization", "name": "Charon",
            "url": SITE_URL + "/", "logo": SITE_URL + "/assets/logo-black.png",
            "description": desc}, ensure_ascii=False) + "</script>")
    if meta.get("faq_ld"):
        ld += '<script type="application/ld+json">' + json.dumps(meta["faq_ld"], ensure_ascii=False) + "</script>"
    return f'''<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{full_title}</title>
<meta name="description" content="{desc}">
{robots}
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:locale" content="tr_TR">
<meta property="og:site_name" content="Charon">
<meta property="og:title" content="{full_title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE_URL}/assets/og.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#ffffff">
<link rel="icon" type="image/png" sizes="32x32" href="/assets/favicon-32.png">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<link rel="preload" href="/assets/fonts/inter-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/site.css">
{ld}
</head>
<body>
<a class="skip" href="#main">İçeriğe geç</a>
{header(meta.get("nav"))}
<main id="main">
{body}
</main>
{FOOTER}
<script src="/assets/site.js" defer></script>
</body>
</html>
'''

def faq_ld(body):
    qs = re.findall(r'<summary>(.*?)<span class="pm"></span></summary>\s*<div class="ans">(.*?)</div>', body, re.S)
    if not qs:
        return None
    strip = lambda s: re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s)).strip()
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": strip(q), "acceptedAnswer": {"@type": "Answer", "text": strip(a)}} for q, a in qs]}

def with_base(text):
    """Kök göreli adreslere (/x) BASE_PATH ekler; tam adreslere (https://, //) dokunmaz."""
    if not BASE_PATH:
        return text
    text = re.sub(r'((?:href|src|action)=")/(?!/)', r"\1" + BASE_PATH + "/", text)
    return re.sub(r"url\(/(?!/)", "url(" + BASE_PATH + "/", text)

def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(SRC / "assets", OUT / "assets")
    css = OUT / "assets" / "site.css"
    css.write_text(with_base(css.read_text(encoding="utf-8")), encoding="utf-8")
    urls = []
    for f in sorted((SRC / "pages").glob("*.html")):
        raw = f.read_text(encoding="utf-8")
        m = re.match(r"<!--(\{.*?\})-->\s*", raw, re.S)
        meta, body = json.loads(m.group(1)), raw[m.end():]
        body = re.sub(r"\{\{icon:(\w+)\}\}", lambda x: icon(x.group(1)), body)
        body = body.replace("{{APP_LOGIN}}", APP_LOGIN)
        if meta.get("faq"):
            meta["faq_ld"] = faq_ld(body)
        html = with_base(layout(meta, body))
        p = meta["path"]
        dest = OUT / "index.html" if p == "/" else (OUT / "404.html" if p == "/404" else OUT / p.strip("/") / "index.html")
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(html, encoding="utf-8")
        if not meta.get("noindex"):
            urls.append(p)
        print("  ", dest.relative_to(ROOT))
    today = datetime.date.today().isoformat()
    sm = "".join(f"  <url><loc>{SITE_URL}{u}</loc><lastmod>{today}</lastmod></url>\n" for u in urls)
    (OUT / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{sm}</urlset>\n', encoding="utf-8")
    robots_txt = "User-agent: *\nDisallow: /\n" if NOINDEX else f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n"
    (OUT / "robots.txt").write_text(robots_txt, encoding="utf-8")
    (OUT / ".nojekyll").write_text("", encoding="utf-8")
    print(f"{len(urls)} sayfa sitemap'te.")

if __name__ == "__main__":
    main()
