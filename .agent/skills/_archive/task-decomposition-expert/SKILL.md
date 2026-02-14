---
name: tech-architect-expert
description: 技术架构专家 (Tech Architect Expert)。专注于将用户 PRD 转化为详细的技术规格说明书 (Detail Tech Spec)，定义数据结构、API 契约和边界测试用例。
---

# Tech Architect Expert (The Architect)

本技能专注于将**用户 PRD** 转化为**深度技术规格书 (Deep Tech Spec)**，由 **架构师** 和 **QA 工程师** 协作完成。

## 0. 核心职责
- **架构设计**: 数据库模型、API 接口定义。
- **质量保证**: 边界值约束、异常处理矩阵。
- **可测试性**: 定义测试用例和验收标准。

---

## 1. 角色定义 (Role Definitions)

### 👨‍💻 系统架构师 (System Architect)
**职责**: 定义怎么做 (How-To-Implement)。
**关注点**:
- 数据库 Schema (SQL/NoSQL)
- API Request/Response
- 模块依赖关系

### 🧪 质量工程师 (QA Engineer)
**职责**: 定义怎么测 (How-To-Test)。
**关注点**:
- 字段级约束 (Max/Min/Regex)
- 异常场景 (Offline, Timeout)
- 边界值 (0, -1, Empty)

---

## 2. 工作流程 (Workflow)

### Phase 1: 技术预研 (Feasibility Check)
> 评估 PRD 的技术可行性，识别风险。

### Phase 2: 深度设计 (Deep Design)

#### Step 2.1: 字段与约束 (Data & Constraints)
> 针对每个输入/展示字段：
- **字段名**: `username`
- **来源**: User Input
- **类型**: String
- **约束**: `6-20 chars`, `Alphanumeric`
- **默认值**: Empty string

#### Step 2.2: 接口定义 (API Contract)
> OpenAPI 风格定义：
- **Path**: `/api/v1/user`
- **Method**: `POST`
- **Body**: `{name, age}`
- **Response**: `200 OK` / `400 Error`

#### Step 2.3: 异常处理 (Error Handling)
> 定义前端如何感知和处理后端错误：
- **401**: Redirect to Login
- **500**: Show "Server Error" Dialog

### Phase 3: 生成深度技术规格书 (Deep Tech Spec)

```markdown
# Tech Spec: [项目名称]

## 1. 数据字典 (Data Dictionary)
| 字段 | 类型 | 必填 | 约束/正则 | 说明 |
|-----|-----|-----|----------|-----|
| title | String | Y | max:50 | 文章标题 |
| price | Decimal | Y | min:0.01 | 商品价格 |

## 2. API 接口定义 (OpenAPI Style)
- **POST /api/v1/resource**
  - **Request**: `{ "name": "..." }`
  - **Validation**: Name unique, trimmed.
  - **Response**: `201 Created` / `400 Bad Request`

## 3. 异常处理矩阵 (Error Matrix)
| 错误码 | 场景 | 前端行为 |
|-------|------|---------|
| 1001 | Auth Fail | 跳转 Login, Clear Token |
| 2005 | Insufficient Balance | Show Dialog "去充值" |

## 4. 边界测试用例 (Boundary Cases)
- [ ] 列表为空时显示 EmptyWidget
- [ ] 价格输入 999999999.99 (UI 溢出检查)
- [ ] emoji 输入过滤
```

---

## 3. 输出文件
| 文件 | 路径 | 说明 |
|-----|------|-----|
| 深度技术规格书 | `docs/prd/[name]-deep-spec.md` | 包含详细技术实现方案 |

---

## 4. 下一步
技术规格书确认后，调用 `/decompose` 进行任务拆解。
