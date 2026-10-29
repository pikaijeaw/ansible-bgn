# Lab 03: Variables, Facts, Conditionals, Loops

**สถานการณ์จริง:** องค์กรมีทั้ง Ubuntu และ RHEL ชื่อ package กับชื่อ service ต่างกัน
เช่น `dnsutils` กับ `bind-utils` หรือ `cron` กับ `crond`
ก่อนติดตั้งอะไรก็ต้องเช็คก่อนว่าเครื่องมี disk และ RAM พอ

## สิ่งที่จะได้เรียน
| เรื่อง | อยู่ตรงไหนใน `preflight.yml` |
|---|---|
| `include_vars` ตาม OS | `vars/Debian.yml`, `vars/RedHat.yml` |
| Facts (`ansible_facts[...]`) | `os_family`, `memtotal_mb`, `processor_vcpus` |
| Jinja2 filters | `trim`, `regex_replace`, `int`, `upper`, `join` |
| `set_fact` / `register` | `df_root` → `root_free_gb`, `kernel`, `tcp_conns` |
| `assert` | หยุดเครื่องที่ไม่ผ่านเงื่อนไข |
| `when` | ทำงานเฉพาะเมื่อเงื่อนไขเป็นจริง |
| `loop` + `loop_control.label` | สร้างโฟลเดอร์และทำให้ output อ่านง่าย |
| `changed_when: false` | task ที่แค่อ่านค่า ไม่ควรขึ้น changed |

## ขั้นตอน
```bash
cd /work/ansible
ansible-playbook labs/lab03-variables-facts/preflight.yml

# ลองปรับค่าตัวแปรจาก command line (extra vars มี precedence สูงสุด)
ansible-playbook labs/lab03-variables-facts/preflight.yml -e min_memory_mb=999999
# ทุกเครื่องจะ fail ที่ assert เพราะ RAM ไม่ถึง
```

## Variable precedence (จากต่ำไปสูง แบบย่อ)
```
role defaults < inventory group_vars/all < group_vars/<group> < host_vars/<host>
  < play vars < include_vars < set_fact/register < extra vars (-e)
```

## แบบฝึกหัด
1. สร้าง `inventory/host_vars/db01.yml` ที่ตั้ง `min_free_disk_gb: 5` แล้วดูว่าเฉพาะ db01 ใช้ค่านี้
2. เพิ่ม task ที่ fail เมื่อ `ansible_facts['selinux']['status'] == 'enabled'` บน RedHat (ใช้ `ansible.builtin.fail` + `when`)
3. ใช้ `ansible.builtin.debug: var=hostvars['db01']['ansible_facts']['default_ipv4']['address']` จากเครื่อง web
4. ลองคำนวณ free space จาก fact `ansible_facts['mounts']` แทน `df` (ใช้ `selectattr('mount','equalto','/')`) แล้วสังเกตว่าทำไมใน container ถึงหาไม่เจอ แต่บน VM จริงหาเจอ
5. เปลี่ยน loop เป็น dict ด้วย `loop: "{{ my_dict | dict2items }}"`
