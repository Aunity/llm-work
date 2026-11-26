#!/usr/bin/env python3
"""Install or update owned Workstyle files without overwriting local edits."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import secrets
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
SKILLS = {
    "workstyle-task": ROOT / "workflow/skills/workstyle-task",
    **{name: ROOT / "workflow/upstream" / name for name in
       ["prototype", "retro", "teach", "writing-for-agents"]},
}


def digest(value):
    return hashlib.sha256(value).hexdigest()


def atomic_write(path, value):
    temporary = path.with_name(path.name + ".workstyle-" + secrets.token_hex(4))
    with temporary.open("xb") as stream:
        os.chmod(temporary, 0o600)
        stream.write(value)
    temporary.replace(path)


def profile_text(browser_executable=None):
    node = shutil.which("node")
    cli = ROOT / "workflow/browser/node_modules/@playwright/mcp/cli.js"
    if not node or not cli.is_file():
        raise RuntimeError("Node and the pinned browser package are required; run python3 workflow/bootstrap.py")
    if browser_executable is None:
        # The installed Playwright knows its revision, OS and configured cache path.
        probe = subprocess.run([node, "-e", "console.log(require('playwright').chromium.executablePath())"],
                               cwd=ROOT / "workflow/browser", capture_output=True, text=True, timeout=30)
        if probe.returncode:
            raise RuntimeError("Cannot locate pinned Chromium; run python3 workflow/bootstrap.py")
        browser_executable = Path(probe.stdout.strip())
    browser_executable = browser_executable.expanduser().resolve()
    if not browser_executable.is_file() or not os.access(browser_executable, os.X_OK):
        raise RuntimeError("Chromium is missing or not executable; run python3 workflow/bootstrap.py")
    text = (ROOT / "workflow/profile.template.toml").read_text()
    for key, value in {"NODE": node, "BROWSER_CLI": str(cli), "CHROME": str(browser_executable),
                       "CORE": (ROOT / "workflow/core.md").read_text(encoding="utf-8")}.items():
        text = text.replace("@" + key + "@", json.dumps(value))
    return text.replace("@SOURCE@", str(ROOT / "workflow/profile.template.toml"))


def links_for(codex_home, bin_dir):
    return {**{codex_home / "skills" / name: source for name, source in SKILLS.items()},
            bin_dir / "codex-work": ROOT / "bin/codex-work"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--codex-home", type=Path,
                        default=Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))))
    parser.add_argument("--bin-dir", type=Path, default=Path.home() / ".local/bin")
    parser.add_argument("--browser-executable", type=Path, help="use an existing Chrome/Chromium executable")
    parser.add_argument("--update", action="store_true", help="replace a previously installed, unedited profile")
    parser.add_argument("--uninstall", action="store_true")
    args = parser.parse_args()
    codex_home = args.codex_home.expanduser().resolve()
    bin_dir = args.bin_dir.expanduser().resolve()
    links = links_for(codex_home, bin_dir)
    profile = codex_home / "workstyle.config.toml"
    state_path = codex_home / "workstyle-install.json"
    if state_path.is_symlink():
        raise RuntimeError("Installation state must not be a symlink: " + str(state_path))
    state = json.loads(state_path.read_text()) if state_path.exists() else {}
    if os.path.lexists(profile) and (profile.is_symlink() or not profile.is_file()):
        raise RuntimeError("Existing profile left untouched: " + str(profile))
    if args.uninstall:
        if profile.exists() and (state.get("root") != str(ROOT) or
                                 state.get("profile_sha256") != digest(profile.read_bytes())):
            raise RuntimeError("Profile is untracked or locally edited; uninstall refused: " + str(profile))
        for destination, source in links.items():
            if destination.is_symlink() and destination.resolve() == source.resolve():
                destination.unlink()
                print("Removed", destination)
        if profile.is_file():
            profile.unlink()
            print("Removed", profile)
        if state_path.exists() and state.get("root") == str(ROOT):
            state_path.unlink()
        return 0
    rendered = profile_text(args.browser_executable).encode("utf-8")
    for name, source in SKILLS.items():
        if not (source / "SKILL.md").is_file():
            raise RuntimeError("Missing skill: " + name)
    for destination, source in links.items():
        if os.path.lexists(destination) and not (
            destination.is_symlink() and destination.resolve() == source.resolve()
        ):
            raise RuntimeError("Existing destination left untouched: " + str(destination))
    previous = profile.read_bytes() if profile.exists() else None
    if previous is not None and previous != rendered:
        if not (args.update and state.get("root") == str(ROOT) and
                state.get("profile_sha256") == digest(previous)):
            raise RuntimeError("Existing profile left untouched; --update requires an unedited managed profile: " + str(profile))
        backups = codex_home / "backups"
        backups.mkdir(mode=0o700, exist_ok=True)
        backup = backups / ("workstyle-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + secrets.token_hex(3))
        backup.mkdir(mode=0o700)
        atomic_write(backup / profile.name, previous)
        print("Profile backup:", backup)
    for destination, source in links.items():
        destination.parent.mkdir(parents=True, exist_ok=True)
        if not destination.is_symlink():
            destination.symlink_to(source, target_is_directory=source.is_dir())
        print("Linked", destination)
    profile.parent.mkdir(parents=True, exist_ok=True)
    if previous != rendered:
        atomic_write(profile, rendered)
    atomic_write(state_path, (json.dumps({"root": str(ROOT), "profile_sha256": digest(rendered)}, indent=2) + "\n").encode())
    print("Ready: run codex-work in your project directory (or codex-work -C /path/to/project)")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, OSError, ValueError, subprocess.TimeoutExpired) as error:
        print("Install failed:", error, file=sys.stderr)
        raise SystemExit(1)
