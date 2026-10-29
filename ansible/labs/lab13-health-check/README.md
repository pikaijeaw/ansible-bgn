# Lab 13: Daily Health Check ทั้ง Fleet

**สถานการณ์จริง:** ทุกเช้าก่อน 9 โมง ทีม Ops ต้องตอบได้ว่า "ระบบปกติดีไหม"
แทนการ ssh ไล่ดูทีละเครื่อง ให้ AWX รัน playbook นี้ตามเวลา ถ้ามีเรื่อง CRIT ให้ job fail เพื่อส่ง alert

## ตรวจอะไรบ้าง
| Check | WARN | CRIT |
|---|---|---|
| disk | ≥ 80% | ≥ 90% |
| memory | ≥ 85% | – |
| load | load1 > vCPU×2 | – |
| failed_units | มี systemd unit ที่ failed | – |
| services | – | service ที่ group ต้องมี (web→nginx, lb→haproxy, db→mariadb) ไม่ได้รัน |

## ขั้นตอน
```bash
cd /work/ansible
ansible-playbook labs/lab13-health-check/healthcheck.yml
```
ผลตัวอย่าง:
```
HOST     CHECK         STATE DETAIL
db01     services      OK    mariadb
lb01     failed_units  WARN  systemd-binfmt.service
web02    services      CRIT  DOWN: nginx
```

## จำลองเหตุการณ์
```bash
ansible web02 -b -a "systemctl stop nginx"
ansible-playbook labs/lab13-health-check/healthcheck.yml      # job fail: CRITICAL: web02:services (DOWN: nginx)
ansible web02 -b -a "systemctl start nginx"

# ลองลดเกณฑ์ disk ให้ขึ้น CRIT แต่ยังไม่ให้ job fail
ansible-playbook labs/lab13-health-check/healthcheck.yml -e disk_crit_pct=20 -e healthcheck_fail_on_critical=false
```

## เทคนิคที่ได้เรียน
- `service_facts`: รู้สถานะทุก service โดยไม่ต้อง parse `systemctl`
- เก็บผลเป็น list ของ dict (`health`) ไว้ใน hostvars แล้วไปสรุปที่ `localhost`
- Jinja2 ขั้นสูง: `select('ge', n)`, `reject('in', list)`, `format()`, loop พร้อม `if` และ whitespace control `{%- -%}`
- ค่าจาก `-e` เป็น string ต้อง `| int` / `| float` ก่อนเปรียบเทียบเสมอ

## แบบฝึกหัด
1. เพิ่ม check วันหมดอายุของ TLS certificate ด้วย `community.crypto.get_certificate` (WARN < 30 วัน, CRIT < 7 วัน)
2. เพิ่ม check `timedatectl show -p NTPSynchronized` (บน VM จริง)
3. ส่งตารางผลเข้า Microsoft Teams/Slack ผ่าน webhook
4. ต่อด้วย [Lab 14](../lab14-incident-response/) เพื่อแก้ปัญหาที่ตรวจเจอแบบอัตโนมัติ
