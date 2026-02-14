---
description: Phase 3: 实施、测试、编译与汇报生成工作流
---

# 工作流：实施交付 (Phase 3)

本工作流执行 Manifest 中的任务，通过测试保证质量，并交付可编译的版本。

## 前置条件
- 已确认的 Manifest 存在于 `docs/tasks/[id]/manifest.md`。

## 执行步骤

1.  **DAG 分析与分发 (DAG Analysis & Dispatch)**
    - **动作**: 读取 `manifest.md`。识别依赖已满足 (Ready to Start) 的任务。
    - **并行执行**:
        - 先读取 `.agent/rules/provider_router.rule`，解析 `WORKER_EXEC`。
        - 启动最多 3 个并行 `{WORKER_EXEC}` Worker。
        - **角色**: 全栈开发者 (Standard Worker)。
        - **输入**: Sub-PRD + Manifest。
        - **要求**: 必须编写测试。必须通过测试。
    - **循环**: 当任务完成 (`[x]`)，检查 DAG 是否有新任务解锁。重复直至所有任务完成。

2.  **编译门禁 (Compilation Gate)**
    - **动作**: 运行全量构建命令 (如 `flutter build apk --debug`)。
    - **检查**:
        - **成功 (Exit Code 0)**: 进入步骤 3。
        - **失败**: 
            - 触发 `/analyze-error` 工作流 (自动修复)。
            - 重试步骤 2。

3.  **汇报与交付 (Reporting & Handover)**
    - **动作**: 生成 **研发交付报告**。
        - 文件: `docs/reports/rd_report_[date].md`。
        - 内容: 功能摘要, 测试覆盖率, 构建包路径, 已知问题。
    - **云端同步**: 
        - 调用 `feishu-doc-assistant` 上传报告。
        - 获取飞书链接。
    - **通知**: "交付完成！🚀\n报告: [链接]\n构建包: [路径]"

## 完成
用户验收交付物。
