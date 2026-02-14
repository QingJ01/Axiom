# Dispatcher Python Legacy (Deprecated)

> **状态**: 已废弃 (2026-02-10)
> **替代方案**: Agent 原生调度 (codex-dispatch.md)

## 废弃原因

经过验证，Gemini Agent 可以直接使用原生工具 (`run_command` + `command_status`) 调用 Codex CLI，
无需 Python 中间层封装。这种方式更简单、更灵活、更易维护。

## 原有功能

| 文件 | 功能 |
|------|------|
| `worker.py` | Codex CLI 子进程封装器 |
| `core.py` | 数据结构定义 (TaskSpec, WorkerResult 等) |
| `decision_engine.py` | PM 自主决策引擎 |
| `git_ops.py` | Git 自动提交 |
| `jsonl_parser.py` | JSONL 事件流解析器 |
| `main.py` | CLI 入口 |
| `prd_updater.py` | PRD 状态回写 |
| `restart_injector.py` | 重启注入机制 |
| `tests/` | 单元测试 |

## 新方案

使用 `.agent/workflows/codex-dispatch.md` 工作流，PM (Axiom) 直接调用：

```bash
# 启动 Codex Worker
run_command("codex exec --json --dangerously-bypass-approvals-and-sandbox {Prompt}")

# 轮询等待结果
command_status(CommandId, WaitDurationSeconds=60)
```

## 恢复方法

如果需要恢复 Python 版本：

```bash
# 将文件移回 dispatcher 目录
Move-Item -Path ".agent\deprecated\dispatcher-python-legacy\*" -Destination ".agent\dispatcher\" -Force
```

---

_Archived by Axiom on 2026-02-10_
