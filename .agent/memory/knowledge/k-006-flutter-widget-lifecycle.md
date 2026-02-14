---
id: k-006
title: Flutter Widget Lifecycle
category: architecture
tags: [flutter, widget, lifecycle]
created: 2026-02-09
confidence: 0.9
references: [seed-knowledge-pack-v1]
---

## Summary
Flutter Widget 有两种类型: StatelessWidget (无生命周期) 和 StatefulWidget (含 createState → initState → build → dispose 完整生命周期)。

## Details
### StatefulWidget 生命周期
1. `createState()` — 创建 State 对象
2. `initState()` — State 初始化 (只调用一次)
3. `didChangeDependencies()` — 依赖变化时
4. `build()` — 构建 Widget 树 (可能多次调用)
5. `didUpdateWidget()` — Widget 重建时
6. `deactivate()` → `dispose()` — 销毁

**关键原则**: 在 `initState` 中初始化, 在 `dispose` 中释放资源。

## Code Example
```
class MyWidget extends StatefulWidget {
  @override
  _MyWidgetState createState() => _MyWidgetState();
}

class _MyWidgetState extends State<MyWidget> {
  late final StreamSubscription _sub;

  @override
  void initState() {
    super.initState();
    _sub = stream.listen((_) => setState(() {}));
  }

  @override
  void dispose() {
    _sub.cancel();
    super.dispose();
  }
}
```
