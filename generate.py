#!/usr/bin/env python3
"""Generate index.html (HyperFrames composition) from data/restaurants.json.
16:9 loop: intro (cream) + restaurant scenes (slate split) + outro (cream)."""
import json, os, html, re

ROOT = os.path.dirname(os.path.abspath(__file__))
data = json.load(open(os.path.join(ROOT, "data/restaurants.json"), encoding="utf-8"))

# --- brand config (reads data/brand-config.json if exists, else uses defaults) ---
_brand_path = os.path.join(ROOT, "data/brand-config.json")
_brand_default = {
    "intro_tagline_l1": "มากกว่าศูนย์อาหาร",
    "intro_tagline_l2": "คือพื้นที่แห่งความสุข",
    "intro_sub": "25 ร้านเด็ด · พัฒนาการ 32",
    "outro_hours": "เปิดบริการทุกวัน · 8:00–21:00 น.",
    "outro_addr": "471 พัฒนาการ 32 · สวนหลวง กทม.",
    "outro_web": "foodstock.info"
}
brand = json.load(open(_brand_path, encoding="utf-8")) if os.path.exists(_brand_path) else _brand_default

# --- timing ---
INTRO_HOLD, SCENE_HOLD, OUTRO_HOLD, XFADE = 3.2, 5.0, 4.0, 0.7

# --- palette (design.md) ---
SLATE900, SLATE700, SLATE600 = "#2A333B", "#495862", "#5C6B75"
CREAM, CREAMDIM, AMBER, INK = "#F5EFE6", "#C7CDD2", "#E0A43B", "#2A333B"

# name-derived signatures for restaurants with no scraped menu (dish is in the shop name)
SIGNATURE = {
    "เนื้อในตำนาน": "เนื้อย่าง · สเต๊กเนื้อ",
    "แกงป่า": "แกงป่า · อาหารตามสั่ง",
    "แกงป่า รามคำแหง 24": "แกงป่า · อาหารตามสั่ง",
    "กินเส้น เดลิเวอรี่": "ก๋วยเตี๋ยว · เมนูเส้น",
    "กินเส้นดิลิเวอรี่": "ก๋วยเตี๋ยว · เมนูเส้น",
    "แม่โจ้ ขนมจีน 4 ภาค": "ขนมจีนน้ำยา 4 ภาค",
    "ขนมจีน 4 ภาค": "ขนมจีนน้ำยา 4 ภาค",
    "โคตรกะเพราจงเจริญ": "กะเพรา · ข้าวราดกะเพรา",
    "มีเรา ข้าวแกงใต้ชาววัง": "แกงใต้ · อาหารปักษ์ใต้",
    "มีเรา ครัวแกงใต้ชาววัง": "แกงใต้ · อาหารปักษ์ใต้",
    "มนตร์ส้มตำ": "ส้มตำ · อาหารอีสาน",
    "มนตร์ส้มตำ แซ่บถูกปาก": "ส้มตำ · อาหารอีสาน",
    "ต้าเฉินก๋วยเตี๋ยวต้มยำ": "ก๋วยเตี๋ยวต้มยำ · น้ำ/แห้ง",
    "ย่างเก่ง": "หมูย่างเกาหลี · เนื้อย่าง",
    "มันส์หมู มันส์ไก่": "หมูย่าง · ไก่ย่าง",
    "HOR DIM SUM": "ติ่มซำนึ่ง · ขนมจีบ",
    "ห่อติ่มซำ": "ติ่มซำนึ่ง · ขนมจีบ",
    "ข้าวมันไก่พร้อม": "ข้าวมันไก่ · ข้าวมันไก่ทอด",
    "พร้อมข้าวมันไก่": "ข้าวมันไก่ · ข้าวมันไก่ทอด",
    "Premium Bakery": "เบเกอรี่โฮมเมด · ขนมอบสด",
    "เฮงยอดผัก กินไม่รู้อิ่ม": "ผัดผักรวม · เมนูผักไม่อั้น",
    "Golden Leaf Eatery": "อาหารจานเดียว · เมนูแนะนำ",
    "ข้าวคลุกน้ำพริก ทองคำ": "ข้าวคลุกน้ำพริก · เครื่องเคียงครบ",
    "ข้าวคลุกน้ำพริกทองคำ": "ข้าวคลุกน้ำพริก · เครื่องเคียงครบ",
}

PROMO_RE = re.compile(r'(สะสมแต้ม|อิ่ม อร่อย|🎉|ทุกมื้อ|วันนี้)')

def display_name(n):
    n = re.sub(r'\s*Food Stock\s*พัฒนาการ\s*$', '', n)
    n = re.sub(r'\s*พัฒนาการ\s*$', '', n).strip()
    return n

def clean_menu(name, menu):
    items = []
    for m in menu:
        m = m.strip()
        if not m or PROMO_RE.search(m):
            continue
        m = re.sub(r'^เมนู\s+', '', m)        # drop leading "เมนู "
        m = re.sub(r'\s+Series$', '', m)        # "Coffee Series" -> "Coffee"
        items.append(m)
    items = items[:3]
    if items:
        return ("ร้านแนะนำ", items)
    sig = SIGNATURE.get(name)
    if sig:
        return ("ซิกเนเจอร์", [sig])
    return ("ร้านแนะนำ", [display_name(name)])

def esc(s):
    return html.escape(s, quote=True)

def overlay_html(overlays):
    imgs = []
    for o in overlays or []:
        if not isinstance(o, dict) or not o.get("src"):
            continue
        src = str(o["src"]).replace("\\", "/").lstrip("/")
        if not src.startswith("data/"):
            src = "data/" + src
        try:
            x = float(o.get("x_pct", 0))
            y = float(o.get("y_pct", 0))
            width = int(float(o.get("width_px", 160)))
        except (TypeError, ValueError):
            continue
        imgs.append(
            f'<img class="overlay" src="{esc(src)}" alt="" '
            f'style="left:{x:.4f}%;top:{y:.4f}%;width:{width}px"/>'
        )
    return "".join(imgs)

# --- build scenes ---
scenes = []  # (id, html, hold, kind)
# intro
scenes.append(("intro", None, INTRO_HOLD, "intro"))
for i, r in enumerate(data, 1):
    scenes.append((f"r{i}", r, SCENE_HOLD, "rest"))
scenes.append(("outro", None, OUTRO_HOLD, "outro"))

# reveal times
reveal = [0.0]
for k in range(1, len(scenes)):
    reveal.append(round(reveal[k-1] + scenes[k-1][2], 3))
TOTAL = round(reveal[-1] + OUTRO_HOLD, 3)

# --- scene html ---
def scene_html(idx, sid, r, kind):
    z = idx + 1
    vis = "" if idx == 0 else "opacity:0;"
    if kind == "intro":
        overlays = overlay_html(brand.get("intro_overlays", []))
        inner = f'''
      <div class="brand">
        <img class="logo" src="data/brand/logo-darkgreen.png" alt="FoodStock"/>
        <div class="tagline">{esc(brand["intro_tagline_l1"])}<br>{esc(brand["intro_tagline_l2"])}</div>
        <div class="rule"></div>
        <div class="sub">{esc(brand["intro_sub"])}</div>
        {overlays}
      </div>'''
        return f'<div id="{sid}" class="scene cream" data-layout-allow-overlap style="z-index:{z};{vis}">{inner}</div>'
    if kind == "outro":
        inner = f'''
      <div class="brand">
        <img class="logo" src="data/brand/logo-outro.png" alt="FoodStock"/>
        <div class="sub big">{esc(brand["outro_hours"])}</div>
        <div class="rule"></div>
        <div class="sub">{esc(brand["outro_addr"])}</div>
        <div class="web">{esc(brand["outro_web"])}</div>
      </div>'''
        return f'<div id="{sid}" class="scene cream" data-layout-allow-overlap style="z-index:{z};{vis}">{inner}</div>'
    # restaurant
    name = display_name(r["name"])
    label, items = clean_menu(r["name"], r["menu"])
    side = "left" if (idx % 2 == 1) else "right"   # alternate photo side
    photo = esc(r["hero_local"]).replace("\\", "/")
    photo = "data/" + photo
    items_html = "".join(f'<li><span class="bullet"></span>{esc(it)}</li>' for it in items)
    num = f'{idx:02d}'
    photo_div = f'<div class="photo-wrap" data-layout-allow-overflow><div class="photo" style="background-image:url(\'{photo}\')"></div><div class="scrim {side}"></div></div>'
    panel = f'''
        <div class="panel">
          <div class="ptop">
            <span class="idx">{num}<span class="idx-tot">/{len(data)}</span></span>
            <span class="plabel">{label}</span>
          </div>
          <h1 class="rname">{esc(name)}</h1>
          <ul class="menu">{items_html}</ul>
          <div class="pmark">FOOD STOCK</div>
        </div>'''
    order = (photo_div + panel) if side == "left" else (panel + photo_div)
    overlays = overlay_html(r.get("overlays", []))
    return f'<div id="{sid}" class="scene slate {side}" data-layout-allow-overlap style="z-index:{z};{vis}"><div class="split">{order}</div>{overlays}</div>'

scenes_html = "\n      ".join(
    scene_html(i, sid, r, kind) for i, (sid, r, hold, kind) in enumerate(scenes)
)

# --- timeline js ---
tw = []
for i, (sid, r, hold, kind) in enumerate(scenes):
    t = reveal[i]
    if i > 0:
        tw.append(f'tl.to("#{sid}", {{opacity:1, duration:{XFADE}, ease:"power1.inOut"}}, {t});')
    seg = round(hold + XFADE, 3)
    if kind == "rest":
        tw.append(f'tl.fromTo("#{sid} .photo", {{scale:1.07}}, {{scale:1.0, duration:{seg}, ease:"sine.inOut"}}, {t});')
        tw.append(f'tl.from("#{sid} .panel .idx", {{y:30, opacity:0, duration:0.5, ease:"power3.out"}}, {t+0.15});')
        tw.append(f'tl.from("#{sid} .panel .plabel", {{y:20, opacity:0, duration:0.5, ease:"power2.out"}}, {t+0.22});')
        tw.append(f'tl.from("#{sid} .rname", {{y:44, opacity:0, duration:0.7, ease:"power3.out"}}, {t+0.28});')
        tw.append(f'tl.from("#{sid} .menu li", {{y:24, opacity:0, duration:0.5, stagger:0.09, ease:"power2.out"}}, {t+0.5});')
        tw.append(f'tl.from("#{sid} .pmark", {{opacity:0, duration:0.6, ease:"sine.out"}}, {t+0.8});')
    else:
        tw.append(f'tl.from("#{sid} .logo", {{y:40, opacity:0, scale:0.92, duration:0.8, ease:"power3.out"}}, {t+0.2});')
        tw.append(f'tl.from("#{sid} .tagline, #{sid} .sub, #{sid} .web", {{y:26, opacity:0, duration:0.6, stagger:0.12, ease:"power2.out"}}, {t+0.5});')
        tw.append(f'tl.from("#{sid} .rule", {{scaleX:0, duration:0.6, ease:"power2.inOut"}}, {t+0.6});')
tw.append(f'tl.set({{}}, {{}}, {TOTAL});')   # sentinel to full duration
timeline_js = "\n      ".join(tw)

HTML = f'''<!DOCTYPE html>
<html lang="th">
<head>
<meta charset="UTF-8"/>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>
  @font-face {{ font-family:"Kanit"; font-weight:400; font-style:normal;
               src:url("fonts/Kanit-Regular.ttf") format("truetype"); }}
  @font-face {{ font-family:"Kanit"; font-weight:600; font-style:normal;
               src:url("fonts/Kanit-SemiBold.ttf") format("truetype"); }}
  @font-face {{ font-family:"Kanit"; font-weight:700; font-style:normal;
               src:url("fonts/Kanit-Bold.ttf") format("truetype"); }}
  @font-face {{ font-family:"Noto Sans Thai"; font-weight:100 900; font-style:normal;
               src:url("fonts/NotoSansThai.ttf") format("truetype"); }}
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ width:1920px; height:1080px; overflow:hidden; background:{SLATE900};
         font-family:"Noto Sans Thai", sans-serif; }}
  .scene {{ position:absolute; top:0; left:0; width:1920px; height:1080px; overflow:hidden; }}
  .cream {{ background:{CREAM}; }}
  .slate {{ background:{SLATE900}; }}
  /* intro / outro brand */
  .brand {{ position:absolute; inset:0; display:flex; flex-direction:column;
            align-items:center; justify-content:center; gap:36px; text-align:center; }}
  .brand .logo {{ width:360px; height:auto; }}
  .brand .tagline {{ font-family:"Kanit", sans-serif; font-weight:700; font-size:64px;
                     line-height:1.18; color:{INK}; }}
  .brand .sub {{ font-size:34px; color:{SLATE700}; letter-spacing:.5px; }}
  .brand .sub.big {{ font-family:"Kanit",sans-serif; font-weight:600; font-size:46px; color:{INK}; }}
  .brand .web {{ font-family:"Kanit",sans-serif; font-weight:600; font-size:30px;
                 color:{AMBER}; letter-spacing:2px; }}
  .brand .rule {{ width:120px; height:4px; background:{AMBER}; border-radius:2px; transform-origin:center; }}
  /* restaurant split */
  .split {{ position:absolute; inset:0; display:flex; }}
  .photo-wrap {{ position:relative; width:52%; height:100%; overflow:hidden; }}
  .photo {{ position:absolute; inset:0; background-size:cover; background-position:center;
            box-shadow: inset 0 0 0 1px rgba(0,0,0,.18); }}
  .scrim {{ position:absolute; top:0; bottom:0; width:220px; }}
  .scrim.left {{ right:0; background:linear-gradient(90deg, rgba(42,51,59,0) 0%, {SLATE900} 100%); }}
  .scrim.right {{ left:0; background:linear-gradient(270deg, rgba(42,51,59,0) 0%, {SLATE900} 100%); }}
  .panel {{ position:relative; width:48%; height:100%; background:{SLATE700};
            padding:118px 96px; display:flex; flex-direction:column; justify-content:center; }}
  .slate.left .panel {{ border-left:4px solid {AMBER}; }}
  .slate.right .panel {{ border-right:4px solid {AMBER}; }}
  .ptop {{ display:flex; align-items:baseline; gap:22px; margin-bottom:26px; }}
  .idx {{ font-family:"Kanit",sans-serif; font-weight:700; font-size:66px; color:{AMBER}; line-height:1; }}
  .idx-tot {{ font-size:30px; color:{CREAMDIM}; font-weight:400; }}
  .plabel {{ font-size:26px; letter-spacing:4px; color:{CREAMDIM}; text-transform:uppercase; }}
  .rname {{ font-family:"Kanit",sans-serif; font-weight:700; font-size:84px; line-height:1.04;
            color:{CREAM}; margin-bottom:40px; white-space:nowrap; }}
  .menu {{ list-style:none; display:flex; flex-direction:column; gap:18px; }}
  .menu li {{ display:flex; align-items:center; gap:18px; font-size:40px; color:{CREAM}; line-height:1.2; }}
  .bullet {{ flex:0 0 auto; width:14px; height:14px; background:{AMBER}; border-radius:50%; }}
  .pmark {{ position:absolute; bottom:60px; font-size:22px; letter-spacing:6px;
            color:{SLATE600}; font-family:"Kanit",sans-serif; font-weight:600; }}
  .overlay {{ position:absolute; height:auto; z-index:5; pointer-events:none;
              filter:drop-shadow(0 4px 10px rgba(0,0,0,.35)); }}
</style>
</head>
<body>
  <div id="root" data-composition-id="foodstock" data-width="1920" data-height="1080"
       data-start="0" data-duration="{TOTAL}">
      {scenes_html}
    <script>
      window.__timelines = window.__timelines || {{}};
      var tl = gsap.timeline({{ paused:true }});
      {timeline_js}
      window.__timelines["foodstock"] = tl;
    </script>
  </div>
<script>
  document.querySelectorAll('.rname').forEach(el => {{
    const panel = el.closest('.panel');
    if (!panel) return;
    const maxW = panel.clientWidth - 192;
    let size = 84;
    while (el.scrollWidth > maxW && size > 36) {{ size -= 2; el.style.fontSize = size + 'px'; }}
  }});
</script>
</body>
</html>'''

open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(HTML)
print(f"wrote index.html | {len(scenes)} scenes | duration {TOTAL}s")
print("reveal times:", reveal)

# --- editor ---
_data_json = json.dumps(data, ensure_ascii=False)
_brand_json = json.dumps(brand, ensure_ascii=False)
EDITOR = f'''<!DOCTYPE html>
<html lang="th">
<head>
<meta charset="UTF-8"/>
<title>FoodStock Scene Editor</title>
<style>
  @font-face {{ font-family:"Kanit"; font-weight:400; src:url("fonts/Kanit-Regular.ttf") format("truetype"); }}
  @font-face {{ font-family:"Kanit"; font-weight:600; src:url("fonts/Kanit-SemiBold.ttf") format("truetype"); }}
  @font-face {{ font-family:"Kanit"; font-weight:700; src:url("fonts/Kanit-Bold.ttf") format("truetype"); }}
  @font-face {{ font-family:"Noto Sans Thai"; font-weight:100 900; src:url("fonts/NotoSansThai.ttf") format("truetype"); }}
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ background:{SLATE900}; color:{CREAM}; font-family:"Noto Sans Thai",sans-serif; height:100vh; display:flex; flex-direction:column; overflow:hidden; }}
  header {{ background:{SLATE700}; border-bottom:2px solid {AMBER}; padding:13px 24px; display:flex; align-items:center; justify-content:space-between; flex-shrink:0; }}
  .title {{ font-family:"Kanit",sans-serif; font-weight:700; font-size:18px; color:{CREAM}; }}
  .title span {{ color:{AMBER}; }}
  #export-btn {{ background:{AMBER}; color:{SLATE900}; border:none; font-family:"Kanit",sans-serif; font-weight:700; font-size:13px; padding:9px 20px; border-radius:5px; cursor:pointer; letter-spacing:.5px; }}
  #export-btn:hover {{ background:#c8922a; }}
  #layout {{ display:flex; flex:1; overflow:hidden; }}
  #sidebar {{ width:240px; background:#1e262d; border-right:1px solid #2e3a42; overflow-y:auto; flex-shrink:0; }}
  .r-item {{ padding:10px 14px; cursor:pointer; border-bottom:1px solid #252f36; display:flex; align-items:center; gap:10px; transition:background .12s; }}
  .r-item:hover {{ background:#252f36; }}
  .r-item.active {{ background:{SLATE700}; border-left:3px solid {AMBER}; padding-left:11px; }}
  .r-num {{ font-family:"Kanit",sans-serif; font-weight:700; font-size:12px; color:{AMBER}; min-width:24px; }}
  .r-name {{ font-size:12px; color:{CREAM}; line-height:1.3; }}
  .r-item.brand-item {{ background:#171f26; }}
  .r-item.brand-item .r-num {{ background:{AMBER}; color:{SLATE900}; border-radius:3px; padding:1px 5px; font-size:9px; letter-spacing:1px; min-width:auto; }}
  #content {{ flex:1; display:flex; overflow:hidden; }}
  #edit-panel {{ width:300px; padding:22px; background:#232c33; border-right:1px solid #2e3a42; overflow-y:auto; flex-shrink:0; display:flex; flex-direction:column; gap:18px; }}
  .scene-badge {{ display:inline-block; font-size:10px; letter-spacing:2px; color:{AMBER}; background:#1e262d; border:1px solid {AMBER}; border-radius:3px; padding:3px 8px; font-family:"Kanit",sans-serif; }}
  .field-label {{ font-size:10px; letter-spacing:3px; color:{CREAMDIM}; text-transform:uppercase; margin-bottom:6px; }}
  .field-input {{ width:100%; background:{SLATE900}; border:1px solid #3a4750; color:{CREAM}; font-family:"Noto Sans Thai",sans-serif; font-size:13px; padding:9px 11px; border-radius:4px; outline:none; transition:border-color .12s; }}
  .field-input:focus {{ border-color:{AMBER}; }}
  .menu-inputs {{ display:flex; flex-direction:column; gap:7px; }}
  .hint {{ font-size:11px; color:#4a5a65; line-height:1.7; margin-top:4px; }}
  .hint code {{ background:#1e262d; padding:2px 5px; border-radius:3px; color:{CREAMDIM}; font-size:10px; }}
  #preview-pane {{ flex:1; display:flex; align-items:center; justify-content:center; background:#161d22; padding:24px; }}
  .preview-wrap {{ overflow:hidden; border-radius:5px; box-shadow:0 8px 32px rgba(0,0,0,.7); flex-shrink:0; }}
  .preview-inner {{ transform-origin:top left; position:relative; background:{SLATE900}; }}
  .preview-inner.cream-bg {{ background:{CREAM}; }}
  /* restaurant scene styles */
  .ms-split {{ position:absolute; inset:0; display:flex; }}
  .ms-photo-wrap {{ position:relative; width:52%; height:100%; overflow:hidden; }}
  .ms-photo {{ position:absolute; inset:0; background-size:cover; background-position:center; }}
  .ms-scrim {{ position:absolute; top:0; bottom:0; width:110px; }}
  .ms-scrim.left {{ right:0; background:linear-gradient(90deg,rgba(42,51,59,0),{SLATE900}); }}
  .ms-scrim.right {{ left:0; background:linear-gradient(270deg,rgba(42,51,59,0),{SLATE900}); }}
  .ms-panel {{ position:relative; width:48%; height:100%; background:{SLATE700}; padding:59px 48px; display:flex; flex-direction:column; justify-content:center; }}
  .ms-panel.bl {{ border-left:2px solid {AMBER}; }}
  .ms-panel.br {{ border-right:2px solid {AMBER}; }}
  .ms-ptop {{ display:flex; align-items:baseline; gap:11px; margin-bottom:13px; }}
  .ms-idx {{ font-family:"Kanit",sans-serif; font-weight:700; font-size:33px; color:{AMBER}; line-height:1; }}
  .ms-tot {{ font-size:15px; color:{CREAMDIM}; }}
  .ms-plabel {{ font-size:13px; letter-spacing:2px; color:{CREAMDIM}; text-transform:uppercase; }}
  .ms-rname {{ font-family:"Kanit",sans-serif; font-weight:700; font-size:42px; line-height:1.04; color:{CREAM}; margin-bottom:20px; max-width:330px; }}
  .ms-menu {{ list-style:none; display:flex; flex-direction:column; gap:9px; }}
  .ms-menu li {{ display:flex; align-items:center; gap:9px; font-size:20px; color:{CREAM}; }}
  .ms-bullet {{ flex:0 0 auto; width:7px; height:7px; background:{AMBER}; border-radius:50%; }}
  .ms-pmark {{ position:absolute; bottom:30px; font-size:11px; letter-spacing:3px; color:{SLATE600}; font-family:"Kanit",sans-serif; font-weight:600; }}
  /* brand (intro/outro) scene styles */
  .ms-brand {{ position:absolute; inset:0; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:18px; text-align:center; }}
  .ms-brand-logo {{ width:180px; height:auto; }}
  .ms-brand-tagline {{ font-family:"Kanit",sans-serif; font-weight:700; font-size:32px; line-height:1.18; color:{INK}; }}
  .ms-brand-sub {{ font-size:17px; color:{SLATE700}; }}
  .ms-brand-sub-big {{ font-family:"Kanit",sans-serif; font-weight:600; font-size:23px; color:{INK}; }}
  .ms-brand-web {{ font-family:"Kanit",sans-serif; font-weight:600; font-size:15px; color:{AMBER}; letter-spacing:2px; }}
  .ms-brand-rule {{ width:60px; height:2px; background:{AMBER}; border-radius:1px; }}
</style>
</head>
<body>
<header>
  <div class="title">Food<span>Stock</span> Scene Editor</div>
  <button id="export-btn" onclick="exportJSON()">&#8595; Export JSON</button>
</header>
<div id="layout">
  <aside id="sidebar"></aside>
  <div id="content">
    <div id="edit-panel"></div>
    <div id="preview-pane">
      <div class="preview-wrap" id="preview-wrap">
        <div class="preview-inner" id="preview-inner" style="width:1920px;height:1080px;"></div>
      </div>
    </div>
  </div>
</div>
<script>
const data = {_data_json};
const brand = {_brand_json};
let current = 0; // index into allScenes

const allScenes = [
  {{type:'intro'}},
  ...data.map((r,i) => ({{type:'rest', index:i}})),
  {{type:'outro'}}
];

function dn(n) {{
  return n.replace(/\\s*Food Stock\\s*พัฒนาการ\\s*$/, '').replace(/\\s*พัฒนาการ\\s*$/, '').trim();
}}

function buildSidebar() {{
  const sb = document.getElementById('sidebar');
  sb.innerHTML = allScenes.map((s,i) => {{
    if (s.type === 'intro') {{
      return `<div class="r-item brand-item${{i===current?' active':''}}" onclick="select(${{i}})"><span class="r-num">INTRO</span><span class="r-name">Scene เปิด</span></div>`;
    }}
    if (s.type === 'outro') {{
      return `<div class="r-item brand-item${{i===current?' active':''}}" onclick="select(${{i}})"><span class="r-num">OUTRO</span><span class="r-name">Scene ปิด</span></div>`;
    }}
    const idx = s.index;
    return `<div class="r-item${{i===current?' active':''}}" onclick="select(${{i}})"><span class="r-num">${{String(idx+1).padStart(2,'0')}}</span><span class="r-name" id="sn-${{idx}}">${{dn(data[idx].name)}}</span></div>`;
  }}).join('');
}}

function select(i) {{
  current = i;
  document.querySelectorAll('.r-item').forEach((el,j) => el.classList.toggle('active', j===i));
  const s = allScenes[i];
  if (s.type === 'intro') {{ showIntroPanelEp(); renderIntroPreview(); }}
  else if (s.type === 'outro') {{ showOutroPanelEp(); renderOutroPreview(); }}
  else {{ showRestPanelEp(s.index); renderRestPreview(s.index); }}
}}

function showRestPanelEp(idx) {{
  const r = data[idx];
  const q = v => v.replace(/"/g,'&quot;');
  document.getElementById('edit-panel').innerHTML = `
    <div><span class="scene-badge">${{String(idx+1).padStart(2,'0')}} / ${{data.length}}</span></div>
    <div><div class="field-label">ชื่อร้าน</div>
      <input id="f-name" class="field-input" type="text" value="${{q(r.name)}}" oninput="updateRest(${{idx}})"/></div>
    <div><div class="field-label">เมนูแนะนำ (สูงสุด 3)</div>
      <div class="menu-inputs">
        <input id="f-m1" class="field-input" type="text" placeholder="เมนู 1" value="${{q(r.menu[0]||'')}}" oninput="updateRest(${{idx}})"/>
        <input id="f-m2" class="field-input" type="text" placeholder="เมนู 2" value="${{q(r.menu[1]||'')}}" oninput="updateRest(${{idx}})"/>
        <input id="f-m3" class="field-input" type="text" placeholder="เมนู 3" value="${{q(r.menu[2]||'')}}" oninput="updateRest(${{idx}})"/>
      </div></div>
    <div class="hint">1. แก้ข้อมูล → Export<br>2. Save <code>data/restaurants.json</code><br>3. <code>python3 generate.py</code><br>4. <code>npx hyperframes render -o foodstock-loop.mp4</code></div>`;
}}

function showIntroPanelEp() {{
  const q = v => v.replace(/"/g,'&quot;');
  document.getElementById('edit-panel').innerHTML = `
    <div><span class="scene-badge">INTRO</span></div>
    <div><div class="field-label">Tagline บรรทัด 1</div>
      <input id="f-it1" class="field-input" type="text" value="${{q(brand.intro_tagline_l1)}}" oninput="updateBrand()"/></div>
    <div><div class="field-label">Tagline บรรทัด 2</div>
      <input id="f-it2" class="field-input" type="text" value="${{q(brand.intro_tagline_l2)}}" oninput="updateBrand()"/></div>
    <div><div class="field-label">Subtitle</div>
      <input id="f-is" class="field-input" type="text" value="${{q(brand.intro_sub)}}" oninput="updateBrand()"/></div>
    <div class="hint">Export → Save <code>data/brand-config.json</code><br>แล้วรัน <code>python3 generate.py</code></div>`;
}}

function showOutroPanelEp() {{
  const q = v => v.replace(/"/g,'&quot;');
  document.getElementById('edit-panel').innerHTML = `
    <div><span class="scene-badge">OUTRO</span></div>
    <div><div class="field-label">เวลาเปิด</div>
      <input id="f-oh" class="field-input" type="text" value="${{q(brand.outro_hours)}}" oninput="updateBrand()"/></div>
    <div><div class="field-label">ที่อยู่</div>
      <input id="f-oa" class="field-input" type="text" value="${{q(brand.outro_addr)}}" oninput="updateBrand()"/></div>
    <div><div class="field-label">Website</div>
      <input id="f-ow" class="field-input" type="text" value="${{q(brand.outro_web)}}" oninput="updateBrand()"/></div>
    <div class="hint">Export → Save <code>data/brand-config.json</code><br>แล้วรัน <code>python3 generate.py</code></div>`;
}}

function updateBrand() {{
  const s = allScenes[current];
  if (s.type === 'intro') {{
    brand.intro_tagline_l1 = document.getElementById('f-it1').value;
    brand.intro_tagline_l2 = document.getElementById('f-it2').value;
    brand.intro_sub = document.getElementById('f-is').value;
    renderIntroPreview();
  }} else if (s.type === 'outro') {{
    brand.outro_hours = document.getElementById('f-oh').value;
    brand.outro_addr = document.getElementById('f-oa').value;
    brand.outro_web = document.getElementById('f-ow').value;
    renderOutroPreview();
  }}
}}

function updateRest(idx) {{
  data[idx].name = document.getElementById('f-name').value;
  data[idx].menu = [
    document.getElementById('f-m1').value,
    document.getElementById('f-m2').value,
    document.getElementById('f-m3').value,
  ].filter(Boolean);
  const el = document.getElementById('sn-'+idx);
  if (el) el.textContent = dn(data[idx].name);
  renderRestPreview(idx);
}}

function renderRestPreview(i) {{
  const r = data[i];
  const side = (i % 2 === 0) ? 'left' : 'right';
  const name = dn(r.name);
  const menus = (r.menu || []).slice(0,3);
  const num = String(i+1).padStart(2,'0');
  const photo = 'data/' + r.hero_local.replace(/\\\\/g,'/');
  const items = menus.map(m => `<li><span class="ms-bullet"></span>${{m}}</li>`).join('');
  const photoDiv = `<div class="ms-photo-wrap"><div class="ms-photo" style="background-image:url('${{photo}}')"></div><div class="ms-scrim ${{side}}"></div></div>`;
  const panel = `<div class="ms-panel ${{side==='left'?'bl':'br'}}"><div class="ms-ptop"><span class="ms-idx">${{num}}<span class="ms-tot">/${{data.length}}</span></span><span class="ms-plabel">ร้านแนะนำ</span></div><h1 class="ms-rname">${{name}}</h1><ul class="ms-menu">${{items}}</ul><div class="ms-pmark">FOOD STOCK</div></div>`;
  const inner = document.getElementById('preview-inner');
  inner.className = 'preview-inner';
  inner.innerHTML = `<div class="ms-split">${{side==='left' ? photoDiv+panel : panel+photoDiv}}</div>`;
  scalePreview();
}}

function renderIntroPreview() {{
  const inner = document.getElementById('preview-inner');
  inner.className = 'preview-inner cream-bg';
  inner.innerHTML = `<div class="ms-brand"><img class="ms-brand-logo" src="data/brand/logo-darkgreen.png" alt="FoodStock"/><div class="ms-brand-tagline">${{brand.intro_tagline_l1}}<br>${{brand.intro_tagline_l2}}</div><div class="ms-brand-rule"></div><div class="ms-brand-sub">${{brand.intro_sub}}</div></div>`;
  scalePreview();
}}

function renderOutroPreview() {{
  const inner = document.getElementById('preview-inner');
  inner.className = 'preview-inner cream-bg';
  inner.innerHTML = `<div class="ms-brand"><img class="ms-brand-logo" src="data/brand/logo-outro.png" alt="FoodStock"/><div class="ms-brand-sub-big">${{brand.outro_hours}}</div><div class="ms-brand-rule"></div><div class="ms-brand-sub">${{brand.outro_addr}}</div><div class="ms-brand-web">${{brand.outro_web}}</div></div>`;
  scalePreview();
}}

function scalePreview() {{
  const pane = document.getElementById('preview-pane');
  const scale = Math.min((pane.clientWidth-48)/1920, (pane.clientHeight-48)/1080);
  const wrap = document.getElementById('preview-wrap');
  wrap.style.width = (1920*scale)+'px';
  wrap.style.height = (1080*scale)+'px';
  document.getElementById('preview-inner').style.transform = `scale(${{scale}})`;
}}

function exportJSON() {{
  const dl = (name, obj) => {{
    const blob = new Blob([JSON.stringify(obj, null, 2)], {{type:'application/json'}});
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = name;
    a.click();
  }};
  dl('restaurants.json', data);
  setTimeout(() => dl('brand-config.json', brand), 300);
}}

window.addEventListener('resize', scalePreview);
buildSidebar();
select(1); // start on first restaurant (index 1 = scene 01)
</script>
</body>
</html>'''

open(os.path.join(ROOT, "editor.html"), "w", encoding="utf-8").write(EDITOR)
print("wrote editor.html")
