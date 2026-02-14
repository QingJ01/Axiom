---
description: 代码模式库 - 存储可复用的代码模式和模板
version: 1.0
last_updated: 2026-02-08
---

# Pattern Library (代码模式库)

本文件存储从项目中识别出的可复用代码模式。

## 1. 模式索引 (Pattern Index)

| ID | Name | Category | Occurrences | Confidence | Status |
|----|------|----------|-------------|------------|--------|
| P-001 | Markdown Workflow Pattern | workflow-def | 5 | 0.9 | active |

## 2. 模式分类 (Categories)

| Category | Description | Count |
|----------|-------------|-------|
| workflow-def | 工作流定义模式 | 1 |
| data-layer | 数据层模式 | 0 |
| ui-layer | UI 层模式 | 0 |
| business-logic | 业务逻辑模式 | 0 |
| common | 通用模式 | 0 |

---

## 3. 模式详情 (Pattern Details)

### P-001: Markdown Workflow Pattern

**Category**: workflow-def  
**Occurrences**: 5 (start.md, feature-flow.md, analyze-error.md, evolve.md, reflect.md)  
**Confidence**: 0.9  
**First Seen**: 2026-02-08  
**Files**: `.agent/workflows/*.md`

**Description**:
> 使用 Markdown 定义原子工作流，包含 Trigger, Steps 和 Output Format 三要素。

**Template**:
```markdown
---
description: [Short Description]
---

# /command - [Workflow Name]

## Trigger
- 用户输入 `/command`

## Steps
// turbo (if auto-run)
1. Step 1...
2. Step 2...

## Output Format
(Template)
```


**Usage**:
```dart
final data = await repository.getWithCache('user_profile', () => api.fetchProfile());
```

---

## 4. 模式匹配规则 (Detection Rules)

> 定义如何自动检测代码中的模式

### 规则格式
```yaml
pattern_id: P-xxx
triggers:
  - keyword: "getWithCache"
  - structure: "class.*Repository.*_cache"
min_occurrences: 3
```

---

## 5. 待验证模式 (Pending Patterns)

> 出现次数不足，暂未提升为正式模式

| ID | Name | Occurrences | Notes |
|----|------|-------------|-------|
| - | - | - | 暂无 |
