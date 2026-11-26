# Workstyle：跨终端 AI 工具的工作与学习流程

在 Codex CLI、Claude Code 和 Cursor Agent CLI 之间复用工作规则、技能和项目任务记录。进入项目文件夹，运行 `workstyle`，即可先了解目录、再安排工作；工具可以切换，项目进度保留在文件里。

项目起源于 Codex 工作方法调研，目标是提高复杂任务的思考、执行、验证和完成质量，支持跨会话恢复、科研与学习。Token 消耗不作为筛选标准。

## 项目组成

| 目录 | 职责 |
| --- | --- |
| `docs/` | 工作方法、技能与 MCP 调研、社区证据和效果评估方案 |
| `baseline/` | 普通 Codex 的 9 个精选 skills、个人约定、Context7 / DeepWiki / Playwright 配置、备份与回退 |
| `workflow/` | 共享核心规则、5 个工作流 skills、CLI 适配、依赖锁定、部署与检查 |
| `bin/workstyle` | 统一日常入口，默认当前目录，记住所选 CLI |
| `bin/codex-work` | 兼容旧命令，始终使用 Codex |
| `tests/` | 不依赖个人配置或网络的安装、更新、回退和启动器测试 |
| `learning/` | 学习入口说明；实际课程与个人记录不进入此仓库 |

每个项目文件夹就是一个工作目录；未指定目录时使用启动命令时所在的文件夹。Codex 通过 profile 和技能链接接入；Claude Code / Cursor Agent 通过会话级本地插件接入。安装后需要保留克隆目录，机器路径由安装器解析。

## 日常使用

```bash
cd /path/to/project
workstyle
```

启动后会自动只读查看当前目录：空目录提示你安排新任务；已有项目先读取说明、进展与交接材料，结合当前文件给出背景摘要和下一步选择。这个阶段不创建任务记录或课程，也不自动执行旧待办。接着直接说明要做的事即可。

选择常用工具一次，之后继续用 `workstyle`：

```bash
workstyle use claude     # 或 codex、cursor
workstyle               # 在当前项目开始
```

临时切换用 `workstyle --harness cursor`，不改变默认选择。`workstyle continue` 读取当前项目 `.workstyle/tasks/` 接续工作；`workstyle resume` 恢复所选 CLI 自己的原对话。指定目录用 `workstyle -C /path/to/project`。启动规则集中维护在 [项目交接指令](workflow/startup.md)。

## 新机器部署

在准备好 Python、Node.js 和所选 CLI 的 Linux / WSL2 环境中：

```bash
git clone https://github.com/Aunity/llm-work.git workstyle
cd workstyle
python3 workflow/bootstrap.py --harness claude
export PATH="$HOME/.local/bin:$PATH"
workstyle -C /path/to/project
```

`--harness` 可选 `codex`、`claude`、`cursor`、`all`；省略时保持原来的 Codex 安装方式。只安装所选工具的适配，不要求机器上同时装三种 CLI。版本与适配边界见 [CLI 接入说明](workflow/HARNESSES.md)，部署、更新与回退见 [快速开始](QUICKSTART.md)。登录和模型配置由各 CLI 自己管理。

## 持续迭代

```bash
python3 -m unittest discover -s tests -v
git diff --check
```

用功能分支修改，检查通过后提交；其他机器拉取同一版本后运行 `python3 workflow/bootstrap.py --harness claude --update`（替换为所用 CLI）。详细约定见 [维护指南](CONTRIBUTING.md)，第三方内容见 [来源与许可证](THIRD_PARTY_NOTICES.md)。

本次 Linux 上的全新克隆部署、自动化测试和真实 MCP 操作结果见 [验收记录](workflow/VALIDATION.md)，其中注明实际验证与未验证范围。

## 背景材料

以下调研的资料核对日期为 **2026 年 11 月 16 日**，保留为当时的研究和安装记录；当前部署方式以快速开始为准。

- [Codex 使用方法与任务完成质量](docs/codex-workflow.md)：任务模板、执行方法与质量标准。
- [Skills 与 MCP 候选全景](docs/skills-mcp-landscape.md)：13 组技能或工作流、22 项 MCP 候选及适用边界。
- [社区实践与技术分享](docs/community-evidence.md)：第一手来源、不同反馈和证据局限。
- [试用与效果评估](docs/evaluation-plan.md)：通过真实任务比较配置的实际收益。
- [普通 Codex 首批安装记录](docs/codex-cli-baseline.md)：9 个技能的选择依据及原机器验收。

候选清单不等于安装清单。程序可运行、MCP 可连接和任务质量提高需要分别验证；当前不宣称完成了技能收益的对照实验。
