---
id: k-012
title: Flutter Theme and Styling
category: architecture
tags: [flutter, theme, ui, design-system]
created: 2026-02-09
confidence: 0.8
references: [seed-knowledge-pack-v1]
---

## Summary
使用 ThemeData 统一管理颜色、字体、间距。创建 AppTheme 类集中定义, 通过 Theme.of(context) 访问。

## Details
### 设计系统要素
1. **Colors**: 定义 ColorScheme, 支持 Light/Dark
2. **Typography**: 定义 TextTheme (headline, body, label)
3. **Spacing**: 定义 EdgeInsets 常量 (S/M/L/XL)
4. **Components**: 统一 Button/Input/Card 样式

**切忌**: 硬编码颜色值, 应通过 Theme.of(context).colorScheme 引用。
