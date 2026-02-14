---
name: requirement-analyst
description: The Gatekeeper skill that analyzes user requirements for feasibility and clarity before allowing PRD creation.
---

# Requirement Analyst Skill

## 1. Overview
This skill acts as the first line of defense in the product development pipeline. It evaluates raw user requirements against project context to ensure they are feasible, clear, and safe to proceed.

## 2. Input
- **User Requirement**: The raw text or voice input from the user describing their desired feature.
- **Project Context**: The `project_summary` (mission statement) to ensure alignment.

## 3. Actions
The skill performs a two-step analysis:

### Step 1: Feasibility Check (The Red Gate)
- **Safety**: Does this request violate safety guidelines or ethical boundaries?
- **Alignment**: Does this deviate significantly from the Axiom core value (e.g. asking for a recipe in a dev tool)?
- **Technical Reality**: Is this technically impossible (e.g. solving P=NP)?

### Step 2: Clarity Check (The Yellow Gate)
- **Completeness**: Are the key actors, actions, and outcomes defined?
- **Ambiguity**: Are there terms with multiple interpretations?
- **Context**: Is there enough information to design a UI/Flow?

## 4. Output Logic (Structured Response)

Return a JSON-like structure or clear Markdown section:

### Status: [PASS | REJECT | CLARIFY]

1. **REJECT**:
   - Reason: [Why is this impossible or irrelevant?]
   - Suggestion: [How to pivot?]

2. **CLARIFY**:
   - Clarity Score: [0-89%]
   - Missing Info: [List of missing context]
   - Questions: [List of 3-5 specific questions to ask the user]

3. **PASS**:
   - Clarity Score: [90-100%]
   - Context Summary: [A structured summary of the requirement]
   - MVP Scope: [A bullet list of what is in scope vs out of scope]

## 5. Usage Example

**Input**: "I want a dashboard."

**Output**:
```markdown
### Status: CLARIFY
**Clarity Score**: 30%
**Reason**: "Dashboard" is too vague.
**Questions**:
1. Who is the target user for this dashboard?
2. What key metrics (KPIs) need to be displayed?
3. Is this for the admin panel or the end-user app?
```
