# BigFix Lab 01: Client Relevance พื้นฐาน (ฝึกด้วย Fixlet Debugger / QnA)

**ทำไมสำคัญ:** ทุกอย่างใน BigFix ไม่ว่าจะเป็น Fixlet, Task, Analysis หรือ Computer Group ล้วนขับเคลื่อนด้วย Relevance
ถ้าเขียน relevance ได้ ก็เขียน content ของ BigFix ได้แทบทั้งหมด

## เครื่องมือ
- **Fixlet Debugger** (`FixletDebugger.exe`): อยู่ใน BigFix Console / Client Deploy Tool (Windows) เลือกโหมด *Local Client Evaluator* แล้วพิมพ์ `Q: ...`
- **QnA** (Linux/macOS): `/opt/BESClient/bin/qna` แล้วพิมพ์ relevance ทีละบรรทัด
- **WebUI Query** หรือ Console → *Query* (BigFix 10+): ยิง relevance ไปที่เครื่องจริงแล้วดูผลแบบ real-time

## รูปแบบภาษา
```
<property> of <object>               name of operating system
<plural> whose (<filter>) of <obj>   files whose (size of it > 1000000) of folder "C:\Temp"
it                                   ตัวที่กำลังพิจารณาอยู่ใน whose
exists / not exists                  ตรวจว่ามีหรือไม่มี (ไม่ error ถ้าไม่มี)
as string / as integer / as version  แปลงชนิดข้อมูล
number of <plural>                   นับจำนวน
"%22"                                ใส่เครื่องหมาย " ใน string (relevance ไม่ใช้ backslash escape)
```
> **Singular กับ Plural:** `file "x"` (singular) ถ้าไม่มีจะ error แต่ `files "x"` (plural) ถ้าไม่มีจะได้ผลว่าง
> Fixlet ที่ relevance error จะถูกมองว่า **ไม่ relevant**

## แบบฝึกหัด 1: ข้อมูลเครื่อง (ทำได้ทั้ง Windows และ Linux)
```
Q: computer name
Q: name of operating system
Q: version of operating system
Q: (name of it, version of it) of operating system
Q: size of ram
Q: number of processors
Q: uptime of operating system
Q: now
Q: version of client
Q: addresses of ip interfaces whose (not loopback of it) of network
```

## แบบฝึกหัด 2: ไฟล์และโฟลเดอร์
```
// Windows
Q: exists file "C:\Windows\System32\notepad.exe"
Q: version of file "C:\Windows\System32\notepad.exe"
Q: (name of it, size of it) of files of folder "C:\Windows\Temp"
Q: number of files whose (modification time of it < now - 7 * day) of folder "C:\Windows\Temp"
Q: free space of drive "C:" / (1024 * 1024 * 1024)

// Linux
Q: exists file "/etc/redhat-release"
Q: lines of file "/etc/os-release"
Q: lines whose (it starts with "PRETTY_NAME=") of file "/etc/os-release"
Q: following text of first "=" of lines whose (it starts with "VERSION_ID=") of file "/etc/os-release"
Q: free space of filesystem "/" / (1024 * 1024 * 1024)
```

## แบบฝึกหัด 3: Registry และโปรแกรมที่ติดตั้ง (Windows)
```
Q: value "ProductName" of key "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion" of native registry
Q: value "SMB1" of key "HKLM\SYSTEM\CurrentControlSet\Services\LanmanServer\Parameters" of native registry
Q: exists regapp "notepad++.exe"
Q: version of regapp "chrome.exe"

// รายชื่อโปรแกรมจาก Uninstall key (ทั้ง 64 และ 32 bit)
Q: values "DisplayName" of keys of keys "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall" of (x64 registries; x32 registries)

// มี 7-Zip เวอร์ชัน >= 24.08 หรือยัง
Q: exists keys whose (exists value "DisplayName" whose (it as string as lowercase starts with "7-zip") of it AND exists value "DisplayVersion" whose (it as string as version >= "24.08" as version) of it) of keys "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall" of (x64 registries; x32 registries)
```

## แบบฝึกหัด 4: Services, WMI, Users
```
Q: (service name of it, state of it, start type of it) of services whose (start type of it = "Automatic" AND state of it != "Running")
Q: state of service "W32Time"
Q: string values of selects "SerialNumber from Win32_BIOS" of wmi
Q: string values of selects "Model from Win32_ComputerSystem" of wmi
Q: names of members of local group "Administrators"
Q: product type of operating system = workstation product type
Q: pending restart
```

## แบบฝึกหัด 5: เขียน relevance ให้ Fixlet (โจทย์)
เขียนเองก่อนแล้วค่อยเปิดเฉลย
1. เครื่อง Windows ที่ไดรฟ์ C เหลือพื้นที่น้อยกว่า 10 GB
2. เครื่อง Linux ตระกูล RHEL ที่ยังไม่มี `/usr/sbin/httpd`
3. Windows ที่ยังเปิด SMBv1 อยู่ (ค่า SMB1 ไม่ใช่ 0 หรือไม่มีค่า)
4. เครื่องที่มีไฟล์ใน `C:\Windows\Temp` เกิน 1000 ไฟล์
5. เครื่องที่ client setting `Environment` เป็น `Production`

<details><summary>เฉลย</summary>

```
1. windows of operating system AND free space of drive of system folder < 10 * 1024 * 1024 * 1024
2. exists file "/etc/redhat-release" AND not exists file "/usr/sbin/httpd"
3. windows of operating system AND not exists value "SMB1" whose (it as integer = 0) of key "HKLM\SYSTEM\CurrentControlSet\Services\LanmanServer\Parameters" of native registry
4. number of files of folder "C:\Windows\Temp" > 1000
5. exists setting "Environment" whose (value of it = "Production") of client
```
ดูของจริงที่ใช้ข้อเหล่านี้ได้ใน lab05, lab07, lab09, lab11 และ lab14
</details>

## ข้อควรระวัง (performance)
- relevance ถูกประเมินบนทุกเครื่องเป็นรอบๆ ห้ามวนอ่านทั้ง disk เช่น `descendants of folder "C:\"`
- ใส่เงื่อนไขที่ถูกและเร็วไว้ก่อน (เช่น `windows of operating system`) เพราะ BigFix หยุดประเมินทันทีเมื่อ relevance ข้อแรกเป็น false
- ใช้ `native registry` หรือ `x64 registries` บน Windows 64-bit มิฉะนั้นจะเห็นแค่ฝั่ง WOW6432Node
