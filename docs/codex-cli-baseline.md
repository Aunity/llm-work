# 普通 Codex CLI：第一批已安装配置

> 本文保留原机器的历史安装记录。新机器部署、更新和回退以 [快速开始](../QUICKSTART.md) 为准，下面的原机器路径不可直接迁移使用。

安装与核验日期：2026 年 11 月 16 日。本机 Codex CLI 版本：0.167.2。

这批配置用于直接运行 `codex` 的场景，不需要 `codex-work` 或 Workstyle profile。目标是补齐调试、审查、科研判断和实际证据获取能力。配置已经安装；下面区分本次新增、原有设置和仍需按任务准备的依赖。

## 已安装的九个 skills

| Skill | 用途 | 来源 |
| --- | --- | --- |
| `diagnosing-bugs` | 先建立复现、提出并验证根因假设，再修改和验证 | Matt Pocock |
| `code-review` | 分别检查需求是否实现、代码质量是否合适，再汇总发现 | Matt Pocock |
| `property-based-testing` | 用性质、不变量和自动生成输入检查边界，适合解析、转换和算法代码 | Trail of Bits |
| `scientific-critical-thinking` | 检查证据强弱、偏差、因果推断和研究结论的适用范围 | K-Dense |
| `experimental-design` | 设计实验、对照、随机化、区组与因素组合 | K-Dense |
| `statistical-analysis` | 选择分析方法，检查假设，报告效应量与不确定性 | K-Dense |
| `literature-review` | 制订检索策略、筛选与提取证据、核验引用、撰写综述 | K-Dense |
| `rdkit` | 分子读取、结构处理、描述符、相似性和子结构检索 | K-Dense |
| `scientific-visualization` | 设计科研图表、选择配色、检查输出和准备投稿格式 | K-Dense |

它们通过 `~/.codex/skills/<name>` 的链接指向本工作区的 `baseline/skills/`。Codex 按任务选择相关技能，也可用 `$名称` 显式调用；不需要每次加载全部九个。此前的 prototype、teach、retro、writing-for-agents 和 workstyle-task 继续保留。

这次安装包含 SKILL.md、配套脚本与参考材料，没有执行第三方 skill 附带的科研计算脚本。**安装 skill 不等于已安装它的全部运行库。** 实际运行时应在目标项目的隔离环境里准备相应 Python 版本、RDKit、统计或绘图库。可选的 Parallel 检索、OpenRouter 示意图和 PDF 导出依赖也未安装或授权；不使用这些可选步骤时不需要它们。

## 已启用的三个 MCP

| 服务 | Codex 中的标识 | 实际核验 |
| --- | --- | --- |
| Context7 | `context7` | 匿名解析 `/psf/requests`，查询并取得 timeout 用法文档 |
| DeepWiki | `workstyle_deepwiki` | 发现三个工具，读取 `psf/requests` 的仓库目录 |
| Playwright | `workstyle_browser` | 发现 25 个工具，隔离浏览器访问临时本地页面并完成点击和结果检查 |

Context7 地址为 `https://mcp.context7.com/mcp`；本次未添加 API key，匿名调用通过。匿名额度和服务可用性可能变化，后续若遇到限流再决定是否配置认证。Context7 的文档覆盖和 DeepWiki 的索引可能滞后，重要结论仍应对应项目使用版本的官方文档或源码。

DeepWiki 与 Playwright 沿用先前已验收的 `workstyle_*` 标识，普通 Codex 和 Workstyle profile 共用相同定义。名字不表示必须用 Workstyle 启动，也不需要额外启动一套同名服务。

浏览器 MCP 固定为 `@playwright/mcp` 0.0.85，使用本机 Node 和缓存 Chromium，启动参数包括 `--headless --isolated`，没有关闭浏览器沙箱。依赖仍位于本工作区。其他已配置的 MCP 保留。

## Harness 设置与个人约定

`~/.codex/config.toml` 本次新增：

```toml
web_search = "live"
plan_mode_reasoning_effort = "xhigh"
```

实时搜索用于需要核实的时效信息；计划模式配置为 xhigh，实际可用性仍受所选模型和管理策略约束。已有模型、推理强度、沙盒和审批设置保持不变。没有调整上下文窗口、压缩阈值、认证、provider 或 hooks。

新增的全局 `~/.codex/AGENTS.md` 内容见 [个人工作约定源文件](../baseline/AGENTS.md)。它要求中文解释、沿用项目规则、核实库版本、完成相关验证、科学任务保留来源与参数，并在屏幕上解释结果。项目具体指令与用户当次要求优先。

项目配置、命令行参数和管理策略可能改变当前会话的有效设置。内置搜索、HTTP MCP 与 shell 联网是不同入口；这批配置没有打开 shell 的全局网络权限。

## 现在如何开始用

打开新会话：

```bash
codex -C /path/to/project
```

进入后使用 `/skills` 查看技能、`/mcp` 查看服务、`/status` 查看当前状态。当前已打开的会话可能需要重新启动才能发现新增配置。

可以直接输入自然语言，也可以明确选择一个 skill：

```text
$diagnosing-bugs 定位这个失败。先复现，列出假设并验证根因，修复后运行相关检查。

$code-review 审查工作区相对 main 的修改，需求依据是 docs/spec.md；给出有证据的问题和未验证范围。

$property-based-testing 为这个序列化模块找关键不变量，检查往返转换、非法输入和边界。

用 Context7 核对项目当前依赖版本的接口，再实现这个功能并验证错误路径。

用 Playwright 检查这个本地页面的上传、错误提示和结果下载，报告实际运行结果。

$scientific-critical-thinking 评估这篇论文的因果主张，区分作者结论、实际证据和仍未排除的解释。

$experimental-design 为这个方法比较设计实验，明确对照、重复、随机化和评价指标。

$statistical-analysis 先检查数据和模型假设，再选择分析方法，报告效应量和不确定性。

$literature-review 围绕这个问题做可追溯的文献综述，记录检索范围并核验关键引用。

$rdkit 在项目隔离环境中处理这批 SMILES，记录无效输入并导出分子描述符。

$scientific-visualization 根据这些数据生成可复现的图表，说明配色、单位与导出格式。
```

向任务提供目标、真实输入、关键约束和可判断的完成条件。让 Codex 在实际任务中解释选择了哪些工具、取得了什么证据，再按遗漏或误用调整配置。

## 版本固定与兼容适配

九个技能的来源、原始文件哈希与适配记录在 [baseline/sources.json](../baseline/sources.json)。固定来源如下：

- [Matt Pocock skills](https://github.com/mattpocock/skills/tree/5863806dd4e15c63174bee4e7515a4256792ecfa)：`diagnosing-bugs`、`code-review`。
- [Trail of Bits skills](https://github.com/trailofbits/skills/tree/149d7b21f4067765b82e67029730b42d228ef4b4)：`property-based-testing`。
- [Scientific Agent Skills](https://github.com/K-Dense-AI/scientific-agent-skills/tree/2d2065fb4520fa3f3f2bcf61cff26ec8b7eba4b5)：六个科研技能。

本机校验器不接受的 `compatibility` 和 `effort` frontmatter 已移入 `metadata`，保留原始说明；性质测试技能中的上游 `effort: low` 不会改变 Codex 的 xhigh 设置。代码审查移除了必须另跑 tracker setup skill 的前提，改为使用项目现有说明、本地需求和用户指定规格。原有审查步骤保留。

上游许可证保存在 [baseline/licenses](../baseline/licenses)。上游工具名和相对路径按个人约定映射到 Codex 实际能力与技能目录。

## 检查结果与复查

本次验收通过：

- 九个 skills 均通过本机 `quick_validate` 格式校验。
- 普通 `codex debug prompt-input` 发现全部九个 skills 和全局 AGENTS；未指定 profile。
- 三个 MCP 的初始化、工具发现和上述最小实际操作通过。
- 六项安装器与启动器测试通过，覆盖原配置保留、重复安装、冲突拒绝、参数原样传递和受保护的回退。

这些是配置与最小操作验收，尚未做真实业务任务的模型调用或质量对照。后续按 [效果评估方案](evaluation-plan.md)观察任务结果。

复查命令：

```bash
python3 baseline/check.py
python3 baseline/check.py --mcp --codex
```

第二条会联网查询公开资料、启动临时本地页面和浏览器，并执行 Codex 上下文诊断，不提交模型推理请求。需要宿主允许相应网络和本地浏览器操作。即时结果保存在 [baseline/check-results.json](../baseline/check-results.json)，已加入 gitignore。

## 备份与回退

安装前的全局配置保存在当前机器的私有备份目录；以下为占位路径，实际位置以安装输出为准：

```text
/path/to/codex/backups/cli-baseline-TIMESTAMP-ID
```

备份目录权限为 0700，配置副本和清单为 0600；配置可能含凭据，未复制到本工作区。安装记录见 [baseline/install-result.json](../baseline/install-result.json)。

需要回退本批配置时运行：

```bash
python3 baseline/apply.py --restore /path/to/codex/backups/cli-baseline-TIMESTAMP-ID
```

回退恢复安装前配置，移除本次新增的九个 skill 链接和个人 AGENTS.md。如果配置在安装后已被修改，脚本会拒绝覆盖，需先合并差异。此前安装的 Workstyle profile、五个技能、启动入口和已有其他设置不属于本批回退范围。

技能链接和浏览器包依赖本工作区，使用期间保留 本仓库克隆目录。此前的 Workstyle 卸载命令只管理它自己创建的 profile 和链接，不会撤回这批普通 Codex 全局配置。
