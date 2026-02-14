#!/usr/bin/env python3
import os
import re

def main():
    agent_file_path = "AGENTS.md"
    if not os.path.exists(agent_file_path):
        agent_file_path = "AGENT.md"
    
    if not os.path.exists(agent_file_path):
        print("Error: AGENTS.md or AGENT.md not found.")
        return

    decisions_path = ".agent/memory/project_decisions.md"
    preferences_path = ".agent/memory/user_preferences.md"

    context_content = []
    
    # Read Project Decisions
    if os.path.exists(decisions_path):
        with open(decisions_path, "r", encoding="utf-8") as f:
            content = f.read()
            # Extract sections: Tech Stack, Architecture, Coding Standards
            # Using regex to find content between headers
            tech_stack = re.search(r"## 1\. 技术栈(.*?)(##|$)", content, re.DOTALL)
            architecture = re.search(r"## 2\. 架构设计(.*?)(##|$)", content, re.DOTALL)
            standards = re.search(r"## 3\. 编码规范(.*?)(##|$)", content, re.DOTALL)
            
            context_content.append("## 📌 项目上下文 (自动同步)")
            if tech_stack:
                context_content.append(f"### 技术栈{tech_stack.group(1).strip()}")
            if architecture:
                context_content.append(f"### 架构设计{architecture.group(1).strip()}")
            if standards:
                context_content.append(f"### 编码规范{standards.group(1).strip()}")

    # Read User Preferences
    if os.path.exists(preferences_path):
        with open(preferences_path, "r", encoding="utf-8") as f:
            content = f.read()
            # Extract Communication Style & Dev Habits
            comm_style = re.search(r"## 1\. 沟通风格(.*?)(##|$)", content, re.DOTALL)
            dev_habits = re.search(r"## 2\. 也是开发习惯(.*?)(##|$)", content, re.DOTALL)
            
            context_content.append("\n## ⚙️ 用户偏好 (自动同步)")
            if comm_style:
                context_content.append(f"### 沟通风格{comm_style.group(1).strip()}")
            if dev_habits:
                context_content.append(f"### 开发习惯{dev_habits.group(1).strip()}")
            
    context_text = "\n\n".join(context_content)
    context_block = f"""<!-- AUTO-GENERATED CONTEXT START -->
{context_text}
<!-- AUTO-GENERATED CONTEXT END -->"""

    # Update AGENTS.md
    with open(agent_file_path, "r", encoding="utf-8") as f:
        original_content = f.read()

    # Check if block exists
    if "<!-- AUTO-GENERATED CONTEXT START -->" in original_content:
        # Replace existing block
        new_content = re.sub(
            r"<!-- AUTO-GENERATED CONTEXT START -->(.*?)<!-- AUTO-GENERATED CONTEXT END -->", 
            context_block, 
            original_content, 
            flags=re.DOTALL
        )
    else:
        # Insert after header (search for first H1 or metadata end)
        # Try to insert after the YAML frontmatter or first H1
        # For AGENTS.md, it starts with # Codex Worker Agent...
        # We'll insert it after the > quote block about role definition
        # Look for "---" after line 6
        insert_marker = "\n---\n"
        parts = original_content.split(insert_marker, 1)
        if len(parts) > 1:
            new_content = parts[0] + insert_marker + context_block + "\n\n" + parts[1]
        else:
            # Fallback: Append to top
            new_content = context_block + "\n\n" + original_content

    with open(agent_file_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    
    print(f"Successfully updated {agent_file_path} with latest context.")

if __name__ == "__main__":
    main()
