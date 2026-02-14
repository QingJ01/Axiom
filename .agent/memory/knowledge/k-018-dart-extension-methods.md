---
id: k-018
title: Dart Extension Methods
category: pattern
tags: [dart, extension, utility]
created: 2026-02-09
confidence: 0.85
references: [seed-knowledge-pack-v1]
---

## Summary
使用 Extension Methods 给现有类添加功能，避免创建工具类。适合字符串处理、日期格式化、集合操作。

## Details
### 使用场景
- 字符串: capitalize, truncate, isEmail
- DateTime: toReadable, isToday, daysUntil
- List: groupBy, sortedBy, firstWhereOrNull
- BuildContext: theme, colorScheme, textTheme shortcuts

### 命名规则
- 文件: `xxx_extensions.dart`
- 类: `XxxExtension on Type`

## Code Example
```
extension StringX on String {
  String get capitalized => '${this[0].toUpperCase()}${substring(1)}';
  bool get isValidEmail => RegExp(r'^[\w-.]+@[\w-]+\.[a-z]+$').hasMatch(this);
}

extension ContextX on BuildContext {
  ThemeData get theme => Theme.of(this);
  ColorScheme get colorScheme => theme.colorScheme;
}
```
