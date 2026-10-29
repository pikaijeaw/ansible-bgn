# Lab 15: จัดการ Windows Server ด้วย Ansible

**สถานการณ์จริง:** องค์กรส่วนใหญ่มีทั้ง Linux และ Windows ส่วน Windows นิยมจัดการด้วย WinRM
(Windows Server 2019 ขึ้นไปใช้ OpenSSH ได้ด้วย)

> **Lab นี้รันใน docker lab ไม่ได้** ต้องมี Windows VM จริง เช่น VirtualBox/Hyper-V
> (ใช้ Windows Server Evaluation 180 วัน ดาวน์โหลดฟรีจาก Microsoft Evaluation Center)
> playbook ทุกไฟล์ผ่าน `ansible-playbook --syntax-check` แล้ว

## เตรียมฝั่ง Windows (PowerShell แบบ Administrator)
```powershell
# เปิด WinRM over HTTPS แบบ self-signed (สำหรับ lab)
Enable-PSRemoting -Force
$cert = New-SelfSignedCertificate -DnsName $env:COMPUTERNAME -CertStoreLocation Cert:\LocalMachine\My
New-Item -Path WSMan:\localhost\Listener -Transport HTTPS -Address * -CertificateThumbPrint $cert.Thumbprint -Force
New-NetFirewallRule -DisplayName "WinRM HTTPS" -Direction Inbound -LocalPort 5986 -Protocol TCP -Action Allow
```

## เตรียมฝั่ง control node
```bash
pip install pywinrm              # มีอยู่แล้วใน control container
ansible-vault create labs/lab15-windows/inventory/group_vars/vault.yml   # ใส่ vault_win_admin_password: ...
```

## ขั้นตอน
```bash
cd /work/ansible
ansible -i labs/lab15-windows/inventory windows -m ansible.windows.win_ping --ask-vault-pass
ansible-playbook -i labs/lab15-windows/inventory labs/lab15-windows/baseline.yml --ask-vault-pass
ansible-playbook -i labs/lab15-windows/inventory labs/lab15-windows/patch.yml --ask-vault-pass
```

## Module ที่ใช้บ่อย (Linux → Windows)
| Linux | Windows |
|---|---|
| `ping` | `ansible.windows.win_ping` |
| `command` / `shell` | `ansible.windows.win_command` / `win_shell` (PowerShell) |
| `copy` / `template` | `ansible.windows.win_copy` / `win_template` |
| `package` | `ansible.windows.win_package` (MSI/EXE), `chocolatey.chocolatey.win_chocolatey` |
| `service` | `ansible.windows.win_service` |
| `user` / `group` | `ansible.windows.win_user` / `win_group_membership` |
| `lineinfile` สำหรับ config | `ansible.windows.win_regedit` (registry) |
| `apt` / `dnf` upgrade | `ansible.windows.win_updates` |
| `reboot` | `ansible.windows.win_reboot` |

## แบบฝึกหัด
1. ติดตั้ง MSI จาก file share ด้วย `win_package` (ระบุ `product_id` เพื่อให้ idempotent)
2. Join domain ด้วย `microsoft.ad.membership`
3. ติดตั้ง BigFix Agent บน Windows ด้วย `win_package` (`BigFix-BES-Client-*.exe /S /v/qn`) พร้อมวาง `masthead.afxm`
