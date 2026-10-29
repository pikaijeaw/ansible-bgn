#!/usr/bin/env python3
"""BigFix REST API client (ใช้แค่ standard library ไม่ต้องติดตั้งอะไรเพิ่ม)

ตัวอย่าง:
  export BIGFIX_URL=https://bigfix.example.com:52311 BIGFIX_USER=api-user BIGFIX_PASSWORD=...
  python3 bigfix_api.py login
  python3 bigfix_api.py query "names of bes computers"
  python3 bigfix_api.py query "(name of it, last report time of it as string) of bes computers" --csv
  python3 bigfix_api.py computers
  python3 bigfix_api.py import ../labs/lab05-software-deploy-windows/install-7zip.bes --site Lab-Automation
  python3 bigfix_api.py deploy --site "Patches for Windows" --fixlet 501 --computers WIN-APP01 WIN-APP02
  python3 bigfix_api.py status 9001

ใช้กับ mock ใน ansible/lab-env ได้: BIGFIX_URL=http://localhost:52311 (user admin / BigFix123!)
"""
import argparse
import base64
import csv
import json
import os
import re
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

ENDPOINT_BY_TYPE = {"Fixlet": "fixlets", "Task": "tasks", "Analysis": "analyses", "ComputerGroup": "computergroups"}


class BigFix:
    def __init__(self, url, user, password, verify=True):
        self.url = url.rstrip("/")
        token = base64.b64encode(f"{user}:{password}".encode()).decode()
        self.headers = {"Authorization": f"Basic {token}"}
        self.ctx = None if verify else ssl._create_unverified_context()

    def request(self, method, path, body=None, content_type="application/xml"):
        headers = dict(self.headers)
        data = None
        if body is not None:
            data = body.encode("utf-8")
            headers["Content-Type"] = content_type
        req = urllib.request.Request(self.url + path, data=data, method=method, headers=headers)
        try:
            with urllib.request.urlopen(req, context=self.ctx, timeout=60) as resp:
                return resp.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            sys.exit(f"HTTP {exc.code} {method} {path}\n{exc.read().decode(errors='replace')}")

    def query(self, relevance):
        """Session relevance -> list of answers (tuple answers come back as lists)"""
        qs = urllib.parse.urlencode({"relevance": relevance, "output": "json"})
        return json.loads(self.request("GET", f"/api/query?{qs}"))["result"]

    def computers(self):
        root = ET.fromstring(self.request("GET", "/api/computers"))
        return [(c.findtext("ID"), c.findtext("LastReportTime")) for c in root.iter("Computer")]

    def import_content(self, path, site, site_type="custom"):
        xml = open(path, encoding="utf-8").read()
        kind = next(iter(ET.fromstring(xml))).tag
        endpoint = ENDPOINT_BY_TYPE[kind]
        resp = self.request("POST", f"/api/{endpoint}/{site_type}/{urllib.parse.quote(site)}", xml)
        return kind, re.search(r"<ID>(\d+)</ID>", resp).group(1)

    def deploy_fixlet(self, site, fixlet_id, computers, action="Action1", title=None):
        targets = "".join(f"<ComputerName>{escape(c)}</ComputerName>" for c in computers)
        body = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<BES xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="BES.xsd">'
            "<SourcedFixletAction>"
            f"<SourceFixlet><Sitename>{escape(site)}</Sitename><FixletID>{fixlet_id}</FixletID><Action>{action}</Action></SourceFixlet>"
            f"<Target>{targets}</Target>"
            f"<Title>{escape(title or f'API: fixlet {fixlet_id}')}</Title>"
            "</SourcedFixletAction></BES>"
        )
        resp = self.request("POST", "/api/actions", body)
        return re.search(r"<ID>(\d+)</ID>", resp).group(1)

    def action_status(self, action_id):
        root = ET.fromstring(self.request("GET", f"/api/action/{action_id}/status"))
        return [(c.get("Name"), c.findtext("Status")) for c in root.iter("Computer")]


def main():
    p = argparse.ArgumentParser(description="BigFix REST API helper")
    p.add_argument("--url", default=os.environ.get("BIGFIX_URL", "http://localhost:52311"))
    p.add_argument("--user", default=os.environ.get("BIGFIX_USER", "admin"))
    p.add_argument("--password", default=os.environ.get("BIGFIX_PASSWORD", "BigFix123!"))
    p.add_argument("--insecure", action="store_true", help="skip TLS verification (lab only)")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("login")
    q = sub.add_parser("query")
    q.add_argument("relevance")
    q.add_argument("--csv", action="store_true")
    sub.add_parser("computers")
    i = sub.add_parser("import")
    i.add_argument("files", nargs="+")
    i.add_argument("--site", required=True)
    d = sub.add_parser("deploy")
    d.add_argument("--site", required=True)
    d.add_argument("--fixlet", required=True, type=int)
    d.add_argument("--computers", nargs="+", required=True)
    d.add_argument("--action", default="Action1")
    s = sub.add_parser("status")
    s.add_argument("action_id")
    args = p.parse_args()

    bf = BigFix(args.url, args.user, args.password, verify=not args.insecure)
    if args.cmd == "login":
        print(bf.request("GET", "/api/login"))
    elif args.cmd == "query":
        rows = bf.query(args.relevance)
        if args.csv:
            w = csv.writer(sys.stdout)
            for r in rows:
                w.writerow(r if isinstance(r, list) else [r])
        else:
            for r in rows:
                print(" | ".join(map(str, r)) if isinstance(r, list) else r)
    elif args.cmd == "computers":
        for cid, last in bf.computers():
            print(f"{cid}\t{last}")
    elif args.cmd == "import":
        for f in args.files:
            kind, new_id = bf.import_content(f, args.site)
            print(f"{kind:<14} {new_id:<8} {f}")
    elif args.cmd == "deploy":
        print("action id:", bf.deploy_fixlet(args.site, args.fixlet, args.computers, args.action))
    elif args.cmd == "status":
        for name, status in bf.action_status(args.action_id):
            print(f"{name:<20} {status}")


if __name__ == "__main__":
    main()
