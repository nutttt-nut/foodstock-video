# FoodStock Video — Workflow Notes

## อยากปรับ workflow (noted 2026-06-26)

Current workflow ยุ่งยาก — ต้องทำ 4 steps ทุกครั้ง:
1. แก้ใน `editor-pro.html` browser
2. Export JSON → ย้ายไป `data/`
3. `python3 generate.py`
4. `npx hyperframes render .`

**Pain point:** editor-pro.html data บางครั้ง out-of-sync กับ `data/restaurants.json` ทำให้ preview ไม่ตรงกับ video จริง

## Ideas ที่น่าปรับ
- [ ] ทำให้ editor-pro.html อ่านข้อมูลจาก `data/restaurants.json` โดยตรง (fetch local) แทน baked-in
- [ ] Script ที่รวม step 2-4 เป็นคำสั่งเดียว (`./build.sh` หรือ Makefile)
- [ ] Auto-sync: เมื่อ Export JSON จาก editor-pro.html ให้ trigger generate.py อัตโนมัติ
