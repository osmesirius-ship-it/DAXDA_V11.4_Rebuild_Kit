import os
import glob

task_dir = r"C:\Users\HomePC\.gemini\antigravity-ide\brain\ef990e4d-9d40-4d5a-8e53-6c38a0595926\.system_generated\tasks"
output_path = r"C:\Users\HomePC\.gemini\antigravity-ide\brain\ef990e4d-9d40-4d5a-8e53-6c38a0595926\daxda_terminal_logs.md"

log_files = sorted(glob.glob(os.path.join(task_dir, "*.log")), key=os.path.getmtime)

markdown_lines = ["# DAXDA Terminal Interactions & Task Logs\n"]

for log_file in log_files:
    task_name = os.path.basename(log_file)
    markdown_lines.append(f"## Task Log: `{task_name}`\n")
    markdown_lines.append("```text")
    try:
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read().strip()
            if content:
                markdown_lines.append(content)
            else:
                markdown_lines.append("(empty log)")
    except Exception as e:
        markdown_lines.append(f"Error reading log: {e}")
    markdown_lines.append("```\n")

with open(output_path, 'w', encoding='utf-8') as out:
    out.write("\n".join(markdown_lines))

print(f"Combined {len(log_files)} terminal logs into:", output_path)
