# Ansible สรุปที่ต้องรู้และใช้งานจริง (Cheat Sheet ภาษาไทย)

เอกสารนี้เก็บเฉพาะเรื่องสำคัญที่ใช้บ่อยในงานจริง อ่านจบใน 15–20 นาที
รายละเอียดเชิงลึกดู [01-ansible-principles.md](01-ansible-principles.md) และลองทำจริงที่ [../ansible/labs](../ansible/labs)

## 1. Ansible คืออะไร (สั้นๆ)
| คำ | ความหมาย |
|---|---|
| Agentless | ไม่ต้องลง agent ที่เครื่องปลายทาง ใช้ SSH (Linux) หรือ WinRM (Windows) |
| Push | control node ส่งงานไปทำที่เครื่องปลายทาง |
| Declarative | บอก "สถานะที่ต้องการ" (เช่น nginx ต้องติดตั้งอยู่) ไม่ใช่ลำดับคำสั่ง |
| Idempotent | รันซ้ำกี่รอบผลก็เหมือนเดิม ถ้าเครื่องถูกต้องอยู่แล้วจะไม่เปลี่ยนอะไร (`changed=0`) |

ทุกครั้งที่รัน Ansible จะ: เชื่อมต่อ SSH → ส่งโมดูล Python ไปรัน → ได้ผลกลับมา → ลบโมดูลทิ้ง

## 2. ศัพท์พื้นฐาน
| คำ | ความหมายภาษาไทย | ตัวอย่าง |
|---|---|---|
| Control node | เครื่องที่ใช้สั่งงาน (ต้องเป็น Linux/macOS/WSL) | laptop, jump host |
| Managed node | เครื่องปลายทางที่ถูกจัดการ | web01, db01 |
| Inventory | รายชื่อเครื่องและกลุ่ม | `inventory/hosts.ini` |
| Playbook | ไฟล์ YAML ที่บอกว่าจะทำอะไรกับเครื่องไหน | `site.yml` |
| Play | ส่วนหนึ่งของ playbook ที่ผูก "กลุ่มเครื่อง" กับ "รายการงาน" | `hosts: web` |
| Task | งานหนึ่งอย่าง = เรียกโมดูลหนึ่งครั้ง | ติดตั้ง nginx |
| Module | ตัวทำงานจริง (ชุดคำสั่งสำเร็จรูป) | `apt`, `copy`, `service` |
| Role | โครงสร้างโฟลเดอร์ที่แพ็กงานให้ใช้ซ้ำ | `roles/nginx` |
| Handler | task พิเศษที่ทำเมื่อถูก `notify` และมีการเปลี่ยนแปลงเท่านั้น (เช่น reload nginx) | `restart nginx` |
| Facts | ข้อมูลเครื่องที่เก็บอัตโนมัติ | `ansible_facts['os_family']` |
| Variable | ตัวแปร | `{{ http_port }}` |
| Collection | ชุดโมดูล/role ที่แจกจ่าย | `ansible.posix`, `community.general` |
| Vault | เข้ารหัสไฟล์/ค่าลับ (รหัสผ่าน, key) | `ansible-vault encrypt` |

## 3. Inventory
```ini
# inventory/hosts.ini
[web]
web01 ansible_host=10.0.0.11
web02 ansible_host=10.0.0.12

[db]
db01 ansible_host=10.0.0.21

[linux:children]      # กลุ่มที่รวมกลุ่มอื่น
web
db

[linux:vars]          # ตัวแปรของทั้งกลุ่ม
ansible_user=ansible
```
ตรวจ inventory: `ansible-inventory --graph`

## 4. Ad-hoc command (สั่งครั้งเดียวไม่ต้องเขียน playbook)
| ต้องการ | คำสั่ง |
|---|---|
| ทดสอบเชื่อมต่อ | `ansible all -m ping` |
| ดูข้อมูลเครื่อง | `ansible web -m setup -a "filter=ansible_distribution*"` |
| รันคำสั่ง | `ansible all -m command -a "uptime"` |
| ติดตั้งแพ็กเกจ (sudo) | `ansible web -b -m apt -a "name=nginx state=present update_cache=true"` |
| ส่งไฟล์ | `ansible all -m copy -a "src=a.txt dest=/tmp/a.txt"` |
| ทำเฉพาะบางเครื่อง | `ansible all -l web01 -m ping` (`-l` = limit) |

`-b` = become (ยกสิทธิ์เป็น root), `-m` = module, `-a` = argument

## 5. Playbook โครงสร้างที่ต้องจำ
```yaml
---
- name: Configure web servers          # ชื่อ play
  hosts: web                            # ใช้กับกลุ่มไหน
  become: true                          # ใช้ sudo
  vars:
    http_port: 80
  tasks:
    - name: Install nginx               # ชื่อ task (ตั้งให้อ่านรู้เรื่อง)
      ansible.builtin.apt:
        name: nginx
        state: present
        update_cache: true
      when: ansible_facts['os_family'] == 'Debian'

    - name: Deploy config
      ansible.builtin.template:
        src: nginx.conf.j2
        dest: /etc/nginx/nginx.conf
        validate: nginx -t -c %s        # ตรวจ syntax ก่อนเขียนทับ
      notify: Reload nginx              # เรียก handler เมื่อไฟล์เปลี่ยน

    - name: Ensure nginx running
      ansible.builtin.service:
        name: nginx
        state: started
        enabled: true

  handlers:
    - name: Reload nginx
      ansible.builtin.service:
        name: nginx
        state: reloaded
```
**กฎเหล็ก:** ใช้ชื่อเต็มของโมดูล (`ansible.builtin.xxx`), ตั้ง `name:` ทุก task, ใช้ `state:` ให้ชัดเจน

## 6. โมดูลที่ใช้บ่อยที่สุด
| หมวด | โมดูล | ใช้ทำอะไร |
|---|---|---|
| แพ็กเกจ | `apt`, `dnf`, `package` | ติดตั้ง/ลบ/อัปเดต |
| บริการ | `service`, `systemd` | start/stop/enable |
| ไฟล์ | `copy`, `template`, `file`, `lineinfile`, `blockinfile` | ส่งไฟล์ / สร้างจาก template / แก้บรรทัด / สิทธิ์ |
| ผู้ใช้ | `user`, `group`, `authorized_key` | จัดการ user และ SSH key |
| คำสั่ง | `command`, `shell`, `script` | รันคำสั่ง (ใช้เมื่อไม่มีโมดูลเฉพาะ) |
| เครือข่าย | `uri`, `get_url`, `wait_for` | เรียก API, ดาวน์โหลด, รอ port พร้อม |
| ข้อมูล | `debug`, `set_fact`, `assert`, `stat`, `find` | ดูค่า, ตั้งตัวแปร, ตรวจเงื่อนไข |
| Cron/ระบบ | `cron`, `reboot`, `sysctl`, `mount` | งานระบบ |
| Git | `git` | ดึงโค้ด |

> เลือกโมดูลเฉพาะทางก่อน `command`/`shell` เสมอ เพราะโมดูลเฉพาะ idempotent เอง ส่วน `command`/`shell` ต้องใส่ `creates:` หรือ `changed_when:` เอง

## 7. ตัวแปรและ Jinja2
```yaml
vars:
  app_name: myapp
  ports: [80, 443]

tasks:
  - debug:
      msg: "{{ app_name }} listens on {{ ports | join(',') }}"
```
ลำดับความสำคัญ (ย่อ จากต่ำไปสูง):
`role defaults` < `inventory vars` < `group_vars` < `host_vars` < `play vars` < `set_fact` < `-e` (extra vars, สูงสุด)

Filter ที่ใช้บ่อย: `default('x')`, `join(',')`, `int`, `lower`, `to_nice_json`, `length`, `select`, `map`

Template (`.j2`):
```jinja
server_name {{ inventory_hostname }};
{% for p in ports %}
listen {{ p }};
{% endfor %}
```

## 8. ควบคุมการทำงาน
| ต้องการ | คีย์เวิร์ด | ตัวอย่าง |
|---|---|---|
| ทำตามเงื่อนไข | `when` | `when: ansible_facts['os_family'] == 'RedHat'` |
| ทำซ้ำ | `loop` | `loop: [git, curl, vim]` แล้วใช้ `{{ item }}` |
| เก็บผลลัพธ์ | `register` | `register: result` แล้วใช้ `result.stdout` |
| กำหนดว่า "เปลี่ยน" เมื่อไร | `changed_when` | `changed_when: false` |
| กำหนดว่า "ล้มเหลว" เมื่อไร | `failed_when` | `failed_when: rc not in [0, 100]` |
| ข้ามข้อผิดพลาด | `ignore_errors` | ใช้เท่าที่จำเป็น |
| จัดการ error | `block / rescue / always` | try / catch / finally |
| ทำทีละกี่เครื่อง | `serial` | `serial: 1` = rolling update ทีละเครื่อง |
| รันบนเครื่องอื่น | `delegate_to` | `delegate_to: localhost` |
| รันครั้งเดียวต่อ play | `run_once` | `run_once: true` |
| รอ/ลองใหม่ | `retries`, `until`, `delay` | รอ service พร้อม |
| แท็ก | `tags` | `--tags nginx` รันเฉพาะบางส่วน |

ตัวอย่าง block/rescue:
```yaml
- block:
    - name: Deploy new version
      ansible.builtin.command: /opt/deploy.sh
  rescue:
    - name: Roll back
      ansible.builtin.command: /opt/rollback.sh
  always:
    - name: Notify
      ansible.builtin.debug: { msg: "deploy finished" }
```

## 9. Role (แพ็กงานให้ใช้ซ้ำ)
```
roles/nginx/
├── tasks/main.yml        # งานหลัก
├── handlers/main.yml     # handlers
├── templates/            # ไฟล์ .j2
├── files/                # ไฟล์ static
├── defaults/main.yml     # ค่า default (override ง่าย)
└── vars/main.yml         # ค่าตัวแปรภายใน (priority สูง)
```
เรียกใช้:
```yaml
- hosts: web
  roles:
    - role: nginx
      vars: { http_port: 8080 }
```
สร้างโครงอัตโนมัติ: `ansible-galaxy init roles/nginx`
ติดตั้ง role/collection ภายนอก: `ansible-galaxy install -r requirements.yml`

## 10. Vault (เก็บความลับอย่างปลอดภัย)
| ต้องการ | คำสั่ง |
|---|---|
| เข้ารหัสไฟล์ | `ansible-vault encrypt group_vars/all/secrets.yml` |
| แก้ไฟล์ที่เข้ารหัส | `ansible-vault edit group_vars/all/secrets.yml` |
| เข้ารหัสเฉพาะค่า | `ansible-vault encrypt_string 'P@ssw0rd' --name db_password` |
| รัน playbook | `ansible-playbook site.yml --ask-vault-pass` หรือ `--vault-password-file ~/.vault_pass` |

**ห้าม** commit ไฟล์รหัสผ่าน vault (`.vault_pass`) เข้า git และอย่าใส่ความลับใน log (`no_log: true`)

## 11. คำสั่ง ansible-playbook ที่ใช้ทุกวัน
| ต้องการ | คำสั่ง |
|---|---|
| ตรวจ syntax | `ansible-playbook site.yml --syntax-check` |
| ลองรันโดยไม่เปลี่ยนจริง | `ansible-playbook site.yml --check --diff` |
| จำกัดเครื่อง | `-l web01` หรือ `--limit web` |
| จำกัดงาน | `--tags nginx` / `--skip-tags slow` |
| ส่งตัวแปร | `-e "http_port=8080"` |
| ดูรายละเอียด | `-v` ถึง `-vvv` (ยิ่งเยอะยิ่งละเอียด) |
| ดู task ทั้งหมด | `--list-tasks` / `--list-hosts` |
| เริ่มจาก task ที่ระบุ | `--start-at-task "Deploy config"` |
| รันทีละ task (ถามยืนยัน) | `--step` |

อ่านผลสรุปท้ายการรัน (PLAY RECAP):
| ค่า | ความหมาย |
|---|---|
| `ok` | ทำสำเร็จ ไม่มีอะไรเปลี่ยน |
| `changed` | มีการเปลี่ยนแปลงจริง |
| `unreachable` | เชื่อมต่อเครื่องไม่ได้ (SSH/เครือข่าย) |
| `failed` | task ล้มเหลว |
| `skipped` | ข้ามเพราะ `when` เป็นเท็จ |

รันซ้ำรอบที่ 2 ควรได้ `changed=0` ถ้าไม่ใช่ แสดงว่า playbook ไม่ idempotent

## 12. ไฟล์ตั้งค่า `ansible.cfg`
```ini
[defaults]
inventory = inventory/hosts.ini
remote_user = ansible
host_key_checking = False      # ใช้เฉพาะ lab เท่านั้น! production ควรเปิดไว้
forks = 20                     # จำนวนเครื่องที่ทำพร้อมกัน
retry_files_enabled = False

[privilege_escalation]
become = True
become_method = sudo
```
ลำดับที่ Ansible หา config: `ANSIBLE_CONFIG` → `./ansible.cfg` → `~/.ansible.cfg` → `/etc/ansible/ansible.cfg`

## 13. Best practice ที่ใช้จริง
1. **เก็บทุกอย่างใน Git** แล้วรีวิวก่อนรัน (Infrastructure as Code)
2. **รัน `--check --diff` ก่อนเสมอ** ใน production และอ่านผลก่อนรันจริง
3. **ให้ idempotent** ใช้โมดูลเฉพาะแทน `shell`, ใส่ `changed_when`/`creates` เมื่อจำเป็น
4. **ตั้งชื่อ task ชัดเจน** อ่าน log แล้วรู้ว่าทำอะไรอยู่
5. **แยกตัวแปรออกจากโค้ด** ใช้ `group_vars/` `host_vars/` และ role `defaults/`
6. **ความลับใช้ Vault** และ `no_log: true`
7. **Rolling update** ด้วย `serial` + `max_fail_percentage` กันล่มพร้อมกันทั้งระบบ
8. **ตรวจ config ก่อนใช้งาน** ด้วย `validate:` (เช่น `nginx -t`, `visudo -cf %s`)
9. **ใช้ ansible-lint** ตรวจคุณภาพ: `ansible-lint` (repo นี้ตั้งไว้ใน CI แล้ว)
10. **Tag เวอร์ชัน collection/role** ใน `requirements.yml` เพื่อให้ผลซ้ำได้
11. **ใช้ least privilege** ให้ `become` เฉพาะ task ที่จำเป็น และใช้ SSH key ไม่ใช้รหัสผ่าน

## 14. ปัญหาที่เจอบ่อยและวิธีแก้
| อาการ | สาเหตุที่พบบ่อย | วิธีแก้ |
|---|---|---|
| `UNREACHABLE` / Permission denied (publickey) | SSH key/user ไม่ถูก | ตรวจ `ansible_user`, key, ลอง `ssh user@host` ตรงๆ |
| `Missing sudo password` | ใช้ `become` แต่ไม่ได้ตั้ง sudo | ตั้ง NOPASSWD หรือใช้ `--ask-become-pass` (`-K`) |
| `No package matching ...` (apt) | ยังไม่ได้ `apt update` | ใส่ `update_cache: true` |
| `Failed to import ... python` / interpreter | เครื่องปลายทางไม่มี Python | ติดตั้ง python3 หรือระบุ `ansible_python_interpreter` |
| YAML parse error | เว้นวรรคผิด / ใช้ tab | ใช้ space 2 ช่อง, รัน `--syntax-check` |
| ตัวแปร undefined | ชื่อผิด/ไม่ได้กำหนด | ใช้ `default()` หรือ `-vvv` ดูค่า |
| `changed` ทุกครั้งที่รัน | ใช้ `shell`/`command` | ใส่ `changed_when`, `creates`, หรือเปลี่ยนไปใช้โมดูลเฉพาะ |
| `--check` ล้มเหลวที่ task service | แพ็กเกจยังไม่ได้ติดตั้งจริงในโหมดทดลอง | เป็นข้อจำกัดของ check mode ปกติ ข้ามหรือใส่ `check_mode: false` เฉพาะจุด |
| `world writable directory` warning | โฟลเดอร์สิทธิ์ 777 (เช่น `/mnt/c` ใน WSL) | ย้ายโปรเจกต์ไปไว้ใน home ของ Linux |

## 15. Roadmap เรียนต่อ
1. ลองทำ lab 01–05 ใน repo นี้ (ad-hoc → playbook → variables → handlers → roles)
2. ฝึกเขียน role จริงจากงานที่ทำประจำ (ลงแพ็กเกจ + config + service)
3. เพิ่ม Vault และ rolling update (lab 08–10)
4. ใช้ `ansible-lint` และ CI ตรวจโค้ดทุกครั้งที่ push
5. ขั้นสูง: dynamic inventory (cloud), AWX/AAP (UI + RBAC + schedule), Molecule (ทดสอบ role), Event-Driven Ansible

## 16. แหล่งอ้างอิง
- เอกสารทางการ: https://docs.ansible.com/ansible/latest/
- รายชื่อโมดูล: https://docs.ansible.com/ansible/latest/collections/index.html
- Galaxy (role/collection): https://galaxy.ansible.com

## 17. ตาราง Option ของคำสั่ง Ansible

### 17.1 `ansible` (ad-hoc)
รูปแบบ: `ansible <pattern> [options]`

| Option | ความหมาย | ตัวอย่าง |
|---|---|---|
| `-m` | module ที่จะใช้ (ค่าเริ่มต้นคือ `command`) | `-m ping`, `-m apt` |
| `-a` | argument ของ module | `-a "name=nginx state=present"` |
| `-i` | ระบุไฟล์ inventory | `-i inventory/hosts.ini` |
| `-l`, `--limit` | จำกัดให้ทำเฉพาะบางเครื่องหรือกลุ่ม | `-l web01`, `-l 'web:!web02'` |
| `-b`, `--become` | ยกสิทธิ์เป็น root (sudo) | `-b` |
| `-K`, `--ask-become-pass` | ถามรหัสผ่าน sudo | `-K` |
| `--become-user` | ยกสิทธิ์เป็น user อื่นที่ไม่ใช่ root | `--become-user postgres` |
| `-u`, `--user` | user ที่ใช้ SSH | `-u ansible` |
| `-k`, `--ask-pass` | ถามรหัสผ่าน SSH | `-k` |
| `--private-key` | ระบุไฟล์ SSH key | `--private-key ~/.ssh/id_ed25519` |
| `-e`, `--extra-vars` | ส่งตัวแปรเข้าไป (priority สูงสุด) | `-e "port=8080"`, `-e @vars.yml` |
| `-f`, `--forks` | จำนวนเครื่องที่ทำพร้อมกัน (ค่าเริ่มต้น 5) | `-f 20` |
| `-o`, `--one-line` | แสดงผลบรรทัดเดียวต่อเครื่อง | `-o` |
| `-t`, `--tree` | บันทึกผลลัพธ์เป็นไฟล์ แยกตามเครื่อง | `-t /tmp/out` |
| `-C`, `--check` | ลองรันโดยไม่เปลี่ยนจริง (dry-run) | `-C` |
| `-D`, `--diff` | แสดงส่วนต่างของไฟล์ที่จะเปลี่ยน | `-CD` |
| `-T`, `--timeout` | timeout ของการเชื่อมต่อ (วินาที) | `-T 30` |
| `-v` ถึง `-vvvv` | ระดับความละเอียดของ log | `-vvv` |
| `--list-hosts` | แสดงรายชื่อเครื่องที่ตรงเงื่อนไข ไม่รันจริง | `--list-hosts` |

> ถ้าคำสั่งมี pipe, `>` หรือตัวแปร shell ให้ใช้ `-m shell` เช่น `-m shell -a "ps aux | wc -l"`

ตัวอย่างรวม:
```bash
ansible web -i inventory/hosts.ini -b -m apt -a "name=nginx state=present update_cache=true" -f 10
```

### 17.2 `ansible-playbook`
รูปแบบ: `ansible-playbook [options] playbook.yml`
รับ option ของ `ansible` ข้างบนได้เกือบทั้งหมด (`-i -l -b -K -u -e -f -C -D -v`) และมีเพิ่มดังนี้

| Option | ความหมาย |
|---|---|
| `--syntax-check` | ตรวจ syntax เท่านั้น ไม่รัน |
| `--list-tasks` | แสดง task ทั้งหมดที่จะรัน |
| `--list-tags` | แสดง tag ทั้งหมด |
| `-t`, `--tags` | รันเฉพาะ task ที่มี tag นี้ (`-t nginx,config`) |
| `--skip-tags` | ข้าม task ที่มี tag นี้ |
| `--start-at-task` | เริ่มรันจาก task ที่ระบุชื่อ |
| `--step` | รันทีละ task พร้อมถามยืนยัน |
| `--vault-password-file` | ไฟล์รหัสผ่านสำหรับถอด Vault |
| `--ask-vault-pass` | ถามรหัสผ่าน Vault |
| `-e @file.yml` | โหลดตัวแปรจากไฟล์ |
| `--force-handlers` | รัน handler แม้ task ก่อนหน้าจะล้มเหลว |
| `--flush-cache` | ล้าง fact cache |

> ระวัง: `-t` ใน `ansible-playbook` คือ `--tags` แต่ใน `ansible` ธรรมดาคือ `--tree`

### 17.3 เครื่องมืออื่นในชุด Ansible
| คำสั่ง | ใช้ทำอะไร | Option ที่ใช้บ่อย |
|---|---|---|
| `ansible-inventory` | ดู inventory | `--graph` (ต้นไม้), `--list` (JSON), `--host web01` |
| `ansible-doc` | อ่านเอกสาร module ในเครื่อง | `ansible-doc apt`, `-l` (รายชื่อทั้งหมด), `-s apt` (สรุป syntax) |
| `ansible-config` | ดู/ตรวจ config | `dump --only-changed`, `list`, `view` |
| `ansible-vault` | เข้ารหัสไฟล์/ค่า | `create`, `encrypt`, `decrypt`, `edit`, `view`, `rekey`, `encrypt_string` |
| `ansible-galaxy` | ติดตั้ง role/collection | `install -r requirements.yml`, `init <role>`, `collection install` |
| `ansible-lint` | ตรวจคุณภาพ playbook | `-p` (ผลย่อ), `--profile production` |
| `ansible-pull` | ให้เครื่องปลายทางดึง playbook จาก Git มารันเอง | `-U <repo-url>` |
| `ansible-console` | โหมดโต้ตอบ (REPL) | `ansible-console web` |

### 17.4 ตัวอย่างที่ใช้จริง
```bash
# ดูว่า inventory อ่านถูกไหม
ansible-inventory --graph

# เช็ก memory ทุกเครื่องในกลุ่ม web
ansible web -m command -a "free -m"

# อ่านวิธีใช้ module dnf
ansible-doc ansible.builtin.dnf

# ลองรันก่อนใช้จริง เฉพาะเครื่อง web01 และเฉพาะ tag nginx
ansible-playbook site.yml -l web01 -t nginx --check --diff

# รันจริง ส่งตัวแปร และดู log ละเอียด
ansible-playbook site.yml -e "http_port=8080" -vv
```
