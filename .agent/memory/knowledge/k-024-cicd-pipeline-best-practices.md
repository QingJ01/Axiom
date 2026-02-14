---
id: k-024
title: CI/CD Pipeline Best Practices
category: workflow
tags: [ci-cd, github-actions, automation]
created: 2026-02-09
confidence: 0.8
references: [seed-knowledge-pack-v1]
---

## Summary
CI Pipeline 三阶段: Lint → Test → Build。PR 必须通过 CI 才可合并。自动化越多, 人为失误越少。

## Details
### Pipeline 设计
1. **Lint**: `flutter analyze` + `dart format --set-exit-if-changed`
2. **Test**: `flutter test --coverage`
3. **Build**: `flutter build apk/ipa`
4. **Deploy**: Fastlane / Firebase App Distribution

### GitHub Actions
- `on: [push, pull_request]`
- 缓存 pub 依赖: `actions/cache` with `~/.pub-cache`
- Matrix testing: 多 Flutter/Dart 版本
