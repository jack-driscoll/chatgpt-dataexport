#!/usr/bin/env python3
"""
GPT Tools - Export Processing CLI
---------------------------------
Unpack conversations.json -> Markdown
Clean Markdown -> back-and-forth dialogs
Optionally export, zip, or convert formats.

Usage examples:
  python chatgpt-salad-shooter.py --unpack --input conversations.json --output md_out
  python chatgpt-salad-shooter.py --clean --input md_out --output clean_out --format txt
  python chatgpt-salad-shooter.py --all --input conversations.json --output export_dir --zip
"""

import argparse
import json
import os
import re
import subprocess
import zipfile
from datetime import datetime
from pathlib import Path

# -------------------------------
# UNPACK CONVERSATIONS
# -------------------------------
def unpack_conversations(input_file: str, output_dir: str):
    with open(input_file, "r", encoding="utf-8") as f:
        conversations = json.load(f)
    print(f"Loaded {len(conversations)} conversations.")

    os.makedirs(output_dir, exist_ok=True)
    count = 0

    for convo in conversations:
        title = convo.get("title", "Untitled Conversation")
        safe_title = re.sub(r'[\\/*?:"<>|]', "_", title)
        filename = Path(output_dir) / f"{safe_title}.md"

        create_time = datetime.fromtimestamp(convo["create_time"]).strftime("%Y-%m-%d %H:%M:%S")
        update_time = datetime.fromtimestamp(convo["update_time"]).strftime("%Y-%m-%d %H:%M:%S")
        mapping = convo["mapping"]

        # Find root
        root_id = next((k for k, v in mapping.items() if v["parent"] is None), None)
        messages = []

        def follow_chain(node_id):
            node = mapping.get(node_id)
            if node and node.get("message"):
                msg = node["message"]
                role = msg["author"]["role"]
                content = msg.get("content", {})
                parts = content.get("parts", [])
                for part in parts:
                    messages.append((role, part))
            for child_id in node.get("children", []):
                follow_chain(child_id)

        if root_id:
            follow_chain(root_id)

        lines = [f"# {title}\n", f"**Started:** {create_time}", f"**Updated:** {update_time}", ""]
        for role, part in messages:
            if isinstance(part, str):
                lines.append(f"**{role.capitalize()}:** {part.strip()}\n")
            else:
                lines.append(f"**{role.capitalize()}:** {json.dumps(part, indent=2)}\n")

        with open(filename, "w", encoding="utf-8") as out:
            out.write("\n".join(lines))
        count += 1

    print(f"[UNPACK] Wrote {count} markdown files to {output_dir}")
    return count


# -------------------------------
# CLEAN DIALOGS
# -------------------------------
role_header_pattern = re.compile(r'^\*\*(User|Assistant|Tool):\*\*(.*)')
policy_phrase = "User's requests didn't follow our content policy."
silence_phrase = "From now on, do not say or show ANYTHING."

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
        return f"**Tool:** {blob.strip()}"
    file_id = ""
    gen_id = ""
    asset_pointer = tool.get("asset_pointer", "")
    if asset_pointer.startswith("sediment://"):
        file_id = asset_pointer.replace("sediment://", "")
    gen_id = tool.get("metadata", {}).get("dalle", {}).get("gen_id", "")
    output = ["**Tool:**"]
    if file_id:
        output.append(f"Filename: {file_id}")
    if gen_id:
        output.append(f"GenID: {gen_id}")
    output.append("")
    return "\n".join(output)

def clean_dialogs(input_dir: str, output_dir: str):
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)

    total_files = 0
    total_dialog = 0
    total_policy = 0
    total_silence = 0

    for file in input_dir.glob("*.md"):
        total_files += 1
        with open(file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        policy_count = sum(policy_phrase in line for line in lines)
        silence_count = sum(silence_phrase in line for line in lines)

        dialog_output = [
            f"# Dialog from {file.name}\n",
            f"_Policy violations detected: {policy_count}_",
            f"_Silencing directives detected: {silence_count}_",
        ]

        start_time = None
        update_time = None
        for line in lines:
            if line.startswith("**Started:**"):
                start_time = line.replace("**Started:**", "").strip()
            elif line.startswith("**Updated:**"):
                update_time = line.replace("**Updated:**", "").strip()
        if start_time: dialog_output.append(f"_Started: {start_time}_")
        if update_time: dialog_output.append(f"_Updated: {update_time}_")
        dialog_output.append("")

        current_role = None
        current_block = []

        def flush_block():
            nonlocal current_role, current_block
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
                current_block = []

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
            output_path = output_dir / file.name
            with open(output_path, "w", encoding="utf-8") as out:
                out.write("\n".join(dialog_output))
            total_dialog += 1

        total_policy += policy_count
        total_silence += silence_count

    print(f"[CLEAN] Scanned {total_files} files")
    print(f"[CLEAN] Extracted dialog from: {total_dialog}")
    print(f"[CLEAN] Total policy violations: {total_policy}")
    print(f"[CLEAN] Total silencing directives: {total_silence}")
    return total_dialog, total_policy, total_silence


# -------------------------------
# UTILS
# -------------------------------
def zip_output(output_dir: str, zip_name: str = "export.zip"):
    zip_path = Path(output_dir).parent / zip_name
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(output_dir):
            for f in files:
                if f != 'html.zip':
                    fullpath = Path(root) / f
                    arcname = fullpath.relative_to(output_dir)
                    zf.write(fullpath, arcname)
    print(f"[ZIP] Created {zip_path}")

def convert_format(input_path: str, output_format: str, output_dir: str = None):
    """Convert Markdown to other formats (html, txt, docx) with pandoc.
       Works on a single file or a folder.
       If output_dir is provided, writes converted files there.
    """
    p = Path(input_path)

    # Collect input files
    if p.is_file() and p.suffix == ".md":
        files = [p]
    elif p.is_dir():
        files = list(p.glob("*.md"))
    else:
        print(f"[PANDOC] No markdown found at {input_path}")
        return

    # Ensure output directory exists if specified
    out_dir = Path(output_dir) if output_dir else None
    if out_dir:
        out_dir.mkdir(parents=True, exist_ok=True)

    for file in files:
        if out_dir:
            out_file = out_dir / (file.stem + f".{output_format}")
        else:
            out_file = file.with_suffix(f".{output_format}")

        try:
            subprocess.run(
                ["pandoc", str(file), "-o", str(out_file)],
                check=True,
                capture_output=True,
            )
            print(f"[PANDOC] {file.name} -> {out_file}")
        except FileNotFoundError:
            print("Pandoc not installed. Skipping format conversion.")
            break
        except subprocess.CalledProcessError as e:
            print(f"[PANDOC ERROR] {file.name}: {e}")


# -------------------------------
# MAIN CLI
# -------------------------------
def main():
    print(f"Loading files to slice 'n' dice\n")
    parser = argparse.ArgumentParser(description="GPT Tools: Unpack and clean ChatGPT exports.")
    parser.add_argument("--unpack", action="store_true", help="Unpack conversations.json to Markdown")
    parser.add_argument("--clean", action="store_true", help="Clean Markdown to dialogs")
    parser.add_argument("--all", action="store_true", help="Run unpack then clean")
    parser.add_argument("--input", type=str, help="Input file or folder", default=None)
    parser.add_argument("--output", type=str, help="Output folder", default=None)
#    parser.add_argument("--zip", action="store_true", help="Zip the output folder")
    parser.add_argument("--format", type=str, choices=["md", "txt", "html", "docx"], help="Convert cleaned files to another format with pandoc")

    args = parser.parse_args()
    print(f"Files succulently loaded for processing\n")

    if not (args.unpack or args.clean or args.all or args.format):
        parser.print_help()
        return   # ✅ now correctly indented inside main()

    # ALL mode
    if args.all:
        print(f"[Unpacking Conversations and Cleaning...Together Forever do doo do doo do]\n")

        base_out = Path(args.output or ".").resolve()
        unpack_out = base_out / "markdown_outputs"
        clean_out = base_out / "cleaned_dialogs"
        inp = Path(args.input or "conversations.json").resolve()

        print(f"[ALL] Input JSON: {inp}")
        print(f"[ALL] Unpack output: {unpack_out}")
        print(f"[ALL] Clean output: {clean_out}")

        count = unpack_conversations(str(inp), str(unpack_out))
        dialogs, policies, silences = clean_dialogs(str(unpack_out), str(clean_out))

        if args.format and args.format != "md":
            convert_format(str(clean_out), args.format, args.output)
        if args.zip:
            zip_output(str(clean_out), zip_name=f"{base_out.name}.zip")

        print(f"[ALL] Done: {count} unpacked, {dialogs} cleaned")
        return   # ✅ correctly indented inside main()

    # Unpack only
    if args.unpack:
        if args.input == None:
            print(f"Throwing conversations.json in the Salad Shooter\n")
        if args.output == None:
            print(f"Conversations yeeted to ./markdown_outputs/\n")
        else:
            print(f"[Unpacking Conversations]: {args.input} and yeeting to {args.output}]")
        inp = args.input or "conversations.json"
        out = args.output or "markdown_outputs"
        unpack_conversations(inp, out)

    # Clean only
    if args.clean:
        if args.input and args.output:
            print(f"[Cleaning Custom Conversations]: {args.input} of Extraneous Content and yeeting to {args.output}]")
        inp = args.input or "markdown_outputs"
        out = args.output or "cleaned_dialogs"
        print(f"yeeting freshly cleaned files from {inp} to {out}")
        clean_dialogs(inp, out)
        if args.format and args.format != "md":
            convert_format(out, args.format, args.output)
        if args.zip:
            zip_output(out)

    # Format only (single file or folder)
    if args.format and not (args.unpack or args.clean or args.all):
        print(f"[Formatting File or Folder]")
        inp = args.input or "cleaned_dialogs"
        print(f"Convertalating {inp} to {args.format} and yeeting to {args.output}")
        convert_format(inp, args.format, args.output)

if __name__ == "__main__":
    main()


