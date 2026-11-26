# 维护与迭代

仓库同时保存可部署配置与选型依据。历史研究注明核对日期；新的判断附上适用版本和实际证据。任务质量的变化按 [效果评估方案](docs/evaluation-plan.md)记录，安装成功不能代替效果评估。

## 修改与验证

```bash
git switch -c feature/short-description
# 修改实现、对应说明和有意义的行为测试
python3 -m unittest discover -s tests -v
git diff --check
git diff
git add 指定的文件
git commit -m "说明具体改变"
```

保持 `main` 可部署。安装器测试覆盖首次安装、重复执行、路径含空格、缺少依赖、用户文件冲突、受保护更新与备份恢复；新增行为沿用 Python unittest。测试使用临时 `WORKSTYLE_HOME`、Codex home 和 bin，不写入真实用户配置。GitHub Actions 在 Python 3.10 与 3.12 上执行相同检查，网络 MCP 测试留给允许联网的部署环境。

真实部署验证使用仓库外的临时 Workstyle home / Codex home / bin，运行带 `--harness` 的 `workflow/bootstrap.py`。发布前检查目标 CLI 的插件或技能发现，以及浏览器和 MCP 行为；保留原生权限和项目规则。通用规则只在 `workflow/core.md` 维护，CLI 参数与生成格式分别在 `harnesses.py`、`launcher.py` 和 `adapter_install.py`；接口依据见 [CLI 接入说明](workflow/HARNESSES.md)。

## 更新第三方内容

技能升级选择明确的上游 commit，保留完整 references、scripts、agents 与许可证，同时更新相应 `sources.json` 的来源、哈希和本地适配。改动仅限需要的能力；候选技能不因列在研究文档中就自动安装。

浏览器升级先修改 `workflow/browser/package.json` 中的确切版本，再生成并提交锁文件：

```bash
npm install --package-lock-only --ignore-scripts --prefix workflow/browser
python3 workflow/bootstrap.py --update
codex-work doctor --mcp
```

同时更新 `workflow/sources.json` 与部署版本说明，核实 Node 要求和新的 Chromium 下载版本。不要手工编辑 `node_modules`。

## 远端与稳定版本

本仓库的远端为 `https://github.com/Aunity/llm-work.git`。已有本地仓库且尚未配置远端时：

```bash
git remote add origin https://github.com/Aunity/llm-work.git
git push -u origin main
```

后续用分支审查与合并维护主线；经部署验证的 commit 可以打版本 tag，再让其他机器检出同一版本。不要自动移动已发布 tag。发布记录应写明变更、检查范围、迁移步骤和已知限制。

## 本地材料

`.gitignore` 排除依赖、虚拟环境、任务记录、即时检查报告、个人课程、凭据和本地 Codex 配置。只提交可重用源码、模板、锁文件、说明及去除私密信息的验证结论。`git status` 和 `git diff --cached` 是每次提交前的检查入口。

公开提交使用 GitHub 隐私邮箱。发布前检查拟推送分支的完整历史与提交身份；忽略规则不会移除已经提交的内容。需要脱敏时在隔离副本操作，原始 Git bundle 和审计明细留在忽略的本地目录；仅推送经过检查的分支。

本仓库自有内容尚未声明统一开源许可证，本次发布不新增授权条款。第三方内容仍遵循各自随附的许可证，见 [第三方说明](THIRD_PARTY_NOTICES.md)。
