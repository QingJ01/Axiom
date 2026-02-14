---
description: Patterns Query Workflow - 查询代码模式库的复用模板
---

# /patterns - 模式查询

检索项目专属代码模式库，查找可复用的架构模式、UI组件或工具类。

## Trigger
- 用户输入 `/patterns [query]` 或 "模式 [query]"

## Steps

### Step 1: 解析查询意图
// turbo
1. 识别用户输入的查询关键词 (query)。
2. 如果未输入查询词，提示用户："请提供查询关键词，例如：`/patterns repository`"

### Step 2: 搜索模式库
1. 读取 `.agent/memory/evolution/pattern_library.md`。
2. 搜索 `Pattern Index` 表中的 `Title`, `Category` 或 `Description`。

### Step 3: 读取模式详情
1. 对于匹配的模式，读取 `Pattern Details` 章节。
2. 提取 `Description` 和 `Template`。

### Step 4: 生成回答
输出模式摘要和代码模板，格式如下：

```markdown
## 🔄 Pattern Results

### 1. [P-xxx] Pattern Name (Confidence: 0.9)
> Description...

**Usage**:
// Code template...

---
*(Found X results for "query")*
```
