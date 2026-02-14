---
id: k-017
title: Dart Async/Await Best Practices
category: architecture
tags: [dart, async, future, stream]
created: 2026-02-09
confidence: 0.9
references: [seed-knowledge-pack-v1]
---

## Summary
优先使用 async/await 而非 .then()。并行任务用 Future.wait()。Stream 用 StreamSubscription 并在 dispose 中取消。

## Details
### 最佳实践
1. 始终 `await` async 函数的返回值
2. 并行执行: `await Future.wait([task1(), task2()])`
3. 超时控制: `future.timeout(Duration(seconds: 10))`
4. 错误处理: try-catch 在 async 函数中使用
5. Stream: 用 `StreamController` 管理, `dispose()` 中 `.close()`

### 常见错误
- 忘记 await → 异步操作不执行
- 未取消 StreamSubscription → 内存泄漏
- 在 sync 函数中调用 async 但不 await
