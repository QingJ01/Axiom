---
id: k-011
title: Flutter Error Handling Pattern
category: debugging
tags: [flutter, error-handling, exception]
created: 2026-02-09
confidence: 0.85
references: [seed-knowledge-pack-v1]
---

## Summary
使用 Either<Failure, T> 或 Result 模式统一错误处理, 避免 try-catch 泛型捕获。Service 层捕获, ViewModel 层处理。

## Details
### 推荐模式
```
Service: 捕获异常 → 返回 Result<T>
ViewModel: 处理 Result → 更新 UI 状态
View: 展示错误 UI
```

### 全局错误处理
- `FlutterError.onError` — 捕获 Widget 异常
- `PlatformDispatcher.instance.onError` — 捕获平台异常
- `runZonedGuarded` — 捕获异步异常
