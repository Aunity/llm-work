"""Open Workstyle in the current project, using the selected terminal CLI."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

from harnesses import HARNESSES, ROOT, codex_home, executable, plugin_path, selected_harness, workstyle_home

PROMPTS = {
    "work": "Use $workstyle-task for this task. Investigate, implement, verify and deliver the requested outcome.",
    "continue": "Use $workstyle-task to recover the requested unfinished task from this project's .workstyle/tasks/ and continue it.",
    "learn": "Use $teach in this teaching workspace. Ground the lesson in reliable sources and include a learner exercise and a transfer check.",
    "retro": "Use $retro and its $writing-for-agents reference to inspect this project's relevant task evidence and session. Map upstream tool names to the actual tools available here. Present concrete environment improvements with supporting evidence.",
}


def prompt_for(mode, request, project, harness, home):
    if request or mode in ("continue", "retro"):
        prompt = PROMPTS[mode]
        if harness != "codex":
            # Explicit user modes can reach user-only skills without depending on
            # each CLI's slash-command parser or plugin namespace spelling.
            for name in ("workstyle-task", "teach", "retro", "writing-for-agents"):
                prompt = prompt.replace("$" + name, name + " skill at " + json.dumps(
                    str(plugin_path(home, harness) / "skills" / name / "SKILL.md"), ensure_ascii=False))
            prompt = "Read and follow the requested skill instructions. " + prompt
        return prompt + ("\n\nUser request:\n" + request if request else "")
    startup = ROOT / "workflow/startup.md"
    try:
        instructions = startup.read_text(encoding="utf-8")
    except OSError as error:
        raise RuntimeError("cannot load startup instructions from " + str(startup) + ": " + str(error)) from error
    name = json.dumps(project.name or str(project), ensure_ascii=False)
    location = json.dumps(str(project), ensure_ascii=False)
    return "项目接手：" + name + "\n项目目录：" + location + "\n\n" + instructions


def ensure_installed(harness, home):
    if harness == "codex":
        if not (codex_home() / "workstyle.config.toml").is_file():
            raise RuntimeError("Workstyle is not installed; run python3 workflow/bootstrap.py --harness codex")
    else:
        from adapter_install import verify_installation
        verify_installation(home, harness)


def main(forced_harness=None):
    parser = argparse.ArgumentParser(description=__doc__)
    modes = [*PROMPTS, "resume", "doctor"] + ([] if forced_harness else ["use"])
    parser.add_argument("mode", nargs="?", default="work", choices=modes,
                        help="resume: native conversation; continue: project task record; use: remember a CLI")
    parser.add_argument("project", nargs="?", help="legacy project directory; for use: codex, claude or cursor")
    parser.add_argument("request", nargs="?", help="legacy positional task or learning topic")
    parser.add_argument("-C", "--project", dest="project_dir", metavar="DIR", help="project directory (default: current directory)")
    parser.add_argument("--request", dest="request_text", metavar="TEXT", help="task or learning topic")
    if not forced_harness:
        parser.add_argument("--harness", choices=HARNESSES, help="use this CLI for this launch only")
    parser.add_argument("--last", action="store_true", help="resume the most recent native conversation in this project")
    parser.add_argument("--dry-run", action="store_true", help="show the command without launching or changing files")
    parser.add_argument("--mcp", action="store_true", help="doctor: exercise the optional MCP servers")
    args = parser.parse_args()
    try:
        home = workstyle_home()
        if args.mode == "use":
            if (args.project not in HARNESSES or args.request is not None or args.project_dir is not None
                    or args.request_text is not None or args.last or args.mcp or args.harness):
                parser.error("usage: workstyle use codex|claude|cursor [--dry-run]")
            if args.dry_run:
                print(json.dumps({"harness": args.project, "settings": str(home / "settings.json")}, ensure_ascii=False))
                return 0
            executable(args.project, probe=True)
            ensure_installed(args.project, home)
            from adapter_install import save_selection
            save_selection(home, args.project)
            print("Default CLI:", args.project, "— run workstyle in your project directory.")
            return 0
        if args.project is not None and args.project_dir is not None:
            parser.error("use either -C/--project or the legacy positional project, not both")
        if args.request is not None and args.request_text is not None:
            parser.error("use either --request or the legacy positional request, not both")
        request = args.request_text if args.request_text is not None else args.request
        if args.last and args.mode != "resume":
            parser.error("--last is only supported in resume mode")
        if args.mcp and args.mode != "doctor":
            parser.error("--mcp is only supported in doctor mode")
        if request is not None and args.mode in ("resume", "doctor"):
            parser.error("requests are not supported in " + args.mode + " mode")
        directory = args.project_dir if args.project_dir is not None else args.project
        project = Path(directory if directory is not None else ".").expanduser().resolve()
        if not project.is_dir():
            parser.error("project must be an existing directory: " + str(project))
        harness = forced_harness or args.harness or selected_harness(home)
        if args.mode == "doctor":
            command = [sys.executable, str(ROOT / "workflow/check.py")] if harness == "codex" else [
                sys.executable, str(ROOT / "workflow/adapter_install.py"), "--harness", harness, "--check"]
            if args.mcp:
                command.append("--mcp")
        else:
            binary = executable(harness)
            if harness != "codex":
                ensure_installed(harness, home)
            if harness == "codex":
                command = [binary, "--profile", "workstyle", "--cd", str(project)]
            elif harness == "claude":
                plugin = plugin_path(home, harness)
                rules = plugin / "rules.md"
                if not rules.is_file():
                    raise RuntimeError("Workstyle is not installed for claude; run python3 workflow/bootstrap.py --harness claude")
                command = [binary, "--plugin-dir", str(plugin), "--append-system-prompt", rules.read_text(encoding="utf-8")]
            else:
                command = [binary, "--workspace", str(project), "--plugin-dir", str(plugin_path(home, harness))]
            if args.mode == "resume":
                command += (["resume", *(["--last"] if args.last else [])] if harness == "codex"
                            else ["--continue" if args.last else "--resume"])
            else:
                prompt = prompt_for(args.mode, request, project, harness, home)
                if harness == "cursor":
                    # In the verified CLI version local plugin skills load, but
                    # alwaysApply plugin rules did not reach the model. Include
                    # the installed rule snapshot on every fresh conversation.
                    rules = (plugin_path(home, harness) / "rules.md").read_text(encoding="utf-8")
                    context = "Workstyle session instructions:\n" + rules + "\n\n"
                    if prompt.startswith("项目接手："):
                        title, body = prompt.split("\n\n", 1)
                        prompt = title + "\n\n" + context + body
                    else:
                        prompt = context + prompt
                command.append(prompt)
        if args.dry_run:
            print(json.dumps(command if forced_harness else {"harness": harness, "cwd": str(project), "argv": command},
                             ensure_ascii=False))
            return 0
        if args.mode == "doctor":
            return subprocess.call(command, cwd=project)
        if harness == "codex":
            ensure_installed(harness, home)
        if harness != "codex":
            executable(harness, probe=True)
        os.chdir(project)
        os.execv(binary, command)
    except (RuntimeError, OSError, ValueError, subprocess.SubprocessError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    raise SystemExit(main())
