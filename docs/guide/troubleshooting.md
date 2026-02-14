# 故障排查

## `/start` 后没有恢复上下文

### 现象

- 系统无法识别当前任务状态
- 总是提示重新开始

### 处理

1. 检查 `.agent/memory/active_context.md` 是否存在
2. 检查 frontmatter 字段是否完整（`task_status` 等）
3. 再次执行 `/start`

## `/status` 信息不完整

### 现象

- 仪表盘缺少知识统计或检查点信息

### 处理

1. 检查 `.agent/memory/evolution/` 目录是否存在
2. 检查 `.agent/config/agent_config.md` 是否存在
3. 再执行 `/status`

## 错误修复循环

### 现象

- 同一错误反复出现
- 自动修复多次失败

### 处理

1. 执行 `/analyze-error` 并贴完整日志
2. 检查 `.agent/memory/project_decisions.md` 的 `Known Issues`
3. 达到重试上限后：回滚到检查点或标记阻塞

## Windows 提示“无法识别 pwsh”

### 现象

- PowerShell 报错：`pwsh` 不是可识别命令

### 处理

1. 直接执行：`.\setup.ps1 -TargetDir "你的项目路径"`
2. 或安装 PowerShell 7 后再用：`pwsh .\setup.ps1 ...`
3. 若执行策略拦截，用：`powershell -ExecutionPolicy Bypass -File .\setup.ps1 ...`

## `/export` 后找不到压缩包

### 现象

- 提示导出成功，但不知道文件在哪

### 处理

1. 优先查看导出结果中的 `Location` 绝对路径
2. 默认输出在项目根目录，文件名形如 `axiom-export-YYYYMMDD.zip`
3. 若仍找不到，确认触发命令时所在目录是否为目标项目
