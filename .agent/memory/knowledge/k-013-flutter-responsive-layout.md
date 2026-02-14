---
id: k-013
title: Flutter Responsive Layout
category: architecture
tags: [flutter, responsive, layout, adaptive]
created: 2026-02-09
confidence: 0.8
references: [seed-knowledge-pack-v1]
---

## Summary
使用 LayoutBuilder + MediaQuery 实现响应式布局。定义断点 (mobile/tablet/desktop), 根据宽度切换布局。

## Details
### 断点定义
- Mobile: < 600dp
- Tablet: 600 ~ 1200dp
- Desktop: > 1200dp

### 实现方式
1. `LayoutBuilder` — 根据父约束适配
2. `MediaQuery.of(context).size` — 根据屏幕尺寸
3. `Flexible` / `Expanded` — 弹性布局
4. `Wrap` — 自动换行
