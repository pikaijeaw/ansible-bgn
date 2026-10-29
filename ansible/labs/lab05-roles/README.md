# Lab 05: Roles — สร้างระบบ Web 3-tier จาก Role ที่ใช้ซ้ำได้

**สถานการณ์จริง:** พอ playbook ยาวขึ้น จะเริ่มมีโค้ดที่ copy ไปมาหลายไฟล์ จนดูแลยาก
วิธีแก้คือแยกเป็น **role** แต่ละ role ทำหน้าที่เดียว แล้วเอามาประกอบกันเป็นระบบ

```
          ┌──────────── lb01 (role: haproxy) ────────────┐
 client → │ :80  roundrobin + health check /healthz       │ → web01 / web02 (role: webapp → nginx)
          │ :8404 stats page                              │
          └───────────────────────────────────────────────┘
 ทุกเครื่อง: role common (packages, timezone, /etc/hosts, motd)
```

## โครงสร้าง Role
```
roles/<name>/
├── defaults/main.yml   # ค่า default (precedence ต่ำสุด override ได้ง่าย)
├── vars/main.yml       # ค่าคงที่ของ role (precedence สูง)
├── tasks/main.yml      # งานหลัก
├── handlers/main.yml   # handler
├── templates/          # ไฟล์ .j2
├── files/              # ไฟล์ static
└── meta/main.yml       # ข้อมูล role + dependencies
```
สร้างโครง role ใหม่ด้วย `ansible-galaxy role init roles/myrole`

| Role | หน้าที่ | จุดที่ควรสังเกต |
|---|---|---|
| `common` | baseline ของทุกเครื่อง | template `/etc/hosts` จาก `groups['all']` |
| `nginx` | ติดตั้ง nginx และ vhost | handler 2 ตัวที่ `listen` topic เดียวกัน (validate แล้วค่อย reload) |
| `webapp` | deploy เว็บเป็นเวอร์ชัน | release folder + symlink `current`, smoke test, เก็บไว้แค่ N release |
| `haproxy` | load balancer | `validate: haproxy -c -f %s` ตรวจ config ก่อนเขียนทับไฟล์จริง |

## ขั้นตอน
```bash
cd /work/ansible
ansible-playbook labs/lab05-roles/site.yml
curl -s http://lb01/ | grep "served by"     # รันหลายรอบ จะสลับ web01/web02
```
เปิด browser ไปที่ `http://localhost:8080` (port 80 ของ lb01) และ `http://localhost:8404` ถ้า map port ไว้ (ดู stats ของ HAProxy)

Override ค่า default ของ role:
```bash
ansible-playbook labs/lab05-roles/site.yml -e webapp_version=1.1.0 -e webapp_color='#1565c0'
```

## บทเรียนจากของจริง (เจอระหว่างเขียน lab นี้)
1. **handler ที่ notify ต่อกันเป็นทอด:** ถ้า handler A เป็น `command` ที่ `changed_when: false` แล้ว notify handler B, B จะไม่ทำงานเลย เพราะ notify ทำงานเฉพาะตอนที่ task ขึ้น `changed` จึงต้องใช้ `listen` แทน
2. **handler หาย:** ถ้า task ไหน fail หลังจาก notify ไปแล้ว handler จะไม่ทำงาน และรอบหน้าไฟล์ก็ไม่เปลี่ยนแล้ว จึงไม่มีใคร reload ให้ วิธีกันคือใส่ `force_handlers: true` ใน play (หรือรันด้วย `--force-handlers`)
3. **ลำดับ handler:** ถ้า task ต้องพึ่ง config ใหม่ (เช่น smoke test) ให้ `meta: flush_handlers` ก่อน

## แบบฝึกหัด
1. สร้าง role `motd_banner` ด้วย `ansible-galaxy role init` แล้วย้าย motd ออกจาก `common`
2. เพิ่ม `haproxy_backend_group` ใน `group_vars/lb.yml` แล้วชี้ไปที่กลุ่มอื่น
3. เขียน `requirements.yml` ดึง role จาก Galaxy เช่น `geerlingguy.ntp` แล้วติดตั้งด้วย `ansible-galaxy install -r`
4. ต่อด้วย [Lab 09](../lab09-rolling-deploy/) ที่ใช้ role เหล่านี้ทำ zero-downtime deployment
