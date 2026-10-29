# BigFix Lab 10: Patch Management (กระบวนการรายเดือน)

**นี่คืองานหลักที่องค์กรส่วนใหญ่ซื้อ BigFix มาใช้** HCL จะปล่อย Fixlet ของ patch ทุกตัวผ่าน External Site
(Patches for Windows, Patches for RHEL, Patches for Ubuntu, Updates for Windows Applications ฯลฯ)
เราไม่ต้องเขียน Fixlet ของ patch เอง แต่ต้องออกแบบกระบวนการให้ดี

## Content ใน lab นี้
| ไฟล์ | ใช้ทำอะไรในกระบวนการ |
|---|---|
| `pre-patch-health-check.bes` | component แรกของ Baseline: ต้องมี disk ≥ 10 GB และไม่มี restart ค้าง |
| `restart-if-pending.bes` | หลัง patch ให้ reboot เฉพาะเครื่องที่ต้อง reboot ใน maintenance window |

## กระบวนการ Patch Tuesday ที่ใช้จริง
```
สัปดาห์ที่ 1 (Patch Tuesday +1 วัน)
  1. Console → Patches for Windows → filter: Source Release Date = เดือนนี้, Severity = Critical/Important
  2. สร้าง Baseline "2026-11 Windows Server Patches"
       component 1: Lab - Pre-patch check (pre-patch-health-check.bes)
       component 2..n: patch ของเดือน (Cumulative Update, .NET, Servicing Stack)
       component สุดท้าย: Lab - Restart computers with a pending restart
  3. Deploy ให้ group "Pilot" (IT เอง + เครื่อง test)
สัปดาห์ที่ 2
  4. ตรวจผล Pilot: Action Status = Fixed? แอปสำคัญยังทำงานได้?
  5. Deploy ให้ Workstations ทั้งหมด (Offer/Restart ให้ user เลื่อนได้)
สัปดาห์ที่ 3
  6. Deploy ให้ Servers แยกตาม Maintenance Window ของแต่ละระบบ (เช่น เสาร์ 22:00-02:00)
       Take Action → Execution → Constraints: Run between 22:00 and 02:00 (client local time)
สัปดาห์ที่ 4
  7. รายงาน compliance (Web Reports / BigFix Insights) แล้วตามเก็บเครื่องที่ fail หรือเครื่องที่ offline
```

## Baseline settings ที่สำคัญ
- **Baseline relevance**: ใช้ relevance ของ component เพื่อไม่ให้ทำงานบนเครื่องที่ไม่ต้องลง
- ✔ *Stop on failure* หาก pre-check ไม่ผ่าน (ไม่ลง patch ให้เครื่องที่ disk เต็ม)
- **Restart**: ตั้งใน Post-Action ของ baseline ครั้งเดียว ไม่ใช่ในทุก component

## ทดสอบ relevance ของ restart pending
```
Q: pending restart
Q: exists key "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate\Auto Update\RebootRequired" of native registry
```

## เปรียบเทียบกับ Ansible lab08 / lab15
| | BigFix | Ansible |
|---|---|---|
| Patch content | HCL ปล่อยให้พร้อม relevance (รู้เองว่าเครื่องไหนต้องลงตัวไหน) | ใช้ package manager / `win_updates` |
| เครื่องที่อยู่นอก network (WFH) | ได้ผ่าน internet relay | ต้องเข้าถึง SSH/WinRM ได้ |
| Rolling ต่อระบบ + ถอดออกจาก LB | ทำได้ยาก | ทำได้ดีมาก (`serial`, `delegate_to`) |
| แนวทางที่นิยม | endpoint และ Windows server ทั่วไป | cluster/app server ที่ต้องคุมลำดับ |

## แบบฝึกหัด
1. สร้าง Baseline ตามขั้นตอนข้างบนบน lab ของคุณ (ใช้ evaluation license)
2. เขียน session relevance หา % compliance ของ baseline เดือนนี้ (ดู lab02)
3. ใช้ Ansible lab16 ดึงรายการ patch ค้างผ่าน REST API มาทำรายงาน
