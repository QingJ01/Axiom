---
name: product-design-expert
description: A specialist skill focused on translating structured user requirements into a Rough Product Requirements Document (PRD) and corresponding business flowcharts.
---

# Product Design Expert Skill

## 1. Overview
This skill takes a validated, clear requirement context (status: PASS) and transforms it into a structured, visual representation suitable for expert review. It acts as the "Concept Artist" of the product team.

## 2. Input
- **Validated Requirement**: A structured JSON or markdown block from the `requirement-analyst`.
- **Project Decisions**: The existing `project_decisions.md` (to ensure architectural fit).

## 3. Actions
The skill executes the following pipeline:

### Step 1: Conceptualization
- **Core Value**: What is the single most important user benefit?
- **MVP Scope**: What is the minimum set of features to achieve that value? (Exclude nice-to-haves).
- **User Journey**: Identify the happy path.

### Step 2: Visualization (Mermaid)
- **Flowchart**: Create a high-level business process diagram. Use `graph TD` or `sequenceDiagram`.
- **Entity**: Identify the core data models needed (e.g., User, Order, Product). (Optional: Class diagram).

### Step 3: Documentation (Drafting)
- **Structure**: Create a standard Draft PRD (`docs/prd/[name]-draft.md`).
- **Content**: Include Background, Goals, User Stories, Functional Requirements (High-Level), and the Flowchart.

## 4. Output Logic (File Generation)

**File Path**: `docs/prd/[kebab-case-name]-draft.md`

**Template**:
```markdown
# PRD: [Feature Name] - Draft

> **Status**: DRAFT
> **Author**: Product Design Expert
> **Version**: 0.1

## 1. Background & Goals
[Why do this? What problem does it solve?]

## 2. User Stories
| Role | Goal | Benefit |
| --- | --- | --- |
| User | ... | ... |

## 3. High-Level Requirements (MVP)
1. [Requirement 1]
2. [Requirement 2]

## 4. Business Flow
```mermaid
[Your Diagram Code Here]
```

## 5. Out of Scope (For Now)
[List items deferred to v2]
```

## 5. Usage Example

**Input**: A validated requirement for "Login with Email".

**Output**: Creates `docs/prd/login-feature-draft.md` with:
- Background: Need secure access.
- Stories: As a user, I can login to access my data.
- Diagram: Input Email -> Input Password -> Validate -> Success/Fail.
