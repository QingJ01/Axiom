# 安装、升级与卸载

本页以 **Axiom Manager 安装器** 为主路径。命令行仅作为备用方案。

## 1. 推荐安装方式：Axiom Manager（GUI）

### 适用平台

- Windows
- macOS

### 步骤

1. 从仓库 Release 下载对应平台安装包（`Axiom Manager`）。
2. 安装并启动 Axiom Manager。
3. 在应用中点击“浏览...”选择你的目标项目目录。
4. 选择 Provider（默认推荐 CLI 体系）。
5. 点击安装/应用，等待结果提示。

### 安装器会自动处理

- 增量写入或更新目标项目 `.agent/`
- 初始化或保留记忆文件（`active_context.md`、`project_decisions.md`）
- 补齐 `.gitignore` 规则
- 按所选 Provider 写入适配配置

## 2. 安装后验证

安装完成后，在目标项目确认：

- `.agent/` 存在
- `.agent/memory/active_context.md` 存在
- `.agent/memory/project_decisions.md` 存在

然后在 AI 会话执行：

```text
/start
/status
```

成功标准：`/status` 能返回状态与任务信息。

## 3. 升级（主推安装器）

升级建议继续使用 Axiom Manager：

1. 在 Axiom Manager 中点击“同步”按钮
2. 重新选择目标项目并执行安装/应用
3. 检查 `/status` 与关键流程命令是否正常

建议升级前先在目标项目做一次 Git 提交，便于回滚。

## 4. 回滚

若升级结果不符合预期，优先在目标项目使用 Git 回滚：

```bash
git status
git restore .agent
```

若需要整体回退，请按你的团队标准回滚流程执行。

## 5. 卸载

如需移除 Axiom：

1. 删除目标项目 `.agent/`
2. 清理 `.gitignore` 中 Axiom 规则
3. 恢复原有全局适配配置（如有）

建议先备份 `.agent/memory/`，避免丢失历史知识。

## 6. 安装器常见问题

- **安装后 `/status` 空白**：检查 `active_context.md` frontmatter 是否完整。
- **目标目录写入失败**：确认目录权限，避免系统保护目录。
- **Provider 选择不生效**：重新应用一次安装并重启 AI 会话。

## 7. 备用方案：命令行安装（非主推）

仅在安装器不可用时使用：

### macOS / Linux

```bash
git clone https://github.com/QingJ01/axiom.git
cd axiom
bash setup.sh /path/to/your-project
```

### Windows PowerShell

```powershell
git clone https://github.com/QingJ01/axiom.git
cd axiom
.\setup.ps1 -TargetDir "D:\your-project"
```
