---
description: 知识图谱索引 - 管理所有知识条目的元信息
version: 1.0
last_updated: 2026-02-09
---

# Knowledge Base (知识图谱索引)

本文件是知识系统的中央索引，记录所有知识条目的元信息。

## 1. 索引表 (Knowledge Index)

| ID | Title | Category | Confidence | Created | Status |
|----|-------|----------|------------|---------|--------|
| k-001 | Global Configuration Pattern (全局配置模式) | architecture | 0.9 | 2026-02-08 | active |
| k-002 | Evolution Engine Architecture (自进化引擎架构) | architecture | 0.85 | 2026-02-08 | active |
| k-003 | GitHub Automation Fallback Strategy (GitHub 自动化降级策略) | tooling | 0.8 | 2026-02-08 | active |
| k-004 | Context Completeness Pattern (上下文完整性模式) | architecture | 0.95 | 2026-02-08 | active |
| k-005 | Agent Native Orchestration (纯 Agent 编排) | architecture | 0.9 | 2026-02-09 | active |
| k-006 | Flutter Widget Lifecycle | architecture | 0.9 | 2026-02-09 | active |
| k-007 | Flutter State Management with Stacked | architecture | 0.9 | 2026-02-09 | active |
| k-008 | Flutter Navigation Best Practices | architecture | 0.85 | 2026-02-09 | active |
| k-009 | Flutter Performance Optimization | architecture | 0.85 | 2026-02-09 | active |
| k-010 | Flutter Testing Strategy | architecture | 0.8 | 2026-02-09 | active |
| k-011 | Flutter Error Handling Pattern | debugging | 0.85 | 2026-02-09 | active |
| k-012 | Flutter Theme and Styling | architecture | 0.8 | 2026-02-09 | active |
| k-013 | Flutter Responsive Layout | architecture | 0.8 | 2026-02-09 | active |
| k-014 | Flutter Localization (i18n) | tooling | 0.75 | 2026-02-09 | active |
| k-015 | Flutter Platform Channels | architecture | 0.75 | 2026-02-09 | active |
| k-016 | Dart Null Safety Patterns | architecture | 0.95 | 2026-02-09 | active |
| k-017 | Dart Async/Await Best Practices | architecture | 0.9 | 2026-02-09 | active |
| k-018 | Dart Extension Methods | pattern | 0.85 | 2026-02-09 | active |
| k-019 | Dart Freezed и Immutable Data | pattern | 0.85 | 2026-02-09 | active |
| k-020 | Dart Collection Operations | pattern | 0.85 | 2026-02-09 | active |
| k-021 | Git Commit Conventions | workflow | 0.95 | 2026-02-09 | active |
| k-022 | Code Review Checklist | workflow | 0.9 | 2026-02-09 | active |
| k-023 | Project Structure Convention | architecture | 0.85 | 2026-02-09 | active |
| k-024 | CI/CD Pipeline Best Practices | workflow | 0.8 | 2026-02-09 | active |
| k-025 | Documentation Standards | workflow | 0.8 | 2026-02-09 | active |
| k-026 | Codex CLI Best Practices (Windows) | tooling | 0.95 | 2026-02-12 | active |
| k-027 | Async Interaction Pattern (Turn-Based Resume) | pattern | 0.9 | 2026-02-12 | active |
| k-028 | Unique Artifact Injection Pattern | architecture | 0.95 | 2026-02-12 | active |

## 2. 分类统计 (Category Stats)

| Category | Count | Description |
|----------|-------|-------------|
| architecture | 15 | 架构相关知识 |
| debugging | 1 | 调试技巧 |
| pattern | 3 | 代码模式 |
| workflow | 4 | 工作流相关 |
| tooling | 2 | 工具使用 |


## 3. 标签云 (Tag Cloud)

> 使用频率: (tag: count)

- flutter: 10
- dart: 5
- memory: 2
- automation: 2
- config: 1
- axiom: 1
- gemini: 1
- evolution: 1
- modules: 1
- github: 1
- fallback: 1
- context: 1
- best-practice: 1
- architecture: 1
- orchestration: 1
- anti-pattern: 1
- widget: 1
- lifecycle: 1
- stacked: 1
- state-management: 1
- mvvm: 1
- navigation: 1
- routing: 1
- performance: 1
- optimization: 1
- testing: 1
- unit-test: 1
- widget-test: 1
- error-handling: 1
- exception: 1
- theme: 1
- ui: 1
- design-system: 1
- responsive: 1
- layout: 1
- adaptive: 1
- i18n: 1
- localization: 1
- l10n: 1
- platform-channel: 1
- native: 1
- ios: 1
- android: 1
- null-safety: 1
- type-system: 1
- async: 1
- future: 1
- stream: 1
- extension: 1
- utility: 1
- freezed: 1
- immutable: 1
- data-class: 1
- collections: 1
- list: 1
- map: 1
- git: 1
- commit: 1
- conventional-commits: 1
- code-review: 1
- quality: 1
- checklist: 1
- project-structure: 1
- clean-architecture: 1
- folder: 1
- ci-cd: 1
- github-actions: 1
- documentation: 1
- dartdoc: 1
- readme: 1

## 4. 知识质量管理

### 4.1 Confidence 分数说明
- `0.9+`: 高置信度，经过多次验证
- `0.7-0.9`: 中等置信度，单次成功经验
- `0.5-0.7`: 低置信度，需要更多验证
- `<0.5`: 待清理，可能已过时

### 4.2 清理规则
- Confidence < 0.5 且超过 30 天未使用 → 标记为 `deprecated`
