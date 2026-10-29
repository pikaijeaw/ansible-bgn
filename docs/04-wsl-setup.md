# ตั้ง Lab บน Windows ด้วย WSL2

คู่มือนี้ใช้รัน Ansible lab (Docker) บนเครื่อง Windows 10/11 ผ่าน WSL2
lab ถูกทดสอบบน Linux (Ubuntu 24.04 + Docker Engine) ส่วนบน WSL2 ยังไม่ได้ทดสอบ แต่ใช้ Docker และ Ubuntu ชุดเดียวกัน
ถ้าเจอปัญหาที่ไม่มีในตารางด้านล่าง ให้เปิด issue พร้อม error ได้เลย

## ทำอะไรใน WSL ได้บ้าง
| ส่วน | ใน WSL |
|---|---|
| Ansible lab 01–14, 16, 17 | ✅ ได้ทั้งหมด |
| Ansible lab 15 (Windows) | ⚠️ ต้องมี Windows VM แยก (Hyper-V/VirtualBox) อย่าใช้ Windows ตัวเครื่องตัวเอง เพราะ playbook แก้ registry และลง Windows Update จริง |
| BigFix: ไฟล์ `.bes`, `validate_bes.py`, `bigfix_api.py`, BigFix API จำลอง | ✅ ได้ |
| BigFix server และ agent จริง | ❌ server ต้องลงบน Windows Server ต้องสร้าง VM แยก (ดู [bigfix/README.md](../bigfix/README.md)) |

## สิ่งที่ต้องมี
- Windows 10 (22H2) หรือ Windows 11 ที่เปิด virtualization ใน BIOS แล้ว
- RAM ว่างประมาณ 4 GB และ disk ว่างประมาณ 10 GB
- WSL **เวอร์ชัน 2** (WSL1 ใช้ Docker ไม่ได้)

## ขั้นที่ 1: ติดตั้ง WSL2 + Ubuntu
เปิด **PowerShell แบบ Administrator**:
```powershell
wsl --install -d Ubuntu-24.04
```
restart เครื่อง แล้วเปิด Ubuntu จาก Start menu เพื่อตั้ง username/password

ตรวจว่าเป็น WSL2 (คอลัมน์ VERSION ต้องเป็น 2):
```powershell
wsl -l -v
```
ถ้ายังเป็น 1:
```powershell
wsl --set-version Ubuntu-24.04 2
```
อัปเดต WSL ให้เป็นเวอร์ชันล่าสุด (ช่วยเรื่อง systemd และ cgroup v2):
```powershell
wsl --update
```

## ขั้นที่ 2: ติดตั้ง Docker (เลือกทางใดทางหนึ่ง)

### ทาง A: Docker Desktop (ง่ายที่สุด)
1. ติดตั้ง Docker Desktop for Windows แล้วเลือก *Use WSL 2 based engine*
2. Settings → **Resources → WSL Integration** → เปิดสวิตช์ให้ `Ubuntu-24.04`
3. ใน Ubuntu ตรวจว่าใช้งานได้:
   ```bash
   docker version
   ```
   ```bash
   docker compose version
   ```

### ทาง B: Docker Engine ติดตั้งใน WSL เอง (ไม่ต้องใช้ Docker Desktop)
1. เปิด systemd ของ WSL โดยใส่ใน `/etc/wsl.conf`:
   ```bash
   sudo tee /etc/wsl.conf <<'EOF'
   [boot]
   systemd=true
   EOF
   ```
2. ใน PowerShell รัน `wsl --shutdown` แล้วเปิด Ubuntu ใหม่
3. ติดตั้ง Docker Engine ตามคู่มือ "Install Docker Engine on Ubuntu" ของ Docker (apt repository)
4. ให้ user ของเราใช้ docker ได้โดยไม่ต้อง sudo:
   ```bash
   sudo usermod -aG docker $USER
   ```
   แล้วปิดและเปิด terminal ใหม่

## ขั้นที่ 3: Clone repo ไว้ใน home ของ WSL (สำคัญมาก)
```bash
cd ~
```
```bash
git clone https://github.com/pikaijeaw/ansible-bgn.git
```
> **ห้าม clone ไว้ใต้ `/mnt/c/...`** (ไดรฟ์ C ของ Windows) เพราะ
> 1. ไฟล์บน `/mnt/c` มีสิทธิ์ 777 Ansible จะ **ไม่อ่าน `ansible.cfg`** ในโฟลเดอร์ที่ใครก็เขียนได้ ทำให้ inventory, user และ SSH key ไม่ถูกโหลด
> 2. SSH key ตั้งสิทธิ์ 600 ไม่ได้
> 3. ช้ากว่าระบบไฟล์ของ WSL หลายเท่า
>
> ถ้าอยากแก้ไฟล์ด้วย VS Code ให้ติดตั้งส่วนขยาย **WSL** แล้วรัน `code .` จากใน Ubuntu

## ขั้นที่ 4: เริ่ม lab
```bash
cd ~/ansible-bgn/ansible/lab-env
```
```bash
./setup.sh
```
ครั้งแรกจะใช้เวลาหลายนาทีเพราะต้อง build image จากนั้นเข้า control node:
```bash
docker compose exec control bash
```
```bash
ansible all -m ping
```
ถ้าทุกเครื่องตอบ `pong` ถือว่าพร้อมแล้ว ทำต่อตาม [ansible/README.md](../ansible/README.md)

เปิดจาก browser บน Windows ได้เลย (WSL ส่งต่อ localhost ให้อัตโนมัติ):
- `http://localhost:8080`: เว็บผ่าน HAProxy (หลังรัน lab05)
- `http://localhost:8404`: หน้า stats ของ HAProxy
- `http://localhost:52311/api/login`: BigFix API จำลอง (user `admin` / `BigFix123!`)

หยุด lab: `docker compose stop` · เริ่มต่อ: `docker compose start` · ลบทิ้ง: `./teardown.sh`

## (ทางเลือก) จำกัด RAM/CPU ที่ WSL ใช้
สร้างไฟล์ `%UserProfile%\.wslconfig` บน Windows:
```ini
[wsl2]
memory=6GB
processors=4
```
แล้วรัน `wsl --shutdown`

## ปัญหาที่อาจเจอและวิธีแก้

### ติดตั้งและเริ่ม lab
| อาการ | สาเหตุ | วิธีแก้ |
|---|---|---|
| `wsl --install` ขึ้น error 0x80370102 | ยังไม่เปิด virtualization | เปิด Intel VT-x / AMD-V ใน BIOS และเปิด feature *Virtual Machine Platform* |
| `Cannot connect to the Docker daemon` | Docker ยังไม่รัน หรือยังไม่เปิด WSL Integration | เปิด Docker Desktop และเปิด WSL Integration ให้ Ubuntu (ทาง B: `sudo systemctl start docker`) |
| `permission denied while trying to connect to the Docker daemon socket` | user ไม่อยู่ในกลุ่ม docker | `sudo usermod -aG docker $USER` แล้วเปิด terminal ใหม่ |
| `/bin/bash^M: bad interpreter` หรือ `$'\r': command not found` | ไฟล์ถูกแปลงเป็น CRLF (มักเกิดเมื่อ clone ด้วย Git for Windows) | clone ใหม่ด้วย git **ใน WSL** (repo มี `.gitattributes` บังคับ LF ไว้แล้ว) หรือรัน `git config --global core.autocrlf input` แล้ว clone ใหม่ |
| `./setup.sh: Permission denied` | ไฟล์ไม่มีสิทธิ์ execute (มักเกิดเมื่อ copy ไฟล์มาจาก Windows) | `chmod +x setup.sh teardown.sh` |
| `Bind for 0.0.0.0:8080 failed: port is already allocated` | port ชนกับโปรแกรมอื่น | แก้ `ports:` ใน `docker-compose.yml` เช่น `"18080:80"` |

### เครื่องใน lab (container)
| อาการ | สาเหตุ | วิธีแก้ |
|---|---|---|
| container `web01`/`db01` ขึ้นแล้วดับทันที หรือ `docker logs web01` มีข้อความเรื่อง cgroup | WSL/Docker เวอร์ชันเก่ายังใช้ cgroup v1 | `wsl --update`, อัปเดต Docker Desktop แล้ว `wsl --shutdown` ตรวจด้วย `stat -fc %T /sys/fs/cgroup` ซึ่งต้องได้ `cgroup2fs` |
| `ansible all -m ping` ขึ้น `UNREACHABLE` | ssh ใน container ยังไม่พร้อม หรือ build ไม่ครบ | รอ 10–20 วินาทีแล้วลองใหม่ ถ้ายังไม่ได้ให้รัน `docker compose ps` และ `docker logs web01` |
| ขึ้น `[WARNING]: Ansible is being run in a world writable directory ... ignoring it as an ansible.cfg source` | repo อยู่ใต้ `/mnt/c` | ย้ายไป `~/ansible-bgn` (ดูขั้นที่ 3) |
| `apt` ใน lab ขึ้น `Temporary failure resolving 'archive.ubuntu.com'` | DNS ของ WSL/Docker ใช้ไม่ได้ (มักเกิดตอนต่อ VPN บริษัท) | ปิด VPN แล้วลองใหม่ หรือตั้ง DNS ให้ Docker: Docker Desktop → Settings → Docker Engine → เพิ่ม `"dns": ["8.8.8.8", "1.1.1.1"]` (ทาง B: ใส่ใน `/etc/docker/daemon.json` แล้ว `sudo systemctl restart docker`) |
| `apt` ขึ้น `Release file ... is not valid yet` | นาฬิกาของ WSL เพี้ยน (มักเกิดหลังเครื่อง sleep/hibernate) | ใน PowerShell รัน `wsl --shutdown` แล้วเปิดใหม่ หรือใน Ubuntu รัน `sudo hwclock -s` |
| `pip`/`apt` ขึ้น SSL error หลัง proxy บริษัท | proxy ดักและเปลี่ยน certificate | ให้ฝ่าย IT ให้ CA certificate ของ proxy แล้วเพิ่มลงใน Dockerfile (`COPY` ไปที่ `/usr/local/share/ca-certificates/` แล้ว `update-ca-certificates`) |
| Lab 08 reboot แล้ว Ansible รอจน timeout | container ไม่ได้ start กลับ | ตรวจว่า `docker-compose.yml` มี `restart: unless-stopped` (มีอยู่แล้ว) และ `docker compose ps` แสดงว่าเครื่องกลับมา `Up` |

### ทรัพยากรเครื่อง
| อาการ | วิธีแก้ |
|---|---|
| เครื่อง Windows ช้า / `vmmem` กิน RAM มาก | จำกัดด้วย `.wslconfig` และหยุด lab ด้วย `docker compose stop` เมื่อไม่ใช้ |
| ไดรฟ์ C เต็ม (ไฟล์ `ext4.vhdx` ใหญ่ขึ้นเรื่อยๆ) | `docker system prune -a` เพื่อลบ image ที่ไม่ใช้ แล้ว `wsl --shutdown` (Docker Desktop: Settings → Resources → *Clean / Purge data* หรือเปิด *Resource Saver*) |

## ตรวจสภาพแวดล้อมแบบเร็ว
รันใน Ubuntu ถ้าทุกบรรทัดไม่มี error ก็พร้อมใช้งาน:
```bash
uname -r                              # ต้องมีคำว่า microsoft-standard-WSL2
stat -fc %T /sys/fs/cgroup            # ต้องได้ cgroup2fs
docker info --format '{{.CgroupVersion}}'   # ต้องได้ 2
docker compose version
pwd                                   # ต้องอยู่ใต้ /home/... ไม่ใช่ /mnt/c/...
```
