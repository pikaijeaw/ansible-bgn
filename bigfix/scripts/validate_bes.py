#!/usr/bin/env python3
"""ตรวจไฟล์ BigFix content (.bes) ก่อน import เข้า Console/REST API

สิ่งที่ตรวจ:
  - เป็น XML ที่ถูกต้อง และ root คือ <BES>
  - ชนิด content ที่รองรับ: Fixlet, Task, Analysis, ComputerGroup
  - ลำดับ element หลักตรงกับ BES.xsd (Console จะปฏิเสธไฟล์ที่ลำดับผิด)
  - มี Title, Relevance, Domain และ Fixlet/Task มี ActionScript ที่ไม่ว่าง
  - Analysis มี Property อย่างน้อย 1 ตัว และ ID ไม่ซ้ำ
  - วงเล็บและเครื่องหมายคำพูดใน relevance เปิดปิดครบ

ใช้: python3 validate_bes.py <ไฟล์หรือโฟลเดอร์> [...]
"""
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

FIXLET_ORDER = [
    "Title", "Description", "Relevance", "GroupRelevance", "Category", "DownloadSize",
    "Source", "SourceID", "SourceReleaseDate", "SourceSeverity", "CVENames", "SANSID",
    "MIMEField", "Domain", "Delay", "DefaultAction", "Action",
]
ANALYSIS_ORDER = [
    "Title", "Description", "Relevance", "Category", "Source", "SourceID", "SourceReleaseDate",
    "SourceSeverity", "CVENames", "SANSID", "MIMEField", "Domain", "Property",
]
GROUP_ORDER = ["Title", "Domain", "JoinByIntersection", "SearchComponentRelevance",
               "SearchComponentPropertyReference", "SearchComponentGroupReference"]
ORDER = {"Fixlet": FIXLET_ORDER, "Task": FIXLET_ORDER, "Analysis": ANALYSIS_ORDER, "ComputerGroup": GROUP_ORDER}


def check_balanced(text):
    """relevance ไม่มี escape ด้วย backslash: เครื่องหมาย " ต้องมาเป็นคู่ และวงเล็บนอก string ต้องครบ"""
    depth, in_str = 0, False
    for ch in text:
        if ch == '"':
            in_str = not in_str
        elif not in_str and ch == "(":
            depth += 1
        elif not in_str and ch == ")":
            depth -= 1
            if depth < 0:
                return "too many ')'"
    if in_str:
        return 'unterminated string (")'
    if depth:
        return "unbalanced '('"
    return None


def check_order(item, order):
    seen = [c.tag for c in item]
    positions = []
    for tag in seen:
        if tag not in order:
            return f"unexpected element <{tag}>"
        positions.append(order.index(tag))
    if positions != sorted(positions):
        return "element order does not match BES.xsd: " + ", ".join(seen)
    return None


def validate(path):
    errors = []
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as exc:
        return [f"XML parse error: {exc}"]
    if root.tag != "BES":
        return ["root element must be <BES>"]
    items = list(root)
    if len(items) != 1:
        errors.append(f"expected exactly one content item, found {len(items)}")
    for item in items:
        kind = item.tag
        if kind not in ORDER:
            errors.append(f"unsupported content type <{kind}>")
            continue
        err = check_order(item, ORDER[kind])
        if err:
            errors.append(err)
        if not (item.findtext("Title") or "").strip():
            errors.append("missing <Title>")
        if (item.findtext("Domain") or "").strip() != "BESC":
            errors.append("<Domain> must be BESC")
        relevances = [r.text or "" for r in item.iter("Relevance")]
        if not relevances or not all(r.strip() for r in relevances):
            errors.append("missing or empty <Relevance>")
        for rel in relevances:
            err = check_balanced(rel)
            if err:
                errors.append(f"relevance {err}: {rel[:80]}")
        if kind in ("Fixlet", "Task"):
            actions = item.findall("DefaultAction") + item.findall("Action")
            if not actions:
                errors.append("Fixlet/Task needs a <DefaultAction>")
            for act in actions:
                script = act.find("ActionScript")
                if script is None or not (script.text or "").strip():
                    errors.append(f"action {act.get('ID')} has empty <ActionScript>")
                if act.find("SuccessCriteria") is None:
                    errors.append(f"action {act.get('ID')} missing <SuccessCriteria>")
        if kind == "Analysis":
            props = item.findall("Property")
            ids = [p.get("ID") for p in props]
            if not props:
                errors.append("Analysis needs at least one <Property>")
            if len(ids) != len(set(ids)):
                errors.append("duplicate Property ID")
            for p in props:
                err = check_balanced(p.text or "")
                if err:
                    errors.append(f"property '{p.get('Name')}' {err}")
    return errors


def main(argv):
    files = []
    for arg in argv or ["."]:
        p = Path(arg)
        files.extend(sorted(p.rglob("*.bes")) if p.is_dir() else [p])
    if not files:
        print("no .bes files found")
        return 1
    failed = 0
    for f in files:
        errors = validate(f)
        if errors:
            failed += 1
            print(f"FAIL  {f}")
            for e in errors:
                print(f"      - {e}")
        else:
            print(f"OK    {f}")
    print(f"\n{len(files) - failed}/{len(files)} files valid")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
