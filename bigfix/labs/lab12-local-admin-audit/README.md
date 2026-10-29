# BigFix Lab 12: Local Administrators Audit & Remediation

**สถานการณ์จริง:** auditor ขอรายชื่อคนที่มีสิทธิ์ admin บนเครื่อง และนโยบายกำหนดว่า user ทั่วไปต้องไม่เป็น local admin

| ไฟล์ | ประเภท | หน้าที่ |
|---|---|---|
| `local-administrators.bes` | Analysis | สมาชิกในกลุ่ม Administrators, จำนวน, local users ที่ enabled |
| `remove-unauthorized-admins.bes` | Task (มี parameter) | ลบทุกคนที่ไม่อยู่ใน allow-list ออกจาก Administrators (เฉพาะ workstation) |

## ขั้นตอน
1. Import แล้ว **Activate** Analysis → ดูผลว่าเครื่องไหนมี admin แปลกปลอม
2. ส่งออกเป็น CSV จาก Web Reports แนบเป็นหลักฐาน access review
3. Take Action `remove-unauthorized-admins` → กรอก allow-list เช่น `Administrator,CORP\Domain Admins,CORP\Desktop Support`
   - **ทดสอบกับ Pilot group ก่อนเสมอ** ถ้า allow-list ผิด อาจทำให้ทีม support เข้าเครื่องไม่ได้
4. ตรวจ log ที่ `C:\Windows\Temp\bigfix-admin-cleanup.log`

## จุดที่ควรสังเกต
- `action parameter query` ทำให้ Task เดียวใช้ได้หลายนโยบาย
- `{parameter "Allowed"}` ถูกแทนค่าลงไปใน PowerShell script ตอนรัน
- relevance จำกัดไว้ที่ `workstation product type` กันไม่ให้ไปลบ admin ของ server โดยไม่ตั้งใจ

## แบบฝึกหัด
1. สร้าง Fixlet ที่ relevant เมื่อ `number of members of local group "Administrators" > 2`
2. เปรียบเทียบกับ Ansible lab15: `win_group_membership: state=pure`
