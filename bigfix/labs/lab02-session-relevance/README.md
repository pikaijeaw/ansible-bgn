# BigFix Lab 02: Session Relevance (ถามข้อมูลจาก Server)

**ความต่างจาก Client Relevance:**
| | Client Relevance | Session Relevance |
|---|---|---|
| ประเมินที่ | agent บนแต่ละเครื่อง | root server / Web Reports / REST API |
| ถามเรื่อง | สถานะของเครื่องนั้น | ข้อมูลที่ agent ทุกตัวรายงานขึ้นมาแล้ว (computers, fixlets, actions, properties) |
| ใช้ใน | Fixlet, Analysis, Group | Dashboard, Web Reports, REST API `/api/query`, Presentation Debugger |

## เครื่องมือ
- Console: เปิด **Presentation Debugger** (กด `Ctrl+Alt+Shift+D` ใน Console แล้วเปิด *Show Debug Menu*)
- REST API: `GET https://<server>:52311/api/query?relevance=...&output=json`
- `bigfix/api/bigfix_api.py query "..."` (ใช้กับ mock ใน `ansible/lab-env` ได้)

## Query ที่ใช้บ่อยในงานจริง
```
// จำนวนเครื่องทั้งหมด
number of bes computers

// inventory: id, ชื่อ, OS, เวลารายงานล่าสุด
(id of it, name of it, operating system of it, last report time of it as string) of bes computers

// agent ที่เงียบเกิน 7 วัน (เครื่องปิดนาน, agent พัง หรือเครื่องถูกทิ้ง)
(name of it, last report time of it as string) of bes computers whose (last report time of it < now - 7 * day)

// patch ที่ยังค้างอยู่ (Fixlet ที่ relevant อยู่อย่างน้อย 1 เครื่อง)
(id of it, name of site of it, name of it, applicable computer count of it) of bes fixlets whose (applicable computer count of it > 0 and fixlet flag of it)

// เครื่องที่ยังต้องลง fixlet ID 501
names of applicable computers of bes fixlets whose (id of it = 501)

// ค่าของ property จาก Analysis
(name of computer of it, values of it) of results of bes property "Serial Number"

// action ที่ยังเปิดอยู่ และใครสร้าง
(id of it, name of it, name of issuer of it, time issued of it as string) of bes actions whose (state of it = "Open")

// ผล action ทีละเครื่อง
(name of computer of it, status of it as string) of results of bes action 9001

// จำนวนเครื่องแยกตาม OS
(it, number of bes computers whose (operating system of it = it)) of unique values of operating systems of bes computers
```
> ชื่อ property/site ใน query ต้องตรงกับใน Console ทุกตัวอักษร

## แบบฝึกหัด
1. ยิง query ข้างบนด้วย `bigfix_api.py` กับ mock (mock รองรับ query ชุดแรกๆ ส่วนที่เหลือใช้กับ server จริง)
   ```bash
   cd bigfix/api
   BIGFIX_URL=http://localhost:52311 python3 bigfix_api.py query "number of bes computers"
   ```
2. เขียน query หา **compliance %** ของ fixlet หนึ่งตัว: `applicable computer count` เทียบกับ `number of bes computers`
3. ทำ CSV รายงานเครื่องที่ BitLocker ยังไม่เปิด จาก property ของ `lab03-inventory-analysis`
4. เทียบกับ Ansible: `ansible/labs/lab16-bigfix-integration/query.yml` ทำงานแบบเดียวกันผ่าน module `uri`
