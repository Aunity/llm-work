# Workstyle 部署与使用

安装、检查与更新命令在本仓库根目录执行；日常使用在各自项目文件夹执行。克隆路径可任意选择；配置由当前路径生成，不绑定原作者机器。

## 前置条件

| 项目 | 要求 |
| --- | --- |
| 系统 | 优先支持 Linux / WSL2；macOS 使用 Playwright 的平台路径解析，但尚未实机验收；Windows 原生未支持 |
| Python | 3.10+；推荐 3.11+，自带 `tomllib` |
| Node.js / npm | Node 20+；本次使用 Node 22；锁定的 Playwright 要求 Node 20+ |
| 所选 CLI | Codex 0.134.0+；或支持本地插件的 Claude Code / Cursor Agent CLI，安装器检查所需接口 |
| 网络 | 首次部署需要 npm registry 和 Playwright 浏览器下载地址；HTTP MCP 另需访问对应服务 |

Python 3.10 需要 `tomli`。在自己的 Python 环境安装 `python3 -m pip install -r requirements.txt`；系统 Python 禁止安装时先建立并激活虚拟环境，后续安装与 `doctor` 使用该环境的 Python。Python 3.11+ 无额外 Python 依赖。

先安装并登录所用工具：[Codex CLI](https://learn.chatgpt.com/docs/cli)、[Claude Code](https://code.claude.com/docs/en/setup)、[Cursor Agent CLI](https://cursor.com/docs/cli/installation)。模型、provider 与账户权限由每台机器单独配置。适配接口、已核对版本和差异见 [CLI 接入说明](workflow/HARNESSES.md)。

## 首次部署

```bash
git clone https://github.com/Aunity/llm-work.git workstyle
cd workstyle
python3 workflow/bootstrap.py --harness claude
export PATH="$HOME/.local/bin:$PATH"
workstyle doctor
```

将 PATH 设置加入自己的 shell 配置，后续新终端即可找到命令。自定义安装目录则将相应 `--bin-dir` 加入 PATH。

`--harness` 选择 `codex`、`claude` 或 `cursor`；`all` 要求三种 CLI 都已安装，省略时沿用旧版 Codex 默认值。安装器按锁文件准备 npm 包和 Chromium，然后部署所选 CLI 的规则、技能与统一入口，最后检查。Claude / Cursor 不需要安装 Codex，也不改它们的账号设置。

默认不安装浏览器系统库；精简 Linux 缺少系统库时，可显式运行：

```bash
python3 workflow/bootstrap.py --harness claude --with-system-deps
```

该选项会调用 Playwright 的系统依赖安装器，可能需要 sudo。已有 Chrome / Chromium 时可以指定 `--browser-executable /absolute/path/to/chrome`；自定义浏览器与固定 Playwright 的兼容性需要实际验证。

常用选项：

```bash
# 只装 5 个工作流技能（选择 Codex 时保留普通 Codex 配置）
python3 workflow/bootstrap.py --harness claude --workflow-only

# 在独立位置试装，使用已经准备好的依赖
python3 workflow/bootstrap.py --harness claude --skip-deps --workstyle-home /tmp/workstyle-data --bin-dir /tmp/workstyle-bin

# 依赖准备完成后的重复安装或离线配置安装
python3 workflow/bootstrap.py --harness claude --skip-deps
```

`--workstyle-home` 默认使用 `WORKSTYLE_HOME`，未设置时为 `~/.local/share/workstyle`；保存插件快照和默认 CLI。自定义试装后，运行时也要设置同值的 `WORKSTYLE_HOME`。第一次安装将该 CLI 设为默认值；后续安装不改变默认选择，用 `workstyle use codex|claude|cursor` 切换。

`--codex-home` 仅用于 Codex，默认使用现有 `CODEX_HOME`，未设置时为 `~/.codex`。自定义路径试装不会更换当前会话的配置；实际启动该副本时需把 Codex 的 `CODEX_HOME` 指向相同目录。

重复运行不会覆盖同名用户技能或不同内容的个人约定。任一步失败都会以非零状态停止；安装按阶段进行，前面已经成功的阶段会保留，解决报错后重新运行即可。

## 工作、学习与恢复

日常只需记住 `workstyle`。进入项目文件夹后启动，它会先了解当前目录，再交给你安排任务：

```bash
cd /path/to/project
workstyle
```

| 场景 | 命令 |
| --- | --- |
| 自动了解当前目录并交接 | `workstyle` |
| 选择以后默认使用的 CLI | `workstyle use claude`（或 `codex`、`cursor`） |
| 仅本次切换 CLI | `workstyle --harness cursor` |
| 选择当前项目的原对话继续 | `workstyle resume` |
| 从其他位置打开指定项目 | `workstyle -C /path/to/project` |

默认项目始终是运行命令时的当前目录，不会自动改成 Workstyle 配置仓库或父目录。`-C`（长名称 `--project`）也适用于其他子命令，例如 `workstyle resume -C /path/to/project`。目标目录必须已存在。

无具体请求时，启动器会发送一条以当前项目名称开头的交接请求。所选 CLI 先只读查看目录，再根据实际内容分流：

- **空目录或尚无实质项目内容**：说明目录状态，等待你安排新任务和预期交付。
- **已有项目内容**：读取项目说明、进展/重启/交接材料和任务记录，按需核对代码、数据、产物及 Git 状态；给出项目背景、当前进度、未完成事项和建议接手点，再由你选择继续哪项工作或安排新任务。

启动阶段不创建任务记录或课程、不修改项目或自动执行旧待办。已有文档优先沿用；无法确认的信息会明确列出。收到具体请求后才进入执行流程，任务记录写在目标项目 `.workstyle/tasks/`；简单问答和很小的修改不需要记录。详细启动规则见 [项目交接指令](workflow/startup.md)。

需要特定操作时再使用以下选项：

| 场景 | 命令 |
| --- | --- |
| 直接恢复当前项目最近一次对话 | `workstyle resume --last` |
| 在新对话中按当前项目任务记录接手 | `workstyle continue` |
| 启动时提供任务 | `workstyle --request "具体任务"` |
| 启动时提供学习主题 | `workstyle learn --request "学习主题"` |
| 复盘当前项目 | `workstyle retro` |
| 检查 Workstyle 安装 | `workstyle doctor` |

`resume` 恢复当前 CLI 在本机保存的原对话；`continue` 新开会话，读取项目的 `.workstyle/tasks/` 恢复任务，可以跨 CLI 接续。原生对话历史不会在工具之间转换。已经用 `--request` 提供具体任务或主题时直接处理请求；这些显式操作不会被自动交接流程覆盖。普通启动无需选择模式。对话中也可以明确要求教学、复盘或原型验证；各 CLI 的原生技能命令格式见其技能列表。

更新工作规则后优先新开会话或用 `continue` 接手；`resume` 保留原对话上下文，旧的非 Workstyle 会话可能没有最新规则。各 CLI 的规则载入差异见 [CLI 接入说明](workflow/HARNESSES.md)。

teach 与 retro 保留上游的显式调用策略，通过 `learn` / `retro` 入口或原生技能命令使用；不出现在默认提示词中的隐式技能清单不代表安装失败。

原来的 `codex-work` 命令仍可用，始终选择 Codex。旧格式 `codex-work work PROJECT [REQUEST]` 与 `continue/learn/retro PROJECT [REQUEST]` 继续兼容。旧格式中第一个位置参数仍是项目目录；使用新格式时，任务或主题通过 `--request` 提供，避免把文字误当成目录。`-C` 不能与旧位置目录同时指定。只给 `work` 或 `learn` 而不给请求时，也先自动了解目录再等待具体任务或学习主题。

任务记录与个人学习材料默认不纳入本配置仓库。跨机器继续同一任务时，另外同步目标项目的记录和所需产物；迁移配置本身不会迁移历史对话。

## 检查实际行为

```bash
python3 -m unittest discover -s tests -v
workstyle doctor
workstyle doctor --mcp

# Codex 专用诊断
python3 workflow/check.py
python3 baseline/check.py --mcp --codex
```

单元测试使用临时目录与惰性运行时替身，无需 Node、浏览器、Codex 登录或网络。`doctor --mcp` 会真实访问 DeepWiki、启动隔离浏览器、打开临时本地页面并验证交互；最后一条还检查 Context7 和普通 Codex 的技能发现。`--codex` 使用本次 CLI 提供的 `debug prompt-input`，其他版本以实际帮助为准。这些诊断不会提交模型推理请求。

Codex 检查器支持 `--codex-home /path/to/codex`，即时报告写入 `workflow/check-results.json` 与 `baseline/check-results.json`，不提交 Git。Claude / Cursor 的 doctor 检查原生接口和插件完整性；Claude 另执行原生插件验证，MCP 检查报告打印到终端。MCP 接通不等于真实业务任务已验收。

## 更新已有机器

在工作区干净且已经配置远端时：

```bash
git pull --ff-only
python3 workflow/bootstrap.py --harness claude --update
python3 -m unittest discover -s tests -v
workstyle doctor --mcp
```

以上 `claude` 替换为所用 CLI；多工具安装可分别更新或使用 `--harness all`。`--update` 按锁文件更新依赖，并仅替换上次安装后未被本地修改的插件或 Codex 受管配置。用户的其他模型配置、provider 和其他 MCP 保留。Codex 技能链接直接指向仓库；Claude / Cursor 使用安装时生成的插件快照。更新后开启新会话。

通用安装记录与插件备份位于 `$WORKSTYLE_HOME/installs/` 和 `backups/`。Codex 另有 `$CODEX_HOME/workstyle-install.json`、`baseline-install.json` 与 `backups/`。发生本地修改冲突时先将个人文件备份到仓库外，再手工合并差异；没有强制覆盖选项。

仅升级统一入口而保留已有 Codex profile 时，可运行 `python3 workflow/adapter_install.py --harness codex`；不会修改原 profile。

旧 Codex 安装若没有状态记录，先运行 `python3 workflow/bootstrap.py --skip-deps --update` 登记；仅在当前文件与期望配置一致时登记。内容不同会保留原文件并停止，需要先核对差异。移动克隆目录前按下节撤回原安装，再从新位置安装。

## 回退与卸载

回退到支持多 CLI 的旧版本时，在干净工作区切换到已验证的 tag / commit，再运行 `python3 workflow/bootstrap.py --harness claude --update`（替换为所用 CLI）。安装状态会验证当前受管文件仍是上一次安装的内容，随后按旧版本重新生成。若回退到仅支持 Codex 的早期版本，先按下方命令卸载新的适配，再切换代码，避免共享入口指向已不存在的文件。

卸载 Claude / Cursor 适配（替换工具名）：

```bash
python3 workflow/adapter_install.py --harness claude --uninstall
```

这会把未被修改的受管插件移到 `backups/`，再删除安装记录。其他适配仍在使用时保留共享入口；默认选择与备份保留。确认无需恢复后可自行删除备份。自定义安装传入相同的 `--workstyle-home` 与 `--bin-dir`。

撤回普通 Codex 配置时，使用安装输出的实际备份目录：

```bash
python3 baseline/apply.py --restore /path/to/codex/backups/cli-baseline-TIMESTAMP-ID
```

回退会恢复原始配置字节和安装状态，删除该次新增的技能链接；若安装前没有 `config.toml`，恢复到不存在。安装后文件有本地修改时拒绝覆盖。多次配置变更的备份应按逆序恢复；不要删除仍需回退的备份。

随后移除 Workstyle 自己的 profile 和链接：

```bash
python3 workflow/install.py --uninstall
python3 workflow/adapter_install.py --harness codex --uninstall
```

自定义安装时传入同一组 `--codex-home` 和 `--bin-dir`。旧版无状态记录的安装需先登记；profile 有个人改动时会拒绝卸载。浏览器缓存、仓库、其他技能和账户信息保留，是否删除依赖目录由你决定。

## 依赖与来源

`@playwright/mcp` 固定为 0.0.85，完整 npm 依赖由 `workflow/browser/package-lock.json` 固定。上游技能随仓库保存，无需部署时克隆其最新分支。来源 commit、原始哈希和本地适配分别在 `workflow/sources.json`、`baseline/sources.json`。

科研技能的 RDKit、统计、绘图与 PDF 等依赖按具体任务准备，不由配置部署统一安装。长期维护步骤见 [维护指南](CONTRIBUTING.md)。
