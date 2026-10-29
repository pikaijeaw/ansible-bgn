#!/usr/bin/env bash
# ลบทุกเครื่องใน lab (เริ่มใหม่ได้ด้วย ./setup.sh)
set -euo pipefail
cd "$(dirname "$0")"
docker compose down -v --remove-orphans
