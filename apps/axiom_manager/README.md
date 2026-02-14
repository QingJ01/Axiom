# Axiom Manager

Flutter Desktop 应用，用于图形化管理 Axiom 导入与健康检查。

## 已实现能力

- 自动同步 Axiom 源：默认在应用同目录 `res/axiom` 执行 clone/update
- 目标项目目录选择器：点击“浏览...”选择目录
- Provider 选择：默认展示 CLI 体系 (`gemini_cli`/`claude_code`/`codex`/`opencode`/`copilot`)
- 兼容 Provider：`gemini` 与 `claude` 默认隐藏，可通过“显示兼容 Provider”开启

## 本地运行

```bash
flutter pub get
flutter run -d windows
```

macOS:

```bash
flutter run -d macos
```

## 测试

```bash
flutter test
```

## 发布（首发无证书）

Windows（PowerShell）：

```powershell
pwsh tool/release_windows.ps1 -Mode unsigned -BuildName 1.0.0 -BuildNumber 1
```

产物目录：`dist/windows/unsigned/`

macOS（Bash）：

```bash
bash tool/release_macos.sh --mode unsigned --build-name 1.0.0 --build-number 1
```

产物目录：`dist/macos/unsigned/`

## signed 模式说明

- `release_windows.ps1 -Mode signed` 预留证书签名接入位。
- `release_macos.sh --mode signed` 预留 `codesign/notarytool` 接入位。
- 当前仓库默认走 unsigned 发布链路。
