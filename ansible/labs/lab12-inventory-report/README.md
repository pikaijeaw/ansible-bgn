# Lab 12: Asset Inventory Report (CSV / HTML / JSON)

**สถานการณ์จริง:** ผู้บริหารหรือ auditor ขอรายชื่อ server ทั้งหมดพร้อม OS, IP, CPU/RAM, disk, port ที่เปิด
และวันที่ patch ล่าสุด ทุกสิ้นเดือน (หรือให้ส่งเข้า CMDB อย่าง ServiceNow)
แทนที่จะทำ Excel มือ ให้ดึงจาก facts แล้วสร้างรายงานอัตโนมัติ

## แนวคิด
- **Play 1** (บนทุกเครื่อง): เก็บ facts + `package_facts` + port ที่เปิด + วันที่ patch ล่าสุด แล้ว `set_fact` เก็บไว้ใน hostvars
- **Play 2** (`localhost`): อ่าน `hostvars` ของทุกเครื่อง แล้ว render template เป็น CSV / HTML / JSON

## ขั้นตอน
```bash
cd /work/ansible
ansible-playbook labs/lab12-inventory-report/report.yml
ls labs/lab12-inventory-report/reports/
column -s, -t < labs/lab12-inventory-report/reports/inventory-*.csv
```
เปิดไฟล์ `.html` ใน browser ได้เลย เครื่องที่ disk ต่ำกว่าเกณฑ์จะเป็นแถวสีส้ม
```bash
ansible-playbook labs/lab12-inventory-report/report.yml -e low_disk_gb=30    # ลองปรับเกณฑ์
```

## สิ่งที่ได้เรียน
- `hostvars[host]['ansible_facts']` และ filter `map('extract', hostvars, ...)`
- `package_facts` (รู้ว่าเครื่องมี package อะไรเวอร์ชันไหน ใช้ตรวจช่องโหว่ได้ เช่น หาเครื่องที่ยังใช้ openssl เวอร์ชันเก่า)
- อย่าตั้งชื่อตัวแปรชนกับ magic variable เช่น `ansible_play_hosts` และค่าจาก `-e` เป็น string เสมอ จึงต้องใช้ `| int` ก่อนเปรียบเทียบ

## แบบฝึกหัด
1. เพิ่มคอลัมน์ `openssl_version` จาก `ansible_facts['packages']['openssl'][0]['version']`
2. ส่งรายงานทางอีเมลด้วย `community.general.mail` (แนบไฟล์ HTML)
3. POST ไฟล์ JSON เข้า CMDB API ด้วย `ansible.builtin.uri` (`method: POST`, `body_format: json`)
4. เทียบกับ BigFix: งานแบบนี้ BigFix ทำด้วย **Analysis + Web Reports** และได้ข้อมูลแทบ real-time (ดู `bigfix/labs/lab03-inventory-analysis`)
