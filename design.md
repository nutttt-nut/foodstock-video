# FoodStock — Loop Video Design

Brand pulled from foodstock.info. Minimal slate roofline logo + calm "พื้นที่แห่งความสุข" mood.
Structural color = slate (logo). Warm amber accent makes food appetizing (per DESIGN.md: warm accent for appetite).

## Palette

| Token | HSL / Hex | Use |
|-------|-----------|-----|
| slate-900 | `#2A333B` | restaurant scene background |
| slate-700 | `#495862` | text panel (exact logo color) |
| slate-600 | `#5C6B75` | hairlines, dim panel edge |
| cream | `#F5EFE6` | intro/outro background, primary text on slate |
| cream-dim | `#C7CDD2` | secondary text on slate |
| amber | `#E0A43B` | accent — index number, menu bullets, accent border |
| amber-bright | `#F2BB52` | hover/glow highlight |
| ink | `#2A333B` | text on cream |

WCAG: cream `#F5EFE6` on slate-700 = ~8:1 ✓. amber `#E0A43B` on slate-900 = ~6:1 ✓ (large text).

## Typography

- **Display / restaurant names:** `Kanit` (700) — geometric Thai, punchy
- **Body / menu items:** `Noto Sans Thai` (400/600)
- Scale (video): name 88–120px (fit), menu 40px, label 26px, index 64px
- `tabular-nums` not needed (no number columns)

## Corners & Depth

- Radius: `0` (panels full-bleed) · `16px` (chips only)
- Accent border: `4px solid amber` on the text panel inner edge (DESIGN.md accent-border)
- Depth: flat. Photo gets one inset hairline `inset 0 0 0 1px rgba(0,0,0,.15)`; soft gradient scrim on photo edge for text legibility only.

## Motion

- Calm, premium. Crossfade dissolve between scenes (0.7s). Photo: slow ken-burns scale 1.06→1.0 over the hold. Text: stagger up-fade (Kanit name first, menu items stagger 90ms).
- Eases: `power3.out` (name), `power2.out` (menu), `sine.inOut` (ken-burns).

## Structure (16:9, 1920×1080)

1. **Intro** (cream bg) — slate logo + tagline "มากกว่าศูนย์อาหาร คือพื้นที่แห่งความสุข" + "16 ร้านเด็ด · พัฒนาการ 32"
2. **16 restaurant scenes** (slate bg) — split: photo 52% (alternating L/R) + slate panel 48% with index `NN/16`, name, เมนูแนะนำ (≤3) or name-derived signature
3. **Outro** (cream bg, matches intro for seamless loop) — logo + "จ–ส 8:00–21:00" + "471 พัฒนาการ 32" + foodstock.info

## Don'ts

- No stretched photos (object-fit: cover; never distort aspect)
- No invented menu items — only scraped dishes or signature literally in the shop name
- No flat grey without the slate hue; no pure black
- No full-screen linear gradients on slate (H.264 banding — use scrim only at photo edge)
