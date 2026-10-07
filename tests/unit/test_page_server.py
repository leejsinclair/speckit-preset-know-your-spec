"""The spec page's server: what it serves, what it refuses, and that it writes nothing.

The server runs in a thread on a system-chosen port and is driven with ``urllib.request``.
"""

import json
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts" / "python"))

import specpage  # noqa: E402

SPEC = """# Feature Specification: Parcel Lockers

## Requirements

- **FR-001**: System MUST release a locker after 72 hours.
- **FR-002**: A released locker follows FR-001 and ISO-8601 timestamps.

## Requirements

Again, with <script>alert(1)</script>.
"""


def snapshot(root: Path) -> dict[str, bytes]:
    return {str(p.relative_to(root)): p.read_bytes() for p in sorted(root.rglob("*")) if p.is_file()}


class ServerCase(unittest.TestCase):
    idle_minutes = 60.0

    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.root = Path(self.dir.name)
        self.spec = self.root / "specs" / "001-lockers" / "spec.md"
        self.spec.parent.mkdir(parents=True)
        self.spec.write_text(SPEC, encoding="utf-8")
        self.before = snapshot(self.root)
        self.server = specpage.make_server(self.spec, port=0, idle_minutes=self.idle_minutes)
        self.thread = threading.Thread(target=self.server.serve_forever, kwargs={"poll_interval": 0.02})
        self.thread.start()
        self.origin = f"http://127.0.0.1:{self.server.port}"

    def tearDown(self):
        self.server.shutdown()
        self.thread.join(5)
        self.server.server_close()
        self.dir.cleanup()

    def request(self, path, *, method="GET", headers=None, token=False):
        headers = dict(headers or {})
        if token:
            headers["X-KYS-Token"] = self.server.token
        data = b"{}" if method == "POST" else None
        try:
            with urlopen(Request(self.origin + path, data=data, headers=headers, method=method), timeout=5) as r:
                return r.status, r.headers, r.read().decode("utf-8")
        except HTTPError as error:
            with error:
                return error.code, error.headers, error.read().decode("utf-8")

    def page(self):
        return self.request(f"/?t={self.server.token}")


class PageTest(ServerCase):
    def test_the_address_shows_the_rendered_spec(self):
        status, headers, text = self.page()
        self.assertEqual(status, 200)
        self.assertTrue(headers["Content-Type"].startswith("text/html"))
        self.assertIn('<h1 id="feature-specification-parcel-lockers">', text)
        self.assertIn('<li id="FR-001">', text)
        self.assertIn("001-lockers/spec.md", text)

    def test_a_defined_code_links_to_its_definition_with_a_preview(self):
        _, _, text = self.page()
        self.assertIn('<a class="ref" href="#FR-001" aria-describedby="pv-FR-001">FR-001</a>', text)
        self.assertIn('<div class="preview" id="pv-FR-001" role="tooltip" hidden>', text)
        self.assertEqual(text.count('id="FR-001"'), 1)

    def test_a_code_the_spec_does_not_define_is_plain_text(self):
        _, _, text = self.page()
        self.assertIn("and ISO-8601 timestamps", text)

    def test_raw_html_in_the_spec_is_shown_as_text(self):
        _, _, text = self.page()
        self.assertNotIn("<script>alert(1)</script>", text)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", text)

    def test_anchors_match_the_ids_on_the_page(self):
        _, _, text = self.page()
        anchors = specpage.anchors_of(SPEC)
        self.assertEqual(anchors["Requirements"], "requirements")
        for ident in anchors.values():
            self.assertIn(f'id="{ident}"', text)
        self.assertIn('id="requirements-2"', text)

    def test_the_page_loads_nothing_from_elsewhere(self):
        _, headers, text = self.page()
        policy = headers["Content-Security-Policy"]
        self.assertIn("default-src 'none'", policy)
        self.assertNotIn("http", policy)
        self.assertNotIn("src=", text)
        self.assertEqual(headers["Cache-Control"], "no-store")

    def test_a_spec_with_a_diagram_may_load_the_diagram_script_and_nothing_else(self):
        self.spec.write_text(SPEC + "\n```mermaid\nflowchart LR\n  A --> B\n```\n", encoding="utf-8")
        _, headers, text = self.page()
        policy = headers["Content-Security-Policy"]
        self.assertIn(f"script-src 'nonce-", policy)
        self.assertEqual(policy.count("http"), 1)
        self.assertIn(specpage.MERMAID_ORIGIN + ";", policy)
        self.assertTrue(specpage.MERMAID_URL.startswith(specpage.MERMAID_ORIGIN + "/"))
        self.assertIn(f'<meta name="kys-diagram-script" content="{specpage.MERMAID_URL}">', text)
        self.assertIn('<pre class="mermaid-src">flowchart LR', text)

    def test_text_that_looks_like_a_diagram_does_not_open_the_policy(self):
        self.spec.write_text(SPEC + '\n<pre class="mermaid-src">x</pre>\n', encoding="utf-8")
        _, headers, text = self.page()
        self.assertNotIn("http", headers["Content-Security-Policy"])
        self.assertNotIn('<meta name="kys-diagram-script"', text)

    def test_the_default_bind_is_every_interface_and_the_address_names_loopback(self):
        self.assertEqual(self.server.bound_host, "0.0.0.0")
        self.assertEqual(self.server.server_address[0], "0.0.0.0")
        self.assertTrue(self.server.address.startswith(f"http://127.0.0.1:{self.server.port}/?t="))
        status, _, _ = self.request(f"/?t={self.server.token}", headers={"Host": f"localhost:{self.server.port + 1}"})
        self.assertEqual(status, 200)

    def test_the_spec_is_read_again_on_every_request(self):
        first = json.loads(self.request("/state", token=True)[2])["hash"]
        self.spec.write_text(SPEC + "\nMore.\n", encoding="utf-8")
        second = json.loads(self.request("/state", token=True)[2])["hash"]
        self.assertNotEqual(first, second)
        self.assertIn("<p>More.</p>", self.page()[2])


class RefusalTest(ServerCase):
    def test_no_token_is_refused_without_the_spec_or_the_token(self):
        for path in ("/", "/?t=wrong", "/state"):
            status, _, text = self.request(path)
            self.assertEqual(status, 403, path)
            self.assertNotIn("Parcel Lockers", text)
            self.assertNotIn(self.server.token, text)

    def test_the_token_in_the_query_does_not_open_state(self):
        self.assertEqual(self.request(f"/state?t={self.server.token}")[0], 403)

    def test_another_host_name_is_refused(self):
        status, _, _ = self.request(f"/?t={self.server.token}", headers={"Host": "evil.example:80"})
        self.assertEqual(status, 403)

    def test_other_methods_are_not_allowed(self):
        for method in ("PUT", "DELETE", "PATCH"):
            self.assertEqual(self.request("/", method=method, token=True)[0], 405, method)

    def test_a_post_from_another_origin_is_refused(self):
        status, _, _ = self.request("/stop", method="POST", token=True, headers={"Origin": "http://evil.example"})
        self.assertEqual(status, 403)

    def test_nothing_else_is_served(self):
        self.assertEqual(self.request("/spec.md", token=True)[0], 404)
        self.assertEqual(self.request("/answer", method="POST", token=True, headers={"Origin": self.origin})[0], 404)

    def test_a_missing_spec_refuses_to_start(self):
        with self.assertRaises(specpage.Refused) as raised:
            specpage.make_server(self.root / "nope.md", port=0)
        self.assertEqual(raised.exception.payload["refusals"][0]["code"], "no-spec")


class LifecycleTest(ServerCase):
    def test_stop_ends_the_server(self):
        status, _, text = self.request("/stop", method="POST", token=True, headers={"Origin": self.origin})
        self.assertEqual((status, json.loads(text)["stopped"]), (200, True))
        self.thread.join(5)
        self.assertFalse(self.thread.is_alive())

    def test_serving_changes_nothing_in_the_project(self):
        self.page()
        self.request("/state", token=True)
        self.request("/stop", method="POST", token=True, headers={"Origin": self.origin})
        self.thread.join(5)
        self.assertEqual(snapshot(self.root), self.before)

    def test_the_runtime_file_is_outside_the_project(self):
        path = specpage.runtime_path(self.spec)
        self.assertEqual(path.parent, Path(tempfile.gettempdir()))
        self.assertNotIn(self.root, path.parents)


class IdleTest(ServerCase):
    idle_minutes = 0.002

    def test_an_unused_page_stops_itself(self):
        self.thread.join(5)
        self.assertFalse(self.thread.is_alive())
        self.assertTrue(self.server.stopped.is_set())


class RuntimeTest(unittest.TestCase):
    """``serve``, ``--status`` and ``--stop`` as the command runs them, through the runtime file."""

    def test_serve_status_stop(self):
        with tempfile.TemporaryDirectory() as held:
            spec = Path(held) / "spec.md"
            spec.write_text(SPEC, encoding="utf-8")
            self.assertFalse(specpage.status(spec)["running"])
            started = threading.Event()
            lines = []

            def emit(payload):
                lines.append(payload)
                started.set()

            # ``serve`` installs signal handlers, which only the main thread may do.
            real = specpage.signal.signal
            specpage.signal.signal = lambda sig, handler: None
            try:
                thread = threading.Thread(target=specpage.serve, args=(spec,), kwargs={"emit": emit, "port": 0})
                thread.start()
                self.assertTrue(started.wait(5))
                self.assertEqual(lines[0]["anchors"]["Requirements"], "requirements")
                running = specpage.status(spec)
                self.assertTrue(running["running"])
                self.assertEqual(running["address"], lines[0]["address"])
                with self.assertRaises(specpage.Refused) as raised:
                    specpage.serve(spec, emit=emit, port=0)
                self.assertEqual(raised.exception.payload["refusals"][0]["code"], "page-running")
                self.assertTrue(specpage.stop(spec)["stopped"])
                thread.join(5)
            finally:
                specpage.signal.signal = real
            self.assertFalse(thread.is_alive())
            self.assertFalse(specpage.runtime_path(spec).exists())
            self.assertFalse(specpage.status(spec)["running"])
            self.assertEqual([p.name for p in Path(held).iterdir()], ["spec.md"])


if __name__ == "__main__":
    unittest.main()
