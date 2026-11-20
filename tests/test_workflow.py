import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from support import checkout

ROOT = Path(__file__).resolve().parent.parent


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root, self.env = checkout(self.temporary.name)

    def test_launch_keeps_user_text_literal_and_project_path_intact(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            project = base / "project with spaces"
            project.mkdir()
            home = base / "codex"
            home.mkdir()
            (home / "workstyle.config.toml").write_text("# fake profile\n")
            # A separate directory avoids conflating an executable with CODEX_HOME.
            fakebin = base / "bin"
            fakebin.mkdir()
            executable = fakebin / "codex"
            executable.write_text("#!/usr/bin/env python3\nimport sys,json\nprint(json.dumps(sys.argv[1:]))\n")
            executable.chmod(0o755)
            marker = base / "must-not-exist"
            request = "check $(touch " + str(marker) + ") `echo literal` $HOME\nsecond line"
            env = {**os.environ, "PATH": str(fakebin) + os.pathsep + os.environ["PATH"], "CODEX_HOME": str(home)}
            run = subprocess.run([sys.executable, str(ROOT / "bin/codex-work"), "work", str(project), request],
                                 env=env, capture_output=True, text=True, check=True)
            arguments = json.loads(run.stdout)
            self.assertEqual(arguments[3], str(project))
            self.assertIn(request, arguments[4])
            self.assertFalse(marker.exists())
            self.assertFalse((project / ".workstyle").exists())

    def test_install_is_additive_idempotent_and_owned_files_can_be_removed(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            home, bindir = base / "codex", base / "bin"
            home.mkdir()
            sentinel = home / "config.toml"
            sentinel.write_text('model_reasoning_effort = "high"\n')
            command = [sys.executable, str(self.root / "workflow/install.py"), "--codex-home", str(home), "--bin-dir", str(bindir)]
            subprocess.run(command, check=True, capture_output=True, env=self.env)
            profile = (home / "workstyle.config.toml").read_bytes()
            subprocess.run(command, check=True, capture_output=True, env=self.env)
            self.assertEqual(profile, (home / "workstyle.config.toml").read_bytes())
            self.assertEqual(sentinel.read_text(), 'model_reasoning_effort = "high"\n')
            subprocess.run([*command, "--uninstall"], check=True, capture_output=True, env=self.env)
            self.assertFalse((home / "workstyle.config.toml").exists())
            self.assertFalse((bindir / "codex-work").exists())
            self.assertTrue(sentinel.exists())

    def test_conflict_is_reported_before_any_installation(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            home, bindir = base / "codex", base / "bin"
            home.mkdir()
            profile = home / "workstyle.config.toml"
            profile.write_text("# existing user profile\n")
            run = subprocess.run([sys.executable, str(self.root / "workflow/install.py"), "--codex-home", str(home),
                                  "--bin-dir", str(bindir)], capture_output=True, text=True, env=self.env)
            self.assertNotEqual(run.returncode, 0)
            self.assertEqual(profile.read_text(), "# existing user profile\n")
            self.assertFalse((home / "skills").exists())
            self.assertFalse(bindir.exists())

    def test_update_refreshes_owned_profile_and_preserves_user_edits(self):
        base = Path(self.temporary.name)
        home, bindir = base / "codex", base / "bin"
        command = [sys.executable, str(self.root / "workflow/install.py"), "--codex-home", str(home), "--bin-dir", str(bindir)]
        subprocess.run(command, check=True, capture_output=True, env=self.env)
        profile = home / "workstyle.config.toml"
        old = profile.read_bytes()
        template = self.root / "workflow/profile.template.toml"
        template.write_bytes(template.read_bytes() + b"\n# next repository version\n")
        denied = subprocess.run(command, capture_output=True, env=self.env)
        self.assertNotEqual(denied.returncode, 0)
        self.assertEqual(profile.read_bytes(), old)
        subprocess.run([*command, "--update"], check=True, capture_output=True, env=self.env)
        self.assertIn(b"next repository version", profile.read_bytes())
        self.assertEqual(next((home / "backups").glob("*/workstyle.config.toml")).read_bytes(), old)
        edited = profile.read_bytes() + b"# personal edit\n"
        profile.write_bytes(edited)
        for action in ("--update", "--uninstall"):
            refused = subprocess.run([*command, action], capture_output=True, env=self.env)
            self.assertNotEqual(refused.returncode, 0)
            self.assertEqual(profile.read_bytes(), edited)
            self.assertTrue((bindir / "codex-work").is_symlink())

    def test_missing_browser_fails_before_installation(self):
        base = Path(self.temporary.name)
        home = base / "codex"
        (base / "runtime/chromium").unlink()
        run = subprocess.run([sys.executable, str(self.root / "workflow/install.py"), "--codex-home", str(home),
                              "--bin-dir", str(base / "bin")], capture_output=True, env=self.env)
        self.assertNotEqual(run.returncode, 0)
        self.assertFalse(home.exists())


if __name__ == "__main__":
    unittest.main()
