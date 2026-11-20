#!/usr/bin/env python3
"""Apply or restore the announced ordinary-Codex baseline with private backups."""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import sys

try:
    import tomllib
except ImportError:
    import tomli as tomllib

ROOT = Path(__file__).resolve().parent.parent
UPDATES = {"web_search": "live", "plan_mode_reasoning_effort": "xhigh"}


def digest(value):
    return hashlib.sha256(value).hexdigest()


def atomic_write(path, value, mode=0o600):
    temporary = path.with_name(path.name + ".baseline-" + secrets.token_hex(4))
    with temporary.open("xb") as stream:
        os.chmod(temporary, mode)
        stream.write(value)
    temporary.replace(path)


def prepare_config(original, services, previous_services=None):
    text = original.decode("utf-8")
    before = tomllib.loads(text)
    expected = deepcopy(before)
    for key, value in UPDATES.items():
        if before.get(key) == value:
            continue
        if key in before:
            text, count = re.subn(r"(?m)^" + re.escape(key) + r"\s*=.*$",
                                  key + " = " + json.dumps(value), text, count=1)
            if count != 1:
                raise RuntimeError("Cannot safely locate top-level setting: " + key)
        else:
            text = key + " = " + json.dumps(value) + "\n" + text
        expected[key] = value
    for name, service in services.items():
        existing = before.get("mcp_servers", {}).get(name)
        if existing is not None:
            if existing != service:
                if (previous_services or {}).get(name) != existing:
                    raise RuntimeError("Existing MCP definition left untouched: " + name)
                pattern = r"(?ms)^\[mcp_servers\." + re.escape(name) + r"\][ \t]*\n.*?(?=^\[|\Z)"
                # Preserve comment-only lines, including notes after the last table.
                def keep_comments(match):
                    return "".join(line + "\n" for line in match.group().splitlines()
                                   if line.lstrip().startswith("#"))
                text, count = re.subn(pattern, keep_comments, text, count=1)
                if count != 1:
                    raise RuntimeError("Cannot safely locate managed MCP table: " + name)
            else:
                continue
        text += "\n[mcp_servers." + name + "]\n"
        for key, value in service.items():
            text += key + " = " + json.dumps(value) + "\n"
        expected.setdefault("mcp_servers", {})[name] = service
    after = tomllib.loads(text)
    if after != expected:
        raise RuntimeError("Proposed config changes values outside the announced settings")
    return text.encode("utf-8")


def restore(home, directory):
    manifest = json.loads((directory / "manifest.json").read_text())
    if Path(manifest["codex_home"]).resolve() != home:
        raise RuntimeError("Backup belongs to a different Codex home")
    config, agents = home / "config.toml", home / "AGENTS.md"
    state_path = home / "baseline-install.json"
    if any(p.is_symlink() for p in (config, agents, state_path)):
        raise RuntimeError("Restore refuses symlinked configuration or state")
    if digest(config.read_bytes()) != manifest["after_config_sha256"]:
        raise RuntimeError("Config has changed since installation; restore refused")
    if not agents.is_file() or digest(agents.read_bytes()) != manifest["after_agents_sha256"]:
        raise RuntimeError("AGENTS.md has changed since installation; restore refused")
    if "after_state_sha256" in manifest and (not state_path.is_file() or
            digest(state_path.read_bytes()) != manifest["after_state_sha256"]):
        raise RuntimeError("Installation state has changed; restore refused")
    for destination, source in manifest["added_links"].items():
        p = Path(destination)
        if os.path.lexists(p) and not (p.is_symlink() and p.resolve() == Path(source).resolve()):
            raise RuntimeError("Installed skill changed; restore refused: " + str(p))
    if manifest.get("config_existed", True):
        atomic_write(config, (directory / "config.toml").read_bytes())
    else:
        config.unlink()
    if manifest["agents_existed"]:
        atomic_write(agents, (directory / "AGENTS.md").read_bytes(), 0o644)
    else:
        agents.unlink()
    for destination in manifest["added_links"]:
        p = Path(destination)
        if p.is_symlink():
            p.unlink()
    if "after_state_sha256" in manifest:
        if manifest["state_existed"]:
            atomic_write(state_path, (directory / "baseline-install.json").read_bytes())
        else:
            state_path.unlink()
    print(json.dumps({"restored_from": str(directory)}, ensure_ascii=False))


def apply(home, report_path=None, update=False):
    config, agents = home / "config.toml", home / "AGENTS.md"
    state_path = home / "baseline-install.json"
    if any(p.is_symlink() for p in (config, agents, state_path)):
        raise RuntimeError("Existing configuration/state symlink left untouched")
    config_existed = config.exists()
    original = config.read_bytes() if config_existed else b""
    old_state = state_path.read_bytes() if state_path.exists() else None
    state = json.loads(old_state) if old_state is not None else {}
    if state or update:
        before = tomllib.loads(original.decode("utf-8"))
        previous_settings = state.get("settings", {})
        for key, value in UPDATES.items():
            if before.get(key) == value or (key not in before and key not in previous_settings):
                continue
            if not (update and key in previous_settings and before.get(key) == previous_settings[key]):
                raise RuntimeError("Locally changed baseline setting left untouched: " + key)
    profile = tomllib.loads((home / "workstyle.config.toml").read_text())
    services = {"context7": {"url": "https://mcp.context7.com/mcp", "startup_timeout_sec": 30,
                              "tool_timeout_sec": 120, "required": False}}
    for name in ["workstyle_deepwiki", "workstyle_browser"]:
        services[name] = profile["mcp_servers"][name]
    proposed = prepare_config(original, services, state.get("services") if update else None)
    desired_agents = (ROOT / "baseline/AGENTS.md").read_bytes()
    if os.path.lexists(agents) and (not agents.is_file() or (agents.read_bytes() != desired_agents and not
            (update and state.get("agents_sha256") == digest(agents.read_bytes())))):
        raise RuntimeError("Existing AGENTS.md left untouched; merge is required")
    sources = json.loads((ROOT / "baseline/sources.json").read_text())["skills"]
    added_links = {}
    for item in sources:
        name = item["name"]
        source, target = ROOT / "baseline/skills" / name, home / "skills" / name
        if not (source / "SKILL.md").is_file():
            raise RuntimeError("Missing selected skill: " + name)
        if os.path.lexists(target):
            if not (target.is_symlink() and target.resolve() == source.resolve()):
                raise RuntimeError("Existing skill left untouched: " + name)
        else:
            added_links[str(target)] = str(source)
    new_state = (json.dumps({"services": services, "settings": UPDATES,
                            "agents_sha256": digest(desired_agents)}, indent=2) + "\n").encode()
    if original == proposed and agents.is_file() and agents.read_bytes() == desired_agents and not added_links:
        atomic_write(state_path, new_state)
        print(json.dumps({"already_configured": True}))
        return
    backups = home / "backups"
    backups.mkdir(mode=0o700, parents=True, exist_ok=True)
    directory = backups / ("cli-baseline-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + secrets.token_hex(3))
    directory.mkdir(mode=0o700)
    atomic_write(directory / "config.toml", original)
    existed = agents.is_file()
    if existed:
        atomic_write(directory / "AGENTS.md", agents.read_bytes())
    if old_state is not None:
        atomic_write(directory / "baseline-install.json", old_state)
    manifest = {"codex_home": str(home), "before_config_sha256": digest(original),
                "after_config_sha256": digest(proposed), "agents_existed": existed,
                "after_agents_sha256": digest(desired_agents), "added_links": added_links,
                "config_existed": config_existed, "state_existed": old_state is not None,
                "after_state_sha256": digest(new_state)}
    atomic_write(directory / "manifest.json", (json.dumps(manifest, indent=2) + "\n").encode())
    if config.exists() != config_existed or (config_existed and config.read_bytes() != original):
        raise RuntimeError("Config changed during preparation; no configuration applied")
    for destination, source in added_links.items():
        target = Path(destination)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.symlink_to(source, target_is_directory=True)
    atomic_write(agents, desired_agents, 0o644)
    atomic_write(config, proposed)
    atomic_write(state_path, new_state)
    report = {"backup": str(directory), "skills_added": len(added_links),
              "settings": UPDATES, "mcp_names": list(services), "global_agents": str(agents)}
    if report_path:
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--codex-home", type=Path,
                        default=Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))))
    parser.add_argument("--restore", type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--update", action="store_true", help="refresh unedited managed MCP definitions and AGENTS.md")
    args = parser.parse_args()
    home = args.codex_home.expanduser().resolve()
    try:
        if args.restore:
            restore(home, args.restore.expanduser().resolve())
        else:
            apply(home, args.report, args.update)
    except (OSError, RuntimeError, KeyError, ValueError) as error:
        print("Baseline configuration stopped:", error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
