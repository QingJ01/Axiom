---
id: k-021
title: Git Commit Conventions
category: workflow
tags: [git, commit, conventional-commits]
created: 2026-02-09
confidence: 0.95
references: [seed-knowledge-pack-v1]
---

## Summary
遵循 Conventional Commits: type(scope): description。type: feat/fix/refactor/docs/test/chore。scope: 模块名。

## Details
### Commit Types
- `feat`: 新功能
- `fix`: 修复 Bug
- `refactor`: 重构 (不改变行为)
- `docs`: 文档变更
- `test`: 测试相关
- `chore`: 构建/工具链
- `style`: 代码格式 (不影响逻辑)

### 示例
- `feat(auth): add OAuth2 login`
- `fix(word-card): prevent double tap crash`
- `refactor(api): extract base client`
