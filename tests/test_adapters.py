"""Portable CLI contracts and ownership protection, using temporary homes only."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from support import checkout


class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.root, self.env = checkout(self.base)
        self.home = Path(self.env["WORKSTYLE_HOME"])
        self.bindir = self.base / "bin"
        self.project = self.base / "project with spaces"
        self.project.mkdir()
        self.codex = self.base / "codex home"
        self.codex.mkdir()
        (self.codex / "workstyle.config.toml").write_text("# test profile\n")
        self.env["CODEX_HOME"] = str(self.codex)
        for name in ("codex", "claude", "cursor-agent"):
            binary = self.base / "runtime" / name
            binary.write_text("""#!/usr/bin/env python3
import json, os, sys
if '--help' in sys.argv:
    print('Cursor Agent --profile --cd --plugin-dir --append-system-prompt --workspace --resume --continue')
elif '--version' in sys.argv:
    print('0.167.2')
elif 'validate' in sys.argv:
    print('Validation passed')
else:
    print(json.dumps({'argv': sys.argv[1:], 'cwd': os.getcwd()}))
""")
            binary.chmod(0o755)

    def install(self, name, *flags, check=True):
        return subprocess.run([sys.executable, str(self.root / "workflow/adapter_install.py"),
                               "--harness", name, "--bin-dir", str(self.bindir), *map(str, flags)],
                              env=self.env, capture_output=True, text=True, check=check)

    def launch(self, *flags, check=True, legacy=False):
        script = self.root / "bin" / ("codex-work" if legacy else "workstyle")
        return subprocess.run([sys.executable, str(script), *map(str, flags)], cwd=self.project,
                              env=self.env, capture_output=True, text=True, check=check)

    def snapshot(self, path):
        return {str(p.relative_to(path)): p.read_bytes() for p in path.rglob("*") if p.is_file()}

    def test_native_install_repeat_remove_preserves_accounts_and_project(self):
        for name in ("claude", "cursor"):
            self.install(name)
            bundle = self.home / "plugins" / name
            self.assertEqual(len(list((bundle / "skills").iterdir())), 14)
            before = self.snapshot(bundle)
            self.install(name)
            self.assertEqual(self.snapshot(bundle), before)
            self.assertFalse((self.home / "backups").exists())
            self.install(name, "--check")
        self.assertEqual(list(self.project.iterdir()), [])
        self.assertEqual(list(self.codex.iterdir()), [self.codex / "workstyle.config.toml"])
        self.install("claude", "--uninstall")
        self.assertTrue((self.bindir / "workstyle").is_symlink())
        self.install("cursor", "--uninstall")
        self.assertFalse((self.bindir / "workstyle").exists())
        self.install("cursor", "--uninstall")
        self.install("cursor")

    def test_generated_plugins_keep_references_licenses_and_explicit_invocation(self):
        source = self.snapshot(self.root / "workflow/upstream")
        for name in ("claude", "cursor"):
            self.install(name)
            bundle = self.home / "plugins" / name
            self.assertTrue((bundle / "licenses/workflow.LICENSE").is_file())
            self.assertTrue((bundle / "skills/teach/MISSION-FORMAT.md").is_file())
            self.assertTrue((bundle / "skills/workstyle-task/references/task-record.md").is_file())
            for skill in ("teach", "retro"):
                self.assertIn("disable-model-invocation: true", (bundle / "skills" / skill / "SKILL.md").read_text())
            mcp = json.loads((bundle / (".mcp.json" if name == "claude" else "mcp.json")).read_text())["mcpServers"]
            self.assertEqual(mcp["workstyle_deepwiki"]["type"], "http")
            self.assertIn("--isolated", mcp["workstyle_browser"]["args"])
        self.assertEqual(source, self.snapshot(self.root / "workflow/upstream"))
        rule = (self.home / "plugins/cursor/rules/workstyle.mdc").read_text()
        self.assertIn("alwaysApply: true", rule)
        self.assertIn((self.root / "workflow/core.md").read_text(), rule)

    def test_workflow_only_contains_five_skills(self):
        self.install("claude", "--workflow-only")
        bundle = self.home / "plugins/claude"
        self.assertEqual(len(list((bundle / "skills").iterdir())), 5)
        self.assertNotIn("个人工作约定", (bundle / "rules.md").read_text())

    def test_conflicts_stop_before_creating_launcher_or_state(self):
        plugin = self.home / "plugins/claude"
        plugin.mkdir(parents=True)
        (plugin / "mine").write_text("personal\n")
        run = self.install("claude", check=False)
        self.assertNotEqual(run.returncode, 0)
        self.assertEqual((plugin / "mine").read_text(), "personal\n")
        self.assertFalse(self.bindir.exists())
        self.assertFalse((self.home / "installs").exists())

    def test_foreign_launcher_is_preserved(self):
        self.bindir.mkdir()
        (self.bindir / "workstyle").write_text("mine\n")
        run = self.install("cursor", check=False)
        self.assertNotEqual(run.returncode, 0)
        self.assertFalse(self.home.exists())

    def test_file_instead_of_bin_directory_fails_before_any_installation(self):
        self.bindir.write_text("personal file\n")
        self.assertNotEqual(self.install("claude", check=False).returncode, 0)
        self.assertFalse(self.home.exists())
        self.bindir.unlink()
        self.install("claude")

    def test_running_bundled_python_does_not_block_launch_update_or_remove(self):
        self.install("claude")
        bundle = self.home / "plugins/claude"
        script = bundle / "skills/scientific-visualization/scripts/_common.py"
        subprocess.run([sys.executable, "-m", "py_compile", str(script)], check=True)
        self.assertTrue(list(bundle.rglob("*.pyc")))
        self.launch("--harness", "claude")
        self.install("claude", "--update")
        self.install("claude", "--uninstall")
        self.assertFalse(bundle.exists())

    def test_uninstall_readonly_subdirectory_preserves_complete_backup(self):
        self.install("cursor")
        bundle = self.home / "plugins/cursor"
        before = self.snapshot(bundle)
        (bundle / "rules").chmod(0o500)
        try:
            self.install("cursor", "--uninstall")
            backup = next((self.home / "backups").glob("cursor-uninstalled-*/cursor"))
            self.assertEqual(self.snapshot(backup), before)
            self.assertFalse(bundle.exists())
            self.assertFalse((self.home / "installs/cursor.json").exists())
            self.install("cursor")
        finally:
            for path in self.home.glob("**/rules"):
                path.chmod(0o755)

    def test_failed_state_write_rolls_back_new_install_and_update(self):
        program = '''
from pathlib import Path
from unittest.mock import patch
import sys
sys.path.insert(0, sys.argv[1])
import adapter_install as adapter
real_write = adapter.atomic_write
def fail_state(path, data):
    if path.name == 'claude.json':
        raise OSError('injected state write failure')
    real_write(path, data)
with patch.object(adapter, 'atomic_write', fail_state):
    try:
        adapter.install_adapter(Path(sys.argv[2]), 'claude', Path(sys.argv[3]), adapter.render_plugin('claude'), update=True)
    except OSError:
        pass
    else:
        raise SystemExit('failure was not exercised')
'''
        command = [sys.executable, "-c", program, str(self.root / "workflow"), str(self.home), str(self.bindir)]
        subprocess.run(command, env=self.env, check=True, capture_output=True)
        self.assertFalse((self.home / "plugins/claude").exists())
        self.assertFalse((self.home / "installs/claude.json").exists())
        self.assertFalse((self.home / "settings.json").exists())
        self.assertFalse((self.bindir / "workstyle").exists())
        self.install("claude")
        bundle = self.home / "plugins/claude"
        before = self.snapshot(bundle)
        state = (self.home / "installs/claude.json").read_bytes()
        core = self.root / "workflow/core.md"
        core.write_text(core.read_text() + "\nUpdated instructions.\n")
        subprocess.run(command, env=self.env, check=True, capture_output=True)
        self.assertEqual(self.snapshot(bundle), before)
        self.assertEqual((self.home / "installs/claude.json").read_bytes(), state)
        self.launch("--harness", "claude")
        self.install("claude", "--update")

    def test_update_backs_up_and_older_source_can_restore(self):
        self.install("claude")
        bundle = self.home / "plugins/claude"
        old_bundle = self.snapshot(bundle)
        core = self.root / "workflow/core.md"
        old_core = core.read_bytes()
        core.write_bytes(old_core + b"\nNew test convention.\n")
        self.assertNotEqual(self.install("claude", check=False).returncode, 0)
        self.assertEqual(self.snapshot(bundle), old_bundle)
        self.install("claude", "--update")
        backup = next((self.home / "backups").glob("*/claude"))
        self.assertEqual(self.snapshot(backup), old_bundle)
        core.write_bytes(old_core)
        self.install("claude", "--update")
        self.assertEqual(self.snapshot(bundle), old_bundle)

    def test_user_changes_and_new_files_block_update_remove_and_launch(self):
        self.install("cursor")
        bundle = self.home / "plugins/cursor"
        (bundle / "personal.md").write_text("keep\n")
        before = self.snapshot(bundle)
        for flags in (("--update",), ("--uninstall",), ("--check",)):
            run = self.install("cursor", *flags, check=False)
            self.assertNotEqual(run.returncode, 0)
            self.assertEqual(self.snapshot(bundle), before)
        self.assertNotEqual(self.launch("--harness", "cursor", check=False).returncode, 0)

    def test_symlink_state_and_plugin_are_not_followed(self):
        self.home.mkdir()
        external = self.base / "external.json"
        external.write_text("{}\n")
        (self.home / "settings.json").symlink_to(external)
        self.assertNotEqual(self.install("claude", check=False).returncode, 0)
        self.assertEqual(external.read_text(), "{}\n")
        (self.home / "settings.json").unlink()
        self.install("claude")
        bundle = self.home / "plugins/claude"
        (bundle / "outside").symlink_to(self.project, target_is_directory=True)
        self.assertNotEqual(self.install("claude", "--uninstall", check=False).returncode, 0)
        self.assertTrue(self.project.is_dir())

    def test_select_once_override_once_and_legacy_always_codex(self):
        self.install("claude")
        self.install("cursor")
        self.launch("use", "cursor")
        current = json.loads(self.launch().stdout)
        self.assertIn("--workspace", current["argv"])
        self.assertEqual(current["cwd"], str(self.project))
        once = json.loads(self.launch("--harness", "claude").stdout)
        self.assertIn("--append-system-prompt", once["argv"])
        self.assertEqual(json.loads((self.home / "settings.json").read_text())["harness"], "cursor")
        old = json.loads(self.launch(legacy=True).stdout)
        self.assertEqual(old["argv"][:2], ["--profile", "workstyle"])
        self.assertEqual(list(self.project.iterdir()), [])

    def test_native_cwd_explicit_paths_and_requests_remain_literal(self):
        other = self.base / 'other "项目"'
        other.mkdir()
        request = 'task $(touch must-not-exist) `echo secret` $HOME\nnext line'
        for name in ("claude", "cursor"):
            self.install(name)
            current = json.loads(self.launch("--harness", name).stdout)
            self.assertEqual(current["cwd"], str(self.project))
            self.assertTrue(current["argv"][-1].startswith("项目接手："))
            run = json.loads(self.launch("--harness", name, "-C", other, "--request", request).stdout)
            self.assertEqual(run["cwd"], str(other))
            self.assertTrue(run["argv"][-1].endswith("User request:\n" + request))
            self.assertIn("skills/workstyle-task/SKILL.md", run["argv"][-1])
        self.assertEqual(list(other.iterdir()), [])
        self.assertEqual(list(self.project.iterdir()), [])

    def test_native_resume_is_distinct_from_shared_task_recovery(self):
        for name in ("claude", "cursor"):
            self.install(name)
            for flags, tail in (((), "--resume"), (("--last",), "--continue")):
                run = json.loads(self.launch("resume", "--harness", name, *flags).stdout)
                self.assertEqual(run["argv"][-1], tail)
                self.assertNotIn("项目接手：", run["argv"][-1])
            task = json.loads(self.launch("continue", "--harness", name).stdout)
            self.assertIn(".workstyle/tasks/", task["argv"][-1])
            for mode, skill in (("learn", "teach"), ("retro", "retro")):
                run = json.loads(self.launch(mode, "--harness", name, "--request", "topic").stdout)
                self.assertIn("skills/" + skill + "/SKILL.md", run["argv"][-1])
        self.assertEqual(list(self.project.iterdir()), [])

    def test_cursor_core_is_in_each_fresh_prompt_but_not_native_resume(self):
        self.install("cursor")
        rules = (self.home / "plugins/cursor/rules.md").read_text()
        cases = ((), ("learn",), ("continue",), ("retro",), ("--request", "task"), ("learn", "--request", "topic"))
        for flags in cases:
            run = json.loads(self.launch(*flags).stdout)
            self.assertIn(rules, run["argv"][-1])
        for flags in (("resume",), ("resume", "--last")):
            run = json.loads(self.launch(*flags).stdout)
            self.assertFalse(any(rules in part for part in run["argv"]))

    def test_native_dry_run_validates_rules_before_reading_them(self):
        self.install("claude")
        rules = self.home / "plugins/claude/rules.md"
        rules.unlink()
        external = self.base / "personal.txt"
        external.write_text("must not be printed\n")
        rules.symlink_to(external)
        run = self.launch("--dry-run", check=False)
        self.assertNotEqual(run.returncode, 0)
        self.assertNotIn("must not be printed", run.stdout + run.stderr)

    def test_dry_run_and_invalid_selection_do_not_write(self):
        self.launch("use", "cursor", "--dry-run")
        self.assertFalse(self.home.exists())
        run = json.loads(self.launch("--harness", "codex", "--dry-run").stdout)
        self.assertEqual(run["cwd"], str(self.project))
        self.assertEqual(run["harness"], "codex")
        for flags in (("use", "unknown"), ("use", "claude"), ("use", "codex", "--last")):
            self.assertNotEqual(self.launch(*flags, check=False).returncode, 0)
        self.assertFalse(self.home.exists())

    def test_unsupported_cli_fails_before_execution(self):
        self.install("cursor")
        binary = self.base / "runtime/cursor-agent"
        binary.write_text("#!/bin/sh\necho old-cli\n")
        run = self.launch("--harness", "cursor", check=False)
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("required interface", run.stderr)

    def test_native_bootstrap_does_not_need_or_install_codex(self):
        (self.base / "runtime/codex").write_text("#!/bin/sh\nexit 91\n")
        home = self.base / "must stay absent"
        run = subprocess.run([sys.executable, str(self.root / "workflow/bootstrap.py"), "--harness", "claude",
                              "--skip-deps", "--codex-home", str(home), "--bin-dir", str(self.bindir)],
                             env=self.env, capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertFalse(home.exists())
        self.assertTrue((self.home / "plugins/claude/.claude-plugin/plugin.json").is_file())


if __name__ == "__main__":
    unittest.main()
