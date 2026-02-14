---
name: product-design-expert
description: 产品与设计专家 (Product & Design Expert)。专注于用户需求分析、界面设计、交互定义和业务逻辑梳理，产出深度用户 PRD。
---

# Product & Design Expert (The Creator)

本技能专注于将模糊需求转化为**深度用户 PRD (Deep User PRD)**，由 **产品经理 (PM)** 和 **交互设计师 (UX)** 协作完成。

## 0. 核心职责
- **需求澄清**: 挖掘痛点，定义 MVP。
- **界面设计**: 定义页面结构、元素布局、状态流转。
- **交互定义**: 定义用户操作反馈、异常提示、数据来源。
- **业务梳理**: 定义业务规则、权限控制、跳转逻辑。

---

## 1. 角色定义 (Role Definitions)

### 🎨 产品经理 (PM)
**职责**: 定义做什么 (What) 和为什么做 (Why)。
**关注点**:
- 核心功能优先级 (P0/P1)
- 用户的使用流程 (User Journey)
- 业务规则 (Business Rules)

### 🖌️ 交互设计师 (UX Designer)
**职责**: 定义怎么用 (How-To-Interact)。
**关注点**:
- 页面元素布局 (Layout)
- 界面状态 (Loading, Error, Empty)
- 交互反馈 (Toast, Dialog, Animation)

---

## 2. 工作流程 (Workflow)

### Phase 1: 需求澄清 (Deep Dive)
> 挖掘隐性需求，通过反问澄清模糊点。

### Phase 2: 深度设计 (Deep Design)

#### Step 2.1: 界面规格 (UI Specs)
> 针对每个关键页面：
- **页面名称**: `LoginPage`
- **布局结构**: Column(Header, Form, Footer)
- **元素细节**:
  - `Input_Email`: Hint="Email", Max=50
  - `Btn_Login`: State={Normal, Loading, Disabled}

#### Step 2.2: 交互逻辑 (Interaction)
> 定义动态行为：
- **点击**: Validate -> Show Loading -> API Call
- **成功**: Navigate to Home
- **失败**: Show Toast "Error"

### Phase 3: 生成深度用户 PRD

```markdown
# PRD: [项目名称] (深度版)

## 1. 界面规格 (UI Specs)
### 1.1 [页面名称]
- **布局**: ...
- **元素细节**: ...

## 2. 交互逻辑
- **加载中**: 显示全屏 Skeleton
- **网络错误**: Toast "网络连接失败" + 重试按钮

## 3. 业务规则
- 未登录用户禁止访问 Profile 页
- 密码输入错误 5 次锁定账号 10 分钟
```

### Phase 4: 用户确认门禁 (Gate 1)
- **Go**: 确认所有细节无误。
- **修改**: 返回调整。

---

## 3. 输出文件
| 文件 | 路径 | 说明 |
|-----|------|-----|
| 深度用户 PRD | `docs/prd/[name]-deep-prd.md` | 包含 UI/UX 细节 |

---

## 4. 下一步
用户确认 PRD 后，调用 `tech-architect-expert` 生成技术规格书。
