"""AI-PM 2.1 authenticated HTTP integration and DEV/PROD isolation contracts.

Serves a real ephemeral localhost HTTP server with in-memory mock snapshot.
Never binds publicly or calls GitHub/DEV or external resources.
"""
import base64
import http.client
import os
import socket
import threading
import unittest
from pathlib import Path
from unittest import mock
from http.server import ThreadingHTTPServer

import app

ROOT=Path(__file__).resolve().parent

class HttpIsolationTests(unittest.TestCase):
    def setUp(self):
        self.auth=mock.patch.dict(os.environ,{"DASHBOARD_USER":"testoperator",
                                             "DASHBOARD_PASSWORD":"a-long-test-password"})
        self.auth.start()
        self.addCleanup(self.auth.stop)
        self.snapshot=mock.patch.object(app,"snapshot",return_value={
            "go_live":"NO_GO_UNTIL_EXPLICIT_ACCEPTANCE",
            "agent_queue":{"execution":"disabled","global_release":"NO_GO"},
            "team":{"state":"loaded","active_agents":0}})
        self.snapshot.start()
        self.addCleanup(self.snapshot.stop)
        self.http=ThreadingHTTPServer(("127.0.0.1",0),app.Handler)
        self.thread=threading.Thread(target=self.http.serve_forever,daemon=True)
        self.thread.start()
        self.addCleanup(self.http.server_close)
        self.addCleanup(self.http.shutdown)
        self.port=self.http.server_address[1]

    def request(self,path,*,auth=False,method="GET"):
        conn=http.client.HTTPConnection("127.0.0.1",self.port,timeout=5)
        headers={}
        if auth:
            encoded=base64.b64encode(b"testoperator:a-long-test-password").decode("ascii")
            headers["Authorization"]="Basic "+encoded
        conn.request(method,path,headers=headers)
        r=conn.getresponse()
        data=r.read()
        out=(r.status,dict(r.getheaders()),data)
        conn.close()
        return out

    def test_all_assets_are_auth_protected(self):
        for path in ("/","/index.html","/team.html","/light-theme.css","/executive.js","/triage.js","/api/snapshot","/media.html","/media.js","/api/media"):
            with self.subTest(path=path):
                status,headers,data=self.request(path)
                self.assertEqual(status,401)
                self.assertNotIn(b"<!doctype",data)
                self.assertIn("no-store",headers["Cache-Control"])
                self.assertEqual(headers["X-Frame-Options"],"DENY")
                self.assertEqual(headers["X-Content-Type-Options"],"nosniff")
                self.assertEqual(headers["Referrer-Policy"],"no-referrer")
                self.assertIn("connect-src 'self'",headers["Content-Security-Policy"])
                self.assertIn("frame-ancestors 'none'",headers["Content-Security-Policy"])
                status,headers,data=self.request(path,auth=True)
                self.assertEqual(status,200)
                self.assertTrue(data)

    def test_media_api_is_read_only_and_auth_protected(self):
        import json
        with mock.patch.object(app, "media_catalog", return_value={
            "state":"loaded", "assets":[], "sources":[], "errors":[], "count":0
        }):
            status,headers,body=self.request("/api/media",auth=True)
            self.assertEqual(status,200)
            self.assertEqual(json.loads(body)["count"],0)
        for path in (
            "/api/media/asset?repo=bad&ref=main&path=x.png",
            "/api/media/asset?repo=x&ref=x&path=y.png&path=z.png",
            "/api/media/table?repo=x&ref=y",
        ):
            with self.subTest(path=path):
                status,_,_=self.request(path,auth=True)
                self.assertIn(status,(400,404,503))
        for method in ("POST","PUT","PATCH","DELETE"):
            status,_,_=self.request("/api/media",auth=True,method=method)
            self.assertEqual(status,501)

    def test_svg_preview_is_sandboxed(self):
        with mock.patch.object(app, "media_asset", return_value=(b"<svg/>", ".svg")):
            status, headers, data = self.request(
                "/api/media/asset?repo=danielwauer-maker%2Fbcsentinel&ref=main&path=src%2Fassets%2Flogo.svg",
                auth=True
            )
        self.assertEqual(status, 200)
        self.assertEqual(data, b"<svg/>")
        self.assertIn("sandbox", headers["Content-Security-Policy"])
        self.assertIn("default-src 'none'", headers["Content-Security-Policy"])
        self.assertNotIn("script-src 'self'", headers["Content-Security-Policy"])

    def test_unauthorized_correct_password_required(self):
        s,_,_=self.request("/api/snapshot",auth=False)
        self.assertEqual(s,401)
        with mock.patch.dict(os.environ,{"DASHBOARD_PASSWORD":"REPLACE_ME_WITH_RANDOM_PASSWORD"}):
            s,_,_=self.request("/api/snapshot",auth=True)
            self.assertEqual(s,401)

    def test_no_write_routes_or_file_traversal(self):
        for path in ("/api/agent/execute","/api/approve","/../../etc/passwd",
                     "/api/snapshot/../agent-control.sqlite3","/.env","/backup_verify.py"):
            with self.subTest(path=path):
                status,_,_=self.request(path,auth=True)
                self.assertEqual(status,404)
        for method in ("POST","PUT","PATCH","DELETE"):
            with self.subTest(method=method):
                status,_,_=self.request("/api/snapshot",auth=True,method=method)
                self.assertEqual(status,501)

    def test_no_go_and_agent_disabled_on_api(self):
        import json
        status,headers,body=self.request("/api/snapshot",auth=True)
        self.assertEqual(status,200)
        obj=json.loads(body)
        self.assertEqual(obj["go_live"],"NO_GO_UNTIL_EXPLICIT_ACCEPTANCE")
        self.assertEqual(obj["agent_queue"]["execution"],"disabled")
        self.assertEqual(obj["team"]["active_agents"],0)

    def test_config_only_private_port_and_two_separate_services(self):
        yml=(ROOT/"compose.example.yml").read_text()
        self.assertIn('127.0.0.1:8090:8090',yml)
        self.assertIn('no-new-privileges:true',yml)
        self.assertIn('cap_drop:',yml)
        self.assertIn('read_only: true',yml)
        self.assertIn('./data:/data:ro',yml)
        self.assertIn('ai-pm-sync:',yml)
        self.assertNotIn('docker.sock',yml)
        self.assertNotIn('network_mode: host',yml)
        self.assertNotIn('privileged: true',yml)

if __name__=="__main__":unittest.main()
