# Workstyle 安装验收

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
