# Workstyle：可迭代的 Codex 工作与学习配置

这个项目从 Codex 工作方法调研发展而来，用于维护一套可检查、可更新、可迁移的个人配置。目标是提高复杂任务的思考、执行、验证和完成质量，支持跨会话恢复、科研与学习。Token 消耗不作为筛选标准。

## 项目组成

| 目录 | 职责 |
| --- | --- |
| `docs/` | 工作方法、技能与 MCP 调研、社区证据和效果评估方案 |
| `baseline/` | 普通 Codex 的 9 个精选 skills、个人约定、Context7 / DeepWiki / Playwright 配置、备份与回退 |
| `workflow/` | Workstyle profile、5 个工作流 skills、依赖锁定、部署与检查 |
| `bin/codex-work` | `work`、`continue`、`learn`、`retro`、`doctor` 入口 |
| `tests/` | 不依赖个人配置或网络的安装、更新、回退和启动器测试 |
| `learning/` | 学习入口说明；实际课程与个人记录不进入此仓库 |

普通 `codex` 使用基础配置；`codex-work` 额外选择 Workstyle profile。技能通过符号链接指向克隆目录，配置中的机器路径在安装时生成，因此安装后需要保留克隆目录。

## 新机器部署

在准备好 Python、Node.js 和 Codex 的 Linux / WSL2 环境中：

```bash
git clone YOUR_REPOSITORY_URL workstyle
cd workstyle
python3 workflow/bootstrap.py
export PATH="$HOME/.local/bin:$PATH"
codex-work work /path/to/project
```

前置版本、Python 3.10 的依赖、浏览器系统库、只安装 Workstyle、更新与回退均见 [快速开始](QUICKSTART.md)。安装器不复制登录信息、API key 或旧机器的个人模型配置。

## 持续迭代

```bash
python3 -m unittest discover -s tests -v
git diff --check
```

用功能分支修改，检查通过后提交；其他机器拉取同一版本后运行 `python3 workflow/bootstrap.py --update`。详细约定见 [维护指南](CONTRIBUTING.md)，第三方内容见 [来源与许可证](THIRD_PARTY_NOTICES.md)。

## 背景材料

以下调研的资料核对日期为 **2026 年 11 月 16 日**，保留为当时的研究和安装记录；当前部署方式以快速开始为准。

- [Codex 使用方法与任务完成质量](docs/codex-workflow.md)：任务模板、执行方法与质量标准。
- [Skills 与 MCP 候选全景](docs/skills-mcp-landscape.md)：13 组技能或工作流、22 项 MCP 候选及适用边界。
- [社区实践与技术分享](docs/community-evidence.md)：第一手来源、不同反馈和证据局限。
- [试用与效果评估](docs/evaluation-plan.md)：通过真实任务比较配置的实际收益。
- [普通 Codex 首批安装记录](docs/codex-cli-baseline.md)：9 个技能的选择依据及原机器验收。

候选清单不等于安装清单。程序可运行、MCP 可连接和任务质量提高需要分别验证；当前不宣称完成了技能收益的对照实验。
