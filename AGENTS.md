# Workstyle 仓库维护约定

默认中文交流。项目背景与目录职责见 README.md，部署和回退见 QUICKSTART.md。

- 配置代码保持 `baseline/` 与 `workflow/` 分层；机器路径在安装时解析。
- 修改安装、更新或卸载行为时，验证空目录、重复执行、冲突保护和恢复；运行 `python3 -m unittest discover -s tests -v`。测试使用临时 Codex home，不写入真实个人配置。
- 更新 vendored skills 或浏览器版本时，阅读 CONTRIBUTING.md，并同步 sources.json、锁文件和许可证。上游参考资料按固定版本理解。
- 多步骤工作记录在本项目 `.workstyle/tasks/`，与用户说明保持一致。配置部署记录和科学结论的证据分别说明。
- 复杂实现完成后请求独立只读子代理审查，向其提供需求与原始文件，核实问题后再修正。简单修改按实际风险验证。
- 提交前运行 `git diff --check` 并检查暂存内容；凭据、个人配置、运行缓存与任务私密材料留在 Git 之外。
