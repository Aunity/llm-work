import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from support import checkout


class BootstrapTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.root, self.env = checkout(self.base)
        self.home, self.bindir = self.base / "empty home", self.base / "bin"

    def run_bootstrap(self, *flags):
        return subprocess.run([sys.executable, str(self.root / "workflow/bootstrap.py"), "--skip-deps",
                               "--codex-home", str(self.home), "--bin-dir", str(self.bindir), *flags],
                              cwd=self.base, env=self.env, capture_output=True, text=True)

    def test_empty_home_full_install_repeat_and_update(self):
        first = self.run_bootstrap()
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        self.assertEqual(len(list((self.home / "skills").iterdir())), 14)
        config = (self.home / "config.toml").read_bytes()
        for flags in ((), ("--update",)):
            again = self.run_bootstrap(*flags)
            self.assertEqual(again.returncode, 0, again.stdout + again.stderr)
            self.assertEqual((self.home / "config.toml").read_bytes(), config)
        self.assertEqual(len(list((self.home / "backups").iterdir())), 1)

    def test_workflow_only_keeps_base_config_absent(self):
        run = self.run_bootstrap("--workflow-only")
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertFalse((self.home / "config.toml").exists())
        self.assertFalse((self.home / "AGENTS.md").exists())
        self.assertEqual(len(list((self.home / "skills").iterdir())), 5)

    def test_dependency_mismatch_stops_before_config_changes(self):
        package = self.root / "workflow/browser/node_modules/@playwright/mcp/package.json"
        package.write_text(json.dumps({"version": "0.0.0"}))
        run = self.run_bootstrap()
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("mismatched", run.stderr)
        self.assertFalse(self.home.exists())

    def test_browser_path_is_relative_to_callers_directory(self):
        run = self.run_bootstrap("--browser-executable", "runtime/chromium")
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertIn(str(self.base / "runtime/chromium"), (self.home / "workstyle.config.toml").read_text())

    def test_later_conflict_reports_retained_stage_without_overwriting(self):
        self.home.mkdir()
        agents = self.home / "AGENTS.md"
        agents.write_text("Personal rules\n")
        run = self.run_bootstrap()
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("Completed stages are retained", run.stderr)
        self.assertEqual(agents.read_text(), "Personal rules\n")
        self.assertFalse((self.home / "config.toml").exists())
        self.assertTrue((self.home / "workstyle.config.toml").exists())
