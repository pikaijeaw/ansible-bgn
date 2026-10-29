# Lab 16: Ansible ร่วมกับ BigFix (ผ่าน BigFix REST API)

**สถานการณ์จริง:** องค์กรใช้ BigFix ดูแล patch/compliance ของ endpoint หลายพันเครื่อง และใช้ Ansible/AWX ทำ automation ฝั่ง server
ต้องการให้ทั้งสองระบบคุยกันได้ เช่น
- ให้ AWX ดึงรายงาน patch ที่ค้างจาก BigFix ไปแสดงหรือส่งต่อ
- ให้ทีม app กดปุ่มใน AWX เพื่อสั่ง BigFix deploy patch ให้เครื่องของตัวเอง (self-service)
- เก็บ Fixlet ไว้ใน Git แล้ว import อัตโนมัติ (content as code)
- ใช้รายชื่อเครื่องใน BigFix สร้าง Ansible inventory

> lab ใช้ **BigFix API จำลอง** (`lab-env/bigfix-mock/bigfix_mock.py`) ที่ให้ request/response รูปแบบเดียวกับของจริงใน endpoint ที่ใช้
> ถ้ามี BigFix จริง ให้ตั้ง `BIGFIX_URL=https://bigfix.example.com:52311` และใส่รหัสผ่านไว้ใน vault (`vault_bigfix_password`)

## BigFix REST API ที่ใช้
| Method | Endpoint | ใช้ทำ |
|---|---|---|
| GET | `/api/login` | ทดสอบ credential |
| GET | `/api/query?relevance=...&output=json` | ถามด้วย **Session Relevance** |
| GET | `/api/computers` | รายชื่อเครื่อง |
| POST | `/api/actions` | สร้าง action (body เป็น BES XML) |
| GET | `/api/action/{id}/status` | ดูผล action ทีละเครื่อง |
| POST | `/api/fixlets/custom/{site}` | import Fixlet/Task/Analysis เข้า custom site |

## ขั้นตอน
```bash
cd /work/ansible

# 1) ถามข้อมูล: inventory + เครื่องที่ไม่รายงานเกิน 7 วัน
ansible-playbook labs/lab16-bigfix-integration/query.yml

# 2) ดูช่องว่างของ patch แล้วสั่ง deploy fixlet 701 ให้เครื่องที่ relevant ทั้งหมด (ช่วง 22:00-05:00)
ansible-playbook labs/lab16-bigfix-integration/patch-compliance.yml
ansible-playbook labs/lab16-bigfix-integration/patch-compliance.yml \
  -e deploy_fixlet_id=701 -e "deploy_site='Patches for Ubuntu 2404'"

# 3) import ไฟล์ .bes ทั้งหมดใน bigfix/labs/ เข้า custom site
ansible-playbook labs/lab16-bigfix-integration/import-content.yml

# 4) สร้าง Ansible inventory จาก BigFix
ansible-playbook labs/lab16-bigfix-integration/bigfix-to-inventory.yml
```

ผลจากการทดสอบกับ mock:
```
STALE: ['WIN-APP02', 'LAPTOP-HR-07']
701 | Patches for Ubuntu 2404 | USN-7089-1 - Linux kernel vulnerabilities - Ubuntu 24.04 | 2
Action 9001 on ['web01', 'web02']: [('web01', 'Fixed'), ('web02', 'Fixed')]
```

## ลองด้วย curl
```bash
curl -s -u admin:'BigFix123!' "http://bigfix-mock:52311/api/query?output=json" \
  --data-urlencode "relevance=names of bes computers" -G | jq
docker logs bigfix-mock      # ดู action ที่ถูกสร้าง
```
ดู script Python ที่ใช้กับ BigFix จริงได้ที่ [`bigfix/api/`](../../../bigfix/api/)

## ข้อควรระวังกับ BigFix จริง
- ใช้ operator ที่สร้างไว้สำหรับ API โดยเฉพาะ ให้สิทธิ์เฉพาะ site และกลุ่มเครื่องที่จำเป็น
- Session relevance ที่หนักจะกิน CPU ของ root server ให้ใส่ `whose` กรองให้แคบที่สุด และไม่ยิงถี่ๆ
- action ที่สร้างผ่าน API จะเห็นใน Console เหมือนสร้างเอง ให้ตั้ง Title ที่บอกได้ว่ามาจาก automation

## แบบฝึกหัด
1. เพิ่ม relevance ใน mock (`QUERIES` ใน `bigfix_mock.py`) แล้วเขียน playbook ใช้งาน
2. ใน AWX ทำ Survey ให้เลือก fixlet ID จาก list ที่ได้จาก `patch-compliance.yml`
3. เขียน GitHub Actions ที่รัน `import-content.yml` เมื่อมี merge เข้า branch main (ใช้ self-hosted runner ที่เข้าถึง BigFix ได้)
