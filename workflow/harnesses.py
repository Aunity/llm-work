"""CLI capabilities and Workstyle-owned paths; no account configuration is read."""
import json
import os
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parent.parent
HARNESSES = {
    "codex": (("codex",), ("--profile", "--cd")),
    "claude": (("claude",), ("--plugin-dir", "--append-system-prompt", "--resume", "--continue")),
    "cursor": (("cursor-agent", "agent"), ("--plugin-dir", "--workspace", "--resume", "--continue")),
}


def workstyle_home():
    return Path(os.environ.get("WORKSTYLE_HOME", str(Path.home() / ".local/share/workstyle"))).expanduser().absolute()


def codex_home():
    return Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))).expanduser().resolve()


def load_json(path):
    if path.is_symlink():
        raise RuntimeError("Workstyle metadata must not be a symlink: " + str(path))
    if not path.exists():
        return {}
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError("Expected a JSON object: " + str(path))
    return value


def selected_harness(home):
    name = load_json(home / "settings.json").get("harness", "codex")
    if not isinstance(name, str) or name not in HARNESSES:
        raise RuntimeError("Unknown saved harness; select one with llm-work use codex|claude|cursor")
    return name


def executable(name, probe=False):
    candidates, required = HARNESSES[name]
    binary = next((found for candidate in candidates if (found := shutil.which(candidate))), None)
    if not binary:
        raise RuntimeError("Install " + " or ".join(candidates) + " and add it to PATH; see QUICKSTART.md")
    if probe:
        result = subprocess.run([binary, "--help"], capture_output=True, text=True, timeout=20)
        help_text = result.stdout + result.stderr
        missing = [flag for flag in required if flag not in help_text]
        if result.returncode or missing or (name == "cursor" and "Cursor Agent" not in help_text):
            raise RuntimeError(name + " CLI does not support the required interface; update it. Missing: " + ", ".join(missing))
    return binary


def plugin_path(home, name):
    return home / "plugins" / name
