---
id: k-009
title: Flutter Performance Optimization
category: architecture
tags: [flutter, performance, optimization]
created: 2026-02-09
confidence: 0.85
references: [seed-knowledge-pack-v1]
---

## Summary
避免不必要的 rebuild: 使用 const Widget, 合理拆分 Widget 树, 使用 ListView.builder 代替 Column+map。

## Details
### 性能清单
1. **const 构造函数**: 尽量使用 const Widget
2. **Widget 拆分**: 将频繁 rebuild 的部分拆为独立 Widget
3. **ListView.builder**: 大列表必须用 builder, 不要 Column + map
4. **RepaintBoundary**: 隔离频繁重绘区域
5. **缓存图片**: 使用 CachedNetworkImage
6. **Isolate**: CPU 密集型任务用 compute()
7. **Key**: 合理使用 ValueKey/ObjectKey 维持状态
