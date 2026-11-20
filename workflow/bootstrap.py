#!/usr/bin/env python3
"""Prepare pinned browser dependencies, install Workstyle, and check the result."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
BROWSER = ROOT / "workflow/browser"


def run(command, cwd=ROOT):
    print("Running:", " ".join(map(str, command)), flush=True)
    subprocess.run([str(part) for part in command], cwd=cwd, check=True)


def prerequisites():
    if sys.version_info < (3, 10):
        raise RuntimeError("Python 3.10 or newer is required")
    if sys.version_info < (3, 11) and importlib.util.find_spec("tomli") is None:
        raise RuntimeError("Python 3.10 needs tomli; install requirements.txt in your Python environment")
    for name in ("node", "npm", "codex"):
        if not shutil.which(name):
            raise RuntimeError(name + " is missing from PATH; see QUICKSTART.md")
    node = subprocess.check_output(["node", "--version"], text=True).strip()
    if int(node.lstrip("v").split(".")[0]) < 20:
        raise RuntimeError("Pinned Playwright requires Node >=20; found " + node)
    codex = subprocess.check_output(["codex", "--version"], text=True).strip()
    match = re.search(r"(\d+)\.(\d+)\.(\d+)", codex)
    if not match or tuple(map(int, match.groups())) < (0, 134, 0):
        raise RuntimeError("Separate profile files require Codex >=0.134.0; found " + codex)
    print("Runtime:", sys.version.split()[0], node, codex, flush=True)


def check_packages():
    locked = json.loads((BROWSER / "package-lock.json").read_text())["packages"]
    for name, package in locked.items():
        if not name or package.get("optional"):
            continue
        installed = BROWSER / name / "package.json"
        if not installed.is_file() or json.loads(installed.read_text())["version"] != package["version"]:
            raise RuntimeError("Missing or mismatched " + name + "; rerun without --skip-deps")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--codex-home", type=Path,
                        default=Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))))
    parser.add_argument("--bin-dir", type=Path, default=Path.home() / ".local/bin")
    parser.add_argument("--workflow-only", action="store_true", help="leave ordinary Codex configuration untouched")
    parser.add_argument("--skip-deps", action="store_true", help="use already prepared pinned npm packages and browser")
    parser.add_argument("--browser-executable", type=Path, help="use existing Chrome/Chromium instead of downloading it")
    parser.add_argument("--with-system-deps", action="store_true", help="allow Playwright to install OS libraries (may need sudo)")
    parser.add_argument("--update", action="store_true", help="refresh installed files that have no local edits")
    parser.add_argument("--mcp", action="store_true", help="also exercise external MCPs and browser interaction")
    args = parser.parse_args()
    if args.skip_deps and args.with_system_deps:
        parser.error("--skip-deps and --with-system-deps cannot be combined")
    if args.browser_executable and args.with_system_deps:
        parser.error("install OS libraries for a custom browser separately")
    prerequisites()
    home, bindir = args.codex_home.expanduser().resolve(), args.bin_dir.expanduser().resolve()
    if not args.skip_deps:
        run(["npm", "ci", "--ignore-scripts", "--no-audit", "--no-fund"], cwd=BROWSER)
    check_packages()
    if not args.skip_deps and not args.browser_executable:
        command = ["node", BROWSER / "node_modules/playwright/cli.js", "install", "chromium", "--no-shell"]
        if args.with_system_deps:
            command.append("--with-deps")
        run(command, cwd=BROWSER)
    common = ["--codex-home", home]
    update = ["--update"] if args.update else []
    browser = ["--browser-executable", args.browser_executable.expanduser().resolve()] if args.browser_executable else []
    run([sys.executable, ROOT / "workflow/install.py", *common, "--bin-dir", bindir, *update, *browser])
    if not args.workflow_only:
        run([sys.executable, ROOT / "baseline/apply.py", *common, *update])
    run([sys.executable, ROOT / "workflow/check.py", *common, *(["--mcp"] if args.mcp else [])])
    if not args.workflow_only:
        run([sys.executable, ROOT / "baseline/check.py", *common, *(["--mcp"] if args.mcp else [])])
    print("Installed and checked. Add", bindir, "to PATH and start a new Codex session.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, OSError, ValueError, subprocess.SubprocessError) as error:
        print("Bootstrap stopped:", error, file=sys.stderr)
        print("Completed stages are retained; resolve the error and rerun. See QUICKSTART.md for rollback.", file=sys.stderr)
        raise SystemExit(1)
