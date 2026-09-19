#!/usr/bin/env python3
"""Build, serve, and live-rebuild the portfolio while source files change."""

from __future__ import annotations

import argparse
import importlib
import json
import sys
import threading
import time
from dataclasses import dataclass
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

import build


ROOT = Path(__file__).resolve().parent
WATCH_PATHS = (
    ROOT / "content",
    ROOT / "templates",
    ROOT / "assets",
    ROOT / "build.py",
    ROOT / "styles.css",
    ROOT / "script.js",
)
LIVE_RELOAD_SCRIPT = b'''<script>
(() => {
  let version;
  const check = async () => {
    try {
      const response = await fetch('/__dev_status', { cache: 'no-store' });
      const state = await response.json();
      if (version === undefined) version = state.version;
      else if (state.version !== version) window.location.reload();
    } catch (_) { /* The server may be restarting. */ }
    window.setTimeout(check, 700);
  };
  check();
})();
</script>'''


@dataclass
class BuildState:
    version: int = 0
    error: str | None = None


def snapshot() -> dict[str, tuple[int, int]]:
    """Return a cheap signature for files that affect the generated site."""
    files: dict[str, tuple[int, int]] = {}
    for target in WATCH_PATHS:
        candidates = target.rglob("*") if target.is_dir() else (target,)
        for path in candidates:
            if not path.is_file():
                continue
            try:
                stat = path.stat()
            except OSError:
                continue
            files[str(path.relative_to(ROOT))] = (stat.st_mtime_ns, stat.st_size)
    return files


def build_once(state: BuildState) -> bool:
    """Build into memory first, so a bad save never replaces good output."""
    try:
        importlib.reload(build)
        projects = build.load_projects()
        outputs = build.build_outputs(projects)
        build.write_outputs(outputs)
    except Exception as exc:
        state.error = str(exc)
        print(f"\nBuild failed:\n{exc}", file=sys.stderr)
        return False
    state.version += 1
    state.error = None
    print(f"Built {len(projects)} projects (revision {state.version}).")
    return True


class DevHandler(SimpleHTTPRequestHandler):
    """Static file handler with a development-only status endpoint and reload script."""

    server: "DevServer"

    def do_GET(self) -> None:  # noqa: N802 - required by the stdlib HTTP server.
        request_path = urlsplit(self.path).path
        if request_path == "/__dev_status":
            payload = json.dumps({"version": self.server.state.version, "error": self.server.state.error}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return

        if self.server.live_reload:
            path = Path(self.translate_path(request_path))
            if path.is_dir():
                path = path / "index.html"
            if path.is_file() and path.suffix.lower() == ".html":
                try:
                    contents = path.read_bytes()
                except OSError:
                    contents = None
                if contents is not None:
                    marker = b"</body>"
                    injection = LIVE_RELOAD_SCRIPT
                    contents = contents.replace(marker, injection + marker, 1) if marker in contents else contents + injection
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.send_header("Cache-Control", "no-store")
                    self.send_header("Content-Length", str(len(contents)))
                    self.end_headers()
                    self.wfile.write(contents)
                    return
        super().do_GET()

    def log_message(self, format: str, *args: object) -> None:
        print(f"serve: {format % args}")


class DevServer(ThreadingHTTPServer):
    allow_reuse_address = True

    def __init__(self, address: tuple[str, int], state: BuildState, live_reload: bool) -> None:
        self.state = state
        self.live_reload = live_reload
        super().__init__(address, DevHandler)


def watch(server: DevServer, state: BuildState, interval: float) -> None:
    previous = snapshot()
    while True:
        time.sleep(interval)
        current = snapshot()
        if current == previous:
            continue
        previous = current
        print("\nChange detected; rebuilding…")
        build_once(state)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1", help="interface to bind (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=4173, help="port to serve (default: 4173)")
    parser.add_argument("--interval", type=float, default=0.5, help="save polling interval in seconds (default: 0.5)")
    parser.add_argument("--no-live-reload", action="store_true", help="serve updates without injecting browser auto-reload")
    args = parser.parse_args()
    if args.interval <= 0:
        parser.error("--interval must be greater than zero")

    state = BuildState()
    build_once(state)
    try:
        server = DevServer((args.host, args.port), state, not args.no_live_reload)
    except OSError as exc:
        print(f"Could not start server on {args.host}:{args.port}: {exc}", file=sys.stderr)
        return 1

    watcher = threading.Thread(target=watch, args=(server, state, args.interval), daemon=True)
    watcher.start()
    print(f"Serving {ROOT} at http://{args.host}:{args.port}/")
    print("Watching content/, templates/, assets/, build.py, styles.css, and script.js. Press Ctrl-C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping development server.")
    finally:
        server.shutdown()
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
