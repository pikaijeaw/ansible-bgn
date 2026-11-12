# ansible-bgn: เรียน Ansible จาก Lab ใช้งานจริง

repo สำหรับเรียน **Ansible** ตั้งแต่หลักการไปจนถึงงานที่ทำกันจริงในองค์กร มี lab ที่รันได้จริง 17 lab (บน Docker)

> ส่วน **HCL BigFix** แยกไปอยู่ที่ repo [bigfix-labs](https://github.com/pikaijeaw/bigfix-labs) แล้ว (15 lab, ไฟล์ Fixlet/Task/Analysis 29 ไฟล์, cheat sheet และตารางเรียน)

## เริ่มที่ไหน
| เอกสาร | เนื้อหา |
|---|---|
| [docs/01-ansible-principles.md](docs/01-ansible-principles.md) | หลักการทำงานของ Ansible |
| [docs/03-learning-plan.md](docs/03-learning-plan.md) | **ตารางการเรียนรู้ Ansible 6 สัปดาห์** ที่ผูกกับทุก lab |
| [docs/04-wsl-setup.md](docs/04-wsl-setup.md) | ตั้ง lab บน Windows ด้วย WSL2 + ปัญหาที่อาจเจอ |
| [docs/05-ansible-cheatsheet.md](docs/05-ansible-cheatsheet.md) | **สรุป Ansible ภาษาไทย** เฉพาะที่สำคัญและใช้งานจริง (cheat sheet) |
| [ansible/README.md](ansible/README.md) | วิธีตั้ง lab (Docker) และรายการ Ansible lab |

## Quick start (Ansible)
บน Windows ให้ทำตาม [docs/04-wsl-setup.md](docs/04-wsl-setup.md) ก่อน
```bash
git clone https://github.com/pikaijeaw/ansible-bgn.git
cd ansible-bgn/ansible/lab-env
./setup.sh
docker compose exec control bash
ansible all -m ping
ansible-playbook labs/lab05-roles/site.yml      # ระบบ web 3-tier ทั้งหมด → เปิด http://localhost:8080
```

## ตัวอย่างงานจริงที่มีใน repo
| งาน | Ansible | BigFix ([bigfix-labs](https://github.com/pikaijeaw/bigfix-labs)) |
|---|---|---|
| Baseline / มาตรฐานเครื่องใหม่ | lab02, lab05 | lab14 (client settings) |
| ติดตั้ง/ถอนซอฟต์แวร์ | lab04, lab11, lab15 | lab05, lab06, lab07 |
| User & access | lab06 (users, sudo, vault) | lab12 (local admin audit) |
| Security hardening (CIS) | lab07 | lab09 |
| Patch management | lab08 (rolling + LB), lab15 (Windows Update) | lab10 (baseline, maintenance window) |
| Deploy แอปแบบ zero downtime | lab09 | – |
| Backup & restore | lab10 | – |
| Monitoring / inventory / report | lab11, lab12, lab13 | lab03, lab13 |
| Self-healing / incident response | lab14 | lab08, lab11 |
| API / integration / CI | lab16, lab17 | lab15 |

## โครงสร้าง repo
```
├── docs/                      หลักการทำงาน, ตารางเรียน, WSL, cheat sheet
├── ansible/
│   ├── lab-env/               Docker lab (control, lb01, web01, web02, db01, bigfix-mock)
│   ├── inventory/  ansible.cfg  requirements.yml
│   └── labs/lab01..lab17/     README + playbook/roles
└── .github/workflows/ci.yml   ansible-lint + syntax check + smoke test BigFix mock
```
