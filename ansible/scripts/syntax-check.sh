#!/usr/bin/env bash
# ตรวจ syntax ของทุก playbook ใน labs/ (ใช้ทั้งบนเครื่องและใน CI)
set -euo pipefail
cd "$(dirname "$0")/.."

status=0
# ใช้เฉพาะไฟล์ที่อยู่ใน git (ไม่รวมไฟล์ที่ lab สร้างขึ้นเอง เช่น report/inventory)
for pb in $( (git ls-files 'labs/' 2>/dev/null || ls labs/*/*.yml) | grep -E '^labs/[^/]+/[^/]+\.yml$'); do
  inv=inventory/hosts.yml
  [[ -d "$(dirname "$pb")/inventory" ]] && inv="$(dirname "$pb")/inventory"
  if ansible-playbook -i "$inv" "$pb" --syntax-check >/dev/null 2>/tmp/syntax-err.txt; then
    echo "OK    $pb"
  else
    echo "FAIL  $pb"; cat /tmp/syntax-err.txt; status=1
  fi
done
exit $status
