# Unique Artifact Injection Pattern

## ID: k-028
## Category: Architecture
## Confidence: 0.95

### 1. The Race Condition
在并行调度（Parallel Dispatch）场景下，多个 Worker 可能会尝试读写同一个临时文件（如 `PROMPT.md` 或 `status.json`）。
即使只是读取，文件锁也可能导致进程崩溃。

### 2. Solution: Immutable Artifacts
**原则**: 任何 injected artifact 必须是 Immutable 且 Unique 的。

**Naming Convention**:
`{ARTIFACT_TYPE}_{TASK_ID}_{TIMESTAMP}_{UUID}.md`

Example: `PROMPT_T006_20260212_a1b2.md`

### 3. Lifecycle
1. **Create**: Dispatch loop start.
2. **Use**: Worker read-only access.
3. **Destroy**: Dispatch loop clean-up (Post-execution).
