# หลักการทำงานของ BigFix

## 1. BigFix คืออะไร
HCL BigFix (เดิมเป็นของ IBM) เป็นแพลตฟอร์ม Endpoint Management สำหรับ Patch Management, Software Distribution,
Compliance (CIS/DISA STIG), Inventory และ Remote Control รองรับได้เป็นแสนเครื่องจาก server เดียว
ใช้ได้กับ Windows, Linux, macOS, AIX และ Solaris

## 2. หลักการสำคัญ (ต่างจาก Ansible มาก)
| หลักการ | ความหมาย |
|---|---|
| **Agent-based** | ทุกเครื่องต้องลง BigFix Agent (BES Client) |
| **Intelligent agent** | agent ประเมินสถานะของเครื่องตัวเองตลอดเวลา server ไม่ต้องคอยสแกน |
| **Pull + Notify** | server ส่งสัญญาณ UDP สั้นๆ บอกว่ามีของใหม่ แล้ว agent ดึงข้อมูลลงมาเอง |
| **Relevance-driven** | ทุก content มีเงื่อนไข (Relevance) ที่ agent ใช้ตัดสินว่า "เรื่องนี้เกี่ยวกับเครื่องเราไหม" |
| **รายงานผลเกือบ real-time** | agent ส่งกลับเฉพาะสิ่งที่เปลี่ยน ใช้ bandwidth น้อย |

## 3. สถาปัตยกรรม
```
                ┌───────────────────────────┐
  Console/WebUI │  BigFix Root Server       │◄── HCL Content Sites (Patches for Windows ฯลฯ)
  Web Reports ─►│  + Database (MSSQL/DB2)   │
  REST API      └────────────┬──────────────┘
                             │ port 52311
                ┌────────────┴────────────┐
           ┌────▼────┐               ┌────▼────┐
           │ Relay A │               │ Relay B │   ← cache ไฟล์/patch และกระจายโหลด
           └────┬────┘               └────┬────┘
       ┌────────┼────────┐                │
    ┌──▼──┐  ┌──▼──┐  ┌──▼──┐          ┌──▼──┐
    │Agent│  │Agent│  │Agent│          │Agent│
    └─────┘  └─────┘  └─────┘          └─────┘
```
| Component | หน้าที่ |
|---|---|
| Root Server | ศูนย์กลาง เก็บ content, action และผลที่ agent รายงานมา |
| Database | SQL Server หรือ DB2 |
| Relay | cache ไฟล์และส่งต่อข้อมูล ลดโหลด server และ WAN (มี internet relay ไว้ให้เครื่องที่ทำงานที่บ้าน) |
| Agent (BES Client) | ประเมิน relevance และรัน action บนเครื่อง |
| Console / WebUI | ใช้สร้างและสั่ง deploy |
| Web Reports / Insights | รายงาน |
| REST API | `https://server:52311/api/...` (lab15 และ Ansible lab16) |

## 4. Flow การทำงานทีละขั้น
1. HCL ปล่อย Fixlet ใหม่เข้า **External Site**
2. Root Server ดึง content มาแล้วส่ง notification (UDP 52311) ผ่าน Relay ไปถึง Agent
3. Agent **gather** content ใหม่จาก Relay
4. Agent **ประเมิน Relevance** ของทุก Fixlet ในเครื่องตัวเอง แล้วรายงานว่าเครื่องตัวเอง relevant กับอะไรบ้าง
5. ใน Console ผู้ดูแลจะเห็นว่า "มี 1,250 เครื่องที่ต้องลง patch นี้" แล้วกด **Take Action** (เลือก target, schedule, maintenance window)
6. Agent ดาวน์โหลดไฟล์จาก Relay แล้วรัน **ActionScript**
7. Agent ประเมิน relevance อีกรอบ ถ้าเป็น false จะรายงาน **Fixed** ถ้ายังเป็น true จะรายงาน **Failed**

## 5. ประเภทของ Content
| Content | คำอธิบาย | Lab |
|---|---|---|
| Fixlet | Relevance + Action โดย relevance ที่เป็น true แปลว่ามีปัญหา เมื่อแก้แล้วต้องกลายเป็น false | 06, 08, 09, 11 |
| Task | เหมือน Fixlet แต่ใช้กับงานทั่วไป (success = action รันจบ) | 05, 07, 10, 12-14 |
| Baseline | กลุ่มของหลาย Fixlet/Task ที่ deploy พร้อมกัน | 10 |
| Analysis | ชุด Property สำหรับ inventory และรายงาน | 03, 12-14 |
| Computer Group | Automatic (ตาม relevance) / Manual | 04 |
| Site | ที่เก็บ content (External, Custom, Operator) | ทุก lab |

## 6. ภาษาที่ต้องรู้
**Client Relevance** (lab01):
```
name of operating system
exists file "C:\Windows\notepad.exe"
free space of drive "C:" / (1024 * 1024 * 1024)
(name of it, version of it) of regapps whose (name of it as lowercase = "notepad++.exe")
```
**Session Relevance** (lab02):
```
(name of it, last report time of it as string) of bes computers whose (last report time of it < now - 7 * day)
```
**ActionScript** (lab05):
```
prefetch npp.exe sha1:<sha1> size:<size> http://fileserver/npp.exe sha256:<sha256>
waithidden __Download\npp.exe /S
continue if {exit code of action = 0}
```

## 7. BigFix เทียบกับ Ansible
| หัวข้อ | Ansible | BigFix |
|---|---|---|
| Agent | ไม่ต้องลง | ต้องลง BES Client |
| Model | Push | Pull + Notify |
| ภาษา | YAML + Jinja2 | Relevance + ActionScript |
| จุดเด่น | config, deploy app, orchestration (rolling, LB) | patch, compliance, inventory ของ endpoint จำนวนมาก |
| เครื่องที่ offline | ต้องต่อถึงกันตอนรัน | agent ทำงานต่อได้ แล้ว sync เมื่อกลับมาออนไลน์ |
| การตรวจ drift | ต้องรันตามรอบ (`--check`) | ตรวจตลอดเวลา (policy action) |
| ใช้ร่วมกัน | ผ่าน BigFix REST API (Ansible lab16 / BigFix lab15) | ← |
