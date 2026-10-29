# BigFix Lab 04: Automatic Computer Groups (Targeting)

**สถานการณ์จริง:** ต้อง deploy patch ให้ "Windows Server ใน production" แยกจาก "Workstation" และ "Linux"
ถ้าใช้ manual group เครื่องใหม่จะตกหล่น ส่วน automatic group จะจัดกลุ่มเครื่องเองตาม relevance

| ไฟล์ | Group | Relevance |
|---|---|---|
| `group-windows-servers.bes` | Windows Servers | `product type of operating system != workstation product type` |
| `group-windows-workstations.bes` | Windows Workstations | `= workstation product type` |
| `group-linux.bes` | Linux | `name of operating system as lowercase contains "linux"` |
| `group-env-production.bes` | Production | client setting `Environment = Production` (ตั้งด้วย lab14) |
| `group-subnet-hq.bes` | HQ subnet | IP ขึ้นต้นด้วย `10.10.` |

## ขั้นตอน
1. Import ไฟล์ด้วย Console (File → Import) หรือ `bigfix_api.py import`
2. Console → **Computer Groups** → ดูสมาชิก (รอ agent ประเมินสักครู่)
3. ลอง deploy Task จาก lab05 แล้วเลือก Target เป็น **"All computers in the group"**

## แนวทางในงานจริง
- ตั้งชื่อเป็นระบบ เช่น `OS - ...`, `Env - ...`, `Location - ...`, `App - ...` จะทำให้เลือก target ได้ง่าย
- ให้ group จาก client setting (Environment, Owner, App) เป็นตัวหลักในการ targeting เพราะชัดเจนกว่าการเดาจากชื่อเครื่อง
- ใช้ group สร้าง **Maintenance Window** ต่อกลุ่ม (BigFix 10+ มี Maintenance Window Dashboard)

## แบบฝึกหัด
1. สร้าง group "Laptops" จาก `exists batteries` หรือ WMI `Win32_Battery`
2. สร้าง group "Pilot" แบบ manual แล้วใช้ deploy patch ให้กลุ่มเล็กก่อนทั้งองค์กร
