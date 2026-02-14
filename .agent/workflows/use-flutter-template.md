---
description: Flutter 模板规范加载与拷贝（flutter-ai-advanced-template）
---

# /use-flutter-template

> 目标: 在开发 Flutter 功能前，将 flutter-ai-advanced-template 的规范内容拷贝到目标项目，确保开发遵守模板铁律。

---

## Step 1: 确认目标项目
- 询问用户目标项目路径（默认 `PROJECT_ROOT`，即 Git 根目录；若无 Git 则当前目录）。
- 若目标不是 Flutter 项目，提示风险并要求确认继续。

## Step 2: 确认模板源
- 默认模板源路径: `[PROJECT_ROOT]/.agent/templates/flutter-ai-advanced-template`。
- 若不存在，则执行克隆:
  ```bash
  git clone --depth 1 https://github.com/flockmaster/flutter-ai-advanced-template.git [PROJECT_ROOT]/.agent/templates/flutter-ai-advanced-template
  ```

## Step 3: 选择拷贝模式
- **模式 A: 规范包（推荐，适合已有 Flutter 项目）**
  - 只拷贝规范与工具，不动业务代码。
- **模式 B: 全量模板（仅适合新项目）**
  - 拷贝模板的基础代码与目录结构，但**不覆盖**现有文件，除非用户明确同意。

## Step 4A: 规范包拷贝清单（默认）
拷贝以下内容到目标项目根目录：
- `.rules`
- `analysis_options.yaml`
- `templates/`
- `scripts/`
- `AI_GUIDE.md`
- `pubspec.yaml.example`

**规则**:
- 任何同名文件已存在时，必须先询问是否覆盖。
- 不拷贝模板内的 `.agent/` 与 `lib/`，避免与项目现有架构冲突。

## Step 4B: 全量模板拷贝清单（新项目）
在用户确认“这是新项目/允许覆盖”后拷贝：
- `assets/`
- `lib/`
- `test/`
- `ui/`
- `.rules`
- `analysis_options.yaml`
- `templates/`
- `scripts/`
- `AI_GUIDE.md`
- `pubspec.yaml.example`

**规则**:
- 默认不拷贝 `.agent/`，避免覆盖 Axiom 的工作流体系。
- 若目标目录非空，必须显式二次确认。

## Step 5: 生效确认
- 提示用户在 Flutter 开发前需先阅读 `.rules`。
- 在本次会话中，将 `.rules` 作为最高约束执行。

## 显性调用
- 用户输入 `/use-flutter-template` 时执行。

## 自然语言触发
- 用户明确要求“开发 Flutter 功能/页面/模块/迭代”时，先执行本工作流，再进入功能开发流程。
