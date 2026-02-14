# 目录结构

## 项目主结构

```text
Project Root/
├── .agent/                 # Axiom 主系统
│   ├── memory/             # 记忆层（决策/上下文/偏好/进化）
│   ├── workflows/          # 工作流定义
│   ├── adapters/           # AI 工具适配器
│   ├── config/             # 系统配置
│   └── knowledge/          # 知识资源
├── setup.sh                # macOS/Linux 安装器
├── setup.ps1               # Windows 安装器
├── README.md               # 项目总览
└── docs/                   # 使用文档
```

## 关键文件

- `.agent/memory/project_decisions.md`：项目技术决策
- `.agent/memory/active_context.md`：当前会话状态
- `.agent/memory/user_preferences.md`：用户偏好
- `.agent/config/agent_config.md`：激活 Provider 配置
