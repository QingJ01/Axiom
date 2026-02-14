---
id: k-010
title: Flutter Testing Strategy
category: architecture
tags: [flutter, testing, unit-test, widget-test]
created: 2026-02-09
confidence: 0.8
references: [seed-knowledge-pack-v1]
---

## Summary
三层测试策略: Unit Test (70%) → Widget Test (20%) → Integration Test (10%)。ViewModel 用 unit test, UI 用 widget test。

## Details
### 测试金字塔
- **Unit**: ViewModel, Service, 工具类 → 快, 多写
- **Widget**: 单个 Widget 渲染 + 交互 → 中等
- **Integration**: 完整用户流程 → 慢, 少写

### Stacked 测试
- Mock Service: `class MockApiService extends Mock implements ApiService {}`
- 用 `getAndRegisterMockService<T>()` 注入 Mock
