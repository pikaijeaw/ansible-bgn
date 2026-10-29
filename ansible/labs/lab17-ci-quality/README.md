# Lab 17: คุณภาพโค้ด Ansible + CI (ansible-lint, syntax check, GitHub Actions)

**สถานการณ์จริง:** พอมีหลายคนแก้ playbook ใน repo เดียวกัน ต้องมีด่านตรวจอัตโนมัติก่อน merge
เพื่อกันโค้ดที่ syntax ผิด ไม่ idempotent หรือไม่ปลอดภัย (เช่น ใช้ shell โดยไม่มี pipefail หรือเขียนรหัสผ่านลง log)

## สิ่งที่ repo นี้มีให้แล้ว
| ไฟล์ | หน้าที่ |
|---|---|
| `ansible/.ansible-lint` | config ของ ansible-lint (profile `production` ระดับเข้มที่สุด) |
| `ansible/scripts/syntax-check.sh` | `--syntax-check` ทุก playbook ใน `labs/` |
| `.github/workflows/ci.yml` | GitHub Actions รัน lint + syntax check + ตรวจไฟล์ BigFix `.bes` ทุก push และ PR |

## ขั้นตอน
```bash
cd /work/ansible
ansible-lint                      # ตรวจทั้ง repo
ansible-lint labs/lab08-rolling-patching/patch.yml
./scripts/syntax-check.sh
```

## Rule ที่เจอจริงตอนเขียน labs นี้ และวิธีแก้
| Rule | ปัญหา | แก้ |
|---|---|---|
| `package-latest` | `state: latest` ทำให้เวอร์ชันไม่คงที่ | ใช้ `present` แต่ถ้าเป็น playbook patch ที่ตั้งใจอัปเกรด ให้ใส่ `# noqa: package-latest` พร้อมเหตุผล |
| `risky-shell-pipe` | ใช้ pipe โดยไม่มี `set -o pipefail` ถ้าคำสั่งแรก fail ก็ยังได้ rc=0 | เพิ่ม `set -o pipefail` และ `executable: /bin/bash` |
| `command-instead-of-module` | ใช้ `systemctl` แทน module | ใช้ `ansible.builtin.systemd`/`service_facts` ถ้า module ทำได้ ถ้าไม่มี module ที่ทำได้จึงใส่ noqa |
| `var-naming[no-reserved]` | `register: action` ชนกับคำสงวน | ตั้งชื่อใหม่เป็น `bigfix_action` |
| `name[template]` | ใส่ `{{ }}` ไว้กลางชื่อ task | ย้าย template ไปไว้ท้ายชื่อ |
| `yaml[line-length]` | บรรทัดยาวเกิน 160 | ใช้ `>-` (folded) หรือแยกเป็น `vars:` |
| `no-changed-when` | `command`/`shell` ไม่บอกว่าเปลี่ยนอะไรหรือไม่ | ใส่ `changed_when:` ทุกครั้ง |

## ขั้นต่อไป: Molecule (ทดสอบ role ใน container)
```bash
pip install molecule molecule-plugins[docker]
cd labs/lab05-roles/roles/nginx
molecule init scenario --driver-name docker
molecule test      # create → converge → idempotence → verify → destroy
```
ขั้น `idempotence` ของ Molecule จะรันซ้ำแล้ว fail ถ้ายังมี task ที่ `changed` ซึ่งเป็นสิ่งเดียวกับที่เราตรวจด้วยมือในทุก lab

## แบบฝึกหัด
1. ทำให้ lint fail โดยตั้งใจ (เช่น ลบ `changed_when` ออกจาก task) แล้ว push ดูว่า GitHub Actions แดง
2. เพิ่ม `pre-commit` hook ที่รัน `ansible-lint` ก่อน commit
3. เพิ่ม job ใน CI ที่รัน `docker compose up` แล้วรัน lab02 จริงบน runner (integration test)
