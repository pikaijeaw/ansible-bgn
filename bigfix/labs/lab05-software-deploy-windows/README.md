# BigFix Lab 05: Software Distribution บน Windows

**สถานการณ์จริง:** ต้องติดตั้งโปรแกรมให้เครื่องหลายพันเครื่อง ทั้งสาขาและคนที่ทำงานที่บ้าน โดย
- ดาวน์โหลดไฟล์ครั้งเดียวที่ relay แล้วกระจายต่อ (ไม่ให้ WAN เต็ม)
- ติดตั้งเฉพาะเครื่องที่ยังไม่มีหรือเวอร์ชันเก่า
- ตรวจ exit code และเก็บ log

| ไฟล์ | สิ่งที่ได้เรียน |
|---|---|
| `install-7zip.bes` | MSI: `prefetch`, `msiexec /qn`, `continue if {exit code ...}`, relevance เช็คเวอร์ชันจาก registry |
| `install-notepadpp-exe.bes` | EXE `/S`, ตรวจผลด้วย PowerShell, `action uses wow64 redirection false`, `{{` escape |

## ขั้นตอน
1. ดาวน์โหลด installer จริงแล้วหา hash:
   ```powershell
   certutil -hashfile 7z2408-x64.msi SHA1
   certutil -hashfile 7z2408-x64.msi SHA256
   (Get-Item 7z2408-x64.msi).Length
   ```
2. แก้บรรทัด `prefetch` ในไฟล์ `.bes` (ค่า `0000...` เป็น placeholder ที่ต้องแทนด้วยค่าจริง)
   หรือใช้ Console → **Tools → Create Task** / **Software Distribution → Manage Software** ซึ่งจะคำนวณ hash ให้
3. Import แล้ว **Take Action** → target เป็น group ทดสอบ (lab04)
4. ดูผลที่แท็บ Action → ทุกเครื่องควรขึ้น **Completed**
5. Task นี้จะหายจากรายการ Relevant ของเครื่องที่ติดตั้งแล้ว เพราะ relevance เป็น false

## ActionScript ที่ใช้บ่อย
| คำสั่ง | ความหมาย |
|---|---|
| `prefetch <name> sha1:<> size:<> <url> sha256:<>` | ดาวน์โหลดผ่าน relay พร้อมตรวจ hash ไฟล์จะอยู่ใน `__Download\` |
| `waithidden <cmd>` | รันแบบซ่อนหน้าต่างและรอจนจบ |
| `run` / `wait` | รันไม่รอ / รันและรอ |
| `continue if {relevance}` | ถ้า false ให้ action fail ทันที |
| `{relevance}` | substitution: ใส่ค่าจาก relevance ลงในคำสั่ง |
| `createfile until <END>` | สร้างไฟล์ (เช่น script) จากเนื้อหาใน action |
| `action uses wow64 redirection false` | ให้ agent 32-bit เรียก program 64-bit ได้ |
| `{{` | ใส่ `{` ตรงตัว (จำเป็นมากในโค้ด PowerShell) |

## แบบฝึกหัด
1. เพิ่ม Action2 "Install and reboot" ที่ต่อท้ายด้วย `action requires restart`
2. ทำ Offer ให้ผู้ใช้กดติดตั้งเองจาก Self-Service Application (Take Action → Offer)
3. เปรียบเทียบกับ Ansible lab15 (`win_package` / `win_chocolatey`)
