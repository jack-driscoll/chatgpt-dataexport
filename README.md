# ChatGPT Data Export Toolkit

Tools and instructions for working with a local export of your ChatGPT data.

---

## 📁 Export Contents & Files
So, you asked for a Data Export from OpenAI and you got a bunch of .dat files, some html and some JSON and you want to pretty it up?
We got you!

When you download your data from ChatGPT, you'll get:

- `conversations.json` – All chat history (structured JSON)
- `shared_conversations.json` – Chats you shared via link
- `user.json` – Account metadata
- `tool_messages.json` – Tool-related responses and metadata
- `.dat` files – Downloaded assets (usually images, mislabeled as `.dat`)
- `.png` files – Sometimes image exports are already labeled
- `.jpg` files - any images you've uploaded


---

## 🎯 Goals

- Make `.json` content human-readable
- Recover `.dat` images
- Extract real dialog from assistant/user
- Preserve timestamps and tool metadata
- Optionally tally policy violations or silencing directives

---

## .dat files
First thing, the .dat files are actually PNGs with C2PA metadata as described here ( https://help.openai.com/en/articles/8912793-c2pa-in-chatgpt-images )

This `.dat` file is actually a PNG image file. We can tell because the first bytes begin with the PNG signature:

\x89PNG\r\n\x1a\n

### Metadata
It looks like the file also contains embedded metadata, possibly related to content provenance or generative origin. I see tags like:

    c2pa — likely referring to C2PA (Coalition for Content Provenance and Authenticity)

    GPT-4o and OpenAI API — indicating this image was generated or modified using OpenAI's tools

    digitalSourceType and softwareAgent — suggesting attribution metadata from a content generation process
	
### 🔍 File Origin & Attribution (C2PA Metadata)

This image uses the C2PA (Content Authenticity Initiative) standard to encode origin and modification data. It shows:

    Created by: GPT-4o

    Converted with: OpenAI API

    Software Agent: ChatGPT via Truepic Lens CLI

### 🧾 C2PA Identifiers and Assertions

    Unique provenance tag:
    urn:c2pa::[REDACTED UNIQUE ID]
    (A specific content claim record)

    Metadata includes:

        c2pa.assertions — Describes actions taken (e.g., creation, conversion)

        c2pa.hash.data — Cryptographic hash of the file for integrity

        c2pa.signature — Digital signature validating the file's authenticity

        c2pa.thumbnail.ingredient.jpeg — Possibly a preview image or source fragment

        c2pa.ingredient.v3 — Suggests layered provenance (e.g., remix or modification lineage)

### ✅ Validation Messages Present

    "claim signature valid"

    "data hash valid"

    "hashed URI matched"

These confirm the image passed integrity checks and hasn’t been altered post-creation.
### 🧠 Key Strings of Interest

    dnamefGPT-4o

    OpenAI API

    ChatGPT

    Truepic Lens CLI

    c2pa_rsf0.48.2 (possibly a reference to a C2PA manifest version or framework)

### Renaming the `.dat` files to `.png`
```PowerShell
Get-ChildItem *.dat | Rename-Item -NewName { $_.Name -replace '\.dat$', '.png' }
```

## JSON & HTML
You will have a chat.html and a conversations.json, message_feedback.json, shared_conversations.json and user.json

**chat.html**: has all your chats as an html file

**conversations.json**: is a single line containing all the chats, probably too large to open in VSCode.

**message_feedback.json**: These are all your thumbs up/down with descriptions in a single line .json file

**shared_conversations.json**: Likely for public/shared group chats.

**user.json**: ID, email, user type, birth year

### Getting nicely formatted JSON from `conversations.json`
Run "python unpack_conversations.py" in the same directory as conversations.json.  It will create a folde called "markdown_outputs" with all the chats as markdown files.

### Getting the Created Date, Dialog and Tool output (cleaning) from the `.md` files
Then run "python clean_dialogs_headers.py" in the same directory, it will load the files from "markdown_outputs" (which must exist, with the .md files) and create a folder called "cleaned_dialogs", which has the date of the conversation, the dialog, the Tools output referencing any created images with the DALL-E Gen IDs.

## About
These tools were created by **Lupa** and slightly modified by **Fitz (Jack'D)**.

If these helped you and you'd like to send me something, my **cashapp is $asdf1239er**, and I can be contacted at **jackd A@T ethertech.org**