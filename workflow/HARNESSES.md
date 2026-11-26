# 终端 CLI 接入

LLM Work 共享项目工作方式，CLI 自己负责模型、登录、权限审批与原生会话。
目前接入 Codex CLI、Claude Code 和 Cursor Agent CLI；Cursor 桌面 IDE 不在本轮范围内。

## 使用与边界

```bash
llm-work use claude             # 记住默认工具，可选 codex / claude / cursor
cd /path/to/project
llm-work                       # 只读了解当前目录并交接
llm-work --harness cursor       # 仅本次切换
llm-work continue              # 新会话读取项目任务记录
llm-work resume                # 当前工具的历史选择器
llm-work resume --last          # 当前工具在此项目的最近对话
```

工具之间可以读取同一份项目文件和 `.workstyle/tasks/`，原生聊天历史分别保存。
跨机器还需同步项目记录与必要产物，安装本仓库只迁移工作流。
`codex-work` 保持旧语法并固定使用 Codex，不受默认工具选择影响。

## 接入方式

| CLI | 持久工作规则 | 技能 | 原生恢复参数 |
| --- | --- | --- | --- |
| Codex | `workstyle.config.toml` 的 `developer_instructions` | Codex home 中的技能链接 | `resume` / `resume --last` |
| Claude Code | `--append-system-prompt` 追加共享规则 | `--plugin-dir` 加载 `.claude-plugin/plugin.json` 和 `skills/` | `--resume` / `--continue` |
| Cursor Agent | 每个新会话的首条请求载入受管 `rules.md`；同时提供原生 `.mdc` 规则 | `--plugin-dir` 加载 `.cursor-plugin/plugin.json` 和 `skills/` | `--resume` / `--continue` |

共享核心在 [core.md](core.md)，无任务启动规则在 [startup.md](startup.md)。Claude 和 Cursor 的插件包含默认 14 个技能、原始参考文件与许可证；`--workflow-only` 只包含 5 个工作流技能。`teach` / `retro` 在生成副本中恢复 `disable-model-invocation: true`，上游 vendored 文件不改写。显式 `learn` / `retro` 启动请求指向所选插件中的技能文件，避免依赖不同工具的斜杠命令命名。

Claude / Cursor 插件带有 DeepWiki 与锁定版本的隔离 Playwright MCP。工具自己的其他 MCP 保留；首次加载可能需要原生审批，启动器不自动批准。Codex 的完整 baseline 另有 Context7 与普通 Playwright 配置；这一层仍按 Codex 格式部署。其他 CLI 可以继续使用已有的 Context7 配置，缺失时按核心规则说明查证限制。

本机 Cursor 2026.11.22 的插件规则虽然能被客户端发现，但在默认模式与 ask 模式的标记实验中都没有自动进入模型上下文。因此启动器把已验证的插件规则快照加入新会话首条请求，保留项目名首行和用户请求原文，不依赖隐式注入。原生 `.mdc` 仍随插件提供。

`resume` 沿用原对话的上下文，不注入新任务或再次执行目录探索；旧的非 Workstyle 会话可能没有工作规则。Claude 恢复已有会话也可能沿用系统提示快照。更新共享规则后应新开会话，用 `continue` 从项目文件接手。CLI 内部上下文、权限模式及工具能力仍有差异，统一工作规则不保证模型输出完全相同。

## 安装文件与保护

默认 `WORKSTYLE_HOME=~/.local/share/workstyle`：

```text
settings.json             # 默认 CLI，llm-work use 修改
installs/<cli>.json        # 源仓库、bin 目录、受管插件逐文件哈希与权限
plugins/claude/            # Claude 原生插件快照
plugins/cursor/            # Cursor 原生插件快照
backups/                  # 更新前的插件副本
```

插件在安装时生成。修改仓库后运行所选 CLI 的 `bootstrap.py --update` 再开新会话。
安装器保护同名文件、其他克隆的安装、本地修改和符号链接；遇到冲突先停下，保留现有文件。
共享 `llm-work` 链接由安装记录管理，卸载一种适配时仍为其他已登记的 CLI 保留。
旧版受管 `workstyle` 链接在成功安装新入口后移除；最后一种适配卸载时也会清理本仓库遗留的旧链接。入口迁移失败会恢复原来的安装状态与链接，其他来源的同名文件保持原样。
卸载将完整插件移入 `backups/` 后移除登记，避免删除中途失败损坏唯一副本。
卸载保留默认选择，若默认工具已移除，执行 `llm-work use` 选择保留的工具。
项目目录中的 `AGENTS.md`、`CLAUDE.md`、`.cursor/` 与 `.workstyle/tasks/` 不由安装器创建或修改。

## 版本依据与扩展

2026-11-26 核对本机 Codex 0.167.2、Claude Code 2.1.272、Cursor Agent 2026.11.22-e9042b2 的 `--help`。Codex 独立 profile 需要 0.134.0+；Claude / Cursor 安装与启动时检测必需参数，缺少接口会明确报错。Cursor 优先调用 `cursor-agent`，也接受官方 `agent`，并检查帮助中的 Cursor Agent 标识，防止调用无关的同名程序。

官方接口依据：[Claude CLI](https://code.claude.com/docs/en/cli-reference)、[Claude 插件清单](https://code.claude.com/docs/en/plugins/manifest-reference)、[Cursor CLI](https://cursor.com/docs/cli/reference/parameters)、[Cursor 插件](https://cursor.com/docs/reference/plugins)、[Cursor Skills](https://cursor.com/docs/skills)。实际通过的检查与未覆盖部分记录在 [VALIDATION.md](VALIDATION.md)。

新增 CLI 时在 `harnesses.py` 定义可执行文件与能力检查，在 `launcher.py` 映射目录、规则、插件及原生恢复参数；若文件格式不同，在 `adapter_install.py` 增加生成器。先核对该版本原生接口，再补隔离测试和实际加载验证；共享规则与任务格式继续复用。
