# Codex 的 Skills 与 MCP 候选全景

本清单围绕需求理解、设计、实现、验证、资料读取和学习筛选扩展。优先级表示与当前工作场景的匹配程度，不代表已经通过本机实测。Token 消耗不参与排序。

资料核对日期：2026 年 11 月 16 日。共整理 13 组 skills 或工作流项目、22 项 MCP 候选，以及相关的使用边界。

## 如何阅读清单

- **A 优先试用**：能直接补齐当前工作中的常见缺口；仍需满足该行的适用条件。
- **B 按场景选择**：已有相应技术栈、账户、数据或工作需求时再接入。
- **C 继续观察**：与已有能力重叠、需要额外基础设施，或效果证据不足。

项目说明只能确认作者提供什么能力。Codex 支持情况分为维护者明确提供 Codex 用法、可迁移的技能内容，以及标准 MCP 接入；这些都不等于在本机完成了端到端验收。

## Skills 与工作流项目

| 编号 | 项目与来源 | 重点内容 | 优先级与适用条件 | Codex 与使用边界 |
| --- | --- | --- | --- | --- |
| S01 | [Superpowers](https://github.com/obra/superpowers) | 系统调试、完成前验证、规划、TDD、代码审查 | A，复杂开发先试调试与验证模块 | 提供 Codex 插件用法；全流程包含设计确认、分阶段执行等约束，应与实际任务授权保持一致 |
| S02 | [Matt Pocock Skills](https://github.com/mattpocock/skills) | 需求澄清、领域建模、原型、实现、审查、复盘、教学 | A，适合按需组合工作与学习流程 | 提供 Codex 安装说明；插件与复制安装选择一种，避免同一技能重复出现 |
| S03 | [Planning with Files](https://github.com/OthmanAdi/planning-with-files) | 计划、发现、进展落盘与恢复 | B，多阶段或跨会话任务 | 提供 Codex 集成；已有 Brain 或任务账本时，先明确哪个系统持有权威任务状态 |
| S04 | [OpenSpec](https://github.com/Fission-AI/OpenSpec) | 提案、需求场景、设计、任务与变更归档 | B，长期维护的软件和接口契约 | 提供 Codex 技能入口；主要解决规格与变更管理，实际行为仍需运行验证 |
| S05 | [GSD Core](https://github.com/open-gsd/gsd-core) | 项目阶段、任务拆分、编排、验证与交付 | C，整项目管理需要明显时试 | 声明支持 Codex；会引入完整流程，宜与已有编排工具 分开比较 |
| S06 | [Addy Osmani Agent Skills](https://github.com/addyosmani/agent-skills) | 规格、接口、增量实现、质量审查、性能与交付 | B，作为另一套工程方法对照 | 提供 Codex 插件说明；单项复制可能遗漏仓库共享 references，应核对依赖是否完整 |
| S07 | [Impeccable](https://github.com/pbakaus/impeccable) | UI critique、audit、polish、适配和交互细节 | A，经常开发和修改 Web 界面时 | 明确支持 Codex；先选具体页面或组件，设计评价需结合真实浏览器行为 |
| S08 | [Vercel Agent Skills](https://github.com/vercel-labs/agent-skills) | React 性能、组件组合、Web 设计检查 | B，React 或 Next.js 项目 | 采用 Agent Skills 格式；建议与项目实际框架版本、编译器和性能测量结合 |
| S09 | [Anthropic Document Skills](https://github.com/anthropics/skills) | PDF、DOCX、PPTX、XLSX 的创建与处理 | B，论文材料、报告、演示文稿和表格 | 面向 Claude 的实现；迁移到 Codex 时检查脚本、运行时和工具映射，输出文件需要打开或渲染验收 |
| S10 | [Trail of Bits Skills](https://github.com/trailofbits/skills) | 性质测试、变异测试、差异审查、规格符合性、修复后验证 | A，关键软件与科学计算适配层 | 提供 Codex 插件用法；选择与代码语言、验证目标相符的模块，扫描结果需要复核 |
| S11 | [Scientific Agent Skills](https://github.com/K-Dense-AI/scientific-agent-skills) | 实验设计、统计、批判性分析、文献、科学可视化与专业工具 | A，科研工作 | 明确支持 Codex；各项依赖不同，应按具体任务选取并核验方法与来源 |
| S12 | [Hugging Face Skills](https://github.com/huggingface/skills) | Hub CLI、数据集、模型评估、Gradio、训练与实验记录 | B，使用 Hub、数据集或模型实验时 | 提供 Codex 说明；先试 hf-cli，训练或托管任务另有账户、运行环境和计算资源条件 |
| S13 | [Playwright CLI with Skills](https://github.com/microsoft/playwright-cli) | 浏览器操作、截图和可脚本化流程 | B，可重复的 Web 验收 | 可供编码代理使用；与 Playwright MCP 按会话状态、检查能力和可靠性比较，本轮不按 tokens 取舍 |

### Matt Pocock 中值得优先阅读的具体技能

| 技能 | 对当前工作的用途 | 本轮核验到的边界 |
| --- | --- | --- |
| [prototype](https://github.com/mattpocock/skills/blob/main/skills/engineering/prototype/SKILL.md) | 用可运行原型回答设计问题 | 当前内容偏逻辑状态与 UI；数值算法的正确性实验需要另设样例和判据 |
| [retro](https://github.com/mattpocock/skills/blob/main/skills/engineering/retro/SKILL.md) | 从实际会话中发现导航、检查和信息获取的改进点 | 当前文件的工作流以提出候选建议为主，不能据旧文章承诺会自动修改全部环境 |
| [teach](https://github.com/mattpocock/skills/blob/main/skills/productivity/teach/SKILL.md) | 维护学习目标、资源、课程与学习记录 | 使用当前目录作为教学工作区；宜在专用学习目录调用 |
| [grill-with-docs 与 to-spec](https://www.aihero.dev/skills/skills-changelog-v13-implement-spec-pr-retro-and-glossary-md) | 澄清有歧义的需求并形成可实施规格 | 已经确定的需求可以直接进入后续步骤；当前命名与旧分享有变化 |

其中 prototype、retro、teach 的关键 SKILL.md 已逐项阅读。其他模块主要核对项目说明与作者分享；安装前继续阅读选定版本的实际文件。

### 科研技能的选择

优先考虑 Scientific Agent Skills 中的 scientific-critical-thinking、experimental-design、statistical-analysis、literature-review、rdkit 和 scientific-visualization。它们分别对应证据评估、实验结构、数据分析、文献综合、分子处理和结果表达。[技能目录](https://github.com/K-Dense-AI/scientific-agent-skills/blob/main/docs/skills.md)

文献流程需要保留搜索式、检索日期、筛选记录和引用位置；工具返回摘要不代表完成全文评估。临床证据分级、计算实验验证和化学结构检查，应根据问题分别选择。[Literature review](https://github.com/K-Dense-AI/scientific-agent-skills/blob/main/skills/literature-review/SKILL.md)

已有的领域专用工作流可以继续复用。新增通用科研技能的作用，是补齐设计、分析和审查；具体作业输入、提交和结果契约仍以各专业应用为准。

## MCP 候选

以下功能依据维护者文档或仓库说明确认。本轮未安装这些候选，也未验证它们在当前 Codex 会话中的实际工具列表和端到端表现。

### 文档检索与代码理解

| 编号 | 项目与来源 | 增加的能力 | 优先级与条件 |
| --- | --- | --- | --- |
| M01 | [Context7](https://github.com/upstash/context7) | 查找库与版本相关文档和示例 | A，框架与 API 用法核验；关键行为仍在已安装版本上运行 |
| M02 | [DeepWiki](https://docs.devin.ai/work-with-devin/deepwiki-mcp) | 读取公开仓库的知识结构并问答 | B，读陌生开源项目；实现结论回到具体源码版本确认 |
| M03 | [Serena](https://github.com/oraios/serena) | 符号、引用、代码关系查询与编辑 | A，大型代码库的跨文件定位与修改；效果依赖语言和项目配置 |
| M04 | [GitNexus](https://github.com/abhigyanpatwari/GitNexus) | 代码图谱、调用路径与变更影响分析 | B，跨模块理解；索引需更新，当前 README 标示 PolyForm Noncommercial 许可 |

GitNexus 的常规 analyze 还会写入项目集成文件；README 提供 index-only 方式。试用时应明确选择索引还是完整集成，避免把建图效果和额外注入的技能、规则混在一起评价。[项目行为说明](https://github.com/abhigyanpatwari/GitNexus)

### 浏览器与工程运行证据

| 编号 | 项目与来源 | 增加的能力 | 优先级与条件 |
| --- | --- | --- | --- |
| M05 | [Playwright MCP](https://github.com/microsoft/playwright-mcp) | 持续浏览器会话、页面操作与结构检查 | A，Web App 的真实用户流程验收 |
| M06 | [Chrome DevTools MCP](https://github.com/ChromeDevTools/chrome-devtools-mcp) | 网络、控制台、截图和性能 trace | B，浏览器故障和性能调查；与 Playwright 的验收职责分开 |
| M07 | [GitHub MCP](https://github.com/github/github-mcp-server) | 仓库、issue、PR 和 CI 上下文 | B，使用 GitHub 的项目；与已有 gh CLI 比较完成同一任务的可靠性 |
| M08 | [Sentry MCP](https://mcp.sentry.dev/) | 错误、性能和项目运行信息 | B，已经使用 Sentry 的项目 |

### 广泛搜索与网页资料

| 编号 | 项目与来源 | 增加的能力 | 优先级与条件 |
| --- | --- | --- | --- |
| M09 | [Exa MCP](https://github.com/exa-labs/exa-mcp-server) | Web 搜索、内容获取和多步研究 | B，需要扩展检索时，与现有搜索在同一问题上比较覆盖和来源质量 |
| M10 | [Tavily MCP](https://github.com/tavily-ai/tavily-mcp) | 搜索、提取、站点映射和抓取 | B，研究型流程；接入选定版本要求的认证 |
| M11 | [Firecrawl MCP](https://github.com/firecrawl/firecrawl-mcp-server) | 搜索、网页抓取、文档解析与站点探索 | B，需收集大量技术资料时；搜索摘要、抓取文本和原始资料的证明力不同 |

这三个项目不必同时启用。值得比较的是目标资料是否找到、日期和版本是否匹配、正文是否完整，以及是否保留可追踪来源。工具覆盖面不能直接替代系统性文献检索设计。

### 论文库与文档处理

| 编号 | 项目与来源 | 增加的能力 | 优先级与条件 |
| --- | --- | --- | --- |
| M12 | [Zotero MCP](https://github.com/54yyyu/zotero-mcp) | 搜索、读取、引用和管理已有论文库 | A，已使用 Zotero 时；社区项目，不是 Zotero 官方产品 |
| M13 | [mcp-pubmed](https://github.com/benoitleq/mcp-pubmed) | 通过 NCBI E-utilities 搜索和获取文献信息 | C，社区实现；本轮仅确认仓库定位，接口、维护与故障行为需进一步验收 |
| M14 | [MarkItDown MCP](https://github.com/microsoft/markitdown/tree/main/packages/markitdown-mcp) | 将文档转换为 Markdown | A，大量文件进入阅读或研究流程时；抽样检查表格、公式和顺序 |
| M15 | [Docling MCP](https://github.com/docling-project/docling-mcp) | 文档转换与结构化处理 | B，复杂 PDF 处理；与 MarkItDown 在同一批文件上比较解析保真度 |

Zotero 本地读取、Web API 与写入模式的要求不同，不能把某一种模式的权限和版本要求推广到全部模式。[配置说明](https://github.com/54yyyu/zotero-mcp/blob/main/docs/configuration.md)

论文处理建议保留原始 PDF、提取文本和页码或段落位置。转换成功只证明文件被处理，不能证明表格、公式和引用均正确。

### 模型实验与数据库

| 编号 | 项目与来源 | 增加的能力 | 优先级与条件 |
| --- | --- | --- | --- |
| M16 | [Hugging Face MCP](https://github.com/huggingface/hf-mcp-server) | Hub 仓库与模型资料，部分 Space 和作业能力 | B，使用 Hub 时；实际工具随配置、账户和服务能力变化 |
| M17 | [W&B MCP](https://github.com/wandb/wandb-mcp-server) | 查询实验、指标、Weave traces 与评估数据 | B，已将实验记录到 W&B 或 Weave 时 |
| M18 | [DBHub](https://github.com/bytebase/dbhub) | 查询表结构、SQL 和多数据库信息 | B，项目数据库调查；先在开发数据上检查查询结果与适当访问范围 |

实验追踪 MCP 的价值在于让代理取得真实 run 和失败案例。最佳指标仍需结合数据划分、评估方法和原始产物审查。

### 记忆与结构化思考

| 编号 | 项目与来源 | 增加的能力 | 优先级与条件 |
| --- | --- | --- | --- |
| M19 | [Qdrant MCP](https://github.com/qdrant/mcp-server-qdrant) | 存储和语义检索资料或记忆 | C，需要可检索资料库时；需设计元数据、来源与更新方式 |
| M20 | [Graphiti MCP](https://github.com/getzep/graphiti/tree/main/mcp_server) | 带时间信息的关系和事件检索 | C，需要跨项目、随时间变化的关系信息时；有额外服务与数据维护工作 |
| M21 | [Knowledge Graph Memory](https://github.com/modelcontextprotocol/servers/tree/main/src/memory) | 本地实体、关系与观察记录 | C，小型跨会话记忆实验；不能自动保证事实正确或仍然有效 |
| M22 | [Sequential Thinking](https://github.com/modelcontextprotocol/servers/tree/main/src/sequentialthinking) | 组织步骤、分支与修订 | C，需要结构化思考记录时做对照；功能说明不等于对当前 Codex 有独立效果证据 |

项目事实、任务进度、个人偏好和文献证据应分别维护。记忆召回时应能回答来源、时间、适用项目与是否已被更新。已有 Brain 和项目文档时，先验证新增检索能否找到此前漏掉的关键信息，再决定扩展。

## 建议的试用顺序

### 软件开发与科学应用

先选一套任务状态记录方式，保留完成前验证。复杂错误可选 Superpowers 的调试与验证，或 Matt 的对应模块；两套应独立试用。Web 项目增加 Playwright，跨文件定位问题明显时增加 Serena，版本相关 API 问题明显时增加 Context7。

第二阶段再按技术栈加入 Impeccable、Vercel 技能、Trail of Bits 的性质测试或 DBHub。GSD、OpenSpec 与已有编排工具 的职责需要事先划分。

### 科研与学习

先选 Scientific Agent Skills 的证据分析与实验设计模块，保留已有远程计算操作流程。论文库若使用 Zotero，则优先试 Zotero MCP；资料读取有明显缺口时，比较 MarkItDown 与 Docling。

学习使用专门工作区试 teach，并要求检索、练习、解释和迁移应用。软件会话复盘可试 retro；运行结果记录可以借鉴 Showboat 的命令与输出同时留存方式。[Simon Willison 的实际测试记录](https://simonwillison.net/guides/agentic-engineering-patterns/agentic-manual-testing/)

## 跨工具移植需要检查什么

SKILL.md 可被发现，不代表其依赖、hook 事件、命令展开、工具名称和子代理行为已经映射到 Codex。选择具体版本后，阅读实际入口及 references，确认外部操作与任务范围一致，再跑一个最小样例。

安装入口以当前维护者说明和本机帮助为准。官方旧 [openai/skills](https://github.com/openai/skills) 已标记弃用并指向 [openai/plugins](https://github.com/openai/plugins)。社区文章中的旧命名、旧安装目录和“某种 hook 不支持”结论，不能直接当作当前版本事实。

效果评估见 [试用与效果评估](evaluation-plan.md)。本轮社区证据及研究分歧见 [社区实践与技术分享](community-evidence.md)。
