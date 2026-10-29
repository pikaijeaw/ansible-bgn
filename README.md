# ansible-bgn: เรียน Ansible + BigFix จาก Lab ใช้งานจริง

repo สำหรับเรียน **Ansible** และ **HCL BigFix** ตั้งแต่หลักการไปจนถึงงานที่ทำกันจริงในองค์กร
มี lab ที่รันได้จริง 17 lab ฝั่ง Ansible (บน Docker) และ 15 lab ฝั่ง BigFix (มี Fixlet/Task/Analysis ที่ import ได้ 29 ไฟล์)

## เริ่มที่ไหน
| เอกสาร | เนื้อหา |
|---|---|
| [docs/01-ansible-principles.md](docs/01-ansible-principles.md) | หลักการทำงานของ Ansible |
| [docs/02-bigfix-principles.md](docs/02-bigfix-principles.md) | หลักการทำงานของ BigFix และการเปรียบเทียบกับ Ansible |
| [docs/03-learning-plan.md](docs/03-learning-plan.md) | **ตารางการเรียนรู้ 12 สัปดาห์** ที่ผูกกับทุก lab |
| [ansible/README.md](ansible/README.md) | วิธีตั้ง lab (Docker) และรายการ Ansible lab |
| [bigfix/README.md](bigfix/README.md) | วิธีตั้ง lab server และรายการ BigFix lab |

## Quick start (Ansible)
```bash
git clone https://github.com/pikaijeaw/ansible-bgn.git
cd ansible-bgn/ansible/lab-env
./setup.sh
docker compose exec control bash
ansible all -m ping
ansible-playbook labs/lab05-roles/site.yml      # ระบบ web 3-tier ทั้งหมด → เปิด http://localhost:8080
```

## ตัวอย่างงานจริงที่มีใน repo
| งาน | Ansible | BigFix |
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
├── docs/                      หลักการทำงาน + ตารางเรียน
├── ansible/
│   ├── lab-env/               Docker lab (control, lb01, web01, web02, db01, bigfix-mock)
│   ├── inventory/  ansible.cfg  requirements.yml
│   └── labs/lab01..lab17/     README + playbook/roles
├── bigfix/
│   ├── labs/lab01..lab15/     README + ไฟล์ .bes
│   ├── api/bigfix_api.py      REST API client
│   └── scripts/validate_bes.py
└── .github/workflows/ci.yml   ansible-lint + syntax check + ตรวจ .bes
```
