# BigFix Lab 08: Self-Healing Services (Policy Action)

**สถานการณ์จริง:** service สำคัญอย่าง Windows Time (เวลาเพี้ยนทำให้ Kerberos login ไม่ได้), WinRM และ RDP มักหยุดเอง
แทนที่จะรอ helpdesk ให้ BigFix ตรวจตลอดเวลาและ start ให้อัตโนมัติ

| ไฟล์ | Platform | Relevant เมื่อ |
|---|---|---|
| `restart-stopped-critical-services.bes` | Windows | W32Time / WinRM / TermService ตั้งเป็น Automatic แต่ไม่ได้ Running |
| `restart-stopped-service-linux.bes` | Linux | มี nginx ติดตั้งแต่ไม่มี `/run/nginx.pid` |

## ขั้นตอน
1. Import แล้ว Take Action แบบ **Policy**:
   - Execution → ✔ *Reapply this action whenever it becomes relevant again* (ตั้งจำนวนครั้งสูงสุด เช่น 3 ครั้งต่อวัน เพื่อกันวนไม่จบ)
   - ✔ *Retry up to 3 times, wait 15 minutes between attempts*
2. ทดสอบบนเครื่อง: `Stop-Service W32Time` แล้วรอไม่กี่นาที service จะกลับมาเอง
3. ดูประวัติใน `C:\Windows\Temp\bigfix-service-heal.log`

## เปรียบเทียบกับ Ansible lab14
| | BigFix | Ansible |
|---|---|---|
| ตรวจจับ | agent ประเมินเองตลอดเวลา | ต้องมี monitoring ยิงมา หรือรัน playbook ตามรอบ |
| ทำงานตอนเครื่องหลุด network | ได้ (agent ทำงานในเครื่อง) | ไม่ได้ |
| เก็บหลักฐานก่อน restart | ต้องเขียนเพิ่มใน action | ทำใน playbook ได้ง่าย (`journalctl` แล้ว `fetch`) |

## แบบฝึกหัด
1. เปลี่ยน relevance ของ Linux ไปใช้ `systemctl is-active` ผ่าน property จาก script (ดูแนวคิดใน lab13)
2. เพิ่ม service ของแอปองค์กร (เช่น agent antivirus) ใน relevance และ action
