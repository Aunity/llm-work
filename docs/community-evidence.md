# Codex 的社区实践与技术分享

社区资料显示，使用者对完整工作流套件的评价存在明显分歧。对当前工作更有用的做法，是从具体失败模式出发，选择能够补充遗漏步骤、事实或验证证据的扩展，再检验实际收益。

资料核对日期：2026 年 11 月 16 日。本文区分维护者的能力说明、作者的工作方法、使用者的自报体验和研究中的对照结果。

## 来源的证明范围

| 类型 | 可以支持什么 | 不能直接支持什么 |
| --- | --- | --- |
| 官方文档与维护者仓库 | 公开功能、接口、安装方法与已说明的限制 | 本机已接通，或一定提高任务质量 |
| 作者技术分享 | 作者如何组织工作及其实际案例 | 对其他模型、项目和人员同样有效 |
| 社区使用反馈 | 某位使用者遇到的收益、问题与待验证假设 | 发生率、因果关系或普遍优劣排序 |
| 配对评估研究 | 给定任务、模型与环境下的增量效果 | 对当前 Codex 与所有扩展的普遍结论 |

没有按点赞、stars 或安装量评定质量。论文结果依据指定版本的摘要与公开研究设计整理，本轮没有独立复现评估。

## 第一手分享与社区讨论

| 来源 | 读到的具体内容 | 对当前工作的启发 |
| --- | --- | --- |
| [Simon Willison 的 Agentic manual testing](https://simonwillison.net/guides/agentic-engineering-patterns/agentic-manual-testing/) | 作者让代理运行真实流程，用 Showboat 留下命令、输出和图片 | 将验证记录做成可检查的产物，便于复核科学应用和 API 的实际行为 |
| [Simon Willison 的 Interactive explanations](https://simonwillison.net/guides/agentic-engineering-patterns/interactive-explanations/) | 作者通过交互演示理解代理生成代码中的算法 | 学习任务可要求可操作的解释、逐步运行和迁移练习，减少对核心实现的理解欠缺 |
| [Matt Pocock 的 v1.3 分享](https://www.aihero.dev/skills/skills-changelog-v13-implement-spec-pr-retro-and-glossary-md) | 将规格、任务、实现、PR 和复盘衔接；文档从 CONTEXT.md 改为 GLOSSARY.md | 跟随选定版本的文件约定，升级技能时同步检查项目文档 |
| [Matt 的 setup 技能说明](https://www.aihero.dev/skills-setup-matt-pocock-skills) | 按项目记录 issue tracker 和领域文档位置；列出了旧文件选择对 Codex 的潜在问题 | 核对规则写入的文件是否会被当前客户端加载；不能只检查安装成功 |
| [Addy Osmani 的 Agent Skills](https://github.com/addyosmani/agent-skills) | 将规格、实施、测试和审查编码成工作流；披露单项复制可能缺共享 references | 好技能应有执行步骤和结束条件；安装时核对整个依赖闭包 |
| [Takahiro Misawa 的计算材料科学技术分享](https://www.r-ccs.riken.jp/fugaku-next/fugakunext_15th_application-seminar.pdf) | 2026 年 5 月 27 日分享，报告科学代码迁移、设计互审与测试变绿但物理错误的情形，重点见 PDF 第 15 至 19 页 | 数值与科学不变量应独立验证；跨代理审查可以辅助发现设计和源码不一致，仍要回到实际计算 |
| [OpenAI 社区的长期上下文讨论](https://community.openai.com/t/how-are-people-managing-context-in-codex/1393098) | 有人认可 Superpowers 对大任务的结构帮助，也讨论阶段切分、外部状态和新会话恢复 | 验证能否从项目状态恢复任务，比仅保留完整聊天更贴近长期交付需求 |
| [Reddit 的框架使用复盘](https://www.reddit.com/r/codex/comments/1xfktrc/using_codex_with_popular_skills_frameworks_my/) | 发帖者报告某些流程将小项目推向过度复杂的架构，之后组合使用工作流与 issue 管理 | 在任务中写明运行规模、部署环境、维护能力和复杂度约束 |
| [Reddit 对 Superpowers 的质疑](https://www.reddit.com/r/codex/comments/1w8cipz/do_you_still_use_the_superpowers_skill/) | 部分回复认为规则冲突、过度规划或默认模型能力已足够 | 将“完整套件是否适合”设为可检验问题；该讨论不是普遍效果评估 |
| [V2EX 的技能使用讨论](https://v2ex.com/t/1225240) | 有人手动选择少量技能，有人更偏好包含 worktree 和审查的完整过程 | 适合同时测试手动模块组合与完整工作流，比较最终质量和接管情况 |
| [V2EX 的项目经验沉淀讨论](https://v2ex.com/t/1222745) | 讨论规范目录、入口文件和跨项目知识组织 | 保留共享知识的权威来源，同时让每个项目维护自身的运行与验证方式 |
| [文浩的 Codex CLI 与 MCP 工作流分享](https://blog.wenhaofree.com/posts/articles/codex-cli-mcp-skills-workflow/) | 2026 年 10 月 26 日文章，将规格、小步实现、验证和复盘串联 | 可作为中文入门材料；其以测试退出码作为唯一准出依据的表述，不足以覆盖科研正确性与需求完整性 |

这些反馈来自有限样本和不同版本环境，不宜将讨论中的模型评价、速度倍数或主观满意度直接用于选型。

## 对照研究并没有给出统一答案

### SkillsBench

[SkillsBench v4](https://arxiv.org/abs/2602.12670v4) 于 2026 年 6 月 14 日更新。摘要报告：在 87 个任务、18 种模型与 harness 配置的配对评估中，精选 skills 使平均通过率从 33.9% 提高到 50.5%。不同配置的增益差异明显，范围较聚焦的技能组合优于大而全的内容。

这支持在专业程序性知识不足时尝试精选技能，但不能推出某个热门套件对当前 Codex 一定有效。

### SWE Skills Bench

[SWE-Skills-Bench v2](https://arxiv.org/abs/2603.15401v2) 于 2026 年 10 月 27 日更新。摘要报告：在其测试的 98 个软件工程 skills 中，92 个没有统计显著效果；平均通过比例从 76.6% 变为 76.9%。有帮助的技能补充代理原本遗漏的程序；有害案例则让代理被自身模板牵引或偏离明确需求。

这支持逐项评估增量效果，而不是把安装完成当作质量提高。

### 现实检索条件下的技能使用

[How Well Do Agentic Skills Work in the Wild](https://arxiv.org/abs/2604.04323) 于 2026 年 4 月 6 日提交。作者将技能选择从直接提供匹配技能，扩展到从大型真实技能库检索；随着匹配条件变差，原有收益减弱。针对任务调整技能，在其评估中能够恢复部分效果。

这说明技能库的规模、发现能力、任务匹配和内容质量需要分别判断。

### 为什么不能合并比较数值

以上研究的任务集、基线、技能选择方式和评估协议不同。一个基准在精选的专业技能上测得收益，另一个在软件工程公共技能上测得有限收益，并不构成直接矛盾。应分别阅读选定版本的方法和结果，不能把它们的通过率直接求平均，或据此宣布某一类 skills 普遍有用或无用。

## 对前一轮建议的修订

### 保留的建议

明确验收、实际运行、保存证据、验证关键未知，以及保持可恢复的项目状态，仍是首要工作。较高推理强度可以保留；新增能力应通过实际任务来判断。

### 调整的建议

本轮进一步限定 Superpowers 的推荐范围：先对复杂任务测试调试与验证模块。同时提高 Matt 的 prototype、retro、teach，以及领域相关验证技能的试用优先级。

按需组合并非为了节省 tokens，而是为了观察哪些规则确实改善当前任务，避免不同流程对同一阶段给出不一致要求。完整套件仍值得在复杂新项目上作为单独方案比较。

### 针对科研补充的建议

优先解决原始材料、数据和运行结果是否可获得：论文库、PDF 解析、专业数据源、实验记录和计算结果契约。把语法正确、程序运行成功、统计解释成立和科学结论成立分开验证。

代码审查和第二模型的意见是额外证据来源。涉及能量符号、单位、坐标、立体化学、数据泄漏或数值收敛时，应安排独立检查或已知基准，不能只依赖代理之间达成共识。

## 版本与来源核验中的具体发现

| 发现 | 处理方式 |
| --- | --- |
| [openai/skills](https://github.com/openai/skills) 已标记弃用并指向 [openai/plugins](https://github.com/openai/plugins) | 当前安装入口回到官方插件说明核对 |
| 社区旧文章把某些 Codex hooks 描述为不支持 | 作为历史版本经验；当前是否支持由本机与官方文档确认 |
| Matt 的博客、README 与具体 SKILL.md 的表述可能不同 | 选择固定版本，以具体技能文件为行为依据；例如当前 retro 先提出建议 |
| 本轮访问旧 handoff 固定文件路径未取得内容 | 不把它列为已逐项核验的可安装技能；继续使用任务交接模板 |
| PubMed MCP 存在多个社区同名实现 | 本文明确列出仓库作者，不称为 NCBI 官方服务；具体工具接口仍待验收 |
| Zotero MCP 出现在 registry 中 | Registry 收录不改变其社区维护者身份 |
| 部分聚合站与镜像自称官方中文文档 | 仅作发现线索，功能判断回到原始官方域名或维护者仓库 |

## 后续适合继续跟踪的资料

- [Simon Willison 的 Agentic Engineering Patterns](https://simonwillison.net/guides/agentic-engineering-patterns/)：测试、验证产物、代码解释与代理工作方法。
- [Matt Pocock 的技能源码](https://github.com/mattpocock/skills)：实际 SKILL.md、版本变更和小型可组合流程。
- [Addy Osmani 的技能源码](https://github.com/addyosmani/agent-skills)：工程阶段与明确检查点。
- [Trail of Bits Skills](https://github.com/trailofbits/skills)：性质测试、变异测试和证据驱动审查。
- [Scientific Agent Skills](https://github.com/K-Dense-AI/scientific-agent-skills)：按领域选择科学工作流，并检查依赖与适用范围。

下一步的验证设计见 [试用与效果评估](evaluation-plan.md)。
