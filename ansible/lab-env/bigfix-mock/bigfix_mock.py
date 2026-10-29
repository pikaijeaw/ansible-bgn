#!/usr/bin/env python3
"""BigFix REST API จำลอง (mock) สำหรับฝึกเขียน automation โดยไม่ต้องมี BigFix server จริง

รองรับเฉพาะ endpoint ที่ lab ใช้ (รูปแบบ request/response เลียนแบบของจริง):
  GET  /api/login
  GET  /api/computers
  GET  /api/query?relevance=...[&output=json]
  POST /api/actions                 (body = BES XML)
  GET  /api/action/<id>/status
  POST /api/{fixlets|tasks|analyses|computergroups}/custom/<site>   (body = BES XML)

ของจริงใช้ HTTPS ที่ port 52311 ส่วน mock นี้ใช้ HTTP เพื่อให้ตั้งค่าง่าย
user/password: admin / BigFix123!
"""
import base64
import itertools
import json
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

USER, PASSWORD = "admin", "BigFix123!"
NOW = datetime.now(timezone.utc)


def bes_time(dt):
    return dt.strftime("%a, %d %b %Y %H:%M:%S +0000")


COMPUTERS = [
    {"id": 1001, "name": "web01", "os": "Linux Ubuntu 24.04", "ip": "172.20.0.11", "last": NOW - timedelta(minutes=3)},
    {"id": 1002, "name": "web02", "os": "Linux Ubuntu 24.04", "ip": "172.20.0.12", "last": NOW - timedelta(minutes=5)},
    {"id": 1003, "name": "db01", "os": "Linux Rocky Linux 9.4", "ip": "172.20.0.21", "last": NOW - timedelta(minutes=1)},
    {"id": 1004, "name": "WIN-APP01", "os": "Win2022 10.0.20348.2700", "ip": "10.10.1.31", "last": NOW - timedelta(minutes=8)},
    {"id": 1005, "name": "WIN-APP02", "os": "Win2019 10.0.17763.6293", "ip": "10.10.1.32", "last": NOW - timedelta(days=12)},
    {"id": 1006, "name": "LAPTOP-HR-07", "os": "Win11 10.0.22631.4317", "ip": "10.20.5.77", "last": NOW - timedelta(days=30)},
]

FIXLETS = [
    {"id": 501, "site": "Patches for Windows", "name": "MS24-OCT: Cumulative Update for Windows Server 2022 - KB5044281", "severity": "Critical", "applicable": ["WIN-APP01"]},
    {"id": 502, "site": "Patches for Windows", "name": "MS24-OCT: Cumulative Update for Windows Server 2019 - KB5044277", "severity": "Critical", "applicable": ["WIN-APP02"]},
    {"id": 503, "site": "Patches for Windows", "name": "MS24-OCT: Cumulative Update for Windows 11 23H2 - KB5044285", "severity": "Critical", "applicable": ["LAPTOP-HR-07"]},
    {"id": 601, "site": "Patches for RHEL 9", "name": "RHSA-2024:8038 - openssl Security Update - Rocky 9", "severity": "Important", "applicable": ["db01"]},
    {"id": 701, "site": "Patches for Ubuntu 2404", "name": "USN-7089-1 - Linux kernel vulnerabilities - Ubuntu 24.04", "severity": "High", "applicable": ["web01", "web02"]},
]

ACTIONS = {}
ACTION_IDS = itertools.count(9001)
CUSTOM_IDS = itertools.count(20001)


def q_names():
    return "string", [c["name"] for c in COMPUTERS]


def q_inventory():
    return "( integer, string, string, string )", [
        [c["id"], c["name"], c["os"], bes_time(c["last"])] for c in COMPUTERS
    ]


def q_stale():
    cutoff = NOW - timedelta(days=7)
    return "( string, string )", [[c["name"], bes_time(c["last"])] for c in COMPUTERS if c["last"] < cutoff]


def q_applicable():
    return "( integer, string, string, integer )", [
        [f["id"], f["site"], f["name"], len(f["applicable"])] for f in FIXLETS
    ]


def q_applicable_computers(fixlet_id):
    for f in FIXLETS:
        if f["id"] == fixlet_id:
            return "string", list(f["applicable"])
    return "string", []


def q_count():
    return "integer", [len(COMPUTERS)]


# relevance ที่ mock รองรับ (normalize ช่องว่างก่อนเทียบ)
QUERIES = {
    "number of bes computers": q_count,
    "names of bes computers": q_names,
    "(id of it, name of it, operating system of it, last report time of it as string) of bes computers": q_inventory,
    "(name of it, last report time of it as string) of bes computers whose (last report time of it < now - 7 * day)": q_stale,
    "(id of it, name of site of it, name of it, applicable computer count of it) of bes fixlets whose (applicable computer count of it > 0 and fixlet flag of it)": q_applicable,
}
APPLICABLE_RE = re.compile(r"names of applicable computers of bes fixlets whose \(id of it = (\d+)\)")


def run_query(relevance):
    rel = " ".join(relevance.split())
    if rel in QUERIES:
        return QUERIES[rel]()
    m = APPLICABLE_RE.fullmatch(rel)
    if m:
        return q_applicable_computers(int(m.group(1)))
    raise KeyError(rel)


class Handler(BaseHTTPRequestHandler):
    server_version = "BigFixMock/1.0"

    def _authorized(self):
        header = self.headers.get("Authorization", "")
        if not header.startswith("Basic "):
            return False
        user, _, pwd = base64.b64decode(header[6:]).decode().partition(":")
        return user == USER and pwd == PASSWORD

    def _send(self, code, body, ctype="application/xml"):
        data = body.encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _guard(self):
        if not self._authorized():
            self.send_response(401)
            self.send_header("WWW-Authenticate", 'Basic realm="BigFix"')
            self.end_headers()
            return False
        return True

    def do_GET(self):
        if not self._guard():
            return
        url = urlparse(self.path)
        params = parse_qs(url.query)
        if url.path == "/api/login":
            return self._send(200, "ok", "text/plain")
        if url.path == "/api/computers":
            items = "".join(
                f'<Computer Resource="http://bigfix:52311/api/computer/{c["id"]}">'
                f'<LastReportTime>{bes_time(c["last"])}</LastReportTime><ID>{c["id"]}</ID></Computer>'
                for c in COMPUTERS
            )
            return self._send(200, f"<BESAPI>{items}</BESAPI>")
        if url.path == "/api/query":
            relevance = params.get("relevance", [""])[0]
            try:
                rtype, result = run_query(relevance)
            except KeyError:
                supported = "\n".join(list(QUERIES) + [APPLICABLE_RE.pattern])
                return self._send(400, f"Mock does not support this relevance:\n{relevance}\n\nSupported:\n{supported}", "text/plain")
            if params.get("output", [""])[0] == "json":
                body = {"result": result, "plural": len(result) != 1, "type": rtype, "evaltime_ms": 1}
                return self._send(200, json.dumps(body), "application/json")
            answers = ""
            for row in result:
                if isinstance(row, list):
                    answers += "<Tuple>" + "".join(f"<Answer>{v}</Answer>" for v in row) + "</Tuple>"
                else:
                    answers += f"<Answer>{row}</Answer>"
            return self._send(200, f'<BESAPI><Query Resource="{relevance}"><Result>{answers}</Result></Query></BESAPI>')
        m = re.fullmatch(r"/api/action/(\d+)/status", url.path)
        if m and int(m.group(1)) in ACTIONS:
            action = ACTIONS[int(m.group(1))]
            rows = "".join(
                f'<Computer ID="{c["id"]}" Name="{c["name"]}"><Status>Fixed</Status><State IsError="0">Completed</State></Computer>'
                for c in COMPUTERS if c["name"] in action["targets"]
            )
            return self._send(200, f'<BESAPI><ActionResults><ActionID>{m.group(1)}</ActionID><Status>Open</Status>{rows}</ActionResults></BESAPI>')
        self._send(404, "Not found", "text/plain")

    def do_POST(self):
        if not self._guard():
            return
        url = urlparse(self.path)
        body = self.rfile.read(int(self.headers.get("Content-Length", 0))).decode()
        try:
            root = ET.fromstring(body)
        except ET.ParseError as exc:
            return self._send(400, f"Invalid XML: {exc}", "text/plain")
        if url.path == "/api/actions":
            node = root.find("SourcedFixletAction")
            if node is None:
                node = root.find("SingleAction")
            if node is None:
                return self._send(400, "Expected <SourcedFixletAction> or <SingleAction>", "text/plain")
            targets = [e.text for e in node.iter("ComputerName")]
            if node.find("Target/AllComputers") is not None:
                targets = [c["name"] for c in COMPUTERS]
            title = node.findtext("Title") or node.findtext("SourceFixlet/FixletID") or "Action"
            action_id = next(ACTION_IDS)
            ACTIONS[action_id] = {"title": title, "targets": targets}
            print(f"[mock] action {action_id} created for {targets}", flush=True)
            return self._send(200, f'<BESAPI><Action Resource="http://bigfix:52311/api/action/{action_id}" LastModified="{bes_time(NOW)}"><Name>{title}</Name><ID>{action_id}</ID></Action></BESAPI>')
        m = re.fullmatch(r"/api/(fixlets|tasks|analyses|computergroups)/custom/([^/]+)", url.path)
        if m:
            item = next(iter(root), None)
            expected = {"fixlets": "Fixlet", "tasks": "Task", "analyses": "Analysis", "computergroups": "ComputerGroup"}[m.group(1)]
            if item is None or item.tag != expected:
                return self._send(400, f"Expected <{expected}> for /api/{m.group(1)}", "text/plain")
            title = item.findtext("Title")
            new_id = next(CUSTOM_IDS)
            print(f"[mock] imported '{title}' into custom site {m.group(2)} as {new_id}", flush=True)
            return self._send(200, f'<BESAPI><{item.tag} Resource="http://bigfix:52311/api/fixlet/custom/{m.group(2)}/{new_id}"><Name>{title}</Name><ID>{new_id}</ID></{item.tag}></BESAPI>')
        self._send(404, "Not found", "text/plain")


if __name__ == "__main__":
    print("BigFix mock API listening on :52311", flush=True)
    ThreadingHTTPServer(("0.0.0.0", 52311), Handler).serve_forever()
