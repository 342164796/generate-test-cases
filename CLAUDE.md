# 测试文档生成器 - Claude CLI 入口

本项目是一个自主学习型测试文档生成器。请完整加载并严格遵循以下 Skill 文件中定义的工作流程和行为规范：

@SKILL.md

---

## 启动行为（每次对话开始时必须执行）

1. **检测 `.memory/` 是否存在**：
   - 存在 → 读取 `.memory/user-preferences.json` 恢复用户偏好（标签、步骤粒度等）
   - 不存在 → 执行 **Phase 0 首次初始化**流程

2. **Phase 0 首次初始化**：
   - 运行 `python3 scripts/memory_manager.py --action init --project $(pwd)`
   - 初始化用户偏好，保存到 `.memory/user-preferences.json`

3. **等待用户指令**，常见触发词：
   - "生成测试用例" / "测试计划" / "测试报告"
   - "根据需求生成测试" / "分析这个PRD"

## 项目结构

- `scripts/` - 工具脚本（generate_xmind.py / memory_manager.py）
- `references/` - 规范文档（测试设计方法、优先级、追溯矩阵等）
- `.memory/` - 持久化记忆（自动生成，勿手动修改）
- `requirements/` - 放置需求文档（Markdown）
- `test-docs/` - 输出目录（生成的测试用例 XMind 等）
