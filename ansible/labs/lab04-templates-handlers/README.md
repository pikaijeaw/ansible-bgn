# Lab 04: Templates (Jinja2) + Handlers + Validate & Rollback

**สถานการณ์จริง:**
1. `/etc/hosts` ของทุกเครื่องต้องมีรายชื่อเครื่องในระบบ และต้องอัปเดตอัตโนมัติเมื่อมีเครื่องเพิ่ม
2. ทุกเครื่องต้องมี logrotate policy เดียวกัน
3. Deploy config nginx แล้ว **ห้ามทำเว็บล่ม** ถ้า config ผิดต้อง rollback กลับไฟล์เดิม และห้าม reload

## สิ่งที่จะได้เรียน
- `template` + Jinja2: `for`, `if`, filter, `hostvars`, `groups`, `ansible_managed`
- `handlers` + `notify` + `meta: flush_handlers`: reload เฉพาะเมื่อ config เปลี่ยนจริง
- `block / rescue`: rollback เมื่อ config ใช้ไม่ได้
- `uri`: health check หลัง deploy

## ขั้นตอน
```bash
cd /work/ansible
ansible-playbook labs/lab04-templates-handlers/site.yml
ansible all -a "cat /etc/hosts"
curl -s http://web01/            # จาก control node
curl -s http://web02/healthz
```
รันรอบสอง handler `Reload nginx` จะไม่ทำงาน เพราะไม่มีไฟล์ไหนเปลี่ยน

## ทดลอง rollback (ส่วนสำคัญ)
ใส่ค่าที่ผิดเข้าไปให้ nginx ปฏิเสธ config:
```bash
ansible-playbook labs/lab04-templates-handlers/site.yml -e nginx_client_max_body_size=abc
```
ผลที่ควรได้:
- task `Validate nginx configuration` จะ fail
- `rescue` จะ restore ไฟล์ backup กลับมา
- handler ไม่ทำงาน nginx จึงยังรัน config เดิมอยู่ และเว็บไม่ล่ม
```bash
curl -s http://web01/healthz     # ยังตอบ ok
```

## ทดลอง handler
```bash
ansible-playbook labs/lab04-templates-handlers/site.yml -e nginx_client_max_body_size=20m
# จะเห็น RUNNING HANDLER [Reload nginx]
```

## แบบฝึกหัด
1. เพิ่ม `app_backend_ports: [8081, 8082]` แล้วดูว่า template สร้าง block `upstream` กับ `location /api/` ให้
2. เพิ่ม header `X-Served-By {{ inventory_hostname }}` ใน vhost
3. เขียน template `/etc/ssh/sshd_config.d/99-banner.conf` แล้วใช้ `validate: /usr/sbin/sshd -t -f %s` (ดู lab07)
4. เปลี่ยน logrotate ให้ db01 เก็บ log 30 วัน (ใช้ `host_vars`)
