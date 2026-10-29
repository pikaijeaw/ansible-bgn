# Lab 14: Incident Response Runbooks อัตโนมัติ

**สถานการณ์จริง:** ตี 2 มี alert เข้ามา on-call ต้องตื่นมาแก้ปัญหาเดิมๆ ซ้ำทุกครั้ง
ถ้าเขียน runbook เป็น playbook จะให้ AWX/AAP รันเองเมื่อ monitoring ยิง webhook มา (event-driven) หรือให้ L1 กดรันเองได้

| Playbook | สถานการณ์ |
|---|---|
| `disk-cleanup.yml` | Disk ใกล้เต็มเพราะ log |
| `service-recovery.yml` | Service ล่ม: เก็บ log ก่อน restart แล้วแจ้งเตือน ถ้ายังไม่หายให้ escalate |
| `collect-diagnostics.yml` | เก็บข้อมูลเครื่องเป็นไฟล์ `.tar.gz` ส่ง vendor หรือใช้ทำ postmortem |
| `simulate-disk-full.yml` | สร้างสถานการณ์จำลอง (ใช้เฉพาะในแล็บ) |

## 1) Disk เต็ม
```bash
cd /work/ansible
ansible-playbook labs/lab14-incident-response/simulate-disk-full.yml -e target=web01
ansible web01 -a "du -sh /var/log/company"
ansible-playbook labs/lab14-incident-response/disk-cleanup.yml -e target=web01
```
ผลที่ได้จากการทดสอบ:
```
Deleted 20 old logs, archived 1 big logs
Free /var/log: 26540 MB -> 26975 MB
```
ข้อสังเกตจากงานจริง:
- log ที่ app ยังเปิดอยู่ **ห้าม `rm`** เพราะ process ยังถือ file handle ไว้ และพื้นที่จะไม่ถูกคืน ให้ `truncate` แทน
- task สุดท้ายใช้ `lsof +L1` หาไฟล์ที่ถูกลบแล้วแต่ยังถูกเปิดอยู่ ต้อง restart service ตัวนั้นจึงจะได้พื้นที่คืน

## 2) Service ล่ม
```bash
ansible web02 -b -a "systemctl stop nginx"
ansible-playbook labs/lab14-incident-response/service-recovery.yml \
  -e target=web -e service_name=nginx -e health_url=http://localhost/healthz
ls labs/lab14-incident-response/evidence/      # log ก่อน restart ถูกเก็บไว้
```
web01 ที่ยังปกติจะถูกข้าม (skipped) ส่วน web02 จะขึ้น `RECOVERED nginx on web02`

จำลองกรณีที่ restart แล้วไม่หาย (ต้อง escalate):
```bash
ansible web02 -b -m shell -a "echo 'broken;' > /etc/nginx/conf.d/zz-broken.conf && systemctl stop nginx"
ansible-playbook labs/lab14-incident-response/service-recovery.yml -e target=web02
# → Auto-remediation FAILED for nginx on web02 - page on-call engineer
ansible web02 -b -m shell -a "rm /etc/nginx/conf.d/zz-broken.conf && systemctl start nginx"
```

## 3) Diagnostic bundle
```bash
ansible-playbook labs/lab14-incident-response/collect-diagnostics.yml -e target=db01
tar tzf labs/lab14-incident-response/evidence/diag-db01.tar.gz
```

## ต่อยอดเป็น Event-Driven Ansible (EDA)
```yaml
# rulebook.yml (ansible-rulebook)
- name: Auto-heal from Alertmanager
  hosts: all
  sources:
    - ansible.eda.alertmanager:
        host: 0.0.0.0
        port: 5000
  rules:
    - name: Service down
      condition: event.alert.labels.alertname == "ServiceDown"
      action:
        run_playbook:
          name: labs/lab14-incident-response/service-recovery.yml
          extra_vars:
            target: "{{ event.alert.labels.instance }}"
            service_name: "{{ event.alert.labels.service }}"
```

## แบบฝึกหัด
1. ใส่ `webhook_url` ของ Teams/Slack จริง แล้วดูข้อความแจ้งเตือน
2. เพิ่ม runbook "CPU สูง": หา process ที่กิน CPU 5 อันดับแรก แล้วเก็บ `top -b -n1`
3. เพิ่ม runbook "certificate ใกล้หมดอายุ": renew ด้วย certbot แล้ว reload nginx
