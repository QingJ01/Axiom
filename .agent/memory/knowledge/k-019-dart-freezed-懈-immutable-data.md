---
id: k-019
title: Dart Freezed и Immutable Data
category: pattern
tags: [dart, freezed, immutable, data-class]
created: 2026-02-09
confidence: 0.85
references: [seed-knowledge-pack-v1]
---

## Summary
使用 freezed 包生成不可变数据类, 自动获得 copyWith / == / toString / fromJson。适合 State 对象和 API Response。

## Details
### 核心特性
- 自动生成 `copyWith()` — 部分更新
- 自动生成 `==` / `hashCode` — 值比较
- 自动生成 `fromJson` / `toJson` — 序列化
- Union types / Sealed classes — 状态建模

### 何时使用
- API Response DTO
- 应用状态 (AppState, AuthState)
- 事件定义 (BLoC Events)

## Code Example
```
@freezed
class User with _$User {
  const factory User({
    required String id,
    required String name,
    @Default('') String avatar,
  }) = _User;

  factory User.fromJson(Map<String, dynamic> json) =>
    _$UserFromJson(json);
}
```
