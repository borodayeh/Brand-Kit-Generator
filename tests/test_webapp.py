"""The stdlib web interface."""

from __future__ import annotations

import io
import json
import threading
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from http.server import ThreadingHTTPServer

import pytest

from brand_kit_generator import webapp


@pytest.fixture(scope="module")
def server():
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), webapp.Handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{httpd.server_address[1]}"
    httpd.shutdown()
    httpd.server_close()


def get(url: str):
    with urllib.request.urlopen(url, timeout=10) as response:
        return response.status, response.read(), response.headers


def test_index_is_html(server):
    status, body, headers = get(server + "/")
    assert status == 200
    assert "text/html" in headers["Content-Type"]
    assert b"Brand Kit Generator" in body


def test_index_switches_to_rtl(server):
    _, body, _ = get(server + "/?ui=fa")
    assert b'dir="rtl"' in body
    _, body_en, _ = get(server + "/?ui=en")
    assert b'dir="ltr"' in body_en


def test_healthz(server):
    status, body, _ = get(server + "/healthz")
    assert status == 200 and body == b"ok"


def test_unknown_route_404(server):
    with pytest.raises(urllib.error.HTTPError) as exc:
        get(server + "/nope")
    assert exc.value.code == 404


def test_preview_api(server):
    query = urllib.parse.urlencode({"template": "minimal", "brand": "Nova", "lang": "fa"})
    _, body, _ = get(f"{server}/api/preview?{query}")
    rows = json.loads(body)["rows"]
    assert rows[0]["name"] == "Nova_Brand_Kit"
    assert rows[0]["depth"] == 0
    assert len(rows) == 6


def test_generate_returns_zip(server):
    data = urllib.parse.urlencode({
        "brand": "Acme", "template": "startup",
        "lang": "fa", "samples": "on", "manifest": "on",
    }).encode()
    with urllib.request.urlopen(server + "/generate", data=data, timeout=20) as response:
        assert response.status == 200
        assert response.headers["Content-Type"] == "application/zip"
        assert "Acme_brand_kit.zip" in response.headers["Content-Disposition"]
        blob = response.read()

    with zipfile.ZipFile(io.BytesIO(blob)) as archive:
        names = archive.namelist()
        assert "MANIFEST.md" in names
        readme = archive.read("Acme_Brand_Kit/README.md").decode("utf-8")
    assert 'dir="rtl"' in readme


def test_build_tree_and_zip_helpers():
    rows = webapp.build_tree("minimal", "Nova", "en")
    assert rows[0]["title"] == "Nova Brand Kit"

    name, blob = webapp.build_zip("minimal", "Nova", "en", samples=False, manifest=False)
    assert name == "Nova_brand_kit.zip"
    with zipfile.ZipFile(io.BytesIO(blob)) as archive:
        names = archive.namelist()
    assert "MANIFEST.md" not in names
    assert not any(n.endswith("logo.svg") for n in names)


def test_build_zip_falls_back_to_default_brand():
    rows = webapp.build_tree("minimal", "", "en")
    assert rows[0]["name"] == "My_Brand_Kit"


def test_unknown_template_falls_back_to_default():
    rows = webapp.build_tree("does-not-exist", "X", "en")
    assert rows[0]["name"].startswith("X_")
    assert len(rows) == 55
