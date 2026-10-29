#!/usr/bin/env bash
# สร้าง SSH key สำหรับ lab แล้ว build + start ทุกเครื่อง
set -euo pipefail
cd "$(dirname "$0")"

if [[ ! -f .ssh/id_ed25519 ]]; then
  mkdir -p .ssh
  if command -v ssh-keygen >/dev/null; then
    ssh-keygen -t ed25519 -N "" -C "ansible-lab" -f .ssh/id_ed25519
  else
    # เครื่องที่ไม่มี ssh-keygen: สร้าง key ผ่าน container ชั่วคราว
    docker run --rm -v "$(pwd)/.ssh:/keys" alpine:3.20 \
      sh -c 'apk add -q openssh-client-default && ssh-keygen -t ed25519 -N "" -C ansible-lab -f /keys/id_ed25519'
  fi
fi

docker compose up -d --build

echo
echo "Lab พร้อมแล้ว เข้า control node ด้วย:"
echo "  docker compose -f $(pwd)/docker-compose.yml exec control bash"
echo "แล้วทดสอบ:  ansible all -m ping"
