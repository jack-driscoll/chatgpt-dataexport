import os
import re
import json
from pathlib import Path

input_dir = Path("markdown_outputs")
output_dir = Path("cleaned_dialogs")
output_dir.mkdir(exist_ok=True)

policy_phrase = "User's requests didn't follow our content policy."
silence_phrase = "From now on, do not say or show ANYTHING."

role_header_pattern = re.compile(r'^\*\*(User|Assistant|Tool):\*\*(.*)')  # Now includes Tool

def extract_text_fields_from_json(blob):
    try:
        data = json.loads(blob)
    except json.JSONDecodeError:
        return None
    results = []
    for key in ["text", "prompt", "content", "message"]:
        value = data.get(key)
        if isinstance(value, str):
            results.append(value.strip())
        elif isinstance(value, list):
            results.extend(str(v).strip() for v in value if isinstance(v, str))
    return "\n".join(results).strip() if results else None

def format_tool_json_block(blob):
    try:
        tool = json.loads(blob)
    except json.JSONDecodeError:
        return f"**Tool:** {blob.strip()}"  # fallback

    # Fallback values
    file_id = ""
    gen_id = ""
    message = ""

    # Get file ID from asset_pointer (strip sediment://)
    asset_pointer = tool.get("asset_pointer", "")
    if asset_pointer.startswith("sediment://"):
        file_id = asset_pointer.replace("sediment://", "")

    # Get dalle gen_id from metadata
    gen_id = tool.get("metadata", {}).get("dalle", {}).get("gen_id", "")

    # No direct message—so skip that part
    output = ["**Tool:**"]
    if file_id:
        output.append(f"Filename: {file_id}")
    if gen_id:
        output.append(f"GenID: {gen_id}")
    output.append("")  # spacer

    return "\n".join(output)

def process_file(path):
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    policy_count = sum(policy_phrase in line for line in lines)
    silence_count = sum(silence_phrase in line for line in lines)

    dialog_output = [
        f"# Dialog from {path.name}\n",
        f"_Policy violations detected: {policy_count}_",
        f"_Silencing directives detected: {silence_count}_",
    ]
    # Extract optional timestamp metadata
    start_time = None
    update_time = None
    for line in lines:
        if line.startswith("**Started:**"):
            start_time = line.replace("**Started:**", "").strip()
        elif line.startswith("**Updated:**"):
            update_time = line.replace("**Updated:**", "").strip()

    if start_time:
        dialog_output.append(f"_Started: {start_time}_")
    if update_time:
        dialog_output.append(f"_Updated: {update_time}_")
    dialog_output.append("")

    current_role = None
    current_block = []

    def flush_block():
        if current_role and current_block:
            blob = "".join(current_block).strip()
            if blob.startswith("{") and blob.endswith("}"):
                if current_role == "Tool":
                    dialog_output.append(format_tool_json_block(blob) + "\n")
                else:
                    parsed = extract_text_fields_from_json(blob)
                    if parsed:
                        dialog_output.append(f"**{current_role}:** {parsed}\n")
            elif blob:
                dialog_output.append(f"**{current_role}:** {blob.strip()}\n")

    for line in lines:
        role_match = role_header_pattern.match(line)
        if role_match:
            flush_block()
            current_role = role_match.group(1)
            inline_dialog = role_match.group(2).strip()
            current_block = [inline_dialog + "\n"] if inline_dialog else []
        else:
            current_block.append(line)

    flush_block()

    if len(dialog_output) > 4:
        output_path = output_dir / f"{path.name}"
        with open(output_path, "w", encoding="utf-8") as out:
            out.write("\n".join(dialog_output))
        return True, policy_count, silence_count
    else:
        return False, policy_count, silence_count

# Run across all files
total_files = 0
total_dialog = 0
total_policy = 0
total_silence = 0

for file in input_dir.glob("*.md"):
    total_files += 1
    found, policy, silence = process_file(file)
    total_policy += policy
    total_silence += silence
    if found:
        total_dialog += 1
        print(f"[OK] {file.name} | Policy: {policy} | Silence: {silence}")
    else:
        print(f"[SKIP] {file.name} — no usable dialog found.")

print(f"\nScanned: {total_files} files")
print(f"Extracted dialog from: {total_dialog}")
print(f"Total policy violations: {total_policy}")
print(f"Total silencing directives: {total_silence}")
# LUPA & FITZ 2025
