---
id: k-002
title: Evolution Engine Architecture (自进化引擎架构)
category: architecture
tags: [evolution, modules, memory]
created: 2026-02-08
confidence: 0.85
references: [evolution-engine-v1]
---

## Summary
自进化引擎通过六大模块闭环实现 Agent 的自我提升：能够感知（Metrics）、学习（Harvester）、沉淀（Knowledge）、识别（Pattern）、反思（Reflection）和执行（Orchestrator）。

## Details
**核心模块**:
1. **Knowledge Harvester**: 从对话/代码中提取结构化知识。
2. **Workflow Optimizer**: 基于数据(`workflow_metrics`)优化流程。
3. **Pattern Detector**: 识别跨功能的代码/设计模式。
4. **Reflection Engine**: 任务后自动反思，生成 Action Items。
5. **Learning Queue**: 异步处理学习素材，避免阻塞主流程。
6. **Evolution Orchestrator**: 协调上述模块的运行。

## Related Knowledge
- k-001: Global Configuration Pattern
