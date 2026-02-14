---
description: Meta Command - 对 Axiom 系统本身进行修改的入口
---

# /meta - 系统修改命令

当用户需要改进 **Axiom 系统本身**（而非项目业务代码）时使用此命令。

## Trigger
- 用户输入 `/meta [description]` 或 "系统改进 [description]"

## 作用范围

此命令明确指示 Agent：本次修改的目标是 **系统配置文件**，而非业务代码。

| 可修改范围 | 文件路径 |
|-----------|---------|
| 工作流 | `.agent/workflows/*.md` |
| 技能 | `.agent/skills/*/SKILL.md` |
| 路由规则 | `.agent/rules/router.rule` |
| 记忆模板 | `.agent/memory/*.md` |
| 进化引擎 | `.agent/memory/evolution/*.md` |
| 全局配置模板 | `.gemini/GEMINI.md.example` |
| README | `README.md` (系统说明部分) |

**禁止修改**:
- `lib/` (业务代码)
- `test/` (业务测试)
- `pubspec.yaml` (项目依赖)

## Steps

### Step 1: 识别修改意图
// turbo
1. 解析用户的 `[description]`。
2. 判断涉及的系统模块（工作流 / 技能 / 规则 / 记忆）。

### Step 2: 读取当前配置
1. 根据意图读取相关的配置文件。
2. 理解当前结构和逻辑。

### Step 3: 执行修改
1. 按照用户描述修改配置文件。
2. 保持与现有系统的格式一致性。

### Step 4: 验证一致性
1. 检查修改后是否与其他模块冲突。
2. 如有路由表相关修改，同步更新 `router.rule` 和 `GEMINI.md.example`。

### Step 5: 提交变更
// turbo
1. 使用 Git 提交修改（需用户明确允许），commit message 前缀使用 `meta:`
2. 例如: `meta: optimize evolve workflow`

## Output Format
```markdown
## 🔧 Meta Change Applied

**Modified Files**:
- `.agent/workflows/evolve.md`

**Change Summary**:
[Description of changes]

**Commit**: `meta: [commit message]`
```

## 使用示例

| 用户输入 | Agent 理解 |
|---------|-----------|
| `/meta 添加 /status 工作流` | 在 `.agent/workflows/` 创建 status.md |
| `/meta 优化知识收割逻辑` | 修改 `evolution-engine/SKILL.md` |
| `/meta 更新 README 的命令列表` | 修改 `README.md` |
| `/meta 给 router.rule 添加新路由` | 修改 `.agent/rules/router.rule` |
