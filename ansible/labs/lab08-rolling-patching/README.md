# Lab 08: Rolling OS Patching แบบ Zero Downtime

**สถานการณ์จริง:** ทุกเดือนต้อง patch Linux ทุกเครื่อง (มักทำใน maintenance window) โดยมีข้อกำหนดว่า
- เว็บห้ามล่ม ต้อง patch ทีละเครื่อง และถอดเครื่องออกจาก load balancer ก่อนทุกครั้ง
- ถ้าเครื่องไหน patch ไม่ผ่าน ต้องหยุดทันที ห้ามลามไปเครื่องอื่น
- reboot เฉพาะเครื่องที่จำเป็นจริง
- ต้องมีรายงานก่อนและหลัง patch ให้ CAB (Change Advisory Board)

> ต้องรัน [Lab 05](../lab05-roles/) ก่อน เพื่อให้มี haproxy และเว็บ

## Flow ของ `patch.yml`
```
for each host (serial: 1, max_fail_percentage: 0):
  pre_tasks : เช็ค disk → snapshot hook → drain ออกจาก haproxy (delegate_to lb01)
  tasks     : apt dist-upgrade / dnf update → ตรวจว่าต้อง reboot ไหม → reboot → เขียน log
  post_tasks: health check /healthz → ใส่กลับเข้า haproxy
```

| เทคนิค | ใช้ทำอะไร |
|---|---|
| `serial: 1` / `serial: "30%"` | ทำทีละ batch |
| `max_fail_percentage: 0` | มีเครื่องพัง 1 เครื่องก็หยุดทั้ง play |
| `delegate_to` | สั่งงานบนเครื่องอื่น (lb01) ในนามของเครื่องที่กำลัง patch |
| `community.general.haproxy` | disable/drain/enable backend ผ่าน admin socket |
| `ansible.builtin.reboot` | reboot แล้วรอจนเครื่องกลับมา (ตรวจด้วย `boot_time_command`) |
| `/var/run/reboot-required` | Ubuntu บอกว่าต้อง reboot |
| `needs-restarting -r` | RHEL บอกว่าต้อง reboot (rc=1) |

## ขั้นตอน
```bash
cd /work/ansible

# 1) รายงาน package ที่รออัปเดต (ใช้ประกอบ change request)
ansible-playbook labs/lab08-rolling-patching/report.yml
cat labs/lab08-rolling-patching/pending-updates.txt

# 2) เปิดอีก terminal แล้วยิง request ใส่ LB ตลอดเวลา เพื่อพิสูจน์ว่าไม่มี downtime
while true; do curl -s -o /dev/null -w "%{http_code} " http://lb01/; sleep 0.5; done

# 3) Patch กลุ่ม web แบบบังคับ reboot (ในแล็บ package มักใหม่อยู่แล้ว จึงต้องบังคับ reboot เพื่อให้เห็นภาพ)
ansible-playbook labs/lab08-rolling-patching/patch.yml -e target=web -e patch_force_reboot=true

# 4) ดู stats ของ HAProxy ระหว่าง patch: http://localhost:8404  (เครื่องจะขึ้นเป็น MAINT/DRAIN)

# 5) Patch ที่เหลือ
ansible-playbook labs/lab08-rolling-patching/patch.yml -e target='db:lb'
```
ผลที่ได้จากการทดสอบจริง: ระหว่างที่ web01 และ web02 reboot ทีละเครื่อง request ผ่าน LB ได้ HTTP 200 ทุกครั้ง

## ตัวเลือกที่ใช้บ่อย
```bash
-e patch_batch='50%'                 # ทำทีละครึ่ง
-e patch_allow_reboot=false          # ลง patch แต่ยังไม่ reboot (reboot เองในรอบถัดไป)
-e '{"patch_exclude": ["nginx*"]}'   # ยกเว้นบาง package
-e patch_security_only=true          # RHEL: เฉพาะ security errata
```

## หมายเหตุสำหรับ lab
container ใช้ kernel ร่วมกับ host ค่า `boot_id` จึงไม่เปลี่ยนตอน reboot
lab จึง override `lab_boot_time_command` ใน `inventory/group_vars/all.yml` ไว้ เมื่อใช้กับ VM จริงให้ลบออก

## แบบฝึกหัด
1. เพิ่มการแจ้งเตือนเข้า Slack/Teams ตอนเริ่มและจบ patch (`community.general.slack` หรือ `uri` ไปที่ webhook)
2. เพิ่มการบันทึกรายชื่อ package ที่อัปเกรดลงไฟล์ (Debian: ดู `/var/log/apt/history.log`)
3. ทำให้ db01 patch ได้เฉพาะเสาร์-อาทิตย์ ด้วย `assert` + `now().weekday()`
4. เปรียบเทียบกับ BigFix: BigFix ใช้ Baseline + Maintenance Window ทำงานแบบเดียวกันกับ endpoint หลายพันเครื่อง (ดู `bigfix/labs/lab10-patch-management`)
