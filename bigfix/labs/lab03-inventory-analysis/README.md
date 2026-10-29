# BigFix Lab 03: Hardware & Software Inventory ด้วย Analysis

**สถานการณ์จริง:** ฝ่าย IT Asset ต้องการ serial number, รุ่นเครื่อง, RAM, disk, สถานะ BitLocker และรายชื่อโปรแกรมที่ติดตั้ง ของ endpoint ทุกเครื่อง
โดยไม่ต้องให้คนเดินไปดูหรือสั่ง script ทุกครั้ง

| ไฟล์ | ประเภท | ได้อะไร |
|---|---|---|
| `hardware-inventory-windows.bes` | Analysis | Manufacturer, Model, Serial, CPU, RAM, C: free, IP, Last boot, BitLocker, Agent version |
| `hardware-inventory-linux.bes` | Analysis | Distribution, Kernel, RAM, / free, Uptime, IP |
| `installed-software-windows.bes` | Analysis | รายชื่อโปรแกรม + เวอร์ชัน จาก registry Uninstall (64/32 bit) |

## ขั้นตอน
1. Console → **File → Import** → เลือกไฟล์ `.bes` → เลือก custom site (เช่น `Lab-Automation`)
   หรือใช้ API: `python3 ../../api/bigfix_api.py import *.bes --site Lab-Automation`
2. เปิด Analysis → **Activate** (Analysis จะไม่ทำงานจนกว่าจะ activate)
3. รอ 1–2 รอบการรายงาน แล้วไปที่แท็บ **Results**
4. ทำรายงานใน **Web Reports** → Explore Data → เลือก property → Export CSV

## จุดที่ควรสังเกต
- `EvaluationPeriod` (เช่น `PT1H`, `P1D`) กำหนดความถี่ที่ agent ประเมินใหม่ property ที่เปลี่ยนไม่บ่อย (serial, model) ตั้งเป็นวันละครั้ง เพื่อไม่ให้เปลือง CPU และ bandwidth
- WMI (`selects "... from Win32_..." of wmi`) ช้ากว่า inspector ปกติ ใช้เท่าที่จำเป็น
- ใช้ property ใน Computer Group / Dashboard ต่อได้ เช่นหาเครื่องที่ BitLocker = 0

## แบบฝึกหัด
1. เพิ่ม property `Domain/Workgroup`: `string values of selects "Domain from Win32_ComputerSystem" of wmi`
2. เพิ่ม property `Logged on User`: `names of current users`
3. เขียน session relevance หาเครื่องที่ RAM < 8192 MB (ดู lab02)
4. เปรียบเทียบกับ Ansible lab12 ที่ต้องรัน playbook ทุกครั้ง ส่วน BigFix อัปเดตเองตลอดเวลา
