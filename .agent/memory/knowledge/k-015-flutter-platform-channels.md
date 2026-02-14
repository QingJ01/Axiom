---
id: k-015
title: Flutter Platform Channels
category: architecture
tags: [flutter, platform-channel, native, ios, android]
created: 2026-02-09
confidence: 0.75
references: [seed-knowledge-pack-v1]
---

## Summary
通过 MethodChannel 或 EventChannel 与 Native 通信。使用 Pigeon 自动生成类型安全的桥接代码。

## Details
### Channel 类型
- **MethodChannel**: 请求-响应式 (一次性调用)
- **EventChannel**: 流式 (持续事件流)
- **BasicMessageChannel**: 低层消息传递

### Pigeon (推荐)
自动生成 Dart/Kotlin/Swift 的类型安全接口, 避免手写字符串。

### 注意事项
- 主线程调用, 耗时操作需在 Native 侧异步处理
- 错误处理: PlatformException
