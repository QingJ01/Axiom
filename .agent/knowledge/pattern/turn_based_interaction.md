# Async Interaction Pattern (Turn-Based Resume)

## ID: k-027
## Category: Pattern
## Confidence: 0.90

### 1. Sentinel
不要试图在 `codex exec` 的 stdin 中保持长连接等待（Stream Blocking）。这在自动化脚本中极不可靠。

### 2. The Pattern
将交互拆解为离散的回合 (Turns)：
1.  **Job A**: Worker 执行 -> 遇到问题 -> 输出 JSON `agent_message` -> Exit 0。
2.  **Dispatcher**: 监控到提问 -> 暂停轮询 -> 决策答案。
3.  **Job B**: Resume Session -> `codex exec resume {ID} "My Answer"` -> Worker 继续。

### 3. Advantages
- **Stateless**: 可以在任意时间点中断和恢复。
- **Resilient**: 进程崩溃不影响会话状态（Context 保存在 Codex 侧）。
- **Debuggable**: 每个回合都有独立的日志。
