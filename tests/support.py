"""Isolated checkout and inert runtime for installer tests (no downloads/login)."""
import json
import os
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent.parent


def checkout(directory):
    root = Path(directory) / "checkout with spaces"
    root.mkdir()
    for name in ("baseline", "workflow", "bin"):
        shutil.copytree(ROOT / name, root / name,
                        ignore=shutil.ignore_patterns("node_modules", "__pycache__", "*-results.json", "install-result.json"))
    runtime = Path(directory) / "runtime"
    runtime.mkdir()
    chrome = runtime / "chromium"
    chrome.write_text("#!/bin/sh\nexit 0\n")
    chrome.chmod(0o755)
    node = runtime / "node"
    node.write_text("#!/usr/bin/env python3\nimport sys\nprint('v22.0.0' if '--version' in sys.argv else " + repr(str(chrome)) + ")\n")
    node.chmod(0o755)
    for name, output in (("npm", "10.0.0"), ("codex", "codex-cli 0.167.2")):
        binary = runtime / name
        binary.write_text("#!/bin/sh\nprintf '%s\\n' '" + output + "'\n")
        binary.chmod(0o755)
    browser = root / "workflow/browser"
    for name, package in json.loads((browser / "package-lock.json").read_text())["packages"].items():
        if name:
            destination = browser / name
            destination.mkdir(parents=True, exist_ok=True)
            (destination / "package.json").write_text(json.dumps({"version": package["version"]}))
    (browser / "node_modules/@playwright/mcp/cli.js").touch()
    for name, banner in (("claude", "Claude Code"), ("cursor-agent", "Cursor Agent")):
        binary = runtime / name
        binary.write_text("#!/usr/bin/env python3\nimport sys\nprint(" + repr(
            banner + " --plugin-dir --append-system-prompt --workspace --resume --continue") + ")\n")
        binary.chmod(0o755)
    env = {**os.environ, "PATH": str(runtime) + os.pathsep + os.environ["PATH"],
           "WORKSTYLE_HOME": str(Path(directory) / "workstyle home")}
    return root, env
