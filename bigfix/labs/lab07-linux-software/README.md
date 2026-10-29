# BigFix Lab 07: Software บน Linux

| ไฟล์ | ตัวอย่างของ |
|---|---|
| `install-httpd-rhel.bes` | ActionScript ปกติ + `wait /bin/sh -c "..."` บน RHEL/Rocky |
| `ensure-nginx-ubuntu-sh.bes` | Action แบบ **`application/x-sh`** เขียน bash ตรงๆ (BigFix 9.5+) บน Ubuntu |

## ขั้นตอน
1. ติดตั้ง BigFix agent บน Linux:
   ```bash
   # ดาวน์โหลด BESAgent-<ver>.x86_64.rpm/.deb จาก HCL ให้ตรงกับ distro
   sudo mkdir -p /etc/opt/BESClient
   sudo cp masthead.afxm /etc/opt/BESClient/actionsite.afxm      # ได้จาก server: http://<server>:52311/masthead/masthead.afxm
   sudo rpm -ivh BESAgent-*.rpm    # หรือ sudo dpkg -i BESAgent-*.deb
   sudo systemctl enable --now besclient
   ```
2. Import ไฟล์ `.bes` แล้ว Take Action ให้เครื่อง Linux (group จาก lab04)
3. ตรวจผลที่เครื่อง: `systemctl status httpd` / `curl localhost`
4. ดู log ของ agent: `/var/opt/BESClient/__BESData/__Global/Logs/<date>.log`

## ทดสอบ relevance บนเครื่องด้วย QnA
```bash
sudo /opt/BESClient/bin/qna
Q: exists file "/etc/os-release" whose (exists lines whose (it = "ID=ubuntu") of it)
Q: exists file "/usr/sbin/nginx"
```

## แบบฝึกหัด
1. เพิ่ม relevance ให้ Task httpd ทำงานเฉพาะเครื่องที่ client setting `Role=web`
2. เปรียบเทียบกับ Ansible lab04 ที่ติดตั้ง nginx: BigFix เหมาะกับการบังคับใช้ต่อเนื่อง (policy) ส่วน Ansible เหมาะกับการ deploy ที่มีลำดับขั้นตอน
