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

## `.agents` 显示为快捷方式

### 现象

- Windows 中看到 `.agents` 类似快捷方式

### 处理

- 这是正常行为，`.agents` 是兼容入口
- 主目录始终以 `.agent` 为准
