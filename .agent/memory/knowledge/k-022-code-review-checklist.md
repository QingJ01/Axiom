---
id: k-022
title: Code Review Checklist
category: workflow
tags: [code-review, quality, checklist]
created: 2026-02-09
confidence: 0.9
references: [seed-knowledge-pack-v1]
---

## Summary
代码审查五要素: 正确性 > 可读性 > 性能 > 安全性 > 测试覆盖。重点关注边界条件和错误处理。

## Details
### Review Checklist
1. **正确性**: 逻辑是否正确? 边界条件?
2. **可读性**: 命名清晰? 注释充分?
3. **性能**: 有无 N+1 查询? 不必要的计算?
4. **安全性**: 输入验证? SQL 注入? XSS?
5. **测试**: 有测试? 覆盖边界情况?

### Anti-patterns
- 函数过长 (> 30 行)
- 参数过多 (> 4 个)
- 深层嵌套 (> 3 层)
- Magic Numbers
