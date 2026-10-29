# Lab 09: Zero-downtime Rolling Deployment + Rollback

**สถานการณ์จริง:** ทีม Dev ปล่อยเวอร์ชันใหม่ทุกสัปดาห์ ทีม Ops ต้อง deploy ในเวลาทำงานโดยลูกค้าไม่รู้ตัว
และถ้าเวอร์ชันใหม่มีปัญหา ต้องย้อนกลับได้ภายในไม่กี่วินาที

> ต้องรัน [Lab 05](../lab05-roles/) ก่อน (ใช้ role `webapp`, `nginx`, `haproxy`)

## แนวคิด
```
/var/www/app/
├── releases/
│   ├── 1.0.0/
│   └── 2.0.0/
├── current -> releases/2.0.0     ← nginx ชี้ root ที่นี่ การ deploy คือการสลับ symlink
└── PREVIOUS                      ← เก็บชื่อ release เดิมไว้ใช้ rollback
```

Flow ต่อเครื่อง (`serial: 1`):
1. drain ออกจาก HAProxy (`tasks/lb_member.yml` ซึ่งใช้ซ้ำทั้ง deploy และ rollback)
2. role `webapp`: วางไฟล์ release ใหม่ → บันทึก PREVIOUS → สลับ symlink → smoke test → ลบ release เก่า
3. ตรวจว่าเครื่องนั้นเสิร์ฟเวอร์ชันใหม่จริง
4. ใส่กลับเข้า HAProxy

ตอนท้ายตรวจผ่าน LB อีก 6 request ว่าทุก request ได้เวอร์ชันใหม่

## ขั้นตอน
```bash
cd /work/ansible

# terminal 1: ดูเวอร์ชันที่ลูกค้าเห็น
while true; do curl -s http://lb01/version.txt; sleep 0.5; done

# terminal 2: deploy
ansible-playbook labs/lab09-rolling-deploy/deploy.yml -e webapp_version=2.0.0 -e webapp_color='#1565c0'

# rollback
ansible-playbook labs/lab09-rolling-deploy/rollback.yml

# input validation: ใส่เวอร์ชันผิดรูปแบบจะถูกปฏิเสธตั้งแต่ต้น
ansible-playbook labs/lab09-rolling-deploy/deploy.yml -e webapp_version=latest
```
ผลจากการทดสอบจริง: terminal 1 เห็น `1.0.0` ค่อยๆ เปลี่ยนเป็น `2.0.0` และไม่มี error เลยตลอดการ deploy

เปิด browser ที่ `http://localhost:8080` จะเห็นสีพื้นหลังเปลี่ยนตามเวอร์ชัน

## แบบฝึกหัด
1. Deploy `3.0.0` แล้ว `4.0.0` ดูว่า release เก่ากว่า 3 ตัวถูกลบ (`webapp_keep_releases`)
2. ทำ **canary**: deploy ไปเครื่องแรกก่อน (`--limit web01`) แล้วรอให้คนกด confirm ด้วย `ansible.builtin.pause` ก่อนทำเครื่องที่เหลือ
3. ทำให้ smoke test fail (เช่นแก้ template ให้ `version.txt` ผิด) แล้วดูว่า `max_fail_percentage: 0` หยุดไม่ให้ไปถึง web02 และ web01 ยังถูกถอดออกจาก LB อยู่ จากนั้นเขียน `rescue` ให้ rollback อัตโนมัติ
4. ใน AWX/AAP ทำ Job Template ที่มี Survey ให้กรอก `webapp_version` เพื่อให้ Dev deploy เองได้ (self-service)
