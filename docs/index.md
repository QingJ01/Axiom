---
title: Axiom
description: Axiom 官方文档
---

# Axiom

给 AI 编程助手提供工程化运行环境：可持续记忆、可验证流程、可复盘协作。

## 从这里开始

- 新用户建议顺序：
  1. `guide/install-and-upgrade` 完成安装
  2. `guide/quickstart` 跑通第一条流程
  3. `concepts/how-it-works` 理解系统原理
  4. `guide/commands` 查命令细节

## 文档地图

### Concepts（是什么 + 为什么）

- `concepts/purpose-and-scope`：项目用途与适用边界
- `concepts/feature-map`：能力地图与输入输出矩阵
- `concepts/how-it-works`：路由、流程、门禁、记忆、进化原理
- `concepts/principle-qa`：高频原理问题与取舍解释

### Guide（怎么做）

- `guide/install-and-upgrade`：安装、验证、升级、卸载、回滚
- `guide/quickstart`：10 分钟上手路径
- `guide/workflows`：完整流程与操作建议
- `guide/troubleshooting`：常见故障排查

### Reference（查手册）

- `guide/commands`：命令参考
- `reference/configuration`：配置说明
- `reference/structure`：目录结构
- `reference/release` / `reference/changelog`：发布与更新

## 快速安装

```bash
git clone https://github.com/QingJ01/axiom.git
cd axiom
bash setup.sh /path/to/your-project
```

Windows PowerShell:

```powershell
.\setup.ps1 -TargetDir "D:\your-project"
```

## 最小可用命令组

- `/start`：加载上下文并恢复会话
- `/status`：确认系统状态与任务队列
- `/analyze-error`：进入故障分析链路
- `/suspend`：收尾并保存现场

## 下一步建议

- 先看 `guide/install-and-upgrade`
- 再看 `guide/quickstart`
- 有设计疑问时看 `concepts/principle-qa`
