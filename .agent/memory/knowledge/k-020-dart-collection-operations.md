---
id: k-020
title: Dart Collection Operations
category: pattern
tags: [dart, collections, list, map]
created: 2026-02-09
confidence: 0.85
references: [seed-knowledge-pack-v1]
---

## Summary
善用 Dart 集合操作: where / map / fold / expand / groupBy。避免手写 for 循环, 偏好声明式链式调用。

## Details
### 常用操作
- `where()` — 过滤
- `map()` — 转换
- `fold()` — 累加
- `expand()` — 展平
- `firstWhere()` — 查找
- `any()` / `every()` — 断言
- `toSet()` — 去重

### 性能提示
- 大集合避免多次 `.toList()`
- 用 `Iterable` 惰性计算
- `List.unmodifiable()` 防止意外修改

## Code Example
```
// 声明式链式调用
final activeAdmins = users
    .where((u) => u.isActive && u.role == Role.admin)
    .map((u) => u.displayName)
    .toList();

// groupBy (需要 collection package)
final grouped = groupBy(items, (Item i) => i.category);
```
