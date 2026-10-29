# Lab 10: Database Backup อัตโนมัติ + ทดสอบ Restore

**สถานการณ์จริง:** ฐานข้อมูลลูกค้าต้องมี backup ทุกคืน เก็บย้อนหลัง 7 วัน มีสำเนาอยู่นอกเครื่อง
และ auditor ขอหลักฐานว่า **restore ได้จริง** (ไม่ใช่แค่มีไฟล์)

## สิ่งที่ playbook ทำ
| `backup.yml` | `restore-test.yml` |
|---|---|
| ติดตั้ง MariaDB (Ubuntu/RHEL) | สร้าง DB ชั่วคราว `appdb_restoretest` |
| สร้าง DB + user สิทธิ์น้อยที่สุด (`community.mysql`) | restore dump ล่าสุดลงไป |
| ใส่ข้อมูลตัวอย่าง | เทียบจำนวน row กับของจริง |
| วาง script backup (ทีละ DB, `gzip -t` ตรวจไฟล์, ลบไฟล์เกิน 7 วัน) | `always:` ลบ DB ชั่วคราวทิ้ง ไม่ว่าผลจะผ่านหรือไม่ |
| ตั้ง cron 01:30 ทุกคืน | |
| backup ทันที 1 รอบ แล้ว `fetch` สำเนามาที่ control node | |

## ขั้นตอน
```bash
cd /work/ansible
ansible-playbook labs/lab10-database-backup/backup.yml
ls -R labs/lab10-database-backup/backups/          # สำเนา off-site

ansible-playbook labs/lab10-database-backup/restore-test.yml
# ผลที่ควรได้: RESTORE OK: 3 rows in customers

ansible db -b -a "crontab -l"
ansible db -b -a "tail -5 /var/log/company/db_backup.log"
```

## จำลองเหตุการณ์จริง: มีคนลบข้อมูลโดยไม่ได้ตั้งใจ
```bash
ansible db -b -m community.mysql.mysql_query -a "login_db=appdb query='DELETE FROM customers WHERE id=2'"
# restore เฉพาะ appdb จาก backup ล่าสุด
ansible db -b -m shell -a "zcat /opt/backup/mysql/latest/appdb.sql.gz | mysql appdb"
ansible db -b -m community.mysql.mysql_query -a "login_db=appdb query='SELECT * FROM customers'"
```

## หลัก 3-2-1 ของ backup
มี **3** สำเนา บน **2** สื่อที่ต่างกัน และอย่างน้อย **1** สำเนาอยู่นอกสถานที่
ในงานจริงให้เปลี่ยนจาก `fetch` เป็นส่งขึ้น S3/NAS เช่น `amazon.aws.s3_object` หรือ `ansible.posix.synchronize`

## แบบฝึกหัด
1. ย้าย `app_db_password` เข้า Ansible Vault ตามแบบ lab06
2. ส่ง alert (เช่น webhook) เมื่อ backup script fail (`block/rescue` + `uri`)
3. ตั้ง AWX schedule ให้รัน `restore-test.yml` ทุกวันที่ 1 ของเดือน แล้วเก็บผลไว้เป็นหลักฐาน audit
4. ทำ backup ของ PostgreSQL ด้วย `community.postgresql.postgresql_db: state=dump`
