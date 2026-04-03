# 交互模式与问题模板

本文档定义测试文档生成器的交互模式、检查点问题模板和歧义处理规则。

---

## 交互模式定义

### 模式类型

采用快速模式：回车继续，仅在发现问题或异常时询问用户。

### 偏好存储

用户偏好保存在 `.memory/user-preferences.json` 中。

---

## 检查点定义

### 检查点概览

| 检查点 | 阶段 | 行为 |
|--------|------|------|
| 解析确认 | Phase 2.5 | 摘要+问题时询问 |
| 歧义处理 | Phase 2.6 | 仅关键歧义 |
| 生成预览 | Phase 2.8 | 统计数据 |

---

## 问题模板

### 1. 偏好设置（首次运行）

**触发条件**：`.memory/user-preferences.json` 不存在时

**后续处理**：
- 初始化 `.memory/` 文件夹
- 保存默认偏好到 `.memory/user-preferences.json`

---

### 2. 检查点1：解析确认

**触发条件**：Phase 2 解析完成后

#### 解析确认

**显示内容**：
```markdown
## 解析完成

已识别 **{module_count}** 个模块，**{req_count}** 条需求，**{rule_count}** 条业务规则

{如果有警告}
⚠️ 发现以下潜在问题：
- {warning_message}
```

**AskUserQuestion 配置**（仅有警告时）：
```yaml
questions:
  - question: "发现潜在问题，如何处理？"
    header: "解析警告"
    multiSelect: false
    options:
      - label: "忽略，继续生成"
        description: "问题不影响生成质量"
      - label: "查看详情"
        description: "显示完整解析结果"
```

**无警告时**：显示摘要后自动继续

---

### 3. 歧义处理

**触发条件**：检测到不明确的需求描述

**歧义类型**：

| 类型代码 | 类型名称 | 检测模式 | 询问重点 |
|---------|---------|---------|---------|
| `BOUNDARY_UNCLEAR` | 边界不明确 | "适当"、"合理"、"一定" | 询问具体数值 |
| `RULE_CONFLICT` | 规则冲突 | 互斥条件 | 询问优先级 |
| `MISSING_ERROR` | 缺少错误处理 | 无失败子句 | 询问预期行为 |
| `VAGUE_CRITERIA` | 模糊验收标准 | "正常"、"正确" | 询问具体结果 |
| `INCOMPLETE_FLOW` | 流程不完整 | 缺少步骤 | 询问完整流程 |

**AskUserQuestion 配置**：
```yaml
questions:
  - question: "需求存在歧义，请帮助澄清"
    header: "歧义 {current}/{total}"
    multiSelect: false
    options:
      - label: "接受我的理解"
        description: "{interpretation}"
      - label: "提供不同解释"
        description: "我将输入正确的理解"
      - label: "跳过此需求"
        description: "不为此需求生成用例"
      - label: "标记为待确认"
        description: "生成用例但添加待确认标记"
```

**显示上下文**：
```markdown
## 需求歧义确认 ({current}/{total})

**需求原文**：
> {original_text}

**歧义类型**：{ambiguity_type_name}

**我的理解**：
{claude_interpretation}

**影响范围**：
- 可能影响 {affected_cases} 条用例
- 涉及模块：{affected_modules}
```

#### 歧义过滤

仅询问以下情况：
- 影响 P0/P1 用例的歧义
- 涉及核心业务流程的歧义
- 可能导致生成错误的关键歧义

其他歧义自动采用 AI 的理解，并在生成结果中标注。

---

### 4. 检查点2：生成预览

**触发条件**：歧义处理完成，准备生成用例

**显示内容**：
```markdown
## 生成预览

将生成 **{total_cases}** 条用例：
P0:{p0} | P1:{p1} | P2:{p2} | P3:{p3}

覆盖率: {coverage_rate}%
```

**AskUserQuestion 配置**（仅分布异常时）：
```yaml
questions:
  - question: "P0比例({p0_percent}%)超出建议范围(10-15%)，是否调整？"
    header: "分布警告"
    multiSelect: false
    options:
      - label: "自动调整到建议范围"
        description: "将部分 P0 用例降级为 P1"
      - label: "保持当前分布"
        description: "不做调整，继续生成"
```

---

## 响应处理规则

### 用户响应映射

| 用户输入 | 处理动作 |
|---------|---------|
| `确认` / `ok` / `yes` / `y` | 继续下一步 |
| `取消` / `cancel` / `no` / `n` | 中止流程 |
| `详情` / `detail` / `more` | 显示详细信息 |
| `修改` / `edit` / `change` | 进入修改模式 |
| `重试` / `retry` / `redo` | 重新执行当前步骤 |
| `帮助` / `help` / `?` | 显示当前步骤帮助 |

### 超时处理

无超时限制，无异常时自动继续。

### 错误恢复

当用户输入无法识别时：
1. 显示可用选项列表
2. 提示正确的输入格式
3. 等待用户重新输入

---

## 进度指示

### 流程进度显示

```
[■■■■■□□□□□] 50% - 正在解析需求...

阶段: 2/5 需求解析
已处理: 10/20 个需求
当前: 分析登录模块边界条件
```

### 检查点进度

```
检查点 1/3: 解析确认
└── ✓ 模块识别完成
└── ✓ 需求提取完成
└── → 等待用户确认
```

---

## 记忆集成与自学习

### 偏好自动应用

每次启动时从 `.memory/user-preferences.json` 读取：
- `default_output_dir`: XMind 输出目录默认值
- `default_tag`: 上次选择的标签值，作为建议选项

### 歧义决策复用

从 `.memory/ambiguity-decisions.json` 读取历史决策：
- 自动应用历史决策，不再询问

### 学习用户习惯

每次交互后自动记录：
- 用户对歧义的处理偏好（ask/skip/mark）
- 用户常调整的优先级比例
- 用户选择的标签值
- 反馈修正（如删减用例、补充场景）

### 质量趋势

从 `.memory/generation-history.json` 分析：
- 历史生成的优先级分布，作为下次生成的参考基线
- 常见模块清单，优化场景覆盖模式
- 覆盖率趋势，发现系统性遗漏
