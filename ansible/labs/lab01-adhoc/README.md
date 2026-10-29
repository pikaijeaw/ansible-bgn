# Lab 01: Ad-hoc Commands สำหรับงานด่วนประจำวัน

**สถานการณ์จริง:** หัวหน้าถามว่า "เครื่องไหน disk ใกล้เต็ม" หรือ "ช่วย restart nginx ทุกเครื่องหน่อย"
งานแบบนี้ไม่ต้องเขียน playbook ใช้ ad-hoc command ยิงคำสั่งเดียวไปหลายเครื่องพร้อมกันได้เลย

รูปแบบคำสั่ง:
```
ansible <host-pattern> -m <module> -a "<arguments>" [-b]
```
`-b` (become) คือใช้ sudo

## ขั้นตอน (รันใน control node: `cd /work/ansible`)

### 1. เช็คว่าเชื่อมต่อทุกเครื่องได้
```bash
ansible all -m ping
ansible-inventory --graph          # ดูโครงสร้าง group
ansible web --list-hosts           # ดูว่า pattern "web" มีเครื่องอะไรบ้าง
```

### 2. เก็บข้อมูลเครื่อง (facts)
```bash
ansible all -m setup -a "filter=ansible_distribution*"
ansible all -m setup -a "filter=ansible_memtotal_mb"
ansible db01 -m setup | less       # ดู facts ทั้งหมดของเครื่องเดียว
```

### 3. งาน Ops ที่เจอบ่อย
```bash
# disk / memory / uptime ของทุกเครื่อง
ansible all -m shell -a "df -h / | tail -1"
ansible all -m shell -a "free -m | grep Mem"
ansible all -a "uptime"

# หาเครื่องที่มี process ชื่อ nginx
ansible all -m shell -a "pgrep -a nginx || echo 'not running'"

# copy ไฟล์ไปทุกเครื่อง
ansible all -b -m copy -a "content='Authorized access only\n' dest=/etc/issue.net mode=0644"

# ติดตั้ง package (เลือก module ตาม OS อัตโนมัติด้วย module 'package')
ansible all -b -m package -a "name=curl state=present"

# จัดการ service
ansible web -b -m service -a "name=cron state=started enabled=true"

# สร้าง user ชั่วคราว แล้วลบออก
ansible all -b -m user -a "name=tempuser state=present"
ansible all -b -m user -a "name=tempuser state=absent remove=true"

# ดึงไฟล์ log จากทุกเครื่องมาไว้ที่ control node (แยกโฟลเดอร์ตามชื่อเครื่อง)
ansible all -b -m fetch -a "src=/etc/os-release dest=/tmp/collected/"
ls -R /tmp/collected
```

### 4. ทดลอง Pattern
```bash
ansible 'web:db' -a hostname          # web หรือ db
ansible 'linux:!db' -a hostname       # linux ยกเว้น db
ansible 'web01,db01' -a hostname      # ระบุชื่อตรงๆ
ansible all --limit web02 -a hostname
```

### 5. สังเกต Idempotency
รันคำสั่ง copy ในข้อ 3 สองรอบ รอบแรกจะขึ้น `CHANGED` (สีเหลือง) รอบสองจะขึ้น `SUCCESS` (สีเขียว) และ `"changed": false`
แต่ถ้าใช้ `-m shell` จะขึ้น `CHANGED` ทุกครั้ง เพราะ Ansible ไม่รู้ว่าคำสั่งนั้นเปลี่ยนอะไรไปบ้าง
**บทเรียน:** ถ้ามี module เฉพาะงานนั้นอยู่แล้ว ให้ใช้ module ดีกว่า shell

## แบบฝึกหัด
1. หาว่าเครื่องไหนมี RAM น้อยที่สุด (ใช้ `setup` + `filter`)
2. สร้างไฟล์ `/opt/owner.txt` ที่มีข้อความ `owner=ops` บนเฉพาะเครื่องกลุ่ม web
3. ใช้ `-m stat` เช็คว่า `/etc/nginx` มีอยู่ในเครื่องไหนบ้าง
4. ลอง `--check` กับคำสั่ง copy ดูว่ามันบอกอะไร

> ใช้ ad-hoc กับงานครั้งเดียว ถ้าต้องทำซ้ำหรือต้องให้คนอื่นตรวจสอบได้ ให้เขียนเป็น playbook แล้วเก็บเข้า Git
