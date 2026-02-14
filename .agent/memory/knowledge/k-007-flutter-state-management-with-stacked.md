---
id: k-007
title: Flutter State Management with Stacked
category: architecture
tags: [flutter, stacked, state-management, mvvm]
created: 2026-02-09
confidence: 0.9
references: [seed-knowledge-pack-v1]
---

## Summary
使用 Stacked 框架实现 MVVM 架构。ViewModel 管理状态, View 仅负责 UI 渲染, Service 负责业务逻辑。

## Details
### 三层结构
- **View**: 纯 UI, 通过 `ViewModelBuilder` 绑定 ViewModel
- **ViewModel**: 继承 `BaseViewModel` 或 `ReactiveViewModel`, 持有状态
- **Service**: 注入 ViewModel, 封装 API/DB 调用

### 关键规则
- ViewModel **不应持有** BuildContext
- 使用 `locator` 进行依赖注入
- 用 `setBusy(true/false)` 管理加载状态

## Code Example
```
class HomeViewModel extends BaseViewModel {
  final _api = locator<ApiService>();
  List<Item> items = [];

  Future<void> loadItems() async {
    setBusy(true);
    items = await _api.fetchItems();
    setBusy(false);
  }
}
```
