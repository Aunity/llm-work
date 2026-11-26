# Workstyle 安装验收

## 2026 年 11 月 26 日：多终端 CLI 接入

新增统一入口 `workstyle`，接入 Codex CLI、Claude Code、Cursor Agent CLI。共享工作规则、技能与项目任务记录；原生聊天历史分别恢复。`codex-work` 保持兼容并固定使用 Codex。

环境：Linux、Python 3.10.12、Node 22.23.4；Codex 0.167.2、Claude Code 2.1.272、Cursor Agent 2026.11.22-e9042b2。浏览器依赖版本不变。

| 检查 | 实际证据与结果 |
| --- | --- |
| 自动化行为与失败情况 | 53 项 unittest 全部通过：旧入口兼容，默认/显式目录，字面请求，默认工具与临时切换，原生 resume 与项目 continue，插件首次/重复/冲突/更新/卸载，失败回滚，Python 缓存，规则读取前的符号链接保护 |
| 独立部署 | 含空格的独立源码副本、空 Workstyle home / Codex home / bin，以真实三种 CLI 运行 `bootstrap.py --harness all --skip-deps`，首次与重复均通过；复用已锁定的 npm 包与 Chromium 缓存，本轮未重新下载依赖 |
| Claude 原生加载 | `claude plugin validate` 通过；真实 CLI 的 `system/init` 事件列出 Workstyle 插件及 14 个 `workstyle:*` 技能。模型请求被测试环境 API 的 429 响应阻断，未完成模型交接验收 |
| Cursor 规则接入 | 原生插件的技能及相对引用可读取；仅使用插件 `alwaysApply` 规则时，默认与 ask 模式都无法从已加载上下文报告独立标记。核对本机源码，发现 CLI 规则合并器漏接插件规则服务。因此新会话首条请求显式携带受管规则快照；修正后的独立标记实验成功，工具调用数为 0 |
| Cursor 空目录 | 实际模型只读检查空目录，报告为空并等待新任务；前后逐文件快照一致，没有任务记录或课程 |
| Cursor 已有项目 | 实际模型读取说明、进度、样例数据和旧任务，识别过期说明、4 行样例及未实现的导出脚本，并明确 CSV 版本说法缺少实现依据；给出接手选择，没有执行旧任务，文件快照一致 |
| 生成 MCP 配置 | DeepWiki 初始化、工具发现与公开仓库目录查询通过；固定 Chromium 的本地页面导航、按钮操作与结果检查通过。保留原生客户端对 MCP 的审批流程 |
| 独立审查 | 只读审查发现并复核修复：Python 缓存误判、安装失败残留、卸载中途删除。再次核对 Cursor 规则接入和最终启动器差异，无新增阻断项 |

Cursor 的真实交接试验使用临时目录与 ask 模式；仅在测试中信任自建夹具，产品启动器不注入 `--trust`、`--force` 或自动 MCP 批准。规则标记另在默认模式验证。原生历史选择界面、真实历史恢复、长对话压缩后的规则保留和完整跨 CLI 业务任务尚未实测；恢复映射已通过参数测试并核对本机 CLI。未在另一台物理机器、macOS 或 Windows 验收，也未测量任务质量的对照收益。

验收日志留在忽略的本地任务目录。公开内容不包含账号配置、模型服务地址、原始会话日志或个人路径。

## 2026 年 11 月 24 日：公开发布前检查

发布目标为 `Aunity/llm-work`。在隔离副本中检查并脱敏所有待发布历史：提交身份使用 GitHub 隐私邮箱，机器路径、具体备份标识和额外的个人工具链背景改为通用说明。原始历史备份与审计明细仅保留在本地，不纳入发布。

- Gitleaks 8.30.1 对完整待发布历史进行凭据扫描，未发现实际密钥；另外检查个人路径、内部上下文、提交身份及不应跟踪的运行文件。
- 独立只读复核确认历史中的两份文档已脱敏，运行代码、上游技能和许可证与原版一致。
- 隔离公开副本运行 `python3 -m unittest discover -s tests -v`：33 项通过；Git 空白检查通过。
- `.gitignore` 覆盖嵌套私有配置、SSH 材料、认证文件、证书及 Git bundle；部署说明使用实际公开仓库地址。

隐私清理使提交哈希发生变化，以下历史验收的版本引用已对应到脱敏后的相同实现。检查覆盖已知敏感信息模式与人工发现，未把扫描无命中当作绝对无泄露保证；本轮不重复改变运行行为，也不重复宣称完成新的模型、浏览器或其他物理机器验收。

## 2026 年 11 月 20 日：自动了解目录与项目交接

在省略具体请求时，`codex-work` 现在发送包含项目名和所选目录的启动交接请求。规则集中在 `workflow/startup.md`：Codex 先只读检查真实内容，空目录准备接新任务，已有项目先理解背景并给出交接摘要和下一步选择；此阶段不新建任务记录、不改项目、不自动执行唯一的旧待办。显式请求、`continue`、`retro` 与 `resume` 保持原语义。

| 检查 | 证据与结果 |
| --- | --- |
| 自动化回归 | `python3 -m unittest discover -s tests -v`：33 项通过，覆盖目录选择、无请求触发、不同项目首行、包含特殊字符的路径、请求与恢复互不覆盖、独立克隆中的规则文件定位与文件缺失报错 |
| 独立只读审查 | 审查实现、指令与说明，12 项启动器测试通过；额外验证缺失 startup.md 只阻止需要该规则的启动，显式操作仍正常 |
| 空目录的实际模型行为 | 使用启动器生成的原始交接请求，原生 Codex CLI 0.167.2 `exec --ephemeral --json` 在隔离项目运行；模型确认无实质项目内容，询问新任务与预期交付，exit 0 |
| 已有项目的实际模型行为 | 示例包含过期 README、当前进展、数据指针与四行数据、未实现函数和唯一一条进行中任务；模型核对出 v2 / 4 条数据、指出 README 过期、确认 TSV 导出未实现，并提供下一步选择，没有恢复执行旧任务，exit 0 |
| 只读边界与清理 | 两场景前后文件内容和修改时间快照一致；模型事件中无 file_change，只有只读检查；未执行项目脚本。临时项目与账户配置用后清理，原始报告仅留在忽略的本地任务材料中 |

两场景各实际运行一次，使用临时 Codex home 和本机所选 Workstyle 配置；分别耗时约 56 秒和 68 秒。空目录在沙盒视图中带有空的受保护元数据目录，模型正确视为无实质项目内容。首次在受限网络下出现 workspace routing discovery failed，未执行模型任务；在允许联网的环境重试后完成上述验收。

这是实际模型与工具执行的验收，复用启动器生成的完整请求；未操作交互 TUI、验证会话标题的最终显示或对大型真实项目做重复稳定性测试。启动名称、路径和显式操作的参数边界由自动化测试覆盖。下节保存前一版本的历史检查，不代表当前无参数启动行为。

## 2026 年 11 月 20 日：上一版入口简化（历史记录，49440c7）

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

验收对象：代码版本 `0f93d74`。从本地 Git 仓库真实克隆到含空格的新路径，使用空 npm 缓存、空浏览器缓存、空 Codex home 和独立 bin 目录；未复用原工作区的 node_modules 或原用户配置。

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
