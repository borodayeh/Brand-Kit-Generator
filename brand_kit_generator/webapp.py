"""
Local web interface for Brand Kit Generator.
رابط وب محلی برای مولد کیت برند.

Standard library only: no Flask, no build step. Start it with:

    brandkit --web
    python -m brand_kit_generator --web --host 0.0.0.0 --port 8000
"""

from __future__ import annotations

import html
import io
import json
import shutil
import tempfile
import urllib.parse
import zipfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from . import cli

MAX_BODY = 64 * 1024


# --------------------------------------------------------------------------- #
# Core helpers
# --------------------------------------------------------------------------- #

def _load(template: str) -> tuple[dict[str, Any], dict[str, Any]]:
    templates = cli.available_templates()
    path = templates.get(template) or templates[cli.DEFAULT_TEMPLATE]
    data = json.loads(path.read_text(encoding="utf-8"))
    return cli.split_meta(data)


def build_tree(template: str, brand: str, lang: str) -> list[dict[str, Any]]:
    """A flat, depth-tagged listing used by the live preview."""
    nodes, meta = _load(template)
    brand = brand.strip() or str(meta.get("default_brand") or cli.DEFAULT_BRAND)
    nodes = cli.apply_brand(nodes, brand)

    rows: list[dict[str, Any]] = []

    def walk(items: dict[str, Any], depth: int) -> None:
        for name, item in items.items():
            rows.append({
                "depth": depth,
                "name": cli.sanitize_component(str(item.get("path") or name)),
                "title": cli.node_title(item, name, "fa" if lang == "fa" else "en"),
            })
            if isinstance(item.get("subdirs"), dict):
                walk(item["subdirs"], depth + 1)

    walk(nodes, 0)
    return rows


def build_zip(template: str, brand: str, lang: str,
              samples: bool, manifest: bool) -> tuple[str, bytes]:
    """Generate the kit in a temp directory and return (filename, zip bytes)."""
    nodes, meta = _load(template)
    brand = brand.strip() or str(meta.get("default_brand") or cli.DEFAULT_BRAND)
    nodes = cli.apply_brand(nodes, brand)

    opts = cli.Options(
        lang=lang, force=True, dry_run=False,
        samples=samples, manifest=manifest,
        brand=brand, template=template,
    )
    reporter = cli.Reporter(lang, quiet=True)

    tmp = Path(tempfile.mkdtemp(prefix="brandkit-"))
    try:
        cli.generate(tmp, nodes, opts, reporter)
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
            for item in sorted(tmp.rglob("*")):
                archive.write(item, str(item.relative_to(tmp)))
        return f"{cli.slugify_brand(brand)}_brand_kit.zip", buffer.getvalue()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# --------------------------------------------------------------------------- #
# Page
# --------------------------------------------------------------------------- #

STRINGS = {
    "title": ("Brand Kit Generator", "مولد کیت برند"),
    "subtitle": (
        "Generate a bilingual brand kit and download it as a ZIP.",
        "یک کیت برند دوزبانه بسازید و آن را به‌صورت ZIP دانلود کنید.",
    ),
    "brand": ("Brand name", "نام برند"),
    "template": ("Template", "قالب"),
    "language": ("Language", "زبان"),
    "options": ("Options", "گزینه‌ها"),
    "samples": ("Placeholder asset files", "فایل‌های نمونه"),
    "manifest": ("MANIFEST.md overview", "فایل فهرست MANIFEST.md"),
    "download": ("Download ZIP", "دانلود ZIP"),
    "preview": ("Live preview", "پیش‌نمایش زنده"),
    "folders": ("folders", "پوشه"),
    "both": ("Bilingual", "دوزبانه"),
    "fa": ("Persian", "فارسی"),
    "en": ("English", "انگلیسی"),
    "cli_hint": (
        "Same result from the terminal:",
        "همین نتیجه از خط فرمان:",
    ),
}


def s(key: str, lang: str) -> str:
    en, fa = STRINGS[key]
    if lang == "fa":
        return fa
    if lang == "en":
        return en
    return f"{en} / {fa}"


def render_page(lang: str) -> str:
    rtl = lang == "fa"
    templates = cli.available_templates()
    options = []
    for name, path in templates.items():
        meta = cli.template_meta(path)
        label = meta.get("name_fa") if rtl else meta.get("name_en")
        selected = " selected" if name == cli.DEFAULT_TEMPLATE else ""
        options.append(
            f'<option value="{html.escape(name)}"{selected}>'
            f'{html.escape(name)} — {html.escape(str(label or ""))}</option>'
        )

    return f"""<!DOCTYPE html>
<html lang="{'fa' if rtl else 'en'}" dir="{'rtl' if rtl else 'ltr'}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(s('title', lang))}</title>
<style>
  :root {{ --bg:#0f1117; --card:#171a23; --line:#262b38; --fg:#e7e9ee;
           --muted:#98a0b3; --accent:#6ea8fe; --accent2:#8ce99a; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:var(--bg); color:var(--fg); min-height:100vh;
    font-family:system-ui,"Segoe UI",Tahoma,"Vazirmatn",sans-serif; }}
  header {{ padding:32px 24px 8px; text-align:center; }}
  h1 {{ margin:0 0 6px; font-size:1.7rem; }}
  p.sub {{ margin:0; color:var(--muted); font-size:.95rem; }}
  .wrap {{ display:grid; grid-template-columns:360px 1fr; gap:20px;
    max-width:1100px; margin:24px auto; padding:0 24px 48px; }}
  @media (max-width:820px) {{ .wrap {{ grid-template-columns:1fr; }} }}
  .card {{ background:var(--card); border:1px solid var(--line);
    border-radius:14px; padding:20px; }}
  label {{ display:block; font-size:.85rem; color:var(--muted);
    margin:14px 0 6px; }}
  input[type=text], select {{ width:100%; padding:10px 12px; border-radius:9px;
    border:1px solid var(--line); background:#0d1017; color:var(--fg);
    font-size:.95rem; font-family:inherit; }}
  .chk {{ display:flex; align-items:center; gap:8px; margin:8px 0;
    color:var(--fg); font-size:.9rem; }}
  .chk input {{ accent-color:var(--accent); width:16px; height:16px; }}
  button {{ width:100%; margin-top:18px; padding:12px; border:0; border-radius:9px;
    background:var(--accent); color:#0b0d12; font-weight:700; font-size:1rem;
    cursor:pointer; font-family:inherit; }}
  button:hover {{ filter:brightness(1.08); }}
  .count {{ color:var(--accent2); font-weight:700; }}
  pre {{ margin:0; max-height:60vh; overflow:auto; font-size:.82rem;
    line-height:1.6; color:#cfd6e6; direction:ltr; text-align:left; }}
  code.cmd {{ display:block; margin-top:14px; padding:10px 12px; direction:ltr;
    text-align:left; background:#0d1017; border:1px solid var(--line);
    border-radius:9px; font-size:.8rem; color:var(--accent2);
    overflow-x:auto; white-space:pre; }}
  .head {{ display:flex; justify-content:space-between; align-items:center;
    margin-bottom:12px; font-size:.9rem; color:var(--muted); }}
  .langs {{ display:flex; gap:8px; justify-content:center; margin-top:10px; }}
  .langs a {{ color:var(--muted); text-decoration:none; font-size:.85rem;
    border:1px solid var(--line); padding:4px 10px; border-radius:20px; }}
  .langs a.on {{ color:var(--accent); border-color:var(--accent); }}
</style>
</head>
<body>
<header>
  <h1>{html.escape(s('title', lang))}</h1>
  <p class="sub">{html.escape(s('subtitle', lang))}</p>
  <div class="langs">
    <a href="/?ui=both" class="{'on' if lang == 'both' else ''}">Both</a>
    <a href="/?ui=en" class="{'on' if lang == 'en' else ''}">English</a>
    <a href="/?ui=fa" class="{'on' if lang == 'fa' else ''}">فارسی</a>
  </div>
</header>

<div class="wrap">
  <form class="card" method="post" action="/generate">
    <label for="brand">{html.escape(s('brand', lang))}</label>
    <input type="text" id="brand" name="brand" value="Acme" autocomplete="off">

    <label for="template">{html.escape(s('template', lang))}</label>
    <select id="template" name="template">{''.join(options)}</select>

    <label for="lang">{html.escape(s('language', lang))}</label>
    <select id="lang" name="lang">
      <option value="both">{html.escape(s('both', lang))}</option>
      <option value="fa">{html.escape(s('fa', lang))}</option>
      <option value="en">{html.escape(s('en', lang))}</option>
    </select>

    <label>{html.escape(s('options', lang))}</label>
    <div class="chk"><input type="checkbox" id="samples" name="samples" checked>
      <span>{html.escape(s('samples', lang))}</span></div>
    <div class="chk"><input type="checkbox" id="manifest" name="manifest" checked>
      <span>{html.escape(s('manifest', lang))}</span></div>

    <button type="submit">{html.escape(s('download', lang))}</button>

    <label>{html.escape(s('cli_hint', lang))}</label>
    <code class="cmd" id="cmd"></code>
  </form>

  <div class="card">
    <div class="head">
      <span>{html.escape(s('preview', lang))}</span>
      <span><span class="count" id="count">0</span> {html.escape(s('folders', lang))}</span>
    </div>
    <pre id="tree"></pre>
  </div>
</div>

<script>
const form = document.querySelector("form");
const treeEl = document.getElementById("tree");
const countEl = document.getElementById("count");
const cmdEl = document.getElementById("cmd");

function currentState() {{
  return {{
    brand: document.getElementById("brand").value || "Acme",
    template: document.getElementById("template").value,
    lang: document.getElementById("lang").value,
    samples: document.getElementById("samples").checked,
    manifest: document.getElementById("manifest").checked,
  }};
}}

function renderCmd(st) {{
  let cmd = `brandkit ./${{st.brand.replace(/\\s+/g, "_")}} --brand "${{st.brand}}"`;
  cmd += ` --template ${{st.template}} --lang ${{st.lang}}`;
  if (!st.samples) cmd += " --no-samples";
  if (!st.manifest) cmd += " --no-manifest";
  cmdEl.textContent = cmd + " --zip";
}}

async function refresh() {{
  const st = currentState();
  renderCmd(st);
  const url = "/api/preview?" + new URLSearchParams({{
    brand: st.brand, template: st.template, lang: st.lang
  }});
  const res = await fetch(url);
  const data = await res.json();
  countEl.textContent = data.rows.length;
  treeEl.textContent = data.rows
    .map(r => "  ".repeat(r.depth) + "├─ " + r.name + "   " + r.title)
    .join("\\n");
}}

form.addEventListener("input", refresh);
refresh();
</script>
</body>
</html>
"""


# --------------------------------------------------------------------------- #
# Server
# --------------------------------------------------------------------------- #

class Handler(BaseHTTPRequestHandler):
    server_version = f"BrandKitGenerator/{cli.__version__}"
    ui_lang = "both"

    def log_message(self, fmt: str, *args: Any) -> None:
        print(f"[web] {self.address_string()} {fmt % args}")

    # -- helpers ---------------------------------------------------------- #
    def _send(self, code: int, body: bytes, ctype: str,
              extra: dict[str, str] | None = None) -> None:
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Frame-Options", "ALLOWALL")
        for key, value in (extra or {}).items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(body)

    def _query(self) -> dict[str, str]:
        parsed = urllib.parse.urlparse(self.path)
        return {k: v[0] for k, v in urllib.parse.parse_qs(parsed.query).items()}

    # -- routes ----------------------------------------------------------- #
    def do_GET(self) -> None:
        route = urllib.parse.urlparse(self.path).path
        query = self._query()

        if route == "/":
            lang = query.get("ui", self.ui_lang)
            lang = lang if lang in cli.LANGUAGES else "both"
            self._send(200, render_page(lang).encode("utf-8"),
                       "text/html; charset=utf-8")
        elif route == "/api/preview":
            lang = query.get("lang", "both")
            rows = build_tree(query.get("template", cli.DEFAULT_TEMPLATE),
                              query.get("brand", ""), lang)
            payload = json.dumps({"rows": rows}, ensure_ascii=False).encode("utf-8")
            self._send(200, payload, "application/json; charset=utf-8")
        elif route == "/healthz":
            self._send(200, b"ok", "text/plain; charset=utf-8")
        else:
            self._send(404, b"Not found", "text/plain; charset=utf-8")

    def do_POST(self) -> None:
        route = urllib.parse.urlparse(self.path).path
        if route != "/generate":
            self._send(404, b"Not found", "text/plain; charset=utf-8")
            return

        length = min(int(self.headers.get("Content-Length") or 0), MAX_BODY)
        raw = self.rfile.read(length).decode("utf-8", "replace")
        form = {k: v[0] for k, v in urllib.parse.parse_qs(raw).items()}

        lang = form.get("lang", "both")
        lang = lang if lang in cli.LANGUAGES else "both"

        try:
            name, blob = build_zip(
                template=form.get("template", cli.DEFAULT_TEMPLATE),
                brand=form.get("brand", ""),
                lang=lang,
                samples=form.get("samples") == "on",
                manifest=form.get("manifest") == "on",
            )
        except (cli.StructureError, OSError, KeyError) as exc:
            self._send(400, f"Could not generate the kit: {exc}".encode(),
                       "text/plain; charset=utf-8")
            return

        self._send(200, blob, "application/zip",
                   {"Content-Disposition": f'attachment; filename="{name}"'})


def serve(host: str = "127.0.0.1", port: int = 8000, lang: str = "both") -> int:
    """Run the web interface until interrupted."""
    Handler.ui_lang = lang if lang in cli.LANGUAGES else "both"
    server = ThreadingHTTPServer((host, port), Handler)
    shown = "localhost" if host in ("0.0.0.0", "") else host
    print(f"Brand Kit Generator {cli.__version__} — web UI")
    print(f"  http://{shown}:{port}")
    print("  Ctrl+C to stop / برای توقف Ctrl+C را بزنید")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped. / متوقف شد.")
    finally:
        server.server_close()
    return cli.EXIT_OK
