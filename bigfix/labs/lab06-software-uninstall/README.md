# BigFix Lab 06: ถอนการติดตั้งโปรแกรม และกำจัดโปรแกรมต้องห้าม

| ไฟล์ | ประเภท | ใช้เมื่อ |
|---|---|---|
| `uninstall-msi-by-name.bes` | Task + `action parameter query` | ถอนโปรแกรม MSI ตามชื่อที่กรอกตอน Take Action |
| `remove-prohibited-software.bes` | Fixlet (compliance) | เครื่องที่มีโปรแกรมต้องห้าม (ตัวอย่างนี้คือ TeamViewer) จะขึ้น relevant แล้วลบด้วย UninstallString |

## ขั้นตอน
1. Import ทั้งสองไฟล์
2. ติดตั้ง 7-Zip จาก lab05 บนเครื่องทดสอบ → Take Action `uninstall-msi-by-name` → กรอก `7-Zip`
3. สำหรับโปรแกรมต้องห้าม ให้ Take Action แบบ **Policy**:
   - Execution → ✔ *Reapply this action whenever it becomes relevant again*
   - Target → *Dynamically target by property* หรือ All computers
   - ถ้ามีคนลงกลับ BigFix จะลบให้อัตโนมัติภายในไม่กี่นาที

## จุดที่ควรสังเกต
- Exit code `1605` = ไม่พบสินค้า (ถือว่าสำเร็จ เพราะไม่มีของให้ลบแล้ว)
- Fixlet ใช้ success criteria แบบ **Original Relevance** ถ้าลบแล้วยังเจอโปรแกรมอยู่ จะขึ้น *Failed* ไม่ใช่ *Fixed*
- relevance ที่ได้ค่า plural ใน substitution (`{...}`) จะ error ถ้าเจอหลายตัว ควรทำให้เหลือค่าเดียว

## แบบฝึกหัด
1. ทำให้ `remove-prohibited-software` รองรับหลายโปรแกรม (AnyDesk, uTorrent) โดยใช้ Action แยกกัน
2. สร้าง Analysis property แสดงว่าเครื่องไหนมีโปรแกรมต้องห้ามอะไรบ้าง ใช้เป็นรายงานให้ security
