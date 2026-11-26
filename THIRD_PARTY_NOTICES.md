# 第三方来源与许可证

本仓库保留上游文件及其许可证；本地适配记录由来源清单维护。

| 内容 | 固定来源 | 许可证文件 |
| --- | --- | --- |
| prototype、teach、retro、writing-for-agents | Matt Pocock skills，见 `workflow/sources.json` | [workflow/upstream/LICENSE](workflow/upstream/LICENSE) |
| code-review、diagnosing-bugs | Matt Pocock skills，见 `baseline/sources.json` | [mattpocock.LICENSE](baseline/licenses/mattpocock.LICENSE) |
| property-based-testing | Trail of Bits skills，见 `baseline/sources.json` | [trailofbits.LICENSE](baseline/licenses/trailofbits.LICENSE) |
| 六个科研 skills | K-Dense Scientific Agent Skills，见 `baseline/sources.json` | [scientific-agent-skills.LICENSE.md](baseline/licenses/scientific-agent-skills.LICENSE.md) |
| Playwright MCP 与传递依赖 | npm 包和版本见 `workflow/browser/package-lock.json`，部署时下载 | 各 npm 包随附的 LICENSE / NOTICE |

本说明不改变上游的授权条件，也不为项目自有内容指定开源许可证。

Claude Code / Cursor Agent 的本地插件由安装器从这些固定文件生成，连同参考文件和许可证一并复制。`teach` / `retro` 的显式调用字段只在生成副本中恢复，适配记录见 `workflow/sources.json`；不将账号配置或运行缓存打包。
