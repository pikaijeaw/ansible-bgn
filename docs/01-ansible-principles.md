# หลักการทำงานของ Ansible

## 1. Ansible คืออะไร
Ansible เป็นเครื่องมือ open source ของ Red Hat สำหรับ Configuration Management, Provisioning, Application Deployment และ Orchestration
เราเขียนบอกเป็น YAML ว่าเครื่องควรอยู่ในสภาพไหน แล้ว Ansible จะไปปรับเครื่องให้เป็นแบบนั้น

## 2. หลักการสำคัญ
| หลักการ | ความหมาย |
|---|---|
| **Agentless** | ไม่ต้องลง agent บนเครื่องปลายทาง ใช้ SSH กับ Linux และ WinRM/SSH กับ Windows |
| **Push model** | Control node เป็นฝ่ายส่งคำสั่งไปที่เครื่องปลายทางเอง |
| **Declarative** | บอกแค่ผลลัพธ์ที่ต้องการ เช่น "nginx ต้องติดตั้งแล้วและกำลังรันอยู่" |
| **Idempotent** | รันซ้ำกี่รอบก็ได้ผลเหมือนเดิม ถ้าเครื่องอยู่ในสภาพที่ต้องการแล้วจะไม่แก้อะไร (`ok` ไม่ใช่ `changed`) |

## 3. สถาปัตยกรรม
```
┌──────────────────────┐        SSH / WinRM        ┌──────────────┐
│    Control Node      │ ────────────────────────► │ Managed Node │ web01
│  ansible-playbook    │ ────────────────────────► │ Managed Node │ web02
│  inventory           │ ────────────────────────► │ Managed Node │ db01
│  playbooks / roles   │                           └──────────────┘
│  modules / plugins   │
└──────────────────────┘
```

## 4. สิ่งที่เกิดขึ้นเมื่อรัน Playbook
1. อ่าน **inventory** เพื่อดูว่ามีเครื่องไหนบ้าง และแต่ละเครื่องอยู่กลุ่มไหน
2. อ่าน **playbook** แล้วจับคู่ hosts กับ tasks
3. **Gather facts** คือรัน module `setup` ไปเก็บข้อมูลเครื่อง (OS, IP, RAM, ...)
4. ในแต่ละ task:
   - แปลง module (Python) ให้เป็นสคริปต์ (AnsiballZ)
   - ส่งผ่าน SSH ไปไว้ใน `~/.ansible/tmp` ของเครื่องปลายทาง (ถ้าเปิด `pipelining` จะส่งทาง stdin แทน)
   - รันสคริปต์นั้น ซึ่งจะส่งผลกลับมาเป็น JSON (`ok` / `changed` / `failed` / `skipped`)
   - ลบไฟล์ชั่วคราวทิ้ง
5. ถ้ามี task ที่ `changed` และผูกกับ **handler** ไว้ handler จะทำงานตอนท้ายของ play (หรือเมื่อสั่ง `meta: flush_handlers`)
6. แสดง **PLAY RECAP** สรุปผล

> ค่าเริ่มต้นจะรันพร้อมกัน 5 เครื่อง (`forks`) และใช้ strategy แบบ `linear` คือทุกเครื่องต้องทำ task ปัจจุบันเสร็จก่อน จึงจะขึ้น task ถัดไป
> ถ้าใส่ `serial` จะแบ่งเครื่องเป็น batch (ใช้ทำ rolling update ใน lab08 และ lab09)

## 5. องค์ประกอบหลัก
| องค์ประกอบ | คำอธิบาย | Lab |
|---|---|---|
| Inventory | รายชื่อเครื่องและกลุ่ม (INI/YAML/dynamic) | 01, 16 |
| Module | หน่วยการทำงาน เช่น `apt`, `copy`, `service`, `win_updates` | 01, 02 |
| Task / Play / Playbook | การเรียก module, ชุด task ต่อกลุ่มเครื่อง, ไฟล์ YAML | 02 |
| Variables / Facts | ตัวแปรที่เรากำหนด และข้อมูลที่เก็บจากเครื่อง | 03, 12 |
| Template | Jinja2 สำหรับสร้างไฟล์ config | 04 |
| Handler | task ที่รันเฉพาะเมื่อมีการ notify | 04, 05 |
| Role | โครงสร้างสำหรับนำโค้ดกลับมาใช้ซ้ำ | 05 |
| Collection | แพ็กเกจรวม module/role/plugin (Galaxy) | ทุก lab |
| Vault | เข้ารหัสข้อมูลลับ | 06 |
| block / rescue / always | จัดการ error และ rollback | 04, 10, 14 |
| `serial`, `delegate_to` | rolling update และสั่งงานบนเครื่องอื่น | 08, 09 |
| AWX / AAP | Web UI, RBAC, schedule, API | (ต่อยอด) |

## 6. Variable precedence (ย่อ จากต่ำไปสูง)
```
role defaults → inventory group_vars/all → group_vars/<group> → host_vars/<host>
→ play vars → include_vars → set_fact / register → extra vars (-e)
```

## 7. ตัวอย่างสั้น
```yaml
- name: Setup web servers
  hosts: web
  become: true
  vars:
    http_port: 8080
  tasks:
    - name: Install nginx
      ansible.builtin.apt:
        name: nginx
        state: present
        update_cache: true
    - name: Deploy nginx config
      ansible.builtin.template:
        src: templates/nginx.conf.j2
        dest: /etc/nginx/sites-available/default
      notify: Restart nginx
  handlers:
    - name: Restart nginx
      ansible.builtin.service:
        name: nginx
        state: restarted
```
```bash
ansible-playbook -i inventory.ini site.yml --check --diff   # dry run
ansible-playbook -i inventory.ini site.yml                  # รันจริง (รอบสองต้องได้ changed=0)
```

## 8. บทเรียนจากการทำ labs จริงใน repo นี้
- notify ทำงานเฉพาะเมื่อ task ขึ้น `changed` ดังนั้น handler ที่เป็น validate (`changed_when: false`) จะ notify ต่อไม่ได้ ต้องใช้ `listen` แทน (lab05)
- ถ้า task fail หลังจาก notify ไปแล้ว handler จะไม่ทำงาน ให้ใช้ `force_handlers: true` (lab05)
- ค่าจาก `-e` เป็น string เสมอ ต้อง `| int` ก่อนเปรียบเทียบ (lab12, lab13)
- `validate:` ใน `template`/`copy` ตรวจไฟล์ก่อนเขียนทับไฟล์จริง (sshd, haproxy, sudoers) (lab05, lab06, lab07)
