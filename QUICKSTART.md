# Workstyle 部署与使用

下列命令在仓库根目录执行。克隆路径可任意选择；配置由当前路径生成，不绑定原作者机器。

## 前置条件

| 项目 | 要求 |
| --- | --- |
| 系统 | 优先支持 Linux / WSL2；macOS 使用 Playwright 的平台路径解析，但尚未实机验收；Windows 原生未支持 |
| Python | 3.10+；推荐 3.11+，自带 `tomllib` |
| Node.js / npm | Node 20+；本次使用 Node 22；锁定的 Playwright 要求 Node 20+ |
| Codex CLI | 0.134.0+ 支持独立 profile 文件；本次验收版本 0.167.2 |
| 网络 | 首次部署需要 npm registry 和 Playwright 浏览器下载地址；HTTP MCP 另需访问对应服务 |

Python 3.10 需要 `tomli`。在自己的 Python 环境安装 `python3 -m pip install -r requirements.txt`；系统 Python 禁止安装时先建立并激活虚拟环境，后续安装与 `doctor` 使用该环境的 Python。Python 3.11+ 无额外 Python 依赖。

先按照 [Codex CLI 官方说明](https://learn.chatgpt.com/docs/cli)安装和登录 Codex。模型、provider 与账户权限由每台机器单独配置。独立的 `workstyle.config.toml` 格式依据 [官方 profile 文档](https://learn.chatgpt.com/docs/config-file/config-advanced#profiles)。

## 首次部署

```bash
git clone YOUR_REPOSITORY_URL workstyle
cd workstyle
python3 workflow/bootstrap.py
export PATH="$HOME/.local/bin:$PATH"
codex-work doctor
```

用真实地址替换 `YOUR_REPOSITORY_URL`。将 PATH 设置加入自己的 shell 配置，后续新终端即可找到命令。自定义安装目录则将相应 `--bin-dir` 加入 PATH。

部署入口依次执行：按锁文件 `npm ci`，安装对应版本 Chromium，生成 Workstyle profile 和 5 个技能链接，应用普通 Codex 的 9 个技能与基础配置，最后执行静态检查。默认不安装浏览器系统库；精简 Linux 缺少系统库时，可显式运行：

```bash
python3 workflow/bootstrap.py --with-system-deps
```

该选项会调用 Playwright 的系统依赖安装器，可能需要 sudo。已有 Chrome / Chromium 时可以指定 `--browser-executable /absolute/path/to/chrome`；自定义浏览器与固定 Playwright 的兼容性需要实际验证。

常用选项：

```bash
# 只装 Workstyle，保留普通 Codex 配置
python3 workflow/bootstrap.py --workflow-only

# 在独立位置试装，使用已经准备好的依赖
python3 workflow/bootstrap.py --skip-deps --codex-home /tmp/workstyle-codex --bin-dir /tmp/workstyle-bin

# 依赖准备完成后的重复安装或离线配置安装
python3 workflow/bootstrap.py --skip-deps
```

`--codex-home` 默认使用现有 `CODEX_HOME`，未设置时为 `~/.codex`。自定义路径试装不会更换当前会话的配置；实际启动该副本时需把 Codex 的 `CODEX_HOME` 指向相同目录。

重复运行不会覆盖同名用户技能或不同内容的个人约定。任一步失败都会以非零状态停止；安装按阶段进行，前面已经成功的阶段会保留，解决报错后重新运行即可。

## 工作、学习与恢复

| 场景 | 命令 |
| --- | --- |
| 开始任务 | `codex-work work /path/to/project "具体任务"` |
| 恢复任务 | `codex-work continue /path/to/project` |
| 学习 | `codex-work learn /path/to/learning-dir "学习主题"` |
| 复盘 | `codex-work retro /path/to/project` |
| 静态检查 | `codex-work doctor` |

目标目录必须已存在。未给任务或学习主题时只确认环境并等待，不创建记录或课程。任务记录写入目标项目 `.workstyle/tasks/`；简单问答和很小的修改不需要记录。使用 `$prototype` 可验证状态逻辑或 UI 设计。

任务记录与个人学习材料默认不纳入本配置仓库。跨机器继续同一任务时，另外同步目标项目的记录和所需产物；迁移配置本身不会迁移历史对话。

## 检查实际行为

```bash
python3 -m unittest discover -s tests -v
python3 workflow/check.py
python3 baseline/check.py
codex-work doctor --mcp
python3 baseline/check.py --mcp --codex
```

单元测试使用临时目录与惰性运行时替身，无需 Node、浏览器、Codex 登录或网络。`doctor --mcp` 会真实访问 DeepWiki、启动隔离浏览器、打开临时本地页面并验证交互；最后一条还检查 Context7 和普通 Codex 的技能发现。`--codex` 使用本次 CLI 提供的 `debug prompt-input`，其他版本以实际帮助为准。以上不会提交模型推理请求。

两个检查器都支持 `--codex-home /path/to/codex`。即时报告写入 `workflow/check-results.json` 与 `baseline/check-results.json`，不提交 Git。MCP 接通不等于真实业务任务已验收。

## 更新已有机器

在工作区干净且已经配置远端时：

```bash
git pull --ff-only
python3 workflow/bootstrap.py --update
python3 -m unittest discover -s tests -v
codex-work doctor --mcp
```

`--update` 按锁文件更新依赖，并仅替换上次安装后未被本地修改的受管 profile、MCP 定义、基础设置和个人约定。用户的其他模型配置、provider 和其他 MCP 保留。技能链接直接指向仓库，拉取修改后应开启新会话。

安装状态记录为 `$CODEX_HOME/workstyle-install.json` 和 `baseline-install.json`；配置备份位于 `$CODEX_HOME/backups/`。发生本地修改冲突时先将个人文件备份到仓库外，再手工合并差异；没有强制覆盖选项。

旧安装若没有状态记录，先运行 `python3 workflow/bootstrap.py --skip-deps --update` 登记；仅在当前文件与期望配置一致时登记。内容不同会保留原文件并停止，需要先核对差异。移动克隆目录前按下节撤回原安装，再从新位置安装。

## 回退与卸载

回退代码版本时，在干净工作区切换到已验证的 tag / commit，再运行 `python3 workflow/bootstrap.py --update`。安装状态会验证当前受管文件仍是上一次安装的内容，随后按旧版本重新生成。

撤回普通 Codex 配置时，使用安装输出的实际备份目录：

```bash
python3 baseline/apply.py --restore /path/to/codex/backups/cli-baseline-TIMESTAMP-ID
```

回退会恢复原始配置字节和安装状态，删除该次新增的技能链接；若安装前没有 `config.toml`，恢复到不存在。安装后文件有本地修改时拒绝覆盖。多次配置变更的备份应按逆序恢复；不要删除仍需回退的备份。

随后移除 Workstyle 自己的 profile 和链接：

```bash
python3 workflow/install.py --uninstall
```

自定义安装时传入同一组 `--codex-home` 和 `--bin-dir`。旧版无状态记录的安装需先登记；profile 有个人改动时会拒绝卸载。浏览器缓存、仓库、其他技能和账户信息保留，是否删除依赖目录由你决定。

## 依赖与来源

`@playwright/mcp` 固定为 0.0.85，完整 npm 依赖由 `workflow/browser/package-lock.json` 固定。上游技能随仓库保存，无需部署时克隆其最新分支。来源 commit、原始哈希和本地适配分别在 `workflow/sources.json`、`baseline/sources.json`。

科研技能的 RDKit、统计、绘图与 PDF 等依赖按具体任务准备，不由配置部署统一安装。长期维护步骤见 [维护指南](CONTRIBUTING.md)。
