# Axiom Manager

Flutter Desktop 应用，用于图形化管理 Axiom 导入与健康检查。

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
