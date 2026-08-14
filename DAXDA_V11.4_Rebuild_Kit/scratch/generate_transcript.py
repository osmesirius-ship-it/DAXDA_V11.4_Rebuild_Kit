import json
import os

transcript_path = r"C:\Users\HomePC\.gemini\antigravity-ide\brain\ef990e4d-9d40-4d5a-8e53-6c38a0595926\.system_generated\logs\transcript.jsonl"
output_path = r"C:\Users\HomePC\.gemini\antigravity-ide\brain\ef990e4d-9d40-4d5a-8e53-6c38a0595926\daxda_session_transcript.md"

markdown_lines = ["# DAXDA Capability & Rebuild Session Transcript\n"]

with open(transcript_path, 'r', encoding='utf-8') as f:
    for line in f:
        try:
            data = json.loads(line)
            source = data.get("source", "")
            step_type = data.get("type", "")
            
            if source == "USER_EXPLICIT" and step_type == "USER_INPUT":
                content = data.get("content", "")
                # Extract just the <USER_REQUEST> if it exists
                if "<USER_REQUEST>" in content:
                    req = content.split("<USER_REQUEST>")[1].split("</USER_REQUEST>")[0].strip()
                    markdown_lines.append(f"### 👤 User:\n> {req}\n")
                else:
                    markdown_lines.append(f"### 👤 User:\n> {content.strip()}\n")
                    
            elif source == "MODEL" and step_type == "PLANNER_RESPONSE":
                content = data.get("content", "")
                if content:
                    markdown_lines.append(f"### 🤖 DAXDA Agent:\n{content}\n")
                
                tool_calls = data.get("tool_calls", [])
                for call in tool_calls:
                    name = call.get("name")
                    action = call.get("args", {}).get("toolAction", name)
                    markdown_lines.append(f"*{action}*\n")
                    
        except Exception as e:
            pass

with open(output_path, 'w', encoding='utf-8') as out:
    out.write("\n".join(markdown_lines))

print("Transcript successfully written to:", output_path)
