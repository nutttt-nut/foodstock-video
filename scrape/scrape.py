#!/usr/bin/env python3
"""Scrape foodstock.info tenant directory -> restaurants.json + download hero photos.
Uses curl --compressed for fetching (handles gzip), regex parse (pages are server-rendered HTML)."""
import re, html, json, subprocess, os, sys, urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
PHOTOS = os.path.join(DATA, "photos")
os.makedirs(PHOTOS, exist_ok=True)

def fetch(url):
    r = subprocess.run(["curl", "-sL", "--compressed", url], capture_output=True, text=True)
    return r.stdout

def discover_place_urls():
    urls = []
    seen = set()
    for paged in range(1, 6):  # directory pagination
        u = f"https://foodstock.info/?s=&post_type=place&paged={paged}"
        h = fetch(u)
        found = re.findall(r'href="(https://foodstock\.info/place/[^"#?]+/)"', h)
        found = [x for x in found if '/place/feed/' not in x]
        new = [x for x in dict.fromkeys(found) if x not in seen]
        for x in new:
            seen.add(x); urls.append(x)
        if not new:
            break
    return urls

def strip_size(u):
    return re.sub(r'-\d+x\d+(\.[a-zA-Z]+)$', r'\1', u)

def parse_place(h):
    # name
    m = re.search(r'<title>(.*?)</title>', h, re.S)
    name = html.unescape(m.group(1)).strip() if m else ""
    name = re.sub(r'\s*[-|]\s*Foodstock\s*$', '', name, flags=re.I).strip()

    # recommended menu items: dish titles live in <div class="menu-title"><h4>NAME</h4>
    menu = []
    for m in re.findall(r'class="menu-title"\s*>\s*<h[1-6][^>]*>(.*?)</h[1-6]>', h, re.S):
        t = html.unescape(re.sub(r'<[^>]+>', '', m)).strip()
        if t:
            menu.append(t)
    # dedupe preserve order
    seen=set(); menu=[x for x in menu if not (x in seen or seen.add(x))]

    # hero/highlight full-res images: prefer -scaled.jpg in dated uploads, exclude logo/icons
    imgs = re.findall(r'https://foodstock\.info/wp-content/uploads/[0-9]{4}/[0-9]{2}/[^"\' ]+?\.(?:jpg|jpeg|png)', h)
    heroes = []
    for u in imgs:
        base = u.lower()
        if 'logo' in base or 'cropped' in base or 'untitled-design' in base:
            continue
        if any(k in base for k in ('car-parking','cash-payment','qr-payment','delivery','dine-in','take-away','-icon')):
            continue
        heroes.append(u)
    # prefer -scaled originals; dedupe by stripped base
    scaled = [u for u in heroes if u.endswith('-scaled.jpg') or '-scaled.' in u]
    pool = scaled if scaled else heroes
    seen=set(); uniq=[]
    for u in pool:
        b = strip_size(u)
        if b in seen: continue
        seen.add(b); uniq.append(u)
    return name, menu, uniq

def slugify(name):
    s = re.sub(r'[^A-Za-z0-9ก-๙]+', '-', name).strip('-')
    return s[:40] or 'r'

def main():
    place_urls = discover_place_urls()
    print(f"discovered {len(place_urls)} place urls", file=sys.stderr)
    restaurants = []
    for i, u in enumerate(place_urls, 1):
        h = fetch(u)
        name, menu, heroes = parse_place(h)
        rid = f"{i:02d}-{slugify(name) if name else slugify(urllib.parse.unquote(u))}"
        hero_url = heroes[0] if heroes else ""
        local = ""
        if hero_url:
            ext = os.path.splitext(hero_url.split('?')[0])[1] or '.jpg'
            local = f"photos/{rid}{ext}"
            subprocess.run(["curl", "-sL", "--compressed", hero_url, "-o", os.path.join(DATA, local)])
        restaurants.append({
            "id": rid, "name": name, "url": u,
            "menu": menu[:6], "hero_url": hero_url,
            "hero_local": local, "all_heroes": heroes[:6],
        })
        print(f"[{i}/{len(place_urls)}] {name} | menu={len(menu)} | hero={'Y' if hero_url else 'N'}", file=sys.stderr)
    out = os.path.join(DATA, "restaurants.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(restaurants, f, ensure_ascii=False, indent=2)
    print(f"\nwrote {out} ({len(restaurants)} restaurants)", file=sys.stderr)

if __name__ == "__main__":
    main()
