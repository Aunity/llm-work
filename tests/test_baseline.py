import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest
from support import checkout

ROOT = Path(__file__).resolve().parent.parent
ORIGINAL = b'''# Existing personal configuration\nmodel = "existing-model"\nmodel_reasoning_effort = "high"\n\n[model_providers.example]\nbase_url = "https://example.invalid"\nexperimental_bearer_token = "test-only-do-not-log"\n\n[features]\ntool_search = true\n\n[mcp_servers.existing]\ncommand = "existing-tool"\nargs = ["mcp"]\n'''
PROFILE = '''[mcp_servers.workstyle_deepwiki]\nurl = "https://mcp.deepwiki.com/mcp"\nrequired = false\n[mcp_servers.workstyle_browser]\ncommand = "node"\nargs = ["browser-mcp.js", "--headless"]\nrequired = false\n'''


class BaselineTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root, _ = checkout(self.temporary.name)

    def make_home(self, directory):
        home = Path(directory) / "codex"
        home.mkdir()
        (home / "config.toml").write_bytes(ORIGINAL)
        (home / "workstyle.config.toml").write_text(PROFILE)
        return home

    def run_apply(self, home, *extra):
        return subprocess.run([sys.executable, str(self.root / "baseline/apply.py"),
                               "--codex-home", str(home), *extra], capture_output=True, text=True)

    def test_install_preserves_existing_values_and_restores_original_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            home = self.make_home(directory)
            first = self.run_apply(home)
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertNotIn("test-only-do-not-log", first.stdout + first.stderr)
            report = json.loads(first.stdout)
            backup = Path(report["backup"])
            self.assertEqual((backup / "config.toml").read_bytes(), ORIGINAL)
            self.assertEqual(stat.S_IMODE(backup.stat().st_mode), 0o700)
            self.assertEqual(stat.S_IMODE((backup / "config.toml").stat().st_mode), 0o600)
            current = (home / "config.toml").read_bytes()
            self.assertIn(ORIGINAL, current)
            self.assertEqual(len(list((home / "skills").iterdir())), 9)
            second = self.run_apply(home)
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertTrue(json.loads(second.stdout)["already_configured"])
            restored = self.run_apply(home, "--restore", str(backup))
            self.assertEqual(restored.returncode, 0, restored.stderr)
            self.assertEqual((home / "config.toml").read_bytes(), ORIGINAL)
            self.assertFalse((home / "AGENTS.md").exists())
            self.assertEqual(list((home / "skills").iterdir()), [])
            self.assertEqual((home / "workstyle.config.toml").read_text(), PROFILE)

    def test_skill_conflict_causes_no_partial_install(self):
        with tempfile.TemporaryDirectory() as directory:
            home = self.make_home(directory)
            occupied = home / "skills/rdkit"
            occupied.mkdir(parents=True)
            (occupied / "owned.txt").write_text("existing user skill")
            run = self.run_apply(home)
            self.assertNotEqual(run.returncode, 0)
            self.assertEqual((home / "config.toml").read_bytes(), ORIGINAL)
            self.assertFalse((home / "AGENTS.md").exists())
            self.assertFalse((home / "backups").exists())
            self.assertEqual((occupied / "owned.txt").read_text(), "existing user skill")

    def test_restore_refuses_to_discard_later_user_edits(self):
        with tempfile.TemporaryDirectory() as directory:
            home = self.make_home(directory)
            run = self.run_apply(home)
            self.assertEqual(run.returncode, 0, run.stderr)
            backup = json.loads(run.stdout)["backup"]
            config = home / "config.toml"
            changed = config.read_bytes() + b'\n# user changed this later\n'
            config.write_bytes(changed)
            restore = self.run_apply(home, "--restore", backup)
            self.assertNotEqual(restore.returncode, 0)
            self.assertEqual(config.read_bytes(), changed)
            self.assertTrue((home / "AGENTS.md").is_file())

    def test_fresh_config_can_be_installed_and_restored_to_absence(self):
        with tempfile.TemporaryDirectory() as directory:
            home = self.make_home(directory)
            (home / "config.toml").unlink()
            run = self.run_apply(home)
            self.assertEqual(run.returncode, 0, run.stderr)
            backup = json.loads(run.stdout)["backup"]
            self.assertTrue((home / "config.toml").is_file())
            restored = self.run_apply(home, "--restore", backup)
            self.assertEqual(restored.returncode, 0, restored.stderr)
            self.assertFalse((home / "config.toml").exists())
            self.assertFalse((home / "baseline-install.json").exists())

    def test_update_refreshes_managed_values_and_rollback_restores_state(self):
        with tempfile.TemporaryDirectory() as directory:
            home = self.make_home(directory)
            self.assertEqual(self.run_apply(home).returncode, 0)
            config = home / "config.toml"
            before = config.read_bytes() + b"\n# unrelated personal change\n"
            config.write_bytes(before)
            state = (home / "baseline-install.json").read_bytes()
            agents = (home / "AGENTS.md").read_bytes()
            profile = home / "workstyle.config.toml"
            profile.write_text(PROFILE.replace("browser-mcp.js", "next-browser.js"))
            source = self.root / "baseline/AGENTS.md"
            source.write_bytes(source.read_bytes() + b"\nUpdated repository guidance.\n")
            refused = self.run_apply(home)
            self.assertNotEqual(refused.returncode, 0)
            self.assertEqual(config.read_bytes(), before)
            updated = self.run_apply(home, "--update")
            self.assertEqual(updated.returncode, 0, updated.stderr)
            self.assertIn(b"next-browser.js", config.read_bytes())
            self.assertIn(b"unrelated personal change", config.read_bytes())
            self.assertIn(b"Updated repository guidance", (home / "AGENTS.md").read_bytes())
            restored = self.run_apply(home, "--restore", json.loads(updated.stdout)["backup"])
            self.assertEqual(restored.returncode, 0, restored.stderr)
            self.assertEqual(config.read_bytes(), before)
            self.assertEqual((home / "AGENTS.md").read_bytes(), agents)
            self.assertEqual((home / "baseline-install.json").read_bytes(), state)

    def test_update_refuses_locally_modified_managed_mcp(self):
        with tempfile.TemporaryDirectory() as directory:
            home = self.make_home(directory)
            self.assertEqual(self.run_apply(home).returncode, 0)
            config = home / "config.toml"
            edited = config.read_bytes().replace(b"browser-mcp.js", b"my-personal-browser.js")
            config.write_bytes(edited)
            run = self.run_apply(home, "--update")
            self.assertNotEqual(run.returncode, 0)
            self.assertEqual(config.read_bytes(), edited)

    def test_update_refuses_locally_modified_agents(self):
        with tempfile.TemporaryDirectory() as directory:
            home = self.make_home(directory)
            self.assertEqual(self.run_apply(home).returncode, 0)
            agents = home / "AGENTS.md"
            edited = agents.read_bytes() + b"\nPersonal guidance.\n"
            agents.write_bytes(edited)
            run = self.run_apply(home, "--update")
            self.assertNotEqual(run.returncode, 0)
            self.assertEqual(agents.read_bytes(), edited)

    def test_config_symlink_is_not_replaced(self):
        with tempfile.TemporaryDirectory() as directory:
            home = self.make_home(directory)
            config = home / "config.toml"
            config.unlink()
            target = Path(directory) / "personal-config"
            target.write_bytes(ORIGINAL)
            config.symlink_to(target)
            run = self.run_apply(home)
            self.assertNotEqual(run.returncode, 0)
            self.assertTrue(config.is_symlink())
            self.assertEqual(target.read_bytes(), ORIGINAL)

    def test_user_settings_edits_are_preserved_on_reinstall_and_update(self):
        with tempfile.TemporaryDirectory() as directory:
            home = self.make_home(directory)
            self.assertEqual(self.run_apply(home).returncode, 0)
            config = home / "config.toml"
            edited = config.read_bytes().replace(b'web_search = "live"', b'web_search = "disabled"')
            edited = edited.replace(b'plan_mode_reasoning_effort = "xhigh"', b'plan_mode_reasoning_effort = "medium"')
            config.write_bytes(edited)
            for flags in ((), ("--update",)):
                run = self.run_apply(home, *flags)
                self.assertNotEqual(run.returncode, 0)
                self.assertEqual(config.read_bytes(), edited)

    def test_legacy_adoption_preserves_changed_settings(self):
        with tempfile.TemporaryDirectory() as directory:
            home = self.make_home(directory)
            self.assertEqual(self.run_apply(home).returncode, 0)
            (home / "baseline-install.json").unlink()
            config = home / "config.toml"
            edited = config.read_bytes().replace(b'web_search = "live"', b'web_search = "disabled"')
            config.write_bytes(edited)
            for flags in ((), ("--update",)):
                run = self.run_apply(home, *flags)
                self.assertNotEqual(run.returncode, 0)
                self.assertEqual(config.read_bytes(), edited)
                self.assertFalse((home / "baseline-install.json").exists())

    def test_legacy_backup_restore_removes_adopted_state_and_allows_reinstall(self):
        with tempfile.TemporaryDirectory() as directory:
            home = self.make_home(directory)
            run = self.run_apply(home)
            self.assertEqual(run.returncode, 0, run.stderr)
            backup = Path(json.loads(run.stdout)["backup"])
            manifest_path = backup / "manifest.json"
            manifest = json.loads(manifest_path.read_text())
            for key in ("after_state_sha256", "state_existed", "config_existed"):
                manifest.pop(key)
            manifest_path.write_text(json.dumps(manifest))
            (home / "baseline-install.json").unlink()
            adopted = self.run_apply(home, "--update")
            self.assertEqual(adopted.returncode, 0, adopted.stderr)
            restored = self.run_apply(home, "--restore", str(backup))
            self.assertEqual(restored.returncode, 0, restored.stderr)
            self.assertEqual((home / "config.toml").read_bytes(), ORIGINAL)
            self.assertFalse((home / "baseline-install.json").exists())
            reinstalled = self.run_apply(home)
            self.assertEqual(reinstalled.returncode, 0, reinstalled.stderr)


if __name__ == "__main__":
    unittest.main()
