# 🚀 测试项目 - 从零开始指南

**项目目录**: `D:\Baic-Flutter-APP\test-agent-install`  
**创建时间**: 2026-02-09  
**目的**: 验证 Axiom 从零开始的项目开发能力

---

## 📦 已安装内容

### 核心系统
- ✅ `.agent/` - 主系统 (111个文件)
  - 记忆系统
  - 技能模块 (4个)
  - 工作流 (13个)
  - 进化引擎
  

### 配置与文档
- ✅ `docs/` - 完整文档
  - PRD 文档
  - 用户指南
  
- ✅ `README.md` - 系统说明
- ✅ `setup.ps1` / `setup.sh` - 安装脚本
- ✅ `.gitignore` - Git 规则

### 项目配置
- ✅ `project_decisions.md` - 已配置 Flutter/Dart/MVVM
- ✅ `active_context.md` - 已初始化 IDLE 状态
- ✅ `user_preferences.md` - 用户偏好设置

---

## 🎯 快速开始

### Step 1: 确认系统状态

输入以下命令启动系统：
```
/start
```

**预期输出**:
```
🚀 Axiom 已启动

📊 Context Loaded
   - Status: IDLE
   - Project: Test Flutter App (Flutter/Dart/MVVM)

✅ System ready. What's next?
```

### Step 2: 查看系统状态

```
/status
```

这将显示：
- 知识库统计
- 模式库统计
- 工作流执行记录
- 系统健康度

### Step 3: 开始第一个任务

**方式 A: 创建简单功能**
```
创建一个简单的 Counter Widget
```

**方式 B: 使用 PRD 工作流**
```
/prd 创建一个计数器应用
```

系统会自动：
1. 生成 PRD 文档
2. 等待你确认（Gate 1）
3. 生成代码
4. 自动编译检查
5. 自动测试
6. 自动 Git 提交（Gate 2）
7. 收割知识到知识库

---

## 🧪 验证测试建议

### 测试 1: 基础功能验证
**任务**: 创建一个简单的 Hello World Widget
**验证点**:
- [ ] 启动工作流正常
- [ ] 代码生成成功
- [ ] 记忆系统记录任务

### 测试 2: 自动化流程验证
**任务**: 创建带状态管理的 Counter 应用
**验证点**:
- [ ] PRD 生成并等待确认
- [ ] 代码自动生成
- [ ] 自动运行分析
- [ ] 自动提交代码
- [ ] 知识自动收割

### 测试 3: 错误修复验证
**任务**: 故意引入一个编译错误
**验证点**:
- [ ] 系统自动检测错误
- [ ] 自动尝试修复（最多3次）
- [ ] 错误模式记录到 Known Issues
- [ ] 熔断机制触发（3次失败后）

### 测试 4: 跨会话记忆验证
**操作**:
1. 开始一个任务但不完成
2. 关闭当前会话
3. 重新打开并输入 `/start`

**验证点**:
- [ ] 自动检测到 PENDING 任务
- [ ] 提示是否继续
- [ ] 上下文完整恢复

### 测试 5: 进化能力验证
**操作**:
1. 完成几个任务
2. 输入 `/reflect` 或 `/evolve`

**验证点**:
- [ ] 生成反思报告
- [ ] 知识库自动更新
- [ ] 模式库识别新模式
- [ ] 工作流指标记录

---

## 📊 系统组件说明

### 记忆系统
- **短期记忆**: `active_context.md` - 当前任务和进度
- **长期记忆**: `project_decisions.md` - 架构决策
- **用户偏好**: `user_preferences.md` - 个人习惯

### 技能模块
1. **context-manager** - 记忆管理
2. **evolution-engine** - 自进化引擎
3. **prd-crafter-lite** - 纯净版 PRD 生成
4. **prd-crafter-pro** - 多角色协作 PRD

### 工作流
1. **start** - 启动流程
2. **feature-flow** - 功能开发完整流程
3. **analyze-error** - 错误分析和修复
4. **reflect** - 反思和学习
5. **evolve** - 手动触发进化
6. **rollback** - 回滚到检查点
7. **suspend** - 暂停并保存状态
8. **status** - 查看系统状态
9. 其他...

### 进化引擎
- **knowledge_base.md** - 知识图谱索引
- **pattern_library.md** - 代码模式库
- **learning_queue.md** - 学习队列
- **workflow_metrics.md** - 效能统计
- **reflection_log.md** - 反思日志

---

## 🎯 测试目标

### 主要验证点
1. ✅ 系统能否从零开始启动
2. ⏳ 完整的功能开发流程是否顺畅
3. ⏳ 自动化程度是否达到"喝杯茶"级别
4. ⏳ 知识是否能自动积累
5. ⏳ 跨会话记忆是否有效

### 成功标准
- 任务自动接力无需人工干预
- 编译错误自动修复（3次内）
- Git 自动提交无需提醒
- 知识自动收割到知识库
- 跨会话完美恢复上下文

---

## 📚 参考文档

在 `docs/` 目录中有完整的参考文档：
- `docs/index.md` - 官网首页与导航
- `docs/guide/quickstart.md` - 快速开始
- `docs/guide/tutorial.md` - 实战教程
- `docs/guide/workflows.md` - 工作流说明
- `docs/guide/commands.md` - 命令参考

---

## 🔧 调试命令

当遇到问题时：

```bash
# 查看系统状态
/status

# 查看最近的反思日志
/reflect

# 查询知识库
/knowledge [关键词]

# 查询模式库
/patterns [关键词]

# 手动触发进化
/evolve

# 回滚到上一个检查点
/rollback
```

---

## ⚠️ 注意事项

1. **首次使用**：系统已完全初始化，可直接使用
2. **Git 规则**：动态文件已配置在 `.gitignore` 中
3. **技术栈**：当前配置为 Flutter/Dart，可自行修改
4. **PRD 门禁**：生成 PRD 后必须确认才会继续
5. **自动提交**：编译成功后会自动 commit（可在 user_preferences 中关闭）

---

## 🎉 开始你的测试之旅！

现在，这个目录已经是一个完整的、可以从零开始开发的环境了。

**建议第一步**：
```
/start
```

然后说出你想要实现的第一个功能，系统会自动引导你完成整个开发流程。

Good luck! 🚀
