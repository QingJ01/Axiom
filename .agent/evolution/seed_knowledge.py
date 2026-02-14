"""
Seed Knowledge Generator — 种子知识包 (T-203)

批量生成 20 条通用开发最佳实践知识条目:
  - Flutter 10 条
  - Dart 5 条
  - 工程规范 5 条

Usage:
    python -m evolution.seed_knowledge
"""

from __future__ import annotations
from pathlib import Path
from evolution.harvester import KnowledgeHarvester

# ─── Seed Data ───────────────────────────────────────────────

SEEDS = [
    # ── Flutter (10 条) ──
    {
        "title": "Flutter Widget Lifecycle",
        "category": "architecture",
        "tags": ["flutter", "widget", "lifecycle"],
        "confidence": 0.9,
        "summary": "Flutter Widget 有两种类型: StatelessWidget (无生命周期) 和 StatefulWidget (含 createState → initState → build → dispose 完整生命周期)。",
        "details": (
            "### StatefulWidget 生命周期\n"
            "1. `createState()` — 创建 State 对象\n"
            "2. `initState()` — State 初始化 (只调用一次)\n"
            "3. `didChangeDependencies()` — 依赖变化时\n"
            "4. `build()` — 构建 Widget 树 (可能多次调用)\n"
            "5. `didUpdateWidget()` — Widget 重建时\n"
            "6. `deactivate()` → `dispose()` — 销毁\n\n"
            "**关键原则**: 在 `initState` 中初始化, 在 `dispose` 中释放资源。"
        ),
        "code_example": (
            "class MyWidget extends StatefulWidget {\n"
            "  @override\n"
            "  _MyWidgetState createState() => _MyWidgetState();\n"
            "}\n\n"
            "class _MyWidgetState extends State<MyWidget> {\n"
            "  late final StreamSubscription _sub;\n\n"
            "  @override\n"
            "  void initState() {\n"
            "    super.initState();\n"
            "    _sub = stream.listen((_) => setState(() {}));\n"
            "  }\n\n"
            "  @override\n"
            "  void dispose() {\n"
            "    _sub.cancel();\n"
            "    super.dispose();\n"
            "  }\n"
            "}"
        ),
    },
    {
        "title": "Flutter State Management with Stacked",
        "category": "architecture",
        "tags": ["flutter", "stacked", "state-management", "mvvm"],
        "confidence": 0.9,
        "summary": "使用 Stacked 框架实现 MVVM 架构。ViewModel 管理状态, View 仅负责 UI 渲染, Service 负责业务逻辑。",
        "details": (
            "### 三层结构\n"
            "- **View**: 纯 UI, 通过 `ViewModelBuilder` 绑定 ViewModel\n"
            "- **ViewModel**: 继承 `BaseViewModel` 或 `ReactiveViewModel`, 持有状态\n"
            "- **Service**: 注入 ViewModel, 封装 API/DB 调用\n\n"
            "### 关键规则\n"
            "- ViewModel **不应持有** BuildContext\n"
            "- 使用 `locator` 进行依赖注入\n"
            "- 用 `setBusy(true/false)` 管理加载状态"
        ),
        "code_example": (
            "class HomeViewModel extends BaseViewModel {\n"
            "  final _api = locator<ApiService>();\n"
            "  List<Item> items = [];\n\n"
            "  Future<void> loadItems() async {\n"
            "    setBusy(true);\n"
            "    items = await _api.fetchItems();\n"
            "    setBusy(false);\n"
            "  }\n"
            "}"
        ),
    },
    {
        "title": "Flutter Navigation Best Practices",
        "category": "architecture",
        "tags": ["flutter", "navigation", "routing"],
        "confidence": 0.85,
        "summary": "使用声明式路由 (如 go_router 或 Stacked NavigationService) 替代命令式 Navigator.push。集中定义路由常量。",
        "details": (
            "### 推荐方案\n"
            "1. 集中路由定义 (避免散落在各 Widget 中)\n"
            "2. 使用命名路由或类型安全路由\n"
            "3. 导航逻辑放在 ViewModel, 不在 View\n"
            "4. Deep Link 支持用 go_router\n\n"
            "### Stacked NavigationService\n"
            "- 通过 `locator<NavigationService>()` 注入\n"
            "- `navigateTo(Routes.xxxView)` 跳转"
        ),
    },
    {
        "title": "Flutter Performance Optimization",
        "category": "architecture",
        "tags": ["flutter", "performance", "optimization"],
        "confidence": 0.85,
        "summary": "避免不必要的 rebuild: 使用 const Widget, 合理拆分 Widget 树, 使用 ListView.builder 代替 Column+map。",
        "details": (
            "### 性能清单\n"
            "1. **const 构造函数**: 尽量使用 const Widget\n"
            "2. **Widget 拆分**: 将频繁 rebuild 的部分拆为独立 Widget\n"
            "3. **ListView.builder**: 大列表必须用 builder, 不要 Column + map\n"
            "4. **RepaintBoundary**: 隔离频繁重绘区域\n"
            "5. **缓存图片**: 使用 CachedNetworkImage\n"
            "6. **Isolate**: CPU 密集型任务用 compute()\n"
            "7. **Key**: 合理使用 ValueKey/ObjectKey 维持状态"
        ),
    },
    {
        "title": "Flutter Testing Strategy",
        "category": "architecture",
        "tags": ["flutter", "testing", "unit-test", "widget-test"],
        "confidence": 0.8,
        "summary": "三层测试策略: Unit Test (70%) → Widget Test (20%) → Integration Test (10%)。ViewModel 用 unit test, UI 用 widget test。",
        "details": (
            "### 测试金字塔\n"
            "- **Unit**: ViewModel, Service, 工具类 → 快, 多写\n"
            "- **Widget**: 单个 Widget 渲染 + 交互 → 中等\n"
            "- **Integration**: 完整用户流程 → 慢, 少写\n\n"
            "### Stacked 测试\n"
            "- Mock Service: `class MockApiService extends Mock implements ApiService {}`\n"
            "- 用 `getAndRegisterMockService<T>()` 注入 Mock"
        ),
    },
    {
        "title": "Flutter Error Handling Pattern",
        "category": "debugging",
        "tags": ["flutter", "error-handling", "exception"],
        "confidence": 0.85,
        "summary": "使用 Either<Failure, T> 或 Result 模式统一错误处理, 避免 try-catch 泛型捕获。Service 层捕获, ViewModel 层处理。",
        "details": (
            "### 推荐模式\n"
            "```\n"
            "Service: 捕获异常 → 返回 Result<T>\n"
            "ViewModel: 处理 Result → 更新 UI 状态\n"
            "View: 展示错误 UI\n"
            "```\n\n"
            "### 全局错误处理\n"
            "- `FlutterError.onError` — 捕获 Widget 异常\n"
            "- `PlatformDispatcher.instance.onError` — 捕获平台异常\n"
            "- `runZonedGuarded` — 捕获异步异常"
        ),
    },
    {
        "title": "Flutter Theme and Styling",
        "category": "architecture",
        "tags": ["flutter", "theme", "ui", "design-system"],
        "confidence": 0.8,
        "summary": "使用 ThemeData 统一管理颜色、字体、间距。创建 AppTheme 类集中定义, 通过 Theme.of(context) 访问。",
        "details": (
            "### 设计系统要素\n"
            "1. **Colors**: 定义 ColorScheme, 支持 Light/Dark\n"
            "2. **Typography**: 定义 TextTheme (headline, body, label)\n"
            "3. **Spacing**: 定义 EdgeInsets 常量 (S/M/L/XL)\n"
            "4. **Components**: 统一 Button/Input/Card 样式\n\n"
            "**切忌**: 硬编码颜色值, 应通过 Theme.of(context).colorScheme 引用。"
        ),
    },
    {
        "title": "Flutter Responsive Layout",
        "category": "architecture",
        "tags": ["flutter", "responsive", "layout", "adaptive"],
        "confidence": 0.8,
        "summary": "使用 LayoutBuilder + MediaQuery 实现响应式布局。定义断点 (mobile/tablet/desktop), 根据宽度切换布局。",
        "details": (
            "### 断点定义\n"
            "- Mobile: < 600dp\n"
            "- Tablet: 600 ~ 1200dp\n"
            "- Desktop: > 1200dp\n\n"
            "### 实现方式\n"
            "1. `LayoutBuilder` — 根据父约束适配\n"
            "2. `MediaQuery.of(context).size` — 根据屏幕尺寸\n"
            "3. `Flexible` / `Expanded` — 弹性布局\n"
            "4. `Wrap` — 自动换行"
        ),
    },
    {
        "title": "Flutter Localization (i18n)",
        "category": "tooling",
        "tags": ["flutter", "i18n", "localization", "l10n"],
        "confidence": 0.75,
        "summary": "使用 flutter_localizations + intl 包或 easy_localization 实现多语言。ARB 文件管理翻译文本, 通过 AppLocalizations.of(context) 访问。",
        "details": (
            "### 官方方案\n"
            "1. `pubspec.yaml`: 添加 `flutter_localizations` + `intl`\n"
            "2. 创建 `.arb` 文件 (lib/l10n/app_en.arb, app_zh.arb)\n"
            "3. `l10n.yaml` 配置生成\n"
            "4. 使用: `AppLocalizations.of(context)!.helloWorld`\n\n"
            "### 第三方方案\n"
            "- `easy_localization`: 支持 JSON/YAML, 更灵活\n"
            "- `slang`: 类型安全, 编译时检查"
        ),
    },
    {
        "title": "Flutter Platform Channels",
        "category": "architecture",
        "tags": ["flutter", "platform-channel", "native", "ios", "android"],
        "confidence": 0.75,
        "summary": "通过 MethodChannel 或 EventChannel 与 Native 通信。使用 Pigeon 自动生成类型安全的桥接代码。",
        "details": (
            "### Channel 类型\n"
            "- **MethodChannel**: 请求-响应式 (一次性调用)\n"
            "- **EventChannel**: 流式 (持续事件流)\n"
            "- **BasicMessageChannel**: 低层消息传递\n\n"
            "### Pigeon (推荐)\n"
            "自动生成 Dart/Kotlin/Swift 的类型安全接口, 避免手写字符串。\n\n"
            "### 注意事项\n"
            "- 主线程调用, 耗时操作需在 Native 侧异步处理\n"
            "- 错误处理: PlatformException"
        ),
    },

    # ── Dart (5 条) ──
    {
        "title": "Dart Null Safety Patterns",
        "category": "architecture",
        "tags": ["dart", "null-safety", "type-system"],
        "confidence": 0.95,
        "summary": "Sound null safety 核心原则: 默认不可 null, 用 ? 标记可 null, 用 ! (谨慎) / ?? / ?. 操作符安全处理。",
        "details": (
            "### 核心操作符\n"
            "- `T?`: 可 null 类型\n"
            "- `?.`: null-aware 调用\n"
            "- `??`: null 默认值\n"
            "- `??=`: null 时赋值\n"
            "- `!`: 强制非 null (仅在确信时使用)\n\n"
            "### Late 关键字\n"
            "- `late final`: 延迟初始化 (只赋值一次)\n"
            "- 适用于: initState 中初始化的变量\n"
            "- 风险: 未初始化时访问会抛 LateInitializationError"
        ),
        "code_example": (
            "// Good: null-safe pattern\n"
            "final name = user?.profile?.displayName ?? 'Anonymous';\n\n"
            "// Good: late final\n"
            "late final TextEditingController _controller;\n"
            "void initState() {\n"
            "  _controller = TextEditingController();\n"
            "}\n\n"
            "// Bad: force unwrap without check\n"
            "// final name = user!.profile!.displayName!;"
        ),
    },
    {
        "title": "Dart Async/Await Best Practices",
        "category": "architecture",
        "tags": ["dart", "async", "future", "stream"],
        "confidence": 0.9,
        "summary": "优先使用 async/await 而非 .then()。并行任务用 Future.wait()。Stream 用 StreamSubscription 并在 dispose 中取消。",
        "details": (
            "### 最佳实践\n"
            "1. 始终 `await` async 函数的返回值\n"
            "2. 并行执行: `await Future.wait([task1(), task2()])`\n"
            "3. 超时控制: `future.timeout(Duration(seconds: 10))`\n"
            "4. 错误处理: try-catch 在 async 函数中使用\n"
            "5. Stream: 用 `StreamController` 管理, `dispose()` 中 `.close()`\n\n"
            "### 常见错误\n"
            "- 忘记 await → 异步操作不执行\n"
            "- 未取消 StreamSubscription → 内存泄漏\n"
            "- 在 sync 函数中调用 async 但不 await"
        ),
    },
    {
        "title": "Dart Extension Methods",
        "category": "pattern",
        "tags": ["dart", "extension", "utility"],
        "confidence": 0.85,
        "summary": "使用 Extension Methods 给现有类添加功能，避免创建工具类。适合字符串处理、日期格式化、集合操作。",
        "details": (
            "### 使用场景\n"
            "- 字符串: capitalize, truncate, isEmail\n"
            "- DateTime: toReadable, isToday, daysUntil\n"
            "- List: groupBy, sortedBy, firstWhereOrNull\n"
            "- BuildContext: theme, colorScheme, textTheme shortcuts\n\n"
            "### 命名规则\n"
            "- 文件: `xxx_extensions.dart`\n"
            "- 类: `XxxExtension on Type`"
        ),
        "code_example": (
            "extension StringX on String {\n"
            "  String get capitalized => '${this[0].toUpperCase()}${substring(1)}';\n"
            "  bool get isValidEmail => RegExp(r'^[\\w-.]+@[\\w-]+\\.[a-z]+$').hasMatch(this);\n"
            "}\n\n"
            "extension ContextX on BuildContext {\n"
            "  ThemeData get theme => Theme.of(this);\n"
            "  ColorScheme get colorScheme => theme.colorScheme;\n"
            "}"
        ),
    },
    {
        "title": "Dart Freezed и Immutable Data",
        "category": "pattern",
        "tags": ["dart", "freezed", "immutable", "data-class"],
        "confidence": 0.85,
        "summary": "使用 freezed 包生成不可变数据类, 自动获得 copyWith / == / toString / fromJson。适合 State 对象和 API Response。",
        "details": (
            "### 核心特性\n"
            "- 自动生成 `copyWith()` — 部分更新\n"
            "- 自动生成 `==` / `hashCode` — 值比较\n"
            "- 自动生成 `fromJson` / `toJson` — 序列化\n"
            "- Union types / Sealed classes — 状态建模\n\n"
            "### 何时使用\n"
            "- API Response DTO\n"
            "- 应用状态 (AppState, AuthState)\n"
            "- 事件定义 (BLoC Events)"
        ),
        "code_example": (
            "@freezed\n"
            "class User with _$User {\n"
            "  const factory User({\n"
            "    required String id,\n"
            "    required String name,\n"
            "    @Default('') String avatar,\n"
            "  }) = _User;\n\n"
            "  factory User.fromJson(Map<String, dynamic> json) =>\n"
            "    _$UserFromJson(json);\n"
            "}"
        ),
    },
    {
        "title": "Dart Collection Operations",
        "category": "pattern",
        "tags": ["dart", "collections", "list", "map"],
        "confidence": 0.85,
        "summary": "善用 Dart 集合操作: where / map / fold / expand / groupBy。避免手写 for 循环, 偏好声明式链式调用。",
        "details": (
            "### 常用操作\n"
            "- `where()` — 过滤\n"
            "- `map()` — 转换\n"
            "- `fold()` — 累加\n"
            "- `expand()` — 展平\n"
            "- `firstWhere()` — 查找\n"
            "- `any()` / `every()` — 断言\n"
            "- `toSet()` — 去重\n\n"
            "### 性能提示\n"
            "- 大集合避免多次 `.toList()`\n"
            "- 用 `Iterable` 惰性计算\n"
            "- `List.unmodifiable()` 防止意外修改"
        ),
        "code_example": (
            "// 声明式链式调用\n"
            "final activeAdmins = users\n"
            "    .where((u) => u.isActive && u.role == Role.admin)\n"
            "    .map((u) => u.displayName)\n"
            "    .toList();\n\n"
            "// groupBy (需要 collection package)\n"
            "final grouped = groupBy(items, (Item i) => i.category);"
        ),
    },

    # ── 工程规范 (5 条) ──
    {
        "title": "Git Commit Conventions",
        "category": "workflow",
        "tags": ["git", "commit", "conventional-commits"],
        "confidence": 0.95,
        "summary": "遵循 Conventional Commits: type(scope): description。type: feat/fix/refactor/docs/test/chore。scope: 模块名。",
        "details": (
            "### Commit Types\n"
            "- `feat`: 新功能\n"
            "- `fix`: 修复 Bug\n"
            "- `refactor`: 重构 (不改变行为)\n"
            "- `docs`: 文档变更\n"
            "- `test`: 测试相关\n"
            "- `chore`: 构建/工具链\n"
            "- `style`: 代码格式 (不影响逻辑)\n\n"
            "### 示例\n"
            "- `feat(auth): add OAuth2 login`\n"
            "- `fix(word-card): prevent double tap crash`\n"
            "- `refactor(api): extract base client`"
        ),
    },
    {
        "title": "Code Review Checklist",
        "category": "workflow",
        "tags": ["code-review", "quality", "checklist"],
        "confidence": 0.9,
        "summary": "代码审查五要素: 正确性 > 可读性 > 性能 > 安全性 > 测试覆盖。重点关注边界条件和错误处理。",
        "details": (
            "### Review Checklist\n"
            "1. **正确性**: 逻辑是否正确? 边界条件?\n"
            "2. **可读性**: 命名清晰? 注释充分?\n"
            "3. **性能**: 有无 N+1 查询? 不必要的计算?\n"
            "4. **安全性**: 输入验证? SQL 注入? XSS?\n"
            "5. **测试**: 有测试? 覆盖边界情况?\n\n"
            "### Anti-patterns\n"
            "- 函数过长 (> 30 行)\n"
            "- 参数过多 (> 4 个)\n"
            "- 深层嵌套 (> 3 层)\n"
            "- Magic Numbers"
        ),
    },
    {
        "title": "Project Structure Convention",
        "category": "architecture",
        "tags": ["project-structure", "clean-architecture", "folder"],
        "confidence": 0.85,
        "summary": "按功能 (Feature-First) 组织代码, 而非按类型。每个 Feature 包含 view/viewmodel/service/model 子目录。",
        "details": (
            "### Feature-First (推荐)\n"
            "```\n"
            "lib/\n"
            "├── features/\n"
            "│   ├── auth/\n"
            "│   │   ├── auth_view.dart\n"
            "│   │   ├── auth_viewmodel.dart\n"
            "│   │   └── auth_service.dart\n"
            "│   └── home/\n"
            "│       ├── home_view.dart\n"
            "│       └── home_viewmodel.dart\n"
            "├── shared/\n"
            "│   ├── widgets/\n"
            "│   ├── utils/\n"
            "│   └── constants/\n"
            "└── app/\n"
            "    ├── app.dart\n"
            "    └── locator.dart\n"
            "```\n\n"
            "### 关键原则\n"
            "- Feature 内高内聚\n"
            "- Feature 间通过 Service 通信\n"
            "- Shared 放通用组件"
        ),
    },
    {
        "title": "CI/CD Pipeline Best Practices",
        "category": "workflow",
        "tags": ["ci-cd", "github-actions", "automation"],
        "confidence": 0.8,
        "summary": "CI Pipeline 三阶段: Lint → Test → Build。PR 必须通过 CI 才可合并。自动化越多, 人为失误越少。",
        "details": (
            "### Pipeline 设计\n"
            "1. **Lint**: `flutter analyze` + `dart format --set-exit-if-changed`\n"
            "2. **Test**: `flutter test --coverage`\n"
            "3. **Build**: `flutter build apk/ipa`\n"
            "4. **Deploy**: Fastlane / Firebase App Distribution\n\n"
            "### GitHub Actions\n"
            "- `on: [push, pull_request]`\n"
            "- 缓存 pub 依赖: `actions/cache` with `~/.pub-cache`\n"
            "- Matrix testing: 多 Flutter/Dart 版本"
        ),
    },
    {
        "title": "Documentation Standards",
        "category": "workflow",
        "tags": ["documentation", "dartdoc", "readme"],
        "confidence": 0.8,
        "summary": "三级文档: README (项目) + API Doc (代码) + Architecture Decision Records (决策)。公共 API 必须有 dartdoc 注释。",
        "details": (
            "### 文档层次\n"
            "1. **README.md**: 项目概述、安装、使用\n"
            "2. **dartdoc**: `///` 注释, 描述参数/返回值/异常\n"
            "3. **ADR**: Architecture Decision Records, 记录重大决策\n\n"
            "### dartdoc 规范\n"
            "- 第一行: 一句话概述\n"
            "- 空行后: 详细说明\n"
            "- `@param` / `@return` / `@throws`\n"
            "- 代码示例用 ` ```dart ` 包裹"
        ),
    },
]


def generate_seeds(base_dir: str = ".agent/memory") -> list[str]:
    """生成所有种子知识条目, 返回生成的文件 ID 列表"""
    harvester = KnowledgeHarvester(base_dir=base_dir)
    generated = []

    for seed in SEEDS:
        entry = harvester.harvest(
            source_type="conversation",
            title=seed["title"],
            summary=seed["summary"],
            category=seed["category"],
            tags=seed.get("tags", []),
            details=seed.get("details", ""),
            code_example=seed.get("code_example", ""),
            confidence=seed.get("confidence", 0.7),
            references=["seed-knowledge-pack-v1"],
        )
        generated.append(entry.id)
        print(f"  ✅ {entry.id}: {entry.title}")

    return generated


if __name__ == "__main__":
    import sys
    base = sys.argv[1] if len(sys.argv) > 1 else ".agent/memory"
    print(f"🌱 Generating seed knowledge in {base}...")
    ids = generate_seeds(base)
    print(f"\n✅ Generated {len(ids)} seed knowledge entries.")
