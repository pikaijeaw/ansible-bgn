# BigFix Lab 15: REST API Automation

**สถานการณ์จริง:** ต้องการเชื่อม BigFix กับระบบอื่น เช่น ServiceNow (เปิด ticket แล้วสั่ง deploy), Ansible/AWX, SIEM
หรือเก็บ content ไว้ใน Git แล้ว import อัตโนมัติ (content as code)

## เครื่องมือใน repo
| ไฟล์ | หน้าที่ |
|---|---|
| [`bigfix/api/bigfix_api.py`](../../api/bigfix_api.py) | CLI ภาษา Python (stdlib) เรียก login, query, computers, import, deploy, status |
| [`bigfix/scripts/validate_bes.py`](../../scripts/validate_bes.py) | ตรวจไฟล์ `.bes` ก่อน import (ใช้ใน CI) |
| [`ansible/lab-env/bigfix-mock`](../../../ansible/lab-env/bigfix-mock/) | BigFix API จำลองไว้ฝึกโดยไม่ต้องมี server |
| [`ansible/labs/lab16-bigfix-integration`](../../../ansible/labs/lab16-bigfix-integration/) | ทำงานแบบเดียวกันด้วย Ansible |

## ฝึกกับ mock
```bash
cd ansible/lab-env && docker compose up -d bigfix-mock      # หรือ: python3 bigfix-mock/bigfix_mock.py
cd ../../bigfix/api
export BIGFIX_URL=http://localhost:52311

python3 bigfix_api.py login
python3 bigfix_api.py query "number of bes computers"
python3 bigfix_api.py query "(name of it, last report time of it as string) of bes computers whose (last report time of it < now - 7 * day)" --csv
python3 bigfix_api.py import ../labs/*/*.bes --site Lab-Automation
python3 bigfix_api.py deploy --site "Patches for Windows" --fixlet 501 --computers WIN-APP01
python3 bigfix_api.py status 9001
```
ผลจากการทดสอบ:
```
WIN-APP02,"Sat, 17 Oct 2026 ..."
LAPTOP-HR-07,"Tue, 29 Sep 2026 ..."
ComputerGroup  20030    ../labs/lab04-computer-groups/group-linux.bes
Task           20031    ../labs/lab05-software-deploy-windows/install-7zip.bes
WIN-APP01            Fixed
```

## ใช้กับ server จริง
```bash
export BIGFIX_URL=https://bigfix.example.com:52311 BIGFIX_USER=api-operator
read -s BIGFIX_PASSWORD && export BIGFIX_PASSWORD
python3 bigfix_api.py login            # ถ้า server ใช้ self-signed cert ให้เพิ่ม --insecure (lab เท่านั้น)
```

## curl ล้วน
```bash
curl -k -u "$BIGFIX_USER:$BIGFIX_PASSWORD" -G "$BIGFIX_URL/api/query" \
     --data-urlencode "relevance=names of bes computers" --data-urlencode "output=json"

curl -k -u "$BIGFIX_USER:$BIGFIX_PASSWORD" -X POST -H "Content-Type: application/xml" \
     --data-binary @../labs/lab05-software-deploy-windows/install-7zip.bes \
     "$BIGFIX_URL/api/tasks/custom/Lab-Automation"
```

## แบบฝึกหัด
1. เขียน script ที่ import เฉพาะไฟล์ที่เปลี่ยนใน commit ล่าสุด (`git diff --name-only HEAD~1 -- '*.bes'`)
2. ทำ webhook จาก ServiceNow → script → `deploy` → อัปเดต ticket ด้วยผล `status`
3. เพิ่มคำสั่ง `delete` (`DELETE /api/fixlet/custom/<site>/<id>`) ใน `bigfix_api.py`
