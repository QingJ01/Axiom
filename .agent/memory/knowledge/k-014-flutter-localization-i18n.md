---
id: k-014
title: Flutter Localization (i18n)
category: tooling
tags: [flutter, i18n, localization, l10n]
created: 2026-02-09
confidence: 0.75
references: [seed-knowledge-pack-v1]
---

## Summary
使用 flutter_localizations + intl 包或 easy_localization 实现多语言。ARB 文件管理翻译文本, 通过 AppLocalizations.of(context) 访问。

## Details
### 官方方案
1. `pubspec.yaml`: 添加 `flutter_localizations` + `intl`
2. 创建 `.arb` 文件 (lib/l10n/app_en.arb, app_zh.arb)
3. `l10n.yaml` 配置生成
4. 使用: `AppLocalizations.of(context)!.helloWorld`

### 第三方方案
- `easy_localization`: 支持 JSON/YAML, 更灵活
- `slang`: 类型安全, 编译时检查
