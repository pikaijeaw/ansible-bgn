# BigFix Lab 13: เก็บผลลัพธ์จาก Script กลับขึ้น Console

**ปัญหา:** relevance อ่านข้อมูลบางอย่างไม่ได้ หรืออ่านได้ยาก เช่น certificate ที่ใกล้หมดอายุ หรือผลของคำสั่ง PowerShell/CLI ของ vendor
**วิธีแก้ (pattern ที่ใช้กันมาก):** Task รัน script แล้ว **เขียนผลลงไฟล์** จากนั้น Analysis **อ่านไฟล์นั้น** ด้วย relevance

```
Task (policy, ทุกวัน)                 Analysis
PowerShell → C:\ProgramData\BigFixLab\cert-expiry.txt  ──►  lines of file "...cert-expiry.txt"
```

| ไฟล์ | หน้าที่ |
|---|---|
| `collect-expiring-certificates.bes` | หา cert ใน `LocalMachine\My` ที่หมดอายุภายใน 30 วัน แล้วเขียน `Subject|Thumbprint|NotAfter` |
| `expiring-certificates-analysis.bes` | แสดงผลจากไฟล์ และอายุของไฟล์ (บอกได้ว่า script ยังทำงานอยู่ไหม) |

## ขั้นตอน
1. Import ทั้งสองไฟล์ → Activate Analysis
2. Take Action Task แบบ policy: reapply ทุก 1 วัน (Execution → *Reapply ... while relevant, waiting 1 day between reapplications*)
3. ดู property `Expiring Certificates` (`NONE` = ไม่มี cert ที่ใกล้หมดอายุ)

## ข้อควรระวัง
- ใน `createfile` ต้องเขียน `{` เป็น `{{` ทุกครั้ง แต่ `}` ไม่ต้อง (ดูในไฟล์ `.bes`)
- ไฟล์ผลลัพธ์ควรเล็ก (สรุปแล้ว) เพราะ property ทุกตัวต้องส่งขึ้น server
- ถ้าใช้ BigFix 10 ขึ้นไป อาจใช้ **WebUI Query** แทนสำหรับคำถามแบบครั้งเดียว

## แบบฝึกหัด
1. ทำเวอร์ชัน Linux: หา cert ใน `/etc/pki/tls/certs` ด้วย `openssl x509 -enddate`
2. เปลี่ยนให้ Task เขียนผลเป็น JSON แล้วใช้ `json of file` inspector (BigFix 10+) แยก field
