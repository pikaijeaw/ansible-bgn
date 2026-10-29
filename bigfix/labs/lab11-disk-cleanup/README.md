# BigFix Lab 11: Disk Cleanup อัตโนมัติ

**สถานการณ์จริง:** helpdesk ได้ ticket "เครื่องเต็ม ลงโปรแกรมไม่ได้ / Windows Update ไม่ลง" เป็นประจำ
Fixlet นี้จะ relevant เองเมื่อไดรฟ์ระบบเหลือน้อยกว่า 10 GB แล้วล้างไฟล์ที่ปลอดภัยให้

## `cleanup-low-disk-windows.bes` ทำอะไร
1. `createfile` สร้าง PowerShell script จากเนื้อหาใน action (สังเกต `{{` ที่ใช้ escape ปีกกา)
2. ลบไฟล์ใน `C:\Windows\Temp`, `%TEMP%` ของทุก user และ `SoftwareDistribution\Download` ที่เก่ากว่า 7 วัน
3. เทถังขยะ แล้ว `DISM /StartComponentCleanup`
4. เขียน log ว่าคืนพื้นที่ได้กี่ GB ไว้ที่ `C:\Windows\Temp\bigfix-disk-cleanup.log`
5. Success criteria = original relevance: ถ้ายังเหลือ < 10 GB จะขึ้น **Failed** ให้คนตามดูต่อ (เช่น user เก็บไฟล์ใหญ่ไว้)

## ขั้นตอน
1. Import → ตั้ง Policy action (reapply ได้วันละ 1 ครั้ง)
2. ทดสอบบนเครื่อง lab โดยสร้างไฟล์ใหญ่ให้ disk ต่ำกว่า 10 GB:
   ```powershell
   fsutil file createnew C:\Windows\Temp\big.bin 50000000000
   (Get-Item C:\Windows\Temp\big.bin).LastWriteTime = (Get-Date).AddDays(-30)
   ```
3. รอให้ Fixlet relevant แล้ว action ทำงาน → ดู log

## แบบฝึกหัด
1. ปรับ threshold เป็น % แทน GB: `(free space of it * 100 / total space of it) < 10` ของ `drive of system folder`
2. ทำเวอร์ชัน Linux: ล้าง `/var/log/*.gz` เก่าและ `journalctl --vacuum-size=200M` (ดู Ansible lab14)
