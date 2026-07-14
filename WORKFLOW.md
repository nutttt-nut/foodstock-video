# Data-Driven Loop Video — Workflow

> Stack: **HyperFrames** + **Python generate.py** + **GSAP**
> Output: 1920×1080 · 30fps · MP4 loop สำหรับ TV/จอภายใน

---

## Tools & Dependencies

### Core Pipeline

| Tool | Version | บทบาท | Install |
|------|---------|--------|---------|
| **Python 3** | 3.9+ | รัน generate.py — สร้าง index.html + editor.html จาก JSON | built-in (macOS) |
| **Node.js** | 18+ | runtime สำหรับ HyperFrames | `brew install node` |
| **HyperFrames** | latest | render HTML → frame-by-frame → MP4 | `npm install -g hyperframes` |
| **ffmpeg** | 6+ | video encoding (HyperFrames ใช้ภายใน) | `brew install ffmpeg` |
| **Flask** | 3.x | VPS editor backend สำหรับ save/upload/regenerate | service-local venv on VPS |

### Libraries ใน index.html (video source)

| Library | Version | บทบาท | โหลดจาก |
|---------|---------|--------|---------|
| **GSAP** | 3.14.2 | animation: ken-burns, crossfade, stagger text | jsDelivr CDN |
| **Inter** | — | sans-serif หลักของ Default theme | Google Fonts |

### Libraries ใน direction-preview.html

| Font | บทบาท | ใช้ใน Direction |
|------|--------|----------------|
| **Playfair Display** | serif premium | Warm Kitchen, Cinematic Reel |
| **Inter** | clean sans-serif | Warm Kitchen (menus) |
| **Caveat** | handwriting | Warm Kitchen (menu text) |
| **Space Grotesk** | urban bold | Noir Grid, Street Cut |

### Libraries ใน editor-pro.html

| Library | บทบาท |
|---------|--------|
| Vanilla JS | drag reorder, preview, upload/save controls |
| Flask backend | writes JSON/uploads to disk when opened through SSH tunnel |

### Python stdlib (ไม่ต้อง install เพิ่ม)

```
json · os · html · re
```

---

### Quick Install (ครั้งแรก)

```bash
brew install node ffmpeg
npm install -g hyperframes
# ตรวจสอบ
hyperframes --version
ffmpeg -version | head -1
python3 --version
```

---

## ภาพรวม

```
data/ ──────────────────────┐
  restaurants.json          │
  brand-config.json         ├──► generate.py ──► index.html ──► HyperFrames ──► .mp4
  photos/*.jpg              │                 └──► editor-pro.html (VPS editor)
  overlays/*.png            │
  brand/*.png               │
────────────────────────────┘
```

- **generate.py** — อ่าน data → สร้าง `index.html` และ `editor.html`
- **index.html** — source ของ video
- **editor-pro.html** — browser UI สำหรับแก้ scene, reorder, upload, overlay/icon positioning
- **server.py** — localhost-only Flask backend สำหรับ VPS editing
- **HyperFrames** — render index.html → frame-by-frame → ffmpeg → .mp4

---

## VPS Editor Flow

VPS editing uses `/opt/foodstock-editor/data/` as the canonical copy while editing. The editor is public on port 8090 with Basic Auth:

```text
http://152.42.197.67:8090
```

Credentials are stored on the VPS in `/etc/foodstock-editor.env`.

SSH tunnel fallback/admin access:

```bash
ssh -L 8090:localhost:8090 root@152.42.197.67
```

Then open locally:

```text
http://localhost:8090
```

Editor actions:

1. Reorder restaurant scenes by dragging rows in the sidebar. Intro/outro stay pinned.
2. Upload real restaurant photos from the photo file input. Uploaded files land in `data/photos/`.
3. Upload overlays/icons from the overlay file input. Uploaded files land in `data/overlays/`.
4. Drag overlays directly on the 1920×1080 preview. Positions save as `x_pct` / `y_pct`; width stays `width_px`.
5. Click `Save` to write `data/restaurants.json` and `data/brand-config.json`.
6. Click `Regenerate` to run `python3 generate.py` on the VPS. This updates `index.html`; it does not render the final MP4.

Pull VPS edits back to the local repo when ready:

```bash
scripts/pull-foodstock-editor-data.sh
```

This only rsyncs `/opt/foodstock-editor/data/` into `Output/foodstock-video/data/`. It does not run git commands.

Service management on the VPS:

```bash
systemctl status foodstock-editor
systemctl restart foodstock-editor
```

## โครงสร้างไฟล์

```
foodstock-video/
├── generate.py              # main generator
├── server.py                # localhost-only editor backend
├── index.html               # video source (auto-generated)
├── editor-pro.html          # VPS editor
├── editor.html              # basic generated editor
├── foodstock-loop.mp4       # output
└── data/
    ├── restaurants.json     # ข้อมูลร้านและ scene order
    ├── brand-config.json    # ข้อความ intro/outro (optional)
    ├── photos/              # รูปอาหารแต่ละร้าน (.jpg/.jpeg)
    ├── overlays/            # badge/promo/icon overlays
    └── brand/
        ├── logo-darkgreen.png  # logo สำหรับ intro
        └── logo-outro.png      # logo สำหรับ outro
```

---

## Workflow ทีละขั้น

### 1. แก้เนื้อหา (ไม่ต้อง touch HTML)

**วิธี A — ผ่าน VPS editor-pro.html (แนะนำ)**
```
เปิด http://localhost:8090 ผ่าน SSH tunnel
→ เลือก scene จาก sidebar
→ แก้ข้อความ / รูป / overlays → preview อัปเดต real-time
→ กด Save
→ กด Regenerate เมื่อต้องการอัปเดต index.html
```

**วิธี B — แก้ JSON ตรง**
```
เปิด data/restaurants.json
→ แก้ name / menu1 / menu2 / menu3
เปิด data/brand-config.json (ถ้ามี)
→ แก้ข้อความ intro/outro
```

> ⚠️ ถ้าแก้ผ่าน Numbers/Excel → export เป็น CSV ก่อน (File > Export To > CSV)
> อย่า save ทับไฟล์เดิมโดยตรง — Numbers จะ convert เป็น .iwa binary

---

### 2. Regenerate HTML

```bash
python3 generate.py
```

Output:
```
wrote index.html | 18 scenes | duration 87.2s
wrote editor.html
```

---

### 3. Preview ก่อน render

เปิด index.html ในเบราว์เซอร์ตรวจ layout/ข้อความ
หรือใช้ editor-pro.html เพื่อ preview ทีละ scene

> **กฎเหล็ก**: preview frame ก่อน render เป็น mp4 เสมอ

---

### 4. Render เป็น MP4

```bash
npx hyperframes render index.html --fps 30 --output foodstock-loop.mp4
```

ระยะเวลา: ขึ้นกับจำนวน scene และเครื่องที่ render

---

### 5. ตรวจ output

```
ขนาดไฟล์:  ~80–100 MB
ความยาว:   87.2s (16 ร้าน × 5s + intro 3.2s + outro 3s)
Resolution: 1920×1080
FPS:        30
```

---

## Duration Math

| ค่า | ผลลัพธ์ |
|-----|---------|
| SCENE_HOLD = 5s | จำนวนร้าน × 5s |
| Intro | 3.2s |
| Outro | ~4s |
| **รวม** | intro + restaurant scenes + outro |

เปลี่ยน `SCENE_HOLD` ใน generate.py บรรทัดเดียว → duration เปลี่ยนทั้งหมด

---

## เปลี่ยนรูปภาพ

1. วางรูปใหม่ใน `data/photos/`
2. ตั้งชื่อให้ตรงกับ `id` ใน restaurants.json
   - เช่น id = `07-เนื้อในตำนาน` → ไฟล์ = `07-เนื้อในตำนาน.jpg`
3. รองรับ: `.jpg` `.jpeg` `.png` `.webp`
4. `python3 generate.py` → render ใหม่

---

## เปลี่ยน Visual Direction (Theme)

แต่ละ theme คือ CSS block ใน `generate.py` ฟังก์ชัน `scene_html()`

| Theme | โทน | Background | Typography |
|-------|-----|------------|------------|
| **Default** (ปัจจุบัน) | Dark minimal | Slate `#2A333B` | Inter / split-screen |
| **Warm Kitchen** | Homey × Premium | Cream `#f7efe3` | Playfair + Caveat |
| **Noir Grid** | Urban × Premium | Dark + grain | Space Grotesk bold |
| **Cinematic Reel** | Premium slow | Black + letterbox | Playfair lower-third |
| **Street Cut** | Energetic | Dark overlay | Space Grotesk caps |

---

## Video Source (แทนรูปถ่าย)

แทน `<img>` ด้วย `<video>` ใน scene template:

```html
<!-- แทนที่ img tag -->
<video src="data/clips/07-nntn.mp4"
       autoplay loop muted playsinline
       style="width:100%;height:100%;object-fit:cover">
</video>
```

วาง clip ใน `data/clips/` ตั้งชื่อเหมือน pattern รูป
HyperFrames จะ capture video frame ตาม timestamp อัตโนมัติ

---

## Key Commands

```bash
# regenerate index.html + editor.html
python3 generate.py

# render final mp4
npx hyperframes render index.html --fps 30 --output foodstock-loop.mp4

# render preview (ความละเอียดต่ำ เร็วกว่า)
npx hyperframes render index.html --fps 15 --scale 0.5 --output preview.mp4

# เปิด editor
open editor.html
```

---

## การแก้ไขที่พบบ่อย

| ต้องการแก้ | ทำที่ไหน |
|-----------|---------|
| ข้อความเมนู | editor.html → Export JSON หรือ restaurants.json ตรง |
| ข้อความ intro/outro | editor.html → Export JSON หรือ brand-config.json |
| รูปภาพร้าน | วางไฟล์ใหม่ใน data/photos/ |
| ระยะเวลา scene | SCENE_HOLD ใน generate.py |
| สีพื้นหลัง | CSS ใน scene_html() ใน generate.py |
| Logo | แทนไฟล์ใน data/brand/ |
| เพิ่ม/ลดร้าน | restaurants.json |

---

*FoodStock Video · Agency-Photograph · พัฒนาการ 32*
