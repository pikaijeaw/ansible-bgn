# Lab 02: Playbook แรก — Server Baseline

**สถานการณ์จริง:** ทุกครั้งที่ได้ VM ใหม่ ทีม Ops ต้องลง package พื้นฐาน ตั้ง timezone สร้างโฟลเดอร์มาตรฐาน และใส่ banner
ถ้าทำมือ แต่ละเครื่องจะออกมาไม่เหมือนกัน (configuration drift) เลยเขียนเป็น playbook ให้ทุกเครื่องได้ผลเหมือนกัน

## สิ่งที่จะได้เรียน
- โครงสร้าง playbook: `hosts`, `become`, `vars`, `tasks`
- module พื้นฐาน: `apt`, `package`, `file`, `copy`, `debug`
- `loop` และ `when` เบื้องต้น
- ตัวแปรจาก `inventory/group_vars/all.yml` (`timezone`, `company`, ...)

## ขั้นตอน
```bash
cd /work/ansible

# 1) ตรวจ syntax
ansible-playbook labs/lab02-first-playbook/baseline.yml --syntax-check

# 2) Dry run: ดูว่าจะเปลี่ยนอะไรบ้าง โดยยังไม่แก้จริง
ansible-playbook labs/lab02-first-playbook/baseline.yml --check --diff

# 3) รันจริง
ansible-playbook labs/lab02-first-playbook/baseline.yml

# 4) รันซ้ำ ต้องได้ changed=0 (idempotent)
ansible-playbook labs/lab02-first-playbook/baseline.yml

# 5) ตรวจผล
ansible all -a "cat /etc/motd"
ansible all -a "timedatectl show -p Timezone"
```

## ผลที่ควรได้
```
PLAY RECAP
db01   : ok=8  changed=0  unreachable=0  failed=0  skipped=0
lb01   : ok=8  changed=0  ...
```
ถ้ารันรอบสองแล้วยังมี task ที่ `changed` แสดงว่า task นั้นไม่ idempotent ต้องแก้

## ลองทำให้พัง แล้วแก้
1. ssh เข้าเครื่อง `docker exec -it web01 bash` แล้วแก้ `/etc/motd` เอง จากนั้นรัน playbook ใหม่ จะเห็นว่า Ansible เขียนทับกลับเป็นค่าเดิม (นี่คือการแก้ drift)
2. ลบ package `rsync` ออกจากเครื่องหนึ่ง (`apt remove -y rsync`) แล้วรัน playbook ใหม่

## แบบฝึกหัด
1. เพิ่ม package `htop` แต่ให้ลงเฉพาะเครื่องกลุ่ม `web`
2. ใช้ `--limit db01` เพื่อรันกับเครื่องเดียว
3. ใช้ `--start-at-task "Deploy message of the day"` แล้วลองดูผล
4. ใช้ `--list-tasks` และ `--list-hosts`
