---
id: k-023
title: Project Structure Convention
category: architecture
tags: [project-structure, clean-architecture, folder]
created: 2026-02-09
confidence: 0.85
references: [seed-knowledge-pack-v1]
---

## Summary
按功能 (Feature-First) 组织代码, 而非按类型。每个 Feature 包含 view/viewmodel/service/model 子目录。

## Details
### Feature-First (推荐)
```
lib/
├── features/
│   ├── auth/
│   │   ├── auth_view.dart
│   │   ├── auth_viewmodel.dart
│   │   └── auth_service.dart
│   └── home/
│       ├── home_view.dart
│       └── home_viewmodel.dart
├── shared/
│   ├── widgets/
│   ├── utils/
│   └── constants/
└── app/
    ├── app.dart
    └── locator.dart
```

### 关键原则
- Feature 内高内聚
- Feature 间通过 Service 通信
- Shared 放通用组件
