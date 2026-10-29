# Lab 11: ติดตั้ง Monitoring Agent (Prometheus node_exporter) ทั้ง fleet

**สถานการณ์จริง:** เพิ่งตั้ง Prometheus + Grafana เสร็จ ต้องลง agent ทุกเครื่องให้เป็นมาตรฐานเดียวกัน
พร้อมสร้าง target list ให้ Prometheus โดยอัตโนมัติจาก inventory
(ใช้หลักเดียวกันกับการลง agent อื่น เช่น Zabbix agent, Datadog, CrowdStrike หรือ **BigFix agent**)

## เทคนิคที่ใช้
- `get_url` + `checksum: sha256:<url ของไฟล์ checksum>`: ดาวน์โหลดแล้วตรวจความถูกต้อง กันไฟล์ถูกปลอม
- `unarchive` + `creates`: ไม่แตกไฟล์ซ้ำ
- เขียน systemd unit เองพร้อม hardening (`ProtectSystem`, `NoNewPrivileges`)
- facts → แปลง architecture (`x86_64` → `amd64`)
- `delegate_to: localhost` + `uri`: ตรวจจากมุมของ monitoring server ว่า scrape ได้จริง (รวมถึงว่า firewall เปิดแล้ว)
- play ที่ 2 สร้าง `prometheus-targets.yml` จาก `groups`

## ขั้นตอน
```bash
cd /work/ansible
# แบบมาตรฐาน: binary จาก GitHub (ต้องออก internet ได้)
ansible-playbook labs/lab11-monitoring-agent/install.yml

# แบบ package ของ distro (Ubuntu: prometheus-node-exporter, RHEL: ต้องเปิด EPEL)
ansible-playbook labs/lab11-monitoring-agent/install.yml -e node_exporter_source=package

curl -s http://web01:9100/metrics | grep node_load
cat labs/lab11-monitoring-agent/prometheus-targets.yml
```
> ทดสอบใน sandbox ด้วย `node_exporter_source=package` แล้ว ส่วนแบบ GitHub ทดสอบไม่ได้เพราะ sandbox ออก GitHub ไม่ได้ แต่ผ่าน `--syntax-check` แล้ว

## Textfile collector (ใช้งานจริงบ่อย)
ส่ง metric ของตัวเองเข้า Prometheus ได้ โดยเขียนไฟล์ `.prom` ลงใน `/var/lib/node_exporter/textfile/`
เช่น ให้ script backup จาก lab10 เขียนอายุของ backup ล่าสุด:
```bash
echo "db_backup_last_success_timestamp $(date +%s)" > /var/lib/node_exporter/textfile/backup.prom
```
แล้วตั้ง alert ใน Prometheus เมื่อ backup เก่ากว่า 26 ชั่วโมง

## แบบฝึกหัด
1. แก้ `templates/db_backup.sh.j2` ของ lab10 ให้เขียน metric ข้างบน
2. เพิ่ม `node_exporter_version` ใหม่ แล้วรันใหม่ (handler จะ restart ให้เฉพาะเมื่อ binary เปลี่ยน)
3. เปลี่ยนเป็นติดตั้ง Zabbix agent 2 (`community.zabbix` collection มี role ให้แล้ว)
4. เพิ่ม Prometheus server + Grafana ใน docker-compose แล้วใช้ไฟล์ targets ที่สร้างขึ้น
