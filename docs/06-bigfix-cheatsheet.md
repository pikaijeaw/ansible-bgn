# BigFix สรุปที่ต้องรู้และใช้งานจริง (Cheat Sheet ภาษาไทย)

เอกสารนี้เก็บเฉพาะเรื่องสำคัญที่ใช้บ่อยในงานจริง อ่านจบใน 15–20 นาที
รายละเอียดเชิงลึกดู [02-bigfix-principles.md](02-bigfix-principles.md) และลองทำจริงที่ [../bigfix/labs](../bigfix/labs)

## 1. BigFix คืออะไร (สั้นๆ)
| คำ | ความหมาย |
|---|---|
| Agent-based | ลง agent (BES Client) บนทุกเครื่อง agent ทำงานตลอดเวลา |
| Pull | agent ดึง "สิ่งที่ต้องทำ" จาก server/relay มาเช็กเอง ไม่ใช่ server ผลักไปหา |
| Relevance | ภาษาที่ agent ใช้ถามตัวเองว่า "เงื่อนไขนี้จริงกับเครื่องฉันไหม" |
| Continuous compliance | agent เช็กเงื่อนไขตลอด ถ้าเครื่องหลุดมาตรฐานก็แก้ได้เอง ไม่ต้องรอสั่ง |
| Scale | รองรับหลักแสนเครื่องต่อ root server เพราะ agent คำนวณเอง |

ลำดับการทำงาน: ผู้ดูแลสร้าง Fixlet/Task → ประกาศเข้า Site → agent ดึง Site ผ่าน Relay → agent ประเมิน Relevance → ถ้าจริง ก็แสดงว่า "relevant" และรายงานผลกลับ → ผู้ดูแลสั่ง Action → agent ลงมือทำ

## 2. สถาปัตยกรรม
| ส่วน | หน้าที่ |
|---|---|
| Root Server | ศูนย์กลาง เก็บฐานข้อมูล, จัดการ Site, รับรายงาน |
| Relay | ตัวกลางแจกจ่ายไฟล์และรวบรวมผล ลดภาระ root server และ WAN |
| Agent (BES Client) | ติดตั้งบนเครื่อง ประเมิน relevance และรัน action |
| Console | โปรแกรมสำหรับผู้ดูแล (Windows) |
| WebUI | หน้าเว็บสำหรับงานประจำวัน (patch, query, ค้นหาเครื่อง) |
| Web Reports | รายงานผ่านเว็บ |
| REST API | พอร์ต 52311 สำหรับเขียน script/automation |

พอร์ตหลัก: **52311** (TCP สำหรับ API/ดาวน์โหลด และ UDP สำหรับ "ปลุก" agent)

## 3. ศัพท์พื้นฐาน
| คำ | ความหมายภาษาไทย | ตัวอย่าง |
|---|---|---|
| Fixlet | ข้อความแจ้งปัญหา + วิธีแก้ ทำงานเมื่อ relevance เป็นจริง | "ต้องอัปเดต Chrome" |
| Task | งานที่สั่งรันเมื่อไรก็ได้ ไม่ผูกกับเงื่อนไข | "ล้างไฟล์ temp" |
| Baseline | ชุดของ Fixlet/Task หลายตัวรวมกัน ใช้ทำ patch รอบเดือนหรือ build เครื่องใหม่ | "Patch Tuesday พ.ย." |
| Analysis | ชุดคำถามให้ agent ตอบเป็นข้อมูล (property) ใช้ทำ inventory | "ขนาดดิสก์, ซอฟต์แวร์ที่ลง" |
| Action | การสั่งให้ Fixlet/Task/Baseline ทำงานจริงกับเครื่องเป้าหมาย | "รันคืนนี้ 22:00" |
| Computer Group | กลุ่มเครื่องที่กำหนดด้วยเงื่อนไข (relevance) หรือรายชื่อ | "Windows Server ที่ HQ" |
| Site | แหล่งเก็บเนื้อหา แบ่งเป็น External (ของผู้ผลิต), Custom (ของเราเอง), Operator, Master Action Site | "Patches for Windows" |
| Property | ค่าที่ agent รายงาน (ชื่อ, OS, IP, ...) | `computer name` |
| Relevance | เงื่อนไขที่ใช้ตัดสินว่า item นี้เกี่ยวกับเครื่องไหม | `windows of operating system` |
| ActionScript | สคริปต์ที่ agent รัน ตอนมี Action | `waithidden cmd.exe /c ...` |
| Session Relevance | relevance ที่ถามจาก server (ใช้กับ API / Query) ต่างจากที่ agent ประเมินเอง | `number of bes computers` |

## 4. Relevance Language (ภาษาหลักของ BigFix)
อ่านจากขวาไปซ้ายเหมือนประโยคภาษาอังกฤษ: `<property> of <object>`

### 4.1 ตัวอย่างพื้นฐาน
```
windows of operating system                      -- เป็น Windows ไหม (true/false)
name of operating system                         -- ชื่อ OS
computer name                                    -- ชื่อเครื่อง
free space of drive "C:"                         -- พื้นที่ว่างของไดรฟ์ C
exists file "C:\Windows\notepad.exe"             -- มีไฟล์นี้ไหม
version of file "C:\Windows\notepad.exe"         -- เวอร์ชันของไฟล์
exists key "HKEY_LOCAL_MACHINE\SOFTWARE\Vendor" of registry
exists service "Spooler"                         -- มี service นี้ไหม
```

### 4.2 ตัวดำเนินการและการเปรียบเทียบ
| ต้องการ | เขียนอย่างไร |
|---|---|
| และ / หรือ / ไม่ | `and`, `or`, `not` |
| เท่ากัน / ไม่เท่า | `=`, `!=` |
| มากกว่า / น้อยกว่า | `>`, `<`, `>=`, `<=` |
| เปรียบเทียบเวอร์ชัน | `version of ... >= "10.0.1"` (ชนิด version เปรียบเทียบถูกต้อง) |
| ข้อความมีคำ | `it contains "abc"`, `it starts with "abc"` |
| ไม่สนตัวพิมพ์ | `as lowercase` |
| ถ้าไม่มีค่าให้ใช้ค่าอื่น | `(... | "none")` |
| แปลงชนิด | `as integer`, `as string`, `as version` |

### 4.3 รูปแบบที่ใช้บ่อยในงานจริง
```
-- Fixlet relevance: เครื่อง Windows ที่ Chrome เวอร์ชันต่ำกว่า 120
windows of operating system
and exists keys "HKLM\SOFTWARE\Google\Chrome" of native registry
and (version of file "C:\Program Files\Google\Chrome\Application\chrome.exe" < "120.0.0.0")

-- ซอฟต์แวร์ที่ติดตั้งบนเครื่อง (Windows)
names of registry keys whose (exists value "DisplayName" of it) of key "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall" of native registry

-- ไดรฟ์ที่พื้นที่ว่างน้อยกว่า 10 GB
exists drives whose (type of it = "DRIVE_FIXED" and free space of it < 10 * 1073741824)

-- เครื่อง Linux (Ubuntu)
exists lines whose (it starts with "Ubuntu") of files "/etc/issue"
```

### 4.4 เครื่องมือลองเขียน relevance
| เครื่องมือ | ใช้ทำอะไร |
|---|---|
| **QnA** | ตัวทดสอบ relevance บนเครื่องที่ลง agent (พิมพ์คำถาม ได้คำตอบทันที) |
| **BigFix Query** (Console/WebUI) | ถามหลายเครื่องพร้อมกันและเห็นผลทันที |
| **Presentation Debugger** | ใช้ใน Fix Editor ตรวจ relevance ของ Fixlet |

## 5. ActionScript (สิ่งที่ agent ทำเมื่อมี Action)
| คำสั่ง | ความหมาย |
|---|---|
| `// Download` | ประกาศไฟล์ที่ต้องดาวน์โหลด (ใส่ prefetch) |
| `prefetch name=a.exe sha1:<hash> size:<bytes> http://...` | ให้ relay เตรียมไฟล์ พร้อมตรวจ hash ก่อนใช้ |
| `waithidden "{pathname of file ""a.exe"" of folder ""__Download""}" /S` | รันโปรแกรมแบบซ่อน แล้วรอจบ |
| `wait cmd.exe /c ...` | รันแล้วรอจนจบ |
| `run` | รันแล้วไม่รอ |
| `delete "path"` | ลบไฟล์ |
| `move`, `copy` | ย้าย/คัดลอกไฟล์ |
| `regset "..." "name"="value"` | ตั้งค่า registry |
| `restart {number of seconds}` / `restart` | รีบูต |
| `action may require restart` | แจ้งว่าอาจต้อง restart |
| `if {condition}` ... `endif` | เงื่อนไข |
| `continue if {relevance}` | ถ้า relevance ไม่จริงให้หยุด action |
| `parameter "name"="value"` | กำหนดตัวแปร |
| `{...}` | แทรก relevance ไว้ในสคริปต์ |

ตัวอย่าง Task ติดตั้งซอฟต์แวร์ (Windows):
```
// ตรวจก่อนทำ
continue if {not exists file "C:\Program Files\App\app.exe"}

// ดาวน์โหลดผ่าน relay พร้อมตรวจความถูกต้อง
prefetch app.msi sha1:0123456789abcdef0123456789abcdef01234567 size:1048576 https://repo.example.com/app.msi

waithidden msiexec.exe /i "{pathname of file "app.msi" of folder "__Download"}" /qn /norestart
```
> ใช้ `sha1` และ `size` ใน `prefetch` ทุกครั้ง เพื่อให้ agent ตรวจว่าไฟล์ไม่ถูกแก้ไขระหว่างทาง

## 6. ขั้นตอนทำงานจริง (Workflow)
| ขั้น | ทำอะไร | หมายเหตุ |
|---|---|---|
| 1 | เขียน relevance ใน QnA/Query | ทดสอบกับเครื่องเดียวก่อน |
| 2 | สร้าง Fixlet/Task ใน **Custom Site** | อย่าแก้ External Site |
| 3 | ตั้ง Computer Group สำหรับ pilot | เช่น เครื่องทดสอบ 5–10 เครื่อง |
| 4 | สร้าง Action (ตั้งเวลา, retry, restart policy) | ดู Execution/Constraints |
| 5 | ติดตามผล (Action Status) | ดูจำนวน Evaluating / Executing / Completed / Failed |
| 6 | ขยายเป็นกลุ่มใหญ่เป็นระลอก (rollout) | ทีละ 10% → 50% → 100% |
| 7 | ตรวจซ้ำด้วย Analysis / Web Reports | ยืนยันว่า relevant เหลือ 0 |

### Action ตั้งค่าที่ควรรู้
| ตัวเลือก | ความหมาย |
|---|---|
| Target | เครื่องที่จะทำ (เลือกทีละเครื่อง / Computer Group / relevance) |
| Execution (Start/End) | ช่วงเวลาที่อนุญาตให้ทำ |
| Retry | ลองใหม่เมื่อล้มเหลวกี่ครั้ง/รอกี่นาที |
| Reapply | ให้ทำซ้ำเมื่อเครื่องกลับมา relevant อีก (self-healing) |
| Post-action (Restart/Shutdown) | หลังเสร็จให้รีบูตหรือไม่ พร้อมข้อความแจ้งผู้ใช้ |
| User interaction | แสดงข้อความ / ให้ผู้ใช้เลื่อน (defer) ได้ |
| Stop after N failures | หยุดอัตโนมัติถ้าล้มเหลวเกินกำหนด |

## 7. Patch Management (งานที่ใช้บ่อยที่สุด)
1. Subscribe External Site ที่ต้องการ เช่น *Patches for Windows*, *Patches for RHEL/Ubuntu*
2. สร้าง **Baseline** รวม Fixlet ของเดือนนั้นๆ (กรอง severity ได้)
3. ทดสอบกับกลุ่ม **Pilot** ก่อน แล้วค่อยขยาย
4. ตั้งช่วงเวลา (maintenance window) และนโยบาย restart
5. ติดตามผล และ rerun เฉพาะเครื่องที่ล้มเหลว
6. ปิดรอบด้วยรายงาน compliance (ก่อน CAB / audit)

| ปัญหา | วิธีเช็ก |
|---|---|
| Fixlet แสดง "Not Relevant" ทั้งที่ควรจะต้องแพตช์ | ไซต์ยังไม่ได้ gather ล่าสุด หรือเครื่องไม่ได้ subscribe site |
| Action ค้างที่ "Waiting" | เครื่องปิดอยู่ / อยู่นอกเวลา Execution / constraint ไม่ผ่าน |
| ดาวน์โหลดล้มเหลว | relay ต่อ internet ไม่ได้ หรือ firewall บล็อก 52311 |
| Evaluating นานผิดปกติ | relevance หนักเกินไป (ดู Client Settings: `_BESClient_Resource_WorkIdle`) |

## 8. REST API (พอร์ต 52311)
ใช้ HTTPS และ Basic Auth ด้วยบัญชี operator

| ต้องการ | คำสั่ง (curl) |
|---|---|
| ถาม Session Relevance | `curl -k -u user:pass --data-urlencode "relevance=number of bes computers" https://root:52311/api/query` |
| ดูรายชื่อเครื่อง | `GET /api/computers` |
| ดูรายละเอียดเครื่อง | `GET /api/computer/<id>` |
| ดู Fixlet ใน Site | `GET /api/fixlets/custom/<site>` |
| ดู Action | `GET /api/action/<id>` |
| สถานะ Action | `GET /api/action/<id>/status` |
| สร้าง Action | `POST /api/actions` (ส่ง XML) |
| ส่ง Fixlet/Task เข้า Site | `POST /api/import/custom/<site>` |

> `-k` ใช้ข้ามการตรวจ certificate เฉพาะ lab เท่านั้น ใน production ให้ติดตั้ง CA ของ root server แล้วใช้ `--cacert`

ตัวอย่างหาเครื่องที่ยังไม่ได้ติดต่อ root มากกว่า 7 วัน:
```
(name of it, last report time of it) of bes computers whose (now - last report time of it > 7 * day)
```
ตัวอย่างสคริปต์ Python อยู่ที่ [../bigfix/api/bigfix_api.py](../bigfix/api/bigfix_api.py)

## 9. Client Settings ที่ควรรู้
| Setting | ใช้ทำอะไร |
|---|---|
| `_BESClient_Resource_WorkIdle` / `_SleepIdle` | จำกัดการใช้ CPU ของ agent (ค่ามาก = ใช้เยอะ) |
| `_BESClient_Download_*` | ควบคุมความเร็ว/จำนวนไฟล์ที่ดาวน์โหลด |
| `_BESClient_Comm_CommandPollEnable` | ให้ agent ถาม relay เป็นระยะ (ใช้เมื่อ UDP ถูกบล็อก) |
| `_BESClient_Resource_PowerSaveEnable` | ลดการทำงานเมื่อเครื่องอยู่ในโหมดประหยัดพลังงาน |
| `_BESClient_ActionManager_*` | ปรับพฤติกรรมของ action |

ตั้งค่าได้ที่ Console: คลิกขวาเครื่อง/กลุ่ม → *Edit Computer Settings*
ดู lab: [lab14-client-settings](../bigfix/labs/lab14-client-settings)

## 10. Best practice ที่ใช้จริง
1. **ทดสอบกับ pilot เสมอ** ก่อนสั่งทั้งองค์กร
2. **ทดสอบ relevance ด้วย QnA/Query** ก่อนใส่ใน Fixlet
3. **เขียน relevance ให้เบา** หลีกเลี่ยงการสแกนไฟล์ทั้งดิสก์ หรือ registry ทั้งสาขา
4. **ใช้ prefetch พร้อม hash** ตรวจความถูกต้องของไฟล์
5. **เก็บเนื้อหาของเราใน Custom Site** ไม่แก้ External Site
6. **ตั้งช่วงเวลา (Execution window) และ retry** ให้เหมาะสม
7. **แยกสิทธิ์ operator** ตามบทบาท (least privilege)
8. **เขียน Fixlet ให้ idempotent** มี relevance ที่เป็นเท็จหลังแก้เสร็จ จะได้ไม่รันซ้ำ
9. **ใช้ Baseline** กับงานที่ต้องทำเป็นชุด และมี sync point เมื่อมีหลายขั้น
10. **เก็บ Fixlet เป็นไฟล์ `.bes` ใน Git** (ดู [../bigfix/labs](../bigfix/labs) และ `validate_bes.py`)
11. **ติดตามสุขภาพ agent**: เครื่องที่ไม่ report เกิน 7 วัน ต้องตามแก้

## 11. ปัญหาที่เจอบ่อยและวิธีแก้
| อาการ | สาเหตุที่พบบ่อย | วิธีแก้ |
|---|---|---|
| Fixlet ไม่ relevant ทั้งที่ควร relevant | relevance เขียนผิด, site ไม่ได้ subscribe | ทดสอบใน QnA บนเครื่องนั้น, ตรวจ Site subscription |
| Action ค้าง "Pending Restart" | เครื่องยังไม่ได้รีบูต | ให้ผู้ใช้รีบูต หรือส่ง action restart |
| Action "Failed" exit code != 0 | ติดตั้งผิดพารามิเตอร์ / ไฟล์เสีย | ดู Action Log บนเครื่อง (`__BESData\__Global\Logs`) |
| Download failed / hash mismatch | ไฟล์เปลี่ยน, hash/size ในสคริปต์ผิด | คำนวณ sha1/size ใหม่ ให้ตรงกับไฟล์จริง |
| เครื่องไม่รายงาน | agent หยุด, เครือข่าย/relay ไม่ถึง | ตรวจ service `BESClient`, พอร์ต 52311, ค่า relay selection |
| Console ช้า | มี Analysis/Property เยอะเกินไป | ปิด Analysis ที่ไม่ใช้, ลดความถี่การรายงาน |
| `.bes` import ไม่ผ่าน | XML ไม่ถูกลำดับ/ผิด schema | รัน `python bigfix/scripts/validate_bes.py` |

## 12. เปรียบเทียบสั้นๆ กับ Ansible
| หัวข้อ | BigFix | Ansible |
|---|---|---|
| โมเดล | Agent + Pull | Agentless + Push |
| ภาษา | Relevance + ActionScript | YAML + Jinja2 |
| จุดแข็ง | หลักแสนเครื่อง, patch, compliance ต่อเนื่อง | config management, orchestration, infra ใหม่ |
| ความเร็วตอบสนอง | agent เช็กเอง (ใกล้เคียง real-time) | ตอนที่เรารันเท่านั้น |
| ใช้คู่กัน | BigFix patch/inventory/compliance ทั่วองค์กร | Ansible ทำ provisioning และ deploy ซับซ้อน |

## 13. Roadmap เรียนต่อ
1. ลองทำ lab 01–04 (relevance, session relevance, inventory, computer group)
2. lab 05–08: deploy/uninstall ซอฟต์แวร์, service self-healing
3. lab 09–12: hardening, patch, disk cleanup, local admin audit
4. lab 13–15: จับผล script, client settings, REST API
5. ขั้นสูง: Compliance (SCA), Inventory, Remote Control, BigFix Query ใน WebUI, Software Distribution

## 14. แหล่งอ้างอิง
- เอกสารทางการ: https://help.hcltechsw.com/bigfix/
- Relevance Language: https://developer.bigfix.com/relevance/
- REST API: https://developer.bigfix.com/rest-api/
- ActionScript: https://developer.bigfix.com/action-script/
