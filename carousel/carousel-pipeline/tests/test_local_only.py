"""Carousel Machine answers only this Mac's own pages (audit of 08 Nov 2026).

A web site open in the browser could otherwise POST to 127.0.0.1:8777 (a text/plain POST needs no CORS preflight) and
save, approve, authorize spending or send to Postiz; a DNS-rebinding site could read the drafts with a foreign Host.
"""
import http.client
import sys
import threading
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import review_server as rs  # noqa: E402


class LocalOnly(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = rs.ThreadingHTTPServer(("127.0.0.1", 0), rs.Handler)
        cls.port = cls.server.server_address[1]
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def call(self, method, path, headers=None, body=None):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=10)
        try:
            conn.putrequest(method, path, skip_host=True)
            hdrs = {"Host": f"127.0.0.1:{self.port}", **(headers or {})}
            if body is not None:
                hdrs["Content-Length"] = str(len(body))
            for k, v in hdrs.items():
                if v is not None:
                    conn.putheader(k, v)
            conn.endheaders(body)
            return conn.getresponse().status
        finally:
            conn.close()

    # /api/nope is no route: a request that passes the check gets 404, one that is refused gets 403, and nothing is changed
    def post(self, origin=None, host=None):
        return self.call("POST", "/api/nope", {"Origin": origin, "Content-Type": "text/plain",
                                               **({"Host": host} if host else {})}, b"{}")

    def test_get_from_this_mac(self):
        self.assertEqual(self.call("GET", "/api/ping"), 200)
        self.assertEqual(self.call("GET", "/api/ping", {"Host": f"localhost:{self.port}"}), 200)

    def test_get_with_a_foreign_host_is_refused(self):
        self.assertEqual(self.call("GET", "/api/ping", {"Host": f"rebind.example:{self.port}"}), 403)

    def test_post_without_origin_passes(self):   # the project server's forward, scripts, tests
        self.assertEqual(self.post(), 404)

    def test_post_from_its_own_pages_passes(self):
        self.assertEqual(self.post(f"http://localhost:{self.port}"), 404)
        self.assertEqual(self.post(f"http://127.0.0.1:{self.port}"), 404)
        self.assertEqual(self.post("http://localhost:8780"), 404)

    def test_post_from_another_site_is_refused(self):
        self.assertEqual(self.post("https://evil.example"), 403)
        self.assertEqual(self.post("null"), 403)
        self.assertEqual(self.post("http://localhost:9999"), 403)

    def test_post_with_a_foreign_host_is_refused(self):
        self.assertEqual(self.post(None, f"rebind.example:{self.port}"), 403)


if __name__ == "__main__":
    unittest.main()
