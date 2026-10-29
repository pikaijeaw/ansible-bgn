# BigFix Lab 14: Client Settings, Tagging และ Agent Health

**สถานการณ์จริง:**
- ต้องแบ่งเครื่องตาม environment/เจ้าของ/แอป ให้ targeting ง่าย → ติด tag ด้วย **client setting**
- database server บ่นว่า agent ใช้ CPU → จำกัด CPU ของ agent
- ต้องดูว่า agent ทุกตัวเวอร์ชันล่าสุดและตั้งค่าถูกต้อง

| ไฟล์ | หน้าที่ |
|---|---|
| `set-environment-setting.bes` | ตั้ง setting `Environment` (Production/UAT/Dev) จาก parameter |
| `set-cpu-throttle.bes` | ตั้ง `_BESClient_Resource_WorkIdle=10` และ `_BESClient_Resource_SleepIdle=480` |
| `agent-health.bes` | Analysis: agent version, Environment, WorkIdle/SleepIdle, uptime, พื้นที่ว่างของโฟลเดอร์ agent |

## ขั้นตอน
1. Import ทั้งหมด → Activate `agent-health`
2. Take Action `set-environment-setting` กับเครื่อง production → กรอก `Production`
3. ดู group `Lab - Env - Production (client setting)` จาก lab04 ว่ามีสมาชิกเพิ่มขึ้น
4. อีกทางหนึ่ง: Console → เลือกเครื่อง → คลิกขวา **Edit Computer Settings** (สร้าง action แบบเดียวกันให้)

## Setting ที่ใช้บ่อย
| Setting | ความหมาย |
|---|---|
| `_BESClient_Resource_WorkIdle` / `_SleepIdle` | สัดส่วนเวลาทำงานกับพักของ agent (คุม CPU) |
| `_BESClient_Download_LimitBytesPerSecond` | จำกัด bandwidth ตอนดาวน์โหลด |
| `_BESClient_RelaySelect_FailoverRelay` | relay สำรอง |
| `_BESClient_Comm_CommandPollEnable` / `...PollIntervalSeconds` | ให้ agent poll เองเมื่อ UDP 52311 ถูก firewall บล็อก |
| custom เช่น `Environment`, `Owner`, `App` | tag สำหรับ targeting และรายงาน |

## แบบฝึกหัด
1. ตั้ง `_BESClient_Comm_CommandPollEnable=1` และ `...PollIntervalSeconds=900` ให้เครื่องที่อยู่หลัง NAT
2. ใช้ setting `Environment` จาก BigFix เป็นตัวแบ่ง group ใน Ansible inventory (ต่อยอด Ansible lab16 `bigfix-to-inventory.yml`)
