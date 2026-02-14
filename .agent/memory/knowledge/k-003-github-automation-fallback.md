---
id: k-003
title: GitHub Automation Fallback Strategy (GitHub 自动化降级策略)
category: tooling
tags: [github, automation, fallback]
created: 2026-02-08
confidence: 0.8
references: [evolution-engine-v1]
---

## Summary
在执行 GitHub 自动化任务时，需考虑到环境缺失（无 CLI、无浏览器）的情况，预备降级方案。

## Details
**优先级策略**:
1. **P0 (Browser)**: 使用浏览器模拟用户操作（最直观，但依赖环境）。
2. **P1 (CLI)**: 使用 `gh` 命令行工具（最稳定，需预装）。
3. **P2 (API)**: 使用 `curl` 调用 API（需 Token）。
4. **P3 (Manual)**: 指导用户手动操作，然后接管后续（如 `git remote add`）。

**经验教训**:
不要假设环境完备。在 PRD 阶段应检查环境依赖，或准备好安装脚本（如 `winget install GitHub.cli`）。
