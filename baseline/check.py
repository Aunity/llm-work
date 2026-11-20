#!/usr/bin/env python3
"""Check the ordinary Codex installation, optionally exercising MCPs and prompt discovery."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import time
import urllib.request

try:
    import tomllib
except ImportError:
    import tomli as tomllib

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("workflow_check", ROOT / "workflow/check.py")
workflow_check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(workflow_check)


def check_context7(config):
    session = None

    def send(method, params=None, request_id=None):
        nonlocal session
        payload = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            payload["params"] = params
        if request_id is not None:
            payload["id"] = request_id
        headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
        if session:
            headers["Mcp-Session-Id"] = session
        request = urllib.request.Request(config["url"], json.dumps(payload).encode(), headers=headers)
        with urllib.request.urlopen(request, timeout=40) as response:
            session = response.headers.get("Mcp-Session-Id", session)
            if request_id is None:
                return
            if "text/event-stream" in response.headers.get("Content-Type", ""):
                for line in response:
                    if line.startswith(b"data:"):
                        value = json.loads(line[5:])
                        if value.get("id") == request_id:
                            break
                else:
                    raise RuntimeError("Context7 stream ended without the response")
            else:
                value = json.load(response)
        if "error" in value:
            raise RuntimeError(str(value["error"]))
        return value["result"]

    send("initialize", {"protocolVersion": "2025-03-26", "capabilities": {},
                        "clientInfo": {"name": "codex-baseline-check", "version": "1.0"}}, 1)
    send("notifications/initialized")
    names = [tool["name"] for tool in send("tools/list", {}, 2)["tools"]]
    if not {"resolve-library-id", "query-docs"}.issubset(names):
        raise RuntimeError("Expected Context7 tools are missing")
    resolved = workflow_check.result_text(send("tools/call", {"name": "resolve-library-id", "arguments": {
        "libraryName": "requests", "query": "Python Requests HTTP GET timeout parameter"}}, 3))
    if "/psf/requests" not in resolved:
        raise RuntimeError("Context7 did not resolve the expected public library")
    output = workflow_check.result_text(send("tools/call", {"name": "query-docs", "arguments": {
        "libraryId": "/psf/requests", "query": "How do I set a timeout for requests.get in Python?"}}, 4))
    if not output.strip() or "timeout" not in output.lower():
        raise RuntimeError("Context7 returned no relevant documentation")
    return {"tools": names, "anonymous_access": True, "sample_library": "/psf/requests",
            "library_resolved": True, "documentation_received": True}


def check_prompt(home, skills):
    process = subprocess.run(["codex", "-C", str(ROOT), "debug", "prompt-input", "配置发现检查"],
                             env={**os.environ, "CODEX_HOME": str(home)},
                             capture_output=True, text=True, timeout=90)
    if process.returncode:
        raise RuntimeError("Codex prompt diagnostic failed (exit " + str(process.returncode) + ")")
    # Decode escaped newlines before looking for the skill catalog entries.
    def strings(value):
        if isinstance(value, str):
            yield value
        elif isinstance(value, list):
            for item in value:
                yield from strings(item)
        elif isinstance(value, dict):
            for item in value.values():
                yield from strings(item)
    prompt = "\n".join(strings(json.loads(process.stdout)))
    if "默认用中文交流。先给出主要结论" not in prompt:
        raise RuntimeError("Global AGENTS.md is absent from the ordinary Codex prompt")
    missing = [name for name in skills if not re.search(r"(?m)^- " + re.escape(name) + r":", prompt)]
    if missing:
        raise RuntimeError("Skills absent from the Codex catalog: " + ", ".join(missing))
    return {"global_agents_loaded": True, "skills_discovered": len(skills), "model_request_sent": False,
            "profile_used": None}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mcp", action="store_true")
    parser.add_argument("--codex", action="store_true", help="check ordinary Codex prompt discovery without an LLM request")
    parser.add_argument("--codex-home", type=Path,
                        default=Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))))
    args = parser.parse_args()
    home = args.codex_home.expanduser().resolve()
    config = tomllib.loads((home / "config.toml").read_text())
    skills = [item["name"] for item in json.loads((ROOT / "baseline/sources.json").read_text())["skills"]]
    for name in skills:
        if not (home / "skills" / name / "SKILL.md").is_file():
            raise RuntimeError("Missing skill: " + name)
    for key, value in {"web_search": "live", "plan_mode_reasoning_effort": "xhigh"}.items():
        if config.get(key) != value:
            raise RuntimeError("Unexpected setting: " + key)
    if (home / "AGENTS.md").read_bytes() != (ROOT / "baseline/AGENTS.md").read_bytes():
        raise RuntimeError("Global AGENTS.md differs from the installed source")
    for name in ["context7", "workstyle_deepwiki", "workstyle_browser"]:
        if name not in config.get("mcp_servers", {}):
            raise RuntimeError("Missing MCP definition: " + name)
    browser = config["mcp_servers"]["workstyle_browser"]
    if not Path(browser["command"]).is_file() or not Path(browser["args"][0]).is_file():
        raise RuntimeError("Browser runtime is missing")
    report = {"checked_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
              "installed_skills": skills, "static_checks": "pass",
              "effective_base_settings": {key: config.get(key) for key in ["model", "model_reasoning_effort",
                  "plan_mode_reasoning_effort", "web_search", "approval_policy", "sandbox_mode"]}}
    checks = {}
    if args.mcp:
        checks.update({"context7": lambda: check_context7(config["mcp_servers"]["context7"]),
                       "workstyle_deepwiki": lambda: workflow_check.check_deepwiki(config["mcp_servers"]["workstyle_deepwiki"]),
                       "workstyle_browser": lambda: workflow_check.check_browser(browser)})
    if args.codex:
        checks["ordinary_codex_prompt"] = lambda: check_prompt(home, skills)
    with ThreadPoolExecutor(max_workers=max(1, len(checks))) as pool:
        futures = {pool.submit(check): name for name, check in checks.items()}
        for future in as_completed(futures):
            name = futures[future]
            try:
                report[name] = {"status": "pass", **future.result()}
            except Exception as error:
                report[name] = {"status": "fail", "error": str(error)}
            print(name + ": " + report[name]["status"], flush=True)
    if checks:
        (ROOT / "baseline/check-results.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if any(isinstance(value, dict) and value.get("status") == "fail" for value in report.values()) else 0


if __name__ == "__main__":
    raise SystemExit(main())
