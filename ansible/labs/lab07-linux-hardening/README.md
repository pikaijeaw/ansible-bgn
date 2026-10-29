# Lab 07: Linux Hardening แนว CIS Benchmark + Compliance Audit

**สถานการณ์จริง:** ทีม Security/Audit ให้ทุก server ผ่าน CIS Benchmark Level 1 และต้องส่งหลักฐานทุกไตรมาส
ถ้าไล่แก้มือทีละเครื่อง ไม่นานก็มีคนไปแก้กลับ (drift) จึงต้องเขียนเป็นโค้ด แล้วรันตรวจเป็นระยะ

## Control ที่ทำในแล็บนี้
| หมวด | Control | Tag |
|---|---|---|
| Software | ลบ telnet/rsh/talk/nis | `packages` |
| Kernel | ปิด filesystem ที่ไม่ใช้ (cramfs, udf, ...) | `kernel` |
| Network | sysctl: ปิด redirect/source route, เปิด syncookies | `sysctl` |
| SSH | ห้าม root login, ห้าม password, MaxAuthTries 4, timeout | `ssh` |
| Banner | `/etc/issue`, `/etc/issue.net` | `banner` |
| Accounts | password aging 90 วัน, UMASK 027 | `accounts` |
| Files | สิทธิ์ cron, หาไฟล์ world-writable | `cron`, `audit` |
| Firewall | UFW default deny (**opt-in**) | `firewall` |

## ขั้นตอน
```bash
cd /work/ansible

# 1) Audit mode: ดูว่าเครื่องต่างจาก baseline ตรงไหนบ้าง โดยยังไม่แก้อะไร
ansible-playbook labs/lab07-linux-hardening/hardening.yml --check --diff

# 2) Enforce
ansible-playbook labs/lab07-linux-hardening/hardening.yml

# 3) Verify (ใช้ effective config จริงจาก sshd -T)
ansible-playbook labs/lab07-linux-hardening/verify.yml

# 4) รันเฉพาะบางหมวด
ansible-playbook labs/lab07-linux-hardening/hardening.yml --tags ssh
ansible-playbook labs/lab07-linux-hardening/hardening.yml --skip-tags sysctl
ansible-playbook labs/lab07-linux-hardening/hardening.yml --list-tags
```

## จำลอง drift แล้วตรวจจับ
```bash
docker exec web01 bash -c "echo 'PermitRootLogin yes' > /etc/ssh/sshd_config.d/00-hardening.conf && systemctl reload ssh"
ansible-playbook labs/lab07-linux-hardening/verify.yml          # web01 จะ FAIL
ansible-playbook labs/lab07-linux-hardening/hardening.yml --check --diff --limit web01   # เห็น diff
ansible-playbook labs/lab07-linux-hardening/hardening.yml --limit web01                  # แก้กลับ
```

## จุดที่ต้องระวังในงานจริง
- **ระวังล็อกตัวเองออกจากเครื่อง:** ก่อนตั้ง `PasswordAuthentication no` หรือ `AllowGroups` ต้องแน่ใจว่า user ที่ Ansible ใช้มี key และอยู่ในกลุ่มที่อนุญาต และควรเปิด session สำรองค้างไว้ 1 อัน
- `validate: sshd -t -f %s` ตรวจ syntax ก่อนเขียนทับไฟล์จริง ถ้าผิดจะไม่ถูก apply
- sshd อ่าน `sshd_config.d/*.conf` เรียงตามชื่อและใช้ **ค่าแรกที่เจอ** (เช่น cloud image มักมี `50-cloud-init.conf` ที่เปิด password ไว้) จึงต้องตั้งชื่อไฟล์เป็น `00-`
- ค่า `kernel.*` และ `fs.*` (เช่น `kernel.randomize_va_space`) เป็นค่าของทั้ง host ห้ามตั้งจากใน container แต่บน VM จริงควรเพิ่ม
- ในองค์กรจริงนิยมใช้ role สำเร็จรูป เช่น `ansible-lockdown/UBUNTU24-CIS`, `RHEL9-CIS` หรือ `dev-sec.os-hardening` แล้วปรับ/ปิดบาง control

## แบบฝึกหัด
1. เพิ่ม control ติดตั้งและเปิดใช้ `auditd` พร้อม rule เฝ้าดู `/etc/passwd` (`-w /etc/passwd -p wa -k identity`) ทำบน VM จริง
2. ทำ playbook สร้าง compliance report เป็นไฟล์ CSV (ดู lab12)
3. เพิ่ม `AllowGroups ansible ops-admins` แล้วทดสอบว่า `suda` (developers) login ไม่ได้
