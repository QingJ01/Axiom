---
description: PRD Decomposition Workflow - 复杂任务拆解流水线
---

# PRD Decomposition Workflow

> 本工作流用于将大型 PRD (预计工时 > 1天) 拆解为可执行的原子任务 (Task)。

## 1. 准备工作
- **Trigger**: 用户确认 PRD 终稿，且工作量预估 > 1 人日。
- **Input**: 确认后的 PRD 文件路径 (e.g. `docs/prd/PRD_Final.md`)。
- **Action**:
  - 确定下一个 Task ID (e.g. `T-101`)。
  - 创建目录: `docs/tasks/{TaskID}/`。
  - 创建子目录: `docs/tasks/{TaskID}/sub_prds/`。

## 2. 智能拆解 (Decomposition)
- **[系统指令]**: 启动 Codex Generator。
  ```bash
  codex exec --json --dangerously-bypass-approvals-and-sandbox "请扮演资深架构师。任务：
  1. 读取 PRD: {PRD_PATH}。
  2. 参考拆解标准: docs/architecture/02_Workflow_Task_Decomposition.md。
  3. 生成任务清单: docs/tasks/{TaskID}/manifest.md (必须包含 Mermaid 业务全景图)。
  4. 生成子文档: 将每个拆解出的任务写为 docs/tasks/{TaskID}/sub_prds/xxx.md。
  要求：确保任务粒度适中，依赖关系清晰(DAG)。输出必须使用中文。"
  ```
- **[系统指令]**: 等待命令完成。

## 3. PM 审计 (Audit)
- **Action**: 检查生成的 manifest.md 和子文档。
- **Checklist**:
  - [ ] 所有子任务是否覆盖了原 PRD 的全部需求？
  - [ ] 依赖关系是否闭环 (没有悬空的依赖)？
  - [ ] 命名是否规范？
- **Output**: 生成 `docs/tasks/{TaskID}/summary.md` 简报。

## 4. 交付确认
- 提示用户查阅 `docs/tasks/{TaskID}/summary.md`。
- 等待用户确认进入研发阶段 (/feature-flow)。
