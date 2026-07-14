"""สร้าง contact sheet 6 ร้าน × 3 candidates สำหรับ Nut เลือก hero"""
from PIL import Image, ImageDraw, ImageFont
import os, sys

BASE = os.path.dirname(__file__)
CAND_DIR = os.path.join(BASE, "candidates")
OUT = os.path.join(BASE, "contact_sheet.jpg")

RESTAURANTS = [
    ("01", "แชมป์ เย็นตาโฟ"),
    ("03", "Tsukemen gogo"),
    ("08", "แกงป่า"),
    ("12", "โคตรกะเพรา"),
    ("15", "หมูสะเต๊ะนายหงอก"),
]

THUMB_W, THUMB_H = 600, 400
COLS = 3  # a, b, c
LABEL_H = 36
HEADER_H = 52
PAD = 12

SLATE = (73, 88, 98)    # #495862
AMBER = (245, 158, 11)
WHITE = (255, 255, 255)
DARK  = (30, 30, 30)

rows = len(RESTAURANTS)
sheet_w = COLS * THUMB_W + (COLS + 1) * PAD
sheet_h = rows * (THUMB_H + LABEL_H + PAD) + (rows + 1) * PAD + HEADER_H

sheet = Image.new("RGB", (sheet_w, sheet_h), DARK)
draw = ImageDraw.Draw(sheet)

# try system font, fallback to default
try:
    font_label = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 22)
    font_header = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 28)
    font_letter = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 72)
except:
    font_label = font_header = font_letter = ImageFont.load_default()

# header
draw.rectangle([0, 0, sheet_w, HEADER_H], fill=SLATE)
draw.text((PAD, 12), "FoodStock — Hero Photo Candidates  (เลือก a/b/c ต่อร้าน)", font=font_header, fill=WHITE)

for row_i, (prefix, name) in enumerate(RESTAURANTS):
    y_base = HEADER_H + PAD + row_i * (THUMB_H + LABEL_H + PAD)

    for col_i, suffix in enumerate(["a", "b", "c"]):
        x = PAD + col_i * (THUMB_W + PAD)
        img_path = os.path.join(CAND_DIR, f"{prefix}{suffix}.jpg")

        # amber border for slot
        draw.rectangle([x - 2, y_base - 2, x + THUMB_W + 2, y_base + THUMB_H + LABEL_H + 2], fill=AMBER)
        draw.rectangle([x, y_base, x + THUMB_W, y_base + THUMB_H], fill=(60, 60, 60))

        if os.path.exists(img_path):
            try:
                img = Image.open(img_path)
                img.thumbnail((THUMB_W, THUMB_H), Image.LANCZOS)
                # center crop
                iw, ih = img.size
                px = (THUMB_W - iw) // 2
                py = (THUMB_H - ih) // 2
                sheet.paste(img, (x + px, y_base + py))
            except Exception as e:
                draw.text((x + 10, y_base + 10), f"ERR: {e}", font=font_label, fill=(255, 80, 80))
        else:
            draw.text((x + 10, y_base + 10), "NOT FOUND", font=font_label, fill=(255, 80, 80))

        # label row
        label_y = y_base + THUMB_H
        lbl_bg = SLATE if col_i == 0 else (50, 60, 68)
        draw.rectangle([x, label_y, x + THUMB_W, label_y + LABEL_H], fill=lbl_bg)

        letter = f"  ({suffix.upper()})  {prefix}-{name}" if col_i == 0 else f"  ({suffix.upper()})"
        draw.text((x + 8, label_y + 6), letter, font=font_label, fill=WHITE)

        # big letter overlay top-right
        draw.text((x + THUMB_W - 55, y_base + 5), suffix.upper(), font=font_letter, fill=(255, 255, 255, 180))

sheet.save(OUT, quality=88)
print(f"✅ Saved: {OUT}  ({sheet.size[0]}×{sheet.size[1]})")
