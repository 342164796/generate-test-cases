# 记忆数据结构

定义 `.memory` 目录中各文件的数据结构，支撑跨会话自学习。

## .memory 目录结构

```
.memory/
├── project-context.json      # 项目上下文信息
├── terminology.json          # 领域术语库（自动学习 + 手动添加）
├── generation-history.json   # 生成历史（质量趋势分析）
├── user-preferences.json     # 用户偏好（自动记忆）
└── ambiguity-decisions.json  # 歧义决策记录（避免重复询问）
```

## 各文件 Schema

### project-context.json

项目基本信息，首次 `init` 时创建。

```json
{
  "project_name": "string",
  "initialized_at": "ISO datetime",
  "requirements_dir": "requirements/",
  "output_dir": "test-docs/"
}
```

### terminology.json

领域术语和模块缩写，解析需求时自动提取 + 用户手动补充。

```json
{
  "domain_terms": {
    "GMV": "商品交易总额",
    "SKU": "库存单位"
  },
  "module_abbreviations": {
    "登录": "LOGIN",
    "订单": "ORDER"
  }
}
```

**自学习规则**：
- 解析需求时自动识别 `术语（解释）`、`缩写：全称` 等模式
- 用户修正术语时询问是否记住
- 跨会话复用，减少重复提取

### generation-history.json

生成历史，用于质量趋势分析和生成策略优化。

```json
{
  "generations": [
    {
      "date": "ISO datetime",
      "type": "test_case",
      "source": "requirements/用户登录模块_PRD.md",
      "output": "test-docs/testcases_20260225143022.xmind",
      "case_count": 42,
      "coverage_rate": "100%",
      "priority_distribution": { "P0": 5, "P1": 16, "P2": 17, "P3": 4 },
      "modules": ["用户名密码登录", "手机号验证码登录", "第三方登录"],
      "tag": "C端"
    }
  ]
}
```

**自学习规则**：
- 每次生成后自动写入，积累质量基线
- 下次生成同类需求时参考历史分布（如 P0 占比偏高则自动提示）
- 统计常见模块，优化场景覆盖模式

### user-preferences.json

用户交互偏好，自动记忆操作习惯。

```json
{
  "default_output_dir": "./test-docs",
  "show_samples_in_preview": true,
  "auto_confirm_parsing": false,
  "ambiguity_handling": "ask | skip | mark",
  "priority_distribution": {
    "p0_min": 10,
    "p0_max": 15,
    "warn_on_imbalance": true
  },
  "default_tag": "C端",
  "step_granularity": "fine | normal | coarse",
  "title_style": null,
  "updated_at": "ISO datetime"
}
```

**字段说明**：
| 字段 | 说明 |
|------|------|
| `default_output_dir` | XMind 输出目录 |
| `show_samples_in_preview` | 预览时展示样例 |
| `auto_confirm_parsing` | 自动确认解析结果 |
| `ambiguity_handling` | 歧义处理策略：`ask` 询问 / `skip` 跳过 / `mark` 标记 |
| `priority_distribution` | P0 占比偏好 + 失衡警告开关 |
| `default_tag` | 上次选择的标签值，下次可作为默认建议 |
| `step_granularity` | 用例步骤粒度：`fine` 细化 / `normal` 默认 / `coarse` 粗略 |
| `title_style` | 用户偏好的用例标题风格（如“输入X，结果Y”），null 表示未设置 |

### ambiguity-decisions.json

歧义决策记录，避免相同歧义反复询问用户。

```json
{
  "decisions": [
    {
      "date": "2026-02-25",
      "type": "BOUNDARY_UNCLEAR",
      "context": "密码复杂度",
      "original_text": "密码应有足够的复杂度",
      "user_decision": "长度8-20位，必须包含大小写字母和数字",
      "applied_to": ["REQ_001"]
    }
  ]
}
```

**自学习规则**：
- 每次歧义决策自动存入
- 后续遇到相似歧义时自动复用历史决策

---

## 记忆更新规则

| 时机 | 更新操作 | 脚本调用 |
|------|---------|---------|
| 首次使用 | 创建所有文件 | `memory_manager.py --action init` |
| 解析需求 | 提取新术语 | `memory_manager.py --action update --type terminology` |
| 处理歧义 | 记录决策 | `memory_manager.py --action add-ambiguity` |
| 生成完成 | 写入历史 | `memory_manager.py --action add-record --data '{...}'` |
| 用户反馈 | 更新偏好 | `memory_manager.py --action set-pref` |
| 用户要求 | 清除所有 | `memory_manager.py --action clear` |

## 使用示例

```bash
# 初始化记忆
python3 memory_manager.py --action init --project "${SKILL_ROOT}"

# 读取记忆
python3 memory_manager.py --action read --project "${SKILL_ROOT}"

# 更新术语
python3 memory_manager.py --action update --project "${SKILL_ROOT}" --type terminology \
  --data '{"domain_terms": {"SKU": "库存单位"}}'

# 添加生成记录
python3 memory_manager.py --action add-record --project "${SKILL_ROOT}" \
  --data '{"type":"test_case","source":"requirements/用户登录模块_PRD.md","output":"test-docs/testcases_20260225143022.xmind","case_count":42,"coverage_rate":"100%"}'

# 记录歧义决策
python3 memory_manager.py --action add-ambiguity --project "${SKILL_ROOT}" \
  --keyword "密码复杂度" --data '{"type":"BOUNDARY_UNCLEAR","user_decision":"8-20位含大小写字母和数字"}'

# 查找历史歧义
python3 memory_manager.py --action find-ambiguity --project "${SKILL_ROOT}" --keyword "密码"

# 设置用户偏好
python3 memory_manager.py --action set-pref --project "${SKILL_ROOT}" \
  --data '{"default_tag": "C端"}'

# 清除记忆
python3 memory_manager.py --action clear --project "${SKILL_ROOT}"
```
