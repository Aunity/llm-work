#!/usr/bin/env python3
"""Manage Workstyle's launcher and session-local CLI plugins, never account settings."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile

from harnesses import HARNESSES, ROOT, executable, load_json, plugin_path, workstyle_home
from install import SKILLS, atomic_write, profile_text


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def safe_home(home):
    for path in (home, home / "installs", home / "plugins", home / "backups"):
        if path.is_symlink() or (path.exists() and not path.is_dir()):
            raise RuntimeError("Workstyle directory must be a real directory: " + str(path))
    load_json(home / "settings.json")


def save_selection(home, harness):
    safe_home(home)
    settings = load_json(home / "settings.json")
    settings["harness"] = harness
    home.mkdir(parents=True, exist_ok=True, mode=0o700)
    atomic_write(home / "settings.json", json_bytes(settings))


def tree_files(directory):
    if directory.is_symlink():
        raise RuntimeError("Plugin directory must not be a symlink: " + str(directory))
    if not directory.exists():
        return None
    if not directory.is_dir():
        raise RuntimeError("Plugin path is not a directory: " + str(directory))
    files = {}
    for path in sorted(directory.rglob("*")):
        if path.is_symlink() or not (path.is_dir() or path.is_file()):
            raise RuntimeError("Plugin contains a symlink or special file: " + str(path))
        relative = path.relative_to(directory)
        if "__pycache__" in relative.parts or path.suffix == ".pyc":
            continue
        if path.is_file():
            files[str(relative)] = (path.read_bytes(), stat.S_IMODE(path.stat().st_mode))
    return files


def fingerprints(files):
    return {name: {"sha256": hashlib.sha256(data).hexdigest(), "mode": mode}
            for name, (data, mode) in files.items()}


def render_plugin(harness, browser=None, workflow_only=False):
    try:
        import tomllib
    except ImportError:
        import tomli as tomllib
    config = tomllib.loads(profile_text(browser))
    files = {}

    def put(path, value):
        files[path] = (value.encode("utf-8") if isinstance(value, str) else value, 0o644)

    skills = dict(SKILLS)
    if not workflow_only:
        skills.update({path.name: path for path in (ROOT / "baseline/skills").iterdir() if path.is_dir()})
    for name, source in skills.items():
        if not (source / "SKILL.md").is_file():
            raise RuntimeError("Missing source skill: " + name)
        for relative, value in tree_files(source).items():
            if "__pycache__" in Path(relative).parts or relative.endswith(".pyc"):
                continue
            if relative == "SKILL.md" and name in ("teach", "retro"):
                # The vendored Codex versions keep this policy in openai.yaml.
                # Restore the native Agent Skills field only in generated copies.
                data, mode = value
                value = (data.replace(b"---\n", b"---\ndisable-model-invocation: true\n", 1), mode)
            files["skills/" + name + "/" + relative] = value
    for path in (ROOT / "baseline/licenses").iterdir():
        put("licenses/" + path.name, path.read_bytes())
    put("licenses/workflow.LICENSE", (ROOT / "workflow/upstream/LICENSE").read_bytes())
    for section in ("baseline", "workflow"):
        put("sources/" + section + ".json", (ROOT / section / "sources.json").read_bytes())
    rules = (ROOT / "workflow/core.md").read_text(encoding="utf-8")
    if not workflow_only:
        rules += "\n" + (ROOT / "baseline/AGENTS.md").read_text(encoding="utf-8")
    put("rules.md", rules)
    manifest = {"name": "workstyle", "version": "1.0.0", "description": "Project-oriented work, learning and task handoff across terminal CLIs",
                "author": {"name": "Workstyle contributors"}}
    if harness == "cursor":
        put("rules/workstyle.mdc", "---\ndescription: Workstyle task execution and project handoff\nalwaysApply: true\n---\n\n" + rules)
    put("." + harness + "-plugin/plugin.json", json_bytes(manifest))
    servers = {"workstyle_deepwiki": {"type": "http", "url": config["mcp_servers"]["workstyle_deepwiki"]["url"]}}
    browser_config = config["mcp_servers"]["workstyle_browser"]
    servers["workstyle_browser"] = {"type": "stdio", "command": browser_config["command"], "args": browser_config["args"]}
    put(".mcp.json" if harness == "claude" else "mcp.json", json_bytes({"mcpServers": servers}))
    return files


def owned_state(home, harness):
    path = home / "installs" / (harness + ".json")
    state = load_json(path)
    if path.exists() and (state.get("root") != str(ROOT) or state.get("harness") != harness
                          or not isinstance(state.get("files"), dict) or not isinstance(state.get("bin_dir"), str)):
        raise RuntimeError("Installation belongs to another checkout or has invalid metadata: " + str(path))
    return state


def verify_installation(home, harness):
    safe_home(home)
    state = owned_state(home, harness)
    if not state:
        raise RuntimeError("Workstyle is not installed for " + harness + "; run python3 workflow/bootstrap.py --harness " + harness)
    if harness != "codex":
        files = tree_files(plugin_path(home, harness))
        if files is None or fingerprints(files) != state["files"]:
            raise RuntimeError("Plugin is missing or locally edited; preserve your changes before reinstalling: " + str(plugin_path(home, harness)))
    return state


def install_adapter(home, harness, bindir, rendered=None, update=False, uninstall=False):
    safe_home(home)
    for directory in (home, bindir):
        for path in (directory, *directory.parents):
            if path.exists() and not path.is_dir():
                raise RuntimeError("Installation directory is blocked by a file: " + str(path))
    state = owned_state(home, harness)
    link = bindir / "llm-work"
    source = ROOT / "bin/llm-work"
    legacy_link = bindir / "workstyle"
    legacy_source = ROOT / "bin/workstyle"
    legacy_target = (os.readlink(legacy_link) if legacy_link.is_symlink()
                     and legacy_link.resolve() == legacy_source.resolve() else None)
    if os.path.lexists(link) and not (link.is_symlink() and link.resolve() == source.resolve()):
        raise RuntimeError("Existing launcher left untouched: " + str(link))
    if state and state["bin_dir"] != str(bindir):
        raise RuntimeError("Use the original --bin-dir for this installation: " + state["bin_dir"])
    bundle = plugin_path(home, harness)
    current = tree_files(bundle) if harness != "codex" else None
    if current is not None and (not state or fingerprints(current) != state["files"]):
        raise RuntimeError("Plugin is untracked or locally edited; left untouched: " + str(bundle))
    if not uninstall and current is not None and current != rendered and not update:
        raise RuntimeError("Plugin differs from source; use --update for an unedited managed plugin")
    others = [owned_state(home, name) for name in HARNESSES if name != harness]
    state_path = home / "installs" / (harness + ".json")
    if uninstall:
        # Move the complete snapshot out of service before removing metadata.
        # A recursive delete could destroy half a bundle before failing.
        backup = None
        state_removed = link_removed = legacy_removed = False
        previous_state = state_path.read_bytes() if state else None
        try:
            if current is not None:
                backups = home / "backups"
                backups.mkdir(exist_ok=True)
                destination = Path(tempfile.mkdtemp(prefix=harness + "-uninstalled-", dir=backups)) / harness
                bundle.rename(destination)
                backup = destination
                atomic_write(backup.parent / "install.json", previous_state)
            if state:
                state_path.unlink()
                state_removed = True
            if not any(item.get("bin_dir") == str(bindir) for item in others):
                if link.is_symlink():
                    link.unlink()
                    link_removed = True
                if legacy_target is not None:
                    legacy_link.unlink()
                    legacy_removed = True
        except (OSError, RuntimeError, ValueError):
            if backup:
                backup.rename(bundle)
            if state_removed:
                atomic_write(state_path, previous_state)
            if link_removed:
                link.symlink_to(source)
            if legacy_removed:
                legacy_link.symlink_to(legacy_target)
            raise
        if backup:
            print("Uninstalled plugin backup:", backup)
        print("Removed Workstyle adapter:", harness, "(saved CLI preference retained)")
        return
    home.mkdir(parents=True, exist_ok=True, mode=0o700)
    (home / "installs").mkdir(exist_ok=True)
    previous_state = state_path.read_bytes() if state_path.exists() else None
    link_created = state_written = settings_created = bundle_changed = legacy_removed = False
    backup = None
    try:
        if rendered is not None and current != rendered:
            (home / "plugins").mkdir(exist_ok=True)
            with tempfile.TemporaryDirectory(prefix=".workstyle-stage-", dir=home) as temporary:
                stage = Path(temporary) / harness
                stage.mkdir()
                for relative, (data, mode) in rendered.items():
                    path = stage / relative
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(data)
                    path.chmod(mode)
                if current is not None:
                    backups = home / "backups"
                    backups.mkdir(exist_ok=True)
                    destination = Path(tempfile.mkdtemp(prefix=harness + "-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-", dir=backups)) / harness
                    bundle.rename(destination)
                    backup = destination
                stage.rename(bundle)
                bundle_changed = True
        bindir.mkdir(parents=True, exist_ok=True)
        if not link.is_symlink():
            link.symlink_to(source)
            link_created = True
        if not (home / "settings.json").exists():
            save_selection(home, harness)
            settings_created = True
        atomic_write(state_path, json_bytes({"root": str(ROOT), "harness": harness, "bin_dir": str(bindir),
                                           "files": fingerprints(rendered or {})}))
        state_written = True
        if legacy_target is not None:
            legacy_link.unlink()
            legacy_removed = True
    except (OSError, RuntimeError, ValueError):
        if bundle_changed:
            shutil.rmtree(bundle)
        if backup:
            backup.rename(bundle)
        if link_created:
            link.unlink()
        if settings_created:
            (home / "settings.json").unlink()
        if state_written:
            if previous_state is None:
                state_path.unlink()
            else:
                atomic_write(state_path, previous_state)
        if legacy_removed:
            legacy_link.symlink_to(legacy_target)
        raise
    if backup:
        print("Plugin backup:", backup)
    print("Ready:", harness, "— run llm-work (or llm-work --harness " + harness + ")")


def check_adapter(home, harness, mcp=False):
    binary = executable(harness, probe=True)
    state = verify_installation(home, harness)
    report = {"harness": harness, "static_checks": "pass", "files": len(state["files"])}
    bundle = plugin_path(home, harness)
    if harness == "claude":
        subprocess.run([binary, "plugin", "validate", str(bundle)], check=True, timeout=30)
    if mcp:
        if harness == "codex":
            raise RuntimeError("Use llm-work --harness codex doctor --mcp for Codex")
        from check import check_browser, check_deepwiki
        servers = load_json(bundle / (".mcp.json" if harness == "claude" else "mcp.json"))["mcpServers"]
        for name, checker in (("workstyle_deepwiki", check_deepwiki), ("workstyle_browser", check_browser)):
            try:
                report[name] = {"status": "pass", **checker(servers[name])}
            except Exception as error:
                report[name] = {"status": "fail", "error": str(error)}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if any(isinstance(value, dict) and value.get("status") == "fail" for value in report.values()) else 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--harness", choices=HARNESSES, required=True)
    parser.add_argument("--workstyle-home", type=Path, default=workstyle_home())
    parser.add_argument("--bin-dir", type=Path, default=Path.home() / ".local/bin")
    parser.add_argument("--browser-executable", type=Path)
    parser.add_argument("--workflow-only", action="store_true")
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument("--update", action="store_true")
    actions.add_argument("--uninstall", action="store_true")
    actions.add_argument("--check", action="store_true")
    parser.add_argument("--mcp", action="store_true")
    args = parser.parse_args()
    if args.mcp and not args.check:
        parser.error("--mcp requires --check")
    home = args.workstyle_home.expanduser().absolute()
    if args.check:
        return check_adapter(home, args.harness, args.mcp)
    rendered = None if args.uninstall or args.harness == "codex" else render_plugin(
        args.harness, args.browser_executable, args.workflow_only)
    install_adapter(home, args.harness, args.bin_dir.expanduser().resolve(), rendered, args.update, args.uninstall)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, OSError, ValueError, subprocess.SubprocessError) as error:
        print("Adapter stopped:", error, file=sys.stderr)
        raise SystemExit(1)
