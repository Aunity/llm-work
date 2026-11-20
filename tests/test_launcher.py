"""Exercise the installed launcher contract with an inert Codex executable."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent.parent


class LauncherTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.project = self.base / "current project"
        self.other = self.base / "other project"
        self.project.mkdir()
        self.other.mkdir()
        self.home = self.base / "codex home"
        self.home.mkdir()
        (self.home / "workstyle.config.toml").write_text("# test profile\n")
        bindir = self.base / "bin"
        bindir.mkdir()
        self.codex = bindir / "codex"
        self.codex.write_text("#!/usr/bin/env python3\nimport json, sys\nprint(json.dumps(sys.argv[1:]))\n")
        self.codex.chmod(0o755)
        # Match the installed symlink layout, outside the selected project.
        self.launcher = bindir / "codex-work"
        self.launcher.symlink_to(ROOT / "bin/codex-work")
        self.env = {**os.environ, "PATH": str(bindir) + os.pathsep + os.environ["PATH"],
                    "CODEX_HOME": str(self.home)}

    def launch(self, *arguments, check=True):
        return subprocess.run([sys.executable, str(self.launcher), *map(str, arguments)],
                              cwd=self.project, env=self.env, text=True, capture_output=True, check=check)

    def expected(self, project=None):
        return ["--profile", "workstyle", "--cd", str(project or self.project)]

    def test_no_arguments_uses_callers_directory_without_sending_a_prompt(self):
        for arguments in ((), ("work",), ("learn",)):
            with self.subTest(arguments=arguments):
                self.assertEqual(json.loads(self.launch(*arguments).stdout), self.expected())
        self.assertEqual(list(self.project.iterdir()), [])

    def test_explicit_project_is_resolved_relative_to_callers_directory(self):
        for option in ("-C", "--project"):
            with self.subTest(option=option):
                actual = json.loads(self.launch(option, "../other project").stdout)
                self.assertEqual(actual, self.expected(self.other))
        self.assertEqual(list(self.project.iterdir()), [])
        self.assertEqual(list(self.other.iterdir()), [])

    def test_request_is_literal_text_and_cannot_change_the_project(self):
        # A topic matching a folder name must never select that folder implicitly.
        (self.project / "chemistry").mkdir()
        actual = json.loads(self.launch("--request", "chemistry").stdout)
        self.assertEqual(actual[:4], self.expected())
        self.assertTrue(actual[4].endswith("\n\nUser request:\nchemistry"))
        marker = self.base / "must-not-exist"
        request = "check $(touch " + str(marker) + ") `echo literal` $HOME\nsecond line"
        actual = json.loads(self.launch("-C", self.other, "--request", request).stdout)
        self.assertEqual(actual[:4], self.expected(self.other))
        self.assertTrue(actual[4].endswith("\n\nUser request:\n" + request))
        self.assertFalse(marker.exists())
        self.assertFalse((self.project / ".workstyle").exists())
        self.assertFalse((self.other / ".workstyle").exists())

    def test_resume_reopens_conversations_in_the_selected_project(self):
        for options, project, tail in (
            ((), self.project, ["resume"]),
            (("--last",), self.project, ["resume", "--last"]),
            (("-C", self.other), self.other, ["resume"]),
            (("-C", self.other, "--last"), self.other, ["resume", "--last"]),
        ):
            with self.subTest(options=options):
                actual = json.loads(self.launch("resume", *options).stdout)
                self.assertEqual(actual, self.expected(project) + tail)
        self.assertFalse((self.project / ".workstyle").exists())

    def test_record_recovery_and_retro_keep_their_explicit_skill_requests(self):
        for mode, skill in (("continue", "$workstyle-task"), ("retro", "$retro")):
            with self.subTest(mode=mode):
                actual = json.loads(self.launch(mode).stdout)
                self.assertEqual(actual[:4], self.expected())
                self.assertIn(skill, actual[4])
                self.assertNotEqual(actual[4], "resume")

    def test_learning_topic_uses_current_directory_and_explicit_teach(self):
        actual = json.loads(self.launch("learn", "--request", "统计学").stdout)
        self.assertEqual(actual[:4], self.expected())
        self.assertIn("$teach", actual[4])
        self.assertTrue(actual[4].endswith("\n\nUser request:\n统计学"))
        self.assertEqual(list(self.project.iterdir()), [])

    def test_legacy_project_and_request_arguments_still_work(self):
        for mode, skill in (("work", "$workstyle-task"), ("continue", "$workstyle-task"),
                            ("learn", "$teach"), ("retro", "$retro")):
            with self.subTest(mode=mode):
                actual = json.loads(self.launch(mode, self.other, "existing request").stdout)
                self.assertEqual(actual[:4], self.expected(self.other))
                self.assertIn(skill, actual[4])
                self.assertTrue(actual[4].endswith("\n\nUser request:\nexisting request"))
        self.assertEqual(json.loads(self.launch("work", self.other).stdout), self.expected(self.other))

    def test_invalid_usage_stops_before_launching_codex(self):
        cases = (
            (("-C", self.base / "missing"), "existing directory"),
            (("-C", self.home / "workstyle.config.toml"), "existing directory"),
            (("work", self.project, "-C", self.other), "either -C/--project"),
            (("work", self.project, "one", "--request", "two"), "either --request"),
            (("--last",), "only supported in resume"),
            (("--mcp",), "only supported in doctor"),
            (("doctor", "--last"), "only supported in resume"),
            (("resume", "--request", "task"), "requests are not supported"),
            (("doctor", "--request", "task"), "requests are not supported"),
        )
        for arguments, message in cases:
            with self.subTest(arguments=arguments):
                run = self.launch(*arguments, check=False)
                self.assertEqual(run.returncode, 2)
                self.assertEqual(run.stdout, "")
                self.assertIn(message, run.stderr)

    def test_missing_profile_fails_without_running_codex(self):
        (self.home / "workstyle.config.toml").unlink()
        run = self.launch(check=False)
        self.assertEqual(run.returncode, 2)
        self.assertEqual(run.stdout, "")
        self.assertIn("Workstyle is not installed", run.stderr)
        self.assertEqual(list(self.project.iterdir()), [])

    def test_dry_run_prints_commands_without_starting_codex_or_doctor(self):
        (self.home / "workstyle.config.toml").unlink()
        for options, tail in (((), []), (("resume", "--last"), ["resume", "--last"])):
            with self.subTest(options=options):
                actual = json.loads(self.launch(*options, "--dry-run").stdout)
                self.assertEqual(actual, [str(self.codex), *self.expected(), *tail])
        for options in ((), ("--mcp",)):
            with self.subTest(options=options):
                actual = json.loads(self.launch("doctor", *options, "--dry-run").stdout)
                self.assertEqual(actual, [sys.executable, str(ROOT / "workflow/check.py"), *options])
        self.assertFalse((self.home / "workstyle.config.toml").exists())
        self.assertEqual(list(self.project.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
