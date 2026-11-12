# ตารางการเรียนรู้ Ansible (6 สัปดาห์ วันละประมาณ 1–2 ชั่วโมง)

แต่ละสัปดาห์ผูกกับ lab ใน repo นี้ ทำเสร็จแล้วติ๊ก ☐ → ☑ ได้เลย

## Ansible (สัปดาห์ 1–6)
| สัปดาห์ | หัวข้อ | Lab | เป้าหมาย / หลักฐานว่าผ่าน | ☐ |
|---|---|---|---|---|
| 1 | Linux, SSH key, YAML, ติดตั้ง lab | [lab-env](../ansible/lab-env/) | `./setup.sh` แล้ว `ansible all -m ping` ได้ pong ทุกเครื่อง | ☐ |
| 1 | Ad-hoc, inventory, pattern | [01](../ansible/labs/lab01-adhoc/) | ทำแบบฝึกหัดได้ครบ 4 ข้อ | ☐ |
| 2 | Playbook แรก, idempotency, check mode | [02](../ansible/labs/lab02-first-playbook/) | รันรอบสองได้ `changed=0` | ☐ |
| 2 | Variables, facts, conditionals, loops | [03](../ansible/labs/lab03-variables-facts/) | สร้าง `host_vars/db01.yml` แล้วผลเปลี่ยนตาม | ☐ |
| 3 | Templates, handlers, block/rescue | [04](../ansible/labs/lab04-templates-handlers/) | ทดสอบ rollback ด้วย `-e nginx_client_max_body_size=abc` แล้วเว็บไม่ล่ม | ☐ |
| 3 | Roles | [05](../ansible/labs/lab05-roles/) | `curl lb01` สลับ web01/web02 | ☐ |
| 4 | Users + Vault | [06](../ansible/labs/lab06-users-vault/) | onboard `malee` ได้ และ audit จับ `olduser` ได้ | ☐ |
| 4 | Hardening (CIS) + audit drift | [07](../ansible/labs/lab07-linux-hardening/) | `verify.yml` ผ่านทุกเครื่อง | ☐ |
| 5 | Rolling patching | [08](../ansible/labs/lab08-rolling-patching/) | patch + reboot ระหว่าง curl loop ได้ 200 ตลอด | ☐ |
| 5 | Zero-downtime deploy + rollback | [09](../ansible/labs/lab09-rolling-deploy/) | deploy 2.0.0 แล้ว rollback ได้ | ☐ |
| 5 | DB backup + restore test | [10](../ansible/labs/lab10-database-backup/) | `RESTORE OK` | ☐ |
| 6 | Monitoring agent, inventory report | [11](../ansible/labs/lab11-monitoring-agent/), [12](../ansible/labs/lab12-inventory-report/) | ได้ไฟล์ HTML report | ☐ |
| 6 | Health check, incident runbooks | [13](../ansible/labs/lab13-health-check/), [14](../ansible/labs/lab14-incident-response/) | จับ nginx ล่มได้และ auto-recover | ☐ |
| 6 | Windows, CI/lint | [15](../ansible/labs/lab15-windows/), [17](../ansible/labs/lab17-ci-quality/) | `ansible-lint` ผ่าน, GitHub Actions เขียว | ☐ |
| 6 | **Integration project** (BigFix API จำลอง) | [Ansible lab16](../ansible/labs/lab16-bigfix-integration/) | Ansible ดึง patch ค้างจาก BigFix → สั่ง deploy → สร้าง inventory จาก BigFix | ☐ |

## ต่อด้วย BigFix (สัปดาห์ 7–12)
ตาราง BigFix ย้ายไปอยู่ที่ [bigfix-labs: docs/03-learning-plan.md](https://github.com/pikaijeaw/bigfix-labs/blob/main/docs/03-learning-plan.md)

## ตารางรายวัน (ใช้ซ้ำได้ทุกสัปดาห์)
| วัน | กิจกรรม |
|---|---|
| จันทร์–อังคาร | อ่าน README ของ lab และเอกสารทางการ (30 นาที) แล้วทำตามขั้นตอน (1 ชม.) |
| พุธ–พฤหัส | ทำ "แบบฝึกหัด" ท้าย lab เองโดยไม่ดูเฉลย |
| ศุกร์ | ทบทวน จดโน้ต และ commit งานของตัวเองเข้า Git |
| เสาร์ | Challenge: ทำ "ลองทำให้พัง" หรือทำ lab เดิมบน OS อื่น |
| อาทิตย์ | พัก |

## แหล่งเรียนรู้
- **Ansible:** docs.ansible.com (User Guide), หนังสือ *Ansible for DevOps* (Jeff Geerling), Red Hat interactive labs (ฟรี)
- **BigFix:** HCL BigFix documentation (help.hcltechsw.com), BigFix Forum (forum.bigfix.com) ซึ่งมีตัวอย่าง relevance เยอะมาก, Relevance / ActionScript reference guide
- **ใบรับรอง (ถ้าต้องการ):** Red Hat Certified Engineer (RHCE, EX294 = Ansible), HCL BigFix certification
