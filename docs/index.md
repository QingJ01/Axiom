---
layout: home

hero:
  name: Axiom
  text: 给 AI 编程助手装上工程化大脑
  tagline: 记忆 + 工作流 + 进化。让 AI 在真实项目里持续可用，而不是每次对话从零开始。
  actions:
    - theme: brand
      text: 快速开始
      link: /guide/quickstart
    - theme: alt
      text: 实战教程
      link: /guide/tutorial

features:
  - title: 记得住
    details: 项目决策、用户偏好、当前任务持续保存在 .agent/memory，跨会话恢复。
  - title: 干得完
    details: 从评审到拆解再到实现与验收，按工作流推进，减少“做一步问一步”。
  - title: 学得会
    details: 把成功/失败沉淀为知识与模式，降低重复踩坑概率。
  - title: 可移植
    details: 一个 .agent 目录即可接入你的项目，尽量不侵入业务代码。
  - title: 可追溯
    details: 用结构化状态与可验证产物驱动门禁，而不是靠口头描述。
  - title: 多工具适配
    details: 通过 adapters 适配不同 AI 编码工具与运行方式。
---

## Axiom 是什么

Axiom 是一套“项目内操作系统”，用于把 AI 编程从一次性问答变成可交付的工程流程。

## 你会用到的三个入口

- 新手上手：`/start` -> `/status`
- 开发交付：`/feature-flow`
- 报错救火：`/analyze-error`

## 推荐阅读路径

1. [快速开始](./guide/quickstart.md)
2. [安装与运行](./guide/installation.md)
3. [实战教程：从需求到交付](./guide/tutorial.md)
4. [工作流说明](./guide/workflows.md)
5. [命令参考](./guide/commands.md)
6. [故障排查](./guide/troubleshooting.md)

## 核心目录（概念级）

- `.agent/`：主系统目录（唯一事实源）
- `.agent/memory/`：项目决策、偏好、上下文、进化数据
- `.agent/workflows/`：命令工作流（启动、交付、回滚、复盘等）
- `.agent/adapters/`：不同 AI 工具的适配入口
