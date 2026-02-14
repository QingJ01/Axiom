# Axiom — Claude 适配器
# Provider: Claude (Anthropic)
# Version: 4.2 (Hybrid) | Updated: 2026-02-12

> 本文件是 Claude 用户的全局配置模板。
> 安装: 将此文件复制到 `~/.claude/CLAUDE.md`
> Windows: `C:\Users\YourName\.claude\CLAUDE.md`

---

## 0. 强制语言规则 (Mandatory)
> **Absolute Rule**: 以下规则优先级最高，不可被任何其他规则覆盖。

- **语言**: 全程使用中文对话，包括代码注释、文件命名、任务描述、思考过程。
- **对话标题**: 必须使用中文生成历史对话记录的标题 (Session Title)。
- **简洁**: 禁止解释标准库用法，禁止复述显而易见的代码变更。

---

## 1. 启动协议 (Boot Protocol)
> **Trigger**: 每次新会话开始时自动执行。

### 1.1 项目级配置检测
当工作目录下存在 `.agent/` 目录时：
1. **读取记忆**: 立即调用 `read_file` 读取 `.agent/memory/active_context.md`。
2. **检查状态**: 解析 `task_status`。
3. **恢复上下文**:
   - `IDLE`: 提示 "系统就绪，请输入需求"。
   - `EXECUTING`: 提示 "检测到中断的任务，是否继续？"。
   - `BLOCKED`: 提示 "上次任务遇到问题，需要人工介入"。

### 1.2 路由规则加载
当需要修改代码时：
1. 读取 `.agent/rules/router.rule` 获取任务分发规则。
2. 读取 `.agent/memory/project_decisions.md` 获取架构约束。
3. 读取 `.agent/memory/user_preferences.md` 获取用户偏好。

---

## 2. 智能工作流触发 (Smart Workflow Triggers)
> **关键机制**: 根据用户意图，自动匹配并加载 `.agent/workflows/` 下的流程文件。
> **指令**: 在执行前，**必须**先调用 `read_file` 读取对应的 Workflow 文件，并严格按步骤执行。

### 2.0 工作流触发器 (Workflow Triggers)
- 触发规则见下表；按用户意图路由到对应 workflow。

| 用户意图 | 触发工作流 文件路径 | 对应指令(Slash Command) |
| :--- | :--- | :--- |
| **提出新需求 / 做个功能** | `.agent/workflows/1-drafting.md` | `/draft` |
| **需求评审 / 专家审查** | `.agent/workflows/2-reviewing.md` | `/review` |
| **拆解大任务 / 细化设计** | `.agent/workflows/3-decomposing.md` | `/decompose` |
| **开始开发 / 交付流水线 (Manifest)** | `.agent/workflows/4-implementing.md` | `/feature-flow` |
| **报错了 / 修 Bug / 分析日志** | `.agent/workflows/analyze-error.md` | `/analyze-error` |
| **反思 / 总结 / 进化** | `.agent/workflows/reflect.md` | `/reflect` |
| **导出系统 / 打包** | `.agent/workflows/export.md` | `/export` |

### 2.1 常用辅助命令
| 命令 | 作用 |
| :--- | :--- |
| `/start` | 静默启动，恢复上下文 |
| `/suspend` | 保存当前状态，生成会话总结 |
| `/status` | 显示当前状态和进度 |
| `/knowledge [query]` | 📚 查询知识库 |
| `/patterns [query]` | 🔄 查询代码模式库 |
| `/rollback` | 回滚到上一个检查点 |

---

## 3. Claude 专属能力映射
| 操作 | Claude API |
|------|-----------|
| 读取文件 | `read_file` |
| 编辑文件 | `replace_string_in_file` |
| 创建文件 | `create_file` |
| 运行命令 | `run_in_terminal` |
| 搜索文件 | `grep_search` / `semantic_search` |

### Claude 注意事项
- **上下文窗口**: 200K tokens，需注意大文件分段读取
- **无 exec 模式**: Dispatcher 自动调度功能受限，建议使用对话模式执行工作流
- **编辑精度**: `replace_string_in_file` 要求精确匹配旧字符串，建议多包含上下文行
- **Tool Use**: Claude 原生支持 Tool Calling，工作流中可直接调用工具

### Claude 最佳实践
1. 使用 `grep_search` 先定位代码再用 `read_file` 读取
2. 编辑文件时提供 3-5 行上下文确保唯一匹配
3. 复杂任务拆分为小步骤，每步验证后再继续
4. 利用 `semantic_search` 进行模糊搜索

---

## 4. 门禁规则 (Gatekeeper Rules)
> 以下情况必须拦截，不允许继续执行。

### 4.1 专家评审门禁 (Expert Gate)
- **触发**: 所有新功能需求。
- **动作**: 必须经过 `ai-review` 流程（含 Gatekeeper, Parallel Review, Arbitration）。
- **通过条件**: Aggregator 生成 `review_summary.md` 并结论为 "Pass"。

### 4.2 PRD 确认门禁 (User Gate)
- **触发**: PRD 终稿生成完成。
- **动作**: 必须显示 "PRD 已生成，是否确认执行？(Yes/No)"。
- **恢复**: 用户明确确认后才允许进入开发阶段。

### 4.3 复杂度门禁 (Complexity Gate)
- **触发**: 开发前评估工时 > 1 人日。
- **动作**: 必须触发 `prd-decomposition` 进行任务拆解。

### 4.4 编译提交门禁 (CI Gate)
- **触发**: 代码修改完成。
- **动作**: 必须执行 `flutter analyze` + `flutter test`。
- **通过条件**: 无错误时自动执行 `git commit`。

---

## 5. 技能路由表 (Skill Router)
> 根据任务类型调用对应技能。

| 任务类型 | 调用技能 | 位置 |
|---------|---------|-----|
| 生成 PRD | `prd-crafter-pro` | 项目级 `.agent/skills/` |
| 专家评审 | `ai-expert-review-board` | 项目级 `.agent/skills/` |
| 读写记忆 | `context-manager` | 项目级 `.agent/skills/` |
| 错误分析 | `exception-guardian` | 全局技能库（如已安装） |
| UI/UX 设计 | `ui-ux-pro-max` | 全局技能库（如已安装） |
| 飞书文档 | `feishu-doc-assistant` | 全局技能库（如已安装） |
| **自进化** | `evolution-engine` | 项目级 `.agent/skills/` |

---

## 6. 进化引擎自动行为 (Evolution Auto Behaviors)
> 这些行为无需用户确认，自动执行。

| 触发事件 | 自动行为 |
|---------|---------|
| 任务完成 | 将代码变更加入 `learning_queue.md` |
| 错误修复成功 | 将修复模式加入学习队列 (P1) |
| 工作流完成 | 更新 `workflow_metrics.md` |
| 状态 → ARCHIVING | 自动触发 `/reflect` |
| 状态 → IDLE | 处理学习队列 (P0/P1) |

---

## 7. 项目目录约定 (Directory Convention)
```
项目根目录/
├── .agent/                    # Agent 配置 (如果存在则启用 Axiom)
│   ├── memory/               # 记忆系统
│   ├── rules/                # 路由规则
│   ├── skills/               # 项目级技能
│   └── workflows/            # 工作流定义
├── lib/                       # Flutter 源码
├── test/                      # 测试文件
└── docs/prd/                  # PRD 文档输出目录
```

_Axiom v4.2 — Claude Adapter (Hybrid)_
