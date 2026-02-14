---
description: Knowledge Query Workflow - 查询记忆中的知识条目
---

# /knowledge - 知识查询

检索项目专属知识库，回答关于架构决策、最佳实践的问题。

## Trigger
- 用户输入 `/knowledge [query]` 或 "知识 [query]"

## Steps

### Step 1: 解析查询意图
// turbo
1. 识别用户输入的查询关键词 (query)。
2. 如果未输入查询词，提示用户："请提供查询关键词，例如：`/knowledge 架构`"

### Step 2: 搜索知识库
1. 读取 `.agent/memory/evolution/knowledge_base.md` 索引。
2. 根据关键词匹配 `Title`, `Category` 或 `Tags`。
3. 找到匹配的 `k-xxx` ID。

### Step 3: 读取知识详情
1. 对于前 3 个最相关的匹配项，根据 ID 读取对应的 `.agent/memory/knowledge/k-xxx-title.md` 文件。
2. 提取 `Summary` 和 `Code Example`。

### Step 4: 生成回答
输出知识摘要，格式如下：

```markdown
## 📚 Knowledge Results

### 1. [k-xxx] Title (Confidence: 0.9)
> Summary text...

**Details**:
...

---
*(Found X results for "query")*
```
