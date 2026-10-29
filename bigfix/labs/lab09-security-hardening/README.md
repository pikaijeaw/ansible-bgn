# BigFix Lab 09: Security Hardening (Compliance as Fixlets)

**สถานการณ์จริง:** ผล vulnerability scan / CIS audit ระบุว่าเครื่องยังเปิด SMBv1, TLS 1.0 และให้ root login ผ่าน SSH ได้
ต้องแก้ทั้งองค์กรและพิสูจน์ได้ตลอดเวลาว่ายังแก้อยู่ (ไม่ใช่แก้ครั้งเดียวแล้วจบ)

| ไฟล์ | Control | หมายเหตุ |
|---|---|---|
| `disable-smbv1-server.bes` | SMB1=0 (CIS 18.3.x) | `regset64` + `action requires restart` |
| `disable-tls10-tls11-server.bes` | ปิด TLS 1.0/1.1 ใน SCHANNEL | ทดสอบกับระบบเก่า (SQL 2012, Java เก่า) ก่อน deploy |
| `linux-ssh-disable-root-login.bes` | PermitRootLogin no (CIS 5.2.x) | `createfile` + `install` + `sshd -t` ก่อน reload |

## หลักการ: Fixlet = "ตรวจ + แก้" ในไฟล์เดียว
- **Relevance** = เงื่อนไขที่ "ไม่ผ่าน" ดังนั้นจำนวนเครื่องที่ relevant คือจำนวนเครื่องที่ยัง non-compliant
- **Action** = วิธีแก้
- **Success criteria = Original Relevance**: หลังแก้ agent ประเมินใหม่ ถ้า relevance เป็น false จะขึ้น *Fixed*
- ตั้งเป็น policy action เพื่อแก้ drift อัตโนมัติ (เทียบได้กับรัน Ansible lab07 ตามรอบ)

## ขั้นตอน
1. Import → ดูแท็บ **Applicable Computers** ว่ามีกี่เครื่องที่ยังไม่ผ่าน (ใช้เป็นรายงาน audit ได้ทันที)
2. Take Action กับ Pilot group ก่อน แล้วค่อยขยายไปทั้งองค์กร
3. ตั้ง restart ใน Post-Action ตามนโยบาย (เช่น ให้ผู้ใช้เลื่อนได้ 8 ชั่วโมง)

## ในองค์กรจริง
HCL มี **BigFix Compliance** (SCM) ที่มี checklist CIS/DISA STIG สำเร็จรูปหลายร้อย check พร้อม dashboard
Fixlet ใน lab นี้ช่วยให้เข้าใจว่า checklist เหล่านั้นทำงานอย่างไร และใช้เขียน control ที่ checklist ไม่มี

## แบบฝึกหัด
1. Fixlet ปิด LLMNR: `HKLM\SOFTWARE\Policies\Microsoft\Windows NT\DNSClient` `EnableMulticast=0`
2. Fixlet บังคับ RDP NLA: `...\Terminal Server\WinStations\RDP-Tcp` `UserAuthentication=1`
3. Linux: Fixlet ตั้ง `PASS_MAX_DAYS 90` ใน `/etc/login.defs` (ดูแนวทางจาก Ansible lab07)
