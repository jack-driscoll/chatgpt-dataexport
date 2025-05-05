import json
import os
import re
from datetime import datetime

# Load the list of conversations
with open("conversations.json", "r", encoding="utf-8") as f:
    conversations = json.load(f)
    print(f"Loaded {len(conversations)} conversations.")

os.makedirs("markdown_outputs", exist_ok=True)

for convo in conversations:
    title = convo.get("title", "Untitled Conversation")
    safe_title = re.sub(r'[\\/*?:"<>|]', "_", title)
    filename = f"markdown_outputs/{safe_title}.md"

    create_time = datetime.fromtimestamp(convo["create_time"]).strftime("%Y-%m-%d %H:%M:%S")
    update_time = datetime.fromtimestamp(convo["update_time"]).strftime("%Y-%m-%d %H:%M:%S")
    mapping = convo["mapping"]

    # Find the root message (parent is None)
    root_id = next((k for k, v in mapping.items() if v["parent"] is None), None)

    # Traverse and collect messages
    messages = []

    print(f"Processing: {title}")
    print(f"Root ID: {root_id}")
    def follow_chain(node_id):
        node = mapping.get(node_id)
        if node and node.get("message"):
            msg = node["message"]
            role = msg["author"]["role"]
            content = msg.get("content", {})
            parts = content.get("parts", [])
            #parts = node["message"]["content"]["parts"]
            for part in parts:
                messages.append((role, part))
        for child_id in node.get("children", []):
            follow_chain(child_id)

    if root_id:
        follow_chain(root_id)

    # Write to file
    lines = [f"# {title}\n", f"**Started:** {create_time}", f"**Updated:** {update_time}", ""]
    for role, part in messages:
        if isinstance(part, str):
            lines.append(f"**{role.capitalize()}:** {part.strip()}\n")
        else:
            # fallback: JSON dump for complex content
            lines.append(f"**{role.capitalize()}:** {json.dumps(part, indent=2)}\n")

    with open(filename, "w", encoding="utf-8") as out:
        out.write("\n".join(lines))

# LUPA & FETZ 2025
