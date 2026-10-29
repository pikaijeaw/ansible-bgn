# BigFix Labs (ใช้งานจริง)

BigFix ไม่มีเวอร์ชัน open source ที่รันใน Docker ได้แบบ Ansible ส่วนนี้จึงมี 3 ระดับให้เลือกฝึก
1. **ไม่มี server เลย:** ฝึก relevance ด้วย QnA/Fixlet Debugger บนเครื่องที่ลง agent, ฝึก REST API กับ mock, และตรวจไฟล์ `.bes` ด้วย validator
2. **มี lab server (evaluation):** import ไฟล์ `.bes` ทั้งหมดใน `labs/` แล้วทำตาม README ของแต่ละ lab
3. **ใช้ร่วมกับ Ansible:** ดู [`ansible/labs/lab16-bigfix-integration`](../ansible/labs/lab16-bigfix-integration/)

## ตั้ง Lab Server (แนะนำ)
| เครื่อง | สเปกขั้นต่ำสำหรับ lab | หมายเหตุ |
|---|---|---|
| BigFix Root Server | Windows Server 2019/2022, 4 vCPU, 16 GB RAM, 100 GB | ติดตั้ง SQL Server Express/Developer ได้ใน lab |
| Windows client 1-2 เครื่อง | Windows 10/11 หรือ Server | ลง BigFix Agent |
| Linux client 1 เครื่อง | Rocky 9 / Ubuntu 24.04 | ลง BESAgent rpm/deb |

1. ขอ **evaluation license** จาก HCL (หน้า BigFix บน hcl-software.com → Free Trial) จะได้ license file สำหรับสร้าง masthead
2. ติดตั้ง SQL Server → รัน BigFix Server installer (เลือก *Evaluation*) → ติดตั้ง Console
3. ใน Console: License Overview → เปิด site ที่ต้องใช้ เช่น *Patches for Windows*, *BES Inventory and License*
4. สร้าง custom site ชื่อ `Lab-Automation`
5. ติดตั้ง agent ให้ client:
   - Windows: ใช้ **BigFix Client Deploy Tool** หรือ `BigFix-BES-Client-*.exe` พร้อม `masthead.afxm` ในโฟลเดอร์เดียวกัน
   - Linux: วาง masthead ที่ `/etc/opt/BESClient/actionsite.afxm` แล้วติดตั้ง rpm/deb (ดู lab07)
6. เปิด port **52311 TCP/UDP** ระหว่าง client ↔ relay/server

## Import content จาก repo นี้
```bash
# ตรวจไฟล์ก่อน
python3 bigfix/scripts/validate_bes.py bigfix/labs

# วิธี 1: Console → File → Import → เลือกไฟล์ .bes → เลือก site Lab-Automation
# วิธี 2: REST API
cd bigfix/api
BIGFIX_URL=https://<server>:52311 BIGFIX_USER=<op> BIGFIX_PASSWORD=<pw> \
  python3 bigfix_api.py --insecure import ../labs/*/*.bes --site Lab-Automation
# วิธี 3: Ansible (ansible/labs/lab16-bigfix-integration/import-content.yml)
```

## รายการ Lab
| # | Lab | สถานการณ์จริง | Content |
|---|---|---|---|
| 01 | [Client Relevance](labs/lab01-relevance-basics/) | พื้นฐานที่ต้องใช้ทุกงาน | แบบฝึกหัด QnA พร้อมเฉลย |
| 02 | [Session Relevance](labs/lab02-session-relevance/) | รายงาน / dashboard / API | query ที่ใช้บ่อย |
| 03 | [Inventory Analysis](labs/lab03-inventory-analysis/) | asset inventory, serial, BitLocker | 3 Analyses |
| 04 | [Computer Groups](labs/lab04-computer-groups/) | targeting ตาม OS / env / subnet | 5 Groups |
| 05 | [Software Deploy (Windows)](labs/lab05-software-deploy-windows/) | ติดตั้งโปรแกรมทั้งองค์กร | MSI + EXE Tasks |
| 06 | [Uninstall / Prohibited SW](labs/lab06-software-uninstall/) | ลบโปรแกรมต้องห้ามอัตโนมัติ | Task + Fixlet (policy) |
| 07 | [Linux Software](labs/lab07-linux-software/) | ติดตั้ง package บน RHEL/Ubuntu | ActionScript + `x-sh` |
| 08 | [Self-Healing Services](labs/lab08-service-self-healing/) | service ล่มแล้วกลับมาเอง | 2 Fixlets |
| 09 | [Security Hardening](labs/lab09-security-hardening/) | SMBv1, TLS 1.0, SSH root | 3 Fixlets |
| 10 | [Patch Management](labs/lab10-patch-management/) | Patch Tuesday, baseline, maintenance window | pre-check + restart Tasks |
| 11 | [Disk Cleanup](labs/lab11-disk-cleanup/) | disk เต็ม | Fixlet + PowerShell |
| 12 | [Local Admin Audit](labs/lab12-local-admin-audit/) | access review | Analysis + Task |
| 13 | [Script Result Capture](labs/lab13-script-result-capture/) | ข้อมูลที่ relevance อ่านเองไม่ได้ | Task + Analysis |
| 14 | [Client Settings](labs/lab14-client-settings/) | tagging, คุม CPU, agent health | 2 Tasks + Analysis |
| 15 | [REST API](labs/lab15-rest-api/) | เชื่อมระบบอื่น / content as code | `bigfix_api.py` |

## สถานะการทดสอบ
- ไฟล์ `.bes` ทั้ง 29 ไฟล์ผ่าน `validate_bes.py` (XML, ลำดับ element ตาม BES.xsd, relevance วงเล็บ/quote ครบ) และ import เข้า mock API ได้ครบ
- `bigfix_api.py` และ Ansible lab16 ทดสอบกับ mock แล้ว
- **ยังไม่ได้ทดสอบบน BigFix server จริง** (ใน sandbox ไม่มี license หรือ server) ก่อนใช้งานจริงให้ทดสอบ relevance ทุกข้อด้วย Fixlet Debugger และ deploy กับ Pilot group ก่อน
- `prefetch` ใน lab05 ใช้ hash เป็น placeholder ต้องแทนด้วยค่าจริงก่อนใช้

## Cheat sheet
```
Fixlet  = Relevance (มีปัญหา?) + Action (แก้)  → success: relevance กลายเป็น false = Fixed
Task    = Relevance (ควรทำ?)  + Action         → success: action รันจบ
Baseline= กลุ่มของ Fixlet/Task ที่ deploy พร้อมกัน
Analysis= Property ที่ agent รายงานขึ้นมา (inventory/report)
Group   = Automatic (relevance) / Manual / Server-based
Site    = ที่เก็บ content: External (HCL) / Custom / Operator
Port    = 52311 TCP (gather/report) + UDP (notification)
```
