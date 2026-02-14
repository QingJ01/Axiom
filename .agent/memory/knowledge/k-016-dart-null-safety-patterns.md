---
id: k-016
title: Dart Null Safety Patterns
category: architecture
tags: [dart, null-safety, type-system]
created: 2026-02-09
confidence: 0.95
references: [seed-knowledge-pack-v1]
---

## Summary
Sound null safety 核心原则: 默认不可 null, 用 ? 标记可 null, 用 ! (谨慎) / ?? / ?. 操作符安全处理。

## Details
### 核心操作符
- `T?`: 可 null 类型
- `?.`: null-aware 调用
- `??`: null 默认值
- `??=`: null 时赋值
- `!`: 强制非 null (仅在确信时使用)

### Late 关键字
- `late final`: 延迟初始化 (只赋值一次)
- 适用于: initState 中初始化的变量
- 风险: 未初始化时访问会抛 LateInitializationError

## Code Example
```
// Good: null-safe pattern
final name = user?.profile?.displayName ?? 'Anonymous';

// Good: late final
late final TextEditingController _controller;
void initState() {
  _controller = TextEditingController();
}

// Bad: force unwrap without check
// final name = user!.profile!.displayName!;
```
