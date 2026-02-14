---
id: k-008
title: Flutter Navigation Best Practices
category: architecture
tags: [flutter, navigation, routing]
created: 2026-02-09
confidence: 0.85
references: [seed-knowledge-pack-v1]
---

## Summary
使用声明式路由 (如 go_router 或 Stacked NavigationService) 替代命令式 Navigator.push。集中定义路由常量。

## Details
### 推荐方案
1. 集中路由定义 (避免散落在各 Widget 中)
2. 使用命名路由或类型安全路由
3. 导航逻辑放在 ViewModel, 不在 View
4. Deep Link 支持用 go_router

### Stacked NavigationService
- 通过 `locator<NavigationService>()` 注入
- `navigateTo(Routes.xxxView)` 跳转
