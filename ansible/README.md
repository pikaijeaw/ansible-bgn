# Ansible Labs (ใช้งานจริง)

lab ทั้งหมดรันบน **Docker** ด้วยเครื่องจำลอง 4 เครื่องที่มี systemd + SSH เหมือน VM จริง และมี control node ที่ติดตั้ง Ansible ไว้แล้ว

```
┌──────────────── docker network: labnet ────────────────┐
│  control  (Ansible + collections + ansible-lint)       │
│  lb01     Ubuntu 24.04   haproxy      :8080→80, :8404   │
│  web01    Ubuntu 24.04   nginx                          │
│  web02    Ubuntu 24.04   nginx                          │
│  db01     Rocky Linux 9  MariaDB                        │
│  bigfix-mock  BigFix REST API จำลอง   :52311            │
└────────────────────────────────────────────────────────┘
```

## เริ่มต้น
ต้องมี Docker Desktop (Windows/macOS) หรือ Docker Engine + compose plugin (Linux)
บน Windows ให้ใช้ WSL2
```bash
cd ansible/lab-env
./setup.sh                                  # สร้าง SSH key, build และ start ทุกเครื่อง
docker compose exec control bash            # เข้า control node
ansible all -m ping                         # (อยู่ที่ /work/ansible)
```
หยุดหรือลบ lab: `docker compose stop` / `./teardown.sh`

> ถ้าอยากรัน Ansible จากเครื่องตัวเองแทน control container: `pip install "ansible>=11,<12"`
> แล้วตั้ง `ANSIBLE_PRIVATE_KEY_FILE=lab-env/.ssh/id_ed25519` และ map ชื่อเครื่องใน `/etc/hosts`

## รายการ Lab
| # | Lab | สถานการณ์จริง | ทักษะหลัก |
|---|---|---|---|
| 01 | [Ad-hoc](labs/lab01-adhoc/) | งานด่วนประจำวัน เช็ค disk/restart ทุกเครื่อง | inventory, pattern, module |
| 02 | [Server baseline](labs/lab02-first-playbook/) | setup เครื่องใหม่ให้เป็นมาตรฐาน | playbook, idempotency, check mode |
| 03 | [Variables & facts](labs/lab03-variables-facts/) | Ubuntu + RHEL ปนกัน, pre-flight check | facts, include_vars, assert, loop |
| 04 | [Templates & handlers](labs/lab04-templates-handlers/) | deploy config nginx แล้ว rollback ได้ถ้าผิด | Jinja2, handler, block/rescue |
| 05 | [Roles](labs/lab05-roles/) | ระบบ web 3-tier (haproxy + nginx) | roles, dependencies, listen |
| 06 | [Users & Vault](labs/lab06-users-vault/) | onboarding/offboarding พนักงาน | user, authorized_key, sudoers, vault |
| 07 | [Linux hardening](labs/lab07-linux-hardening/) | CIS benchmark + audit drift | sshd validate, sysctl, tags |
| 08 | [Rolling patching](labs/lab08-rolling-patching/) | patch รายเดือนแบบ zero downtime | serial, delegate_to, reboot |
| 09 | [Rolling deploy](labs/lab09-rolling-deploy/) | deploy เวอร์ชันใหม่ + rollback | release/symlink, include_tasks |
| 10 | [DB backup](labs/lab10-database-backup/) | backup ทุกคืน + ทดสอบ restore | community.mysql, cron, fetch |
| 11 | [Monitoring agent](labs/lab11-monitoring-agent/) | ลง node_exporter ทั้ง fleet | get_url checksum, systemd unit |
| 12 | [Inventory report](labs/lab12-inventory-report/) | รายงาน asset ส่ง audit/CMDB | package_facts, hostvars, report |
| 13 | [Health check](labs/lab13-health-check/) | daily health check + alert | service_facts, Jinja2 ขั้นสูง |
| 14 | [Incident response](labs/lab14-incident-response/) | disk เต็ม / service ล่ม / เก็บ diagnostics | runbook automation, EDA |
| 15 | [Windows](labs/lab15-windows/) | Windows baseline + Windows Update | WinRM, win_* modules |
| 16 | [BigFix integration](labs/lab16-bigfix-integration/) | Ansible คุยกับ BigFix REST API | uri, session relevance |
| 17 | [CI & quality](labs/lab17-ci-quality/) | ตรวจโค้ดก่อน merge | ansible-lint, GitHub Actions |

ลำดับที่แนะนำ: 01 → 05 ตามลำดับ (ต้องรัน 05 ก่อน 08 และ 09) ส่วน lab อื่นทำสลับลำดับได้

## สถานะการทดสอบ
lab 01–14 และ 16 ถูกรันจริงบน lab environment นี้ (ทั้งรอบแรกและรอบซ้ำเพื่อดู idempotency) ตอนทดสอบ db01 ใช้ Ubuntu
เพราะ sandbox ที่ใช้ทดสอบเข้าถึง mirror ของ Rocky ไม่ได้ ส่วน path ของ RHEL ผ่าน syntax check และ lint แล้ว
lab 15 (Windows) และการดาวน์โหลดจาก GitHub ใน lab 11 ตรวจได้แค่ syntax
ทุก playbook ผ่าน `ansible-lint` profile `production`

## โครงสร้าง
```
ansible/
├── ansible.cfg              # config กลาง (inventory, roles_path, ssh options)
├── requirements.yml         # collections (ถ้าไม่ใช้ control container)
├── inventory/               # hosts.yml + group_vars
├── lab-env/                 # Dockerfiles, docker-compose, BigFix mock
├── labs/labNN-*/            # แต่ละ lab: README + playbook
└── scripts/syntax-check.sh
```
