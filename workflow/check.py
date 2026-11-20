#!/usr/bin/env python3
"""Check installation; optionally exercise both MCPs without an LLM request."""
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import selectors
import subprocess
import tempfile
import threading
import time
import urllib.request

try:
    import tomllib
except ImportError:
    import tomli as tomllib

ROOT = Path(__file__).resolve().parent.parent


def result_text(result):
    if result.get("isError"):
        raise RuntimeError(json.dumps(result, ensure_ascii=False)[:1800])
    return "\n".join(item.get("text", "") for item in result.get("content", []))


def check_deepwiki(config):
    session = None

    def rpc(method, params, request_id):
        nonlocal session
        payload = {"jsonrpc": "2.0", "id": request_id, "method": method, "params": params}
        headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
        if session:
            headers["Mcp-Session-Id"] = session
        request = urllib.request.Request(config["url"], json.dumps(payload).encode(), headers=headers)
        with urllib.request.urlopen(request, timeout=35) as response:
            session = response.headers.get("Mcp-Session-Id", session)
            if "text/event-stream" in response.headers.get("Content-Type", ""):
                for line in response:
                    if line.startswith(b"data:"):
                        value = json.loads(line[5:])
                        if value.get("id") == request_id:
                            break
                else:
                    raise RuntimeError("MCP stream ended without the requested response")
            else:
                value = json.load(response)
        if "error" in value:
            raise RuntimeError(str(value["error"]))
        return value["result"]

    rpc("initialize", {"protocolVersion": "2025-03-26", "capabilities": {},
                       "clientInfo": {"name": "workstyle-check", "version": "1.0"}}, 1)
    # HTTP sessions that require an initialized notification receive it before calls.
    payload = {"jsonrpc": "2.0", "method": "notifications/initialized"}
    headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
    if session:
        headers["Mcp-Session-Id"] = session
    request = urllib.request.Request(config["url"], json.dumps(payload).encode(), headers=headers)
    with urllib.request.urlopen(request, timeout=35):
        pass
    tools = rpc("tools/list", {}, 2)["tools"]
    names = [tool["name"] for tool in tools]
    if "read_wiki_structure" not in names:
        raise RuntimeError("Expected read_wiki_structure is not available")
    output = result_text(rpc("tools/call", {"name": "read_wiki_structure",
                         "arguments": {"repoName": "psf/requests"}}, 3))
    if not output.strip():
        raise RuntimeError("DeepWiki returned no repository content")
    return {"tools": names, "sample_repository": "psf/requests", "content_received": True}


def check_browser(config):
    class Page(BaseHTTPRequestHandler):
        def do_GET(self):
            body = b'<title>Workstyle browser ready</title><button onclick="document.querySelector(\'#result\').textContent=\'verified\'">Verify</button><p id="result">pending</p>'
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Page)
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()
    try:
        with tempfile.TemporaryDirectory(prefix="workstyle-browser-") as directory, tempfile.TemporaryFile() as errors:
            process = subprocess.Popen([config["command"], *config["args"]], cwd=directory,
                                       stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=errors)
            selector = selectors.DefaultSelector()
            selector.register(process.stdout, selectors.EVENT_READ)

            def send(value):
                process.stdin.write((json.dumps(value) + "\n").encode())
                process.stdin.flush()

            def rpc(method, params, request_id):
                send({"jsonrpc": "2.0", "id": request_id, "method": method, "params": params})
                deadline = time.monotonic() + 40
                while time.monotonic() < deadline:
                    if not selector.select(timeout=1):
                        continue
                    line = process.stdout.readline()
                    if not line:
                        errors.seek(0)
                        raise RuntimeError("Browser MCP exited: " + errors.read().decode()[-1800:])
                    value = json.loads(line)
                    if "method" in value and "id" in value:
                        response = {"jsonrpc": "2.0", "id": value["id"],
                                    "result": {"roots": [{"uri": Path(directory).as_uri(), "name": "check"}]}}
                        send(response)
                    elif value.get("id") == request_id:
                        if "error" in value:
                            raise RuntimeError(str(value["error"]))
                        return value["result"]
                raise RuntimeError("Browser MCP timed out")

            try:
                rpc("initialize", {"protocolVersion": "2025-03-26", "capabilities": {"roots": {}},
                                  "clientInfo": {"name": "workstyle-check", "version": "1.0"}}, 1)
                send({"jsonrpc": "2.0", "method": "notifications/initialized"})
                names = [tool["name"] for tool in rpc("tools/list", {}, 2)["tools"]]
                output = result_text(rpc("tools/call", {"name": "browser_navigate", "arguments": {
                    "url": "http://127.0.0.1:" + str(server.server_port)}}, 3))
                if "Workstyle browser ready" not in output:
                    raise RuntimeError("Browser did not observe the expected local page")
                output = result_text(rpc("tools/call", {"name": "browser_evaluate", "arguments": {
                    "function": "() => { document.querySelector('button').click(); return document.querySelector('#result').textContent; }"}}, 4))
                if "verified" not in output:
                    raise RuntimeError("Browser interaction did not update the page")
                rpc("tools/call", {"name": "browser_close", "arguments": {}}, 5)
                return {"tools_count": len(names), "local_navigation": True, "page_interaction": True}
            finally:
                selector.close()
                process.stdin.close()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait()
    finally:
        server.shutdown()
        server.server_close()
        worker.join(timeout=2)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mcp", action="store_true", help="exercise DeepWiki and a temporary local browser page")
    parser.add_argument("--profile-file", type=Path)
    parser.add_argument("--codex-home", type=Path,
                        default=Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))))
    args = parser.parse_args()
    home = args.codex_home.expanduser().resolve()
    profile = args.profile_file or home / "workstyle.config.toml"
    config = tomllib.loads(profile.read_text())
    for name in ["workstyle-task", "prototype", "retro", "teach", "writing-for-agents"]:
        if not (home / "skills" / name / "SKILL.md").is_file():
            raise RuntimeError("Missing installed skill: " + name)
    browser = config["mcp_servers"]["workstyle_browser"]
    cli = Path(browser["args"][0])
    chrome = Path(browser["args"][browser["args"].index("--executable-path") + 1])
    if not cli.is_file() or not os.access(browser["command"], os.X_OK) or not os.access(chrome, os.X_OK):
        raise RuntimeError("Browser MCP package, Node or Chromium is missing")
    report = {"checked_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
              "profile": str(profile), "installed_skills": 5, "static_checks": "pass"}
    if args.mcp:
        for name, check in [("workstyle_deepwiki", check_deepwiki), ("workstyle_browser", check_browser)]:
            try:
                report[name] = {"status": "pass", **check(config["mcp_servers"][name])}
            except Exception as error:
                report[name] = {"status": "fail", "error": str(error)}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if args.mcp:
        (ROOT / "workflow/check-results.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    return 1 if any(isinstance(value, dict) and value.get("status") == "fail" for value in report.values()) else 0


if __name__ == "__main__":
    raise SystemExit(main())
