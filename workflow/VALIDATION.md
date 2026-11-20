# Workstyle 安装验收

## 2026 年 11 月 20 日：简化日常入口

`codex-work` 现在省略子命令即可启动，默认项目为调用时的当前目录；显式切换目录用 `-C/--project`。无任务的启动不附加自动开场 prompt。新增 `resume` / `resume --last` 调用本机 Codex 的原生会话恢复；`continue` 保持按项目记录新开会话接手的行为。

| 检查 | 证据与结果 |
| --- | --- |
| 自动化回归 | `python3 -m unittest discover -s tests -v`：31 项通过；新增 10 项启动器测试，覆盖默认目录、显式相对目录、恢复方式、旧参数兼容、文字与目录区分、字面请求、错误参数、缺失 profile 与 dry-run |
| 当前安装入口 | 通过真实 `~/.local/bin/codex-work` 链接，在仓库外含空格的临时目录运行 `--dry-run`；无参数、`resume`、`resume --last` 均保留调用目录，`-C` 正确覆盖目录，无多余 prompt |
| Codex 参数兼容 | 本机 CLI 0.167.2 执行 `codex --profile workstyle --cd <临时目录> resume --help` 成功，接受生成的选项与子命令顺序 |
| 启动副作用 | 测试使用惰性 Codex 进程替身；选定项目未被启动器创建任务记录或课程，`doctor --dry-run` 也不执行诊断脚本 |
| 独立审查 | 只读审查实现、说明与测试，另跑 15 项相关测试通过，未发现需要修复的功能缺陷 |

本次核验启动参数和错误行为，未打开真实恢复选择界面、恢复历史会话或发起模型推理请求；安装机制、MCP 配置与浏览器版本未改变。全新部署的验证范围见下节。

## 2026 年 11 月 20 日：Git 与迁移部署

验收对象：代码版本 `aecf202`。从本地 Git 仓库真实克隆到含空格的新路径，使用空 npm 缓存、空浏览器缓存、空 Codex home 和独立 bin 目录；未复用原工作区的 node_modules 或原用户配置。

环境：Linux，Python 3.10.12 / tomli 2.4.1、Node 22.23.4、npm 10.9.9、Git 2.34.1、Codex CLI 0.167.2。浏览器 MCP 0.0.85、Playwright 1.66.0-alpha-2026-11-09、Chromium revision 1254。

| 检查 | 证据与结果 |
| --- | --- |
| 全新克隆中的自动化测试 | `python3 -m unittest discover -s tests -v`：21 项通过，包含旧安装登记、旧备份恢复、冲突保护、路径含空格、相对浏览器路径 |
| 首次网络部署 | `workflow/bootstrap.py --codex-home … --bin-dir …`：npm ci 下载 3 个锁定包，下载 Chromium / FFmpeg，14 个技能和 profile 安装成功，两层静态检查通过 |
| 重复更新 | `bootstrap.py --skip-deps --update`：通过，baseline 报 already_configured |
| 实际回退与卸载 | 在同一临时安装上恢复首装备份并卸载 Workstyle：配置、14 个受管技能链接与 launcher 移除，Codex 自带 `.system` 技能保留 |
| 普通 Codex | `baseline/check.py --codex-home … --mcp --codex`：全局约定加载、9 个技能发现通过，无模型推理请求 |
| 浏览器 | 实际启动新下载的 Chromium；MCP 本地页面导航、按钮操作与结果检查通过，发现 25 个工具 |
| HTTP MCP | Context7 解析 Requests 并取得 timeout 文档；DeepWiki 读取 psf/requests 目录，均通过 |
| Workstyle profile 与技能清单 | `debug prompt-input` 确认 profile 指令与 3 个默认技能；App Server `skills/list` 确认 5 个工作流技能全部 enabled 且无加载错误，无模型推理请求 |
| 独立审查 | 核实并处理受管设置覆盖、相对路径、分阶段结果说明、旧登记保护与旧备份状态清理；最终针对性复核通过 |
| Git 内容 | 依赖、私人配置、凭据、课程及任务记录由忽略规则排除；自有文件空白检查通过。上游文献技能的既有空白格式原样保留 |

首次在受限沙盒下载时 npm DNS 报 EAI_AGAIN；在允许网络的执行环境重试后完成下载与上述验收。这是本机上隔离克隆与配置目录的验证，**未在另一台物理机器、macOS 或 Windows 运行**。系统库沿用当前 Linux 环境，`--with-system-deps` 未执行。GitHub Actions 配置已加入仓库，尚未提交远端运行；未测试真实模型任务的质量提升。

复查命令和环境前置条件见 [快速开始](../QUICKSTART.md)。即时原始报告保存在本次本地任务记录旁，不含登录信息，不纳入版本控制。

teach / retro 保留 `allow_implicit_invocation: false`，按 [官方技能说明](https://learn.chatgpt.com/docs/build-skills#optional-metadata)使用显式调用；默认 prompt 清单不展示它们。CLI 0.167.2 的 `debug prompt-input` 在本次文本提示实验中也没有注入这两项正文，因此用实际 `skills/list` 检查安装发现状态，没有把目录列表或默认 prompt 当作教学任务已运行的证据。

## 2026 年 11 月 16 日：原始安装记录

核验日期：2026 年 11 月 16 日。

| 检查 | 实际结果 |
| --- | --- |
| 安装 | 新增 workstyle profile、五个 skill 链接与 codex-work 启动链接 |
| 保护已有配置 | 安装器对同名冲突预检；临时目录测试确认基础 config.toml 保持原内容 |
| 重复安装与卸载 | 自动测试通过，保留无关文件 |
| 参数传递 | 含空格的项目路径与含 shell 语法的请求原样传入；未发生 shell 展开 |
| Skill 格式 | 五个技能全部通过 quick_validate |
| Codex 上下文 | prompt-input 诊断成功，发现新增 profile 指令、workstyle-task 与 prototype |
| DeepWiki MCP | initialize、tools/list、读取 psf/requests 仓库目录通过 |
| 浏览器 MCP | initialize、tools/list、隔离浏览器访问临时本地页面、页面交互与关闭通过 |
| 文档 | 快速开始与研究文档的本地链接和代码围栏检查通过 |

本次通过协议冒烟和上下文诊断验收配置，未提交模型推理请求。真实任务的完成质量与长期效果需要继续按 [效果评估方案](../docs/evaluation-plan.md)观察。

MCP 的即时输出在 [check-results.json](check-results.json)。该报告是本机运行记录，已从版本跟踪中排除。
