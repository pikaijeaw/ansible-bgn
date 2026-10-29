# Lab 06: User Management + Ansible Vault (Onboarding / Offboarding)

**สถานการณ์จริง:**
- พนักงานใหม่เข้ามา ต้องมี account บน server ทุกเครื่องในกลุ่มที่เกี่ยวข้อง พร้อม SSH key และสิทธิ์ sudo ตามตำแหน่ง
- พนักงานลาออก ต้องลบ account ออกจากทุกเครื่องภายในวันนั้น (เป็นข้อกำหนดของ audit/ISO 27001)
- รหัสผ่านต้องไม่อยู่ใน Git แบบ plain text

## ไฟล์ใน lab
| ไฟล์ | หน้าที่ |
|---|---|
| `group_vars/linux/users.yml` | รายชื่อ user/group (แก้ไฟล์นี้แล้วรัน playbook) |
| `group_vars/linux/vault.yml` | รหัสผ่านเริ่มต้น **เข้ารหัสด้วย Vault** |
| `files/keys/<user>.pub` | SSH public key ของแต่ละคน |
| `users.yml` | playbook |

> Ansible โหลด `group_vars/` ที่อยู่ข้าง playbook ให้อัตโนมัติ

## ขั้นตอน
รหัสผ่าน vault ของ lab คือ `lab-vault-pass`
```bash
cd /work/ansible

# ดูว่าไฟล์ vault ถูกเข้ารหัสแล้วจริง
cat labs/lab06-users-vault/group_vars/linux/vault.yml

# ดูเนื้อหาจริง (ต้องใส่รหัส)
ansible-vault view labs/lab06-users-vault/group_vars/linux/vault.yml

# สร้าง user ที่ "ลาออกแล้ว" ไว้ก่อน เพื่อดูว่า playbook ลบให้
ansible all -b -m user -a "name=niran"
# สร้าง account แปลกปลอมไว้ 1 ตัว เพื่อดูว่า audit จับได้
ansible web01 -b -m user -a "name=olduser"

# รัน
ansible-playbook labs/lab06-users-vault/users.yml --ask-vault-pass
```

ผลที่ควรได้:
- `somchai` อยู่กลุ่ม `ops-admins` และ sudo ได้ทุกคำสั่ง
- `suda` อยู่กลุ่ม `developers` และ sudo ได้เฉพาะ restart nginx กับ journalctl
- `niran` ถูกลบพร้อม home directory
- user ใหม่ถูกบังคับให้เปลี่ยนรหัสผ่านตอน login ครั้งแรก (`chage -l suda`)
- มี audit finding ว่า `UNMANAGED ACCOUNTS on web01: ['olduser']`

## คำสั่ง Vault ที่ใช้บ่อย
```bash
ansible-vault create  secrets.yml                 # สร้างไฟล์ใหม่ที่เข้ารหัส
ansible-vault edit    group_vars/linux/vault.yml  # แก้ไฟล์
ansible-vault rekey   group_vars/linux/vault.yml  # เปลี่ยนรหัส vault
ansible-vault encrypt_string 'S3cret!' --name 'db_password'   # เข้ารหัสแค่ค่าเดียว
ansible-playbook site.yml --vault-password-file ~/.vault_pass   # สำหรับ CI (ไฟล์นี้ห้าม commit)
```

## Best practices
- ตั้งชื่อตัวแปรลับขึ้นต้นด้วย `vault_` แล้วอ้างถึงจากไฟล์ vars ปกติ จะ grep หาได้ง่าย
- ใส่ `no_log: true` ใน task ที่มีข้อมูลลับ
- ใช้ `update_password: on_create` ไม่อย่างนั้น hash จะเปลี่ยนทุกครั้งที่รัน (เพราะ salt สุ่มใหม่) และ playbook จะไม่ idempotent
- ใน production ให้เก็บ vault password ไว้ใน AWX/AAP Credentials หรือ HashiCorp Vault ไม่ใช่ในไฟล์บนเครื่อง

## แบบฝึกหัด
1. Onboard user ใหม่ชื่อ `malee` (สร้าง key ด้วย `ssh-keygen -t ed25519 -f /tmp/malee`) ให้อยู่กลุ่ม developers
2. ย้าย `suda` ไปกลุ่ม `ops-admins` แล้วรันใหม่
3. ทำให้ user บางคนมีได้เฉพาะบางกลุ่มเครื่อง (เช่น developer มีแค่บน `web`) ด้วย field `hosts_groups` และ `when`
4. ใช้ `ansible-vault encrypt_string` เข้ารหัสรหัสผ่านของ malee แล้วเพิ่มเข้าไปใน `vault.yml`
