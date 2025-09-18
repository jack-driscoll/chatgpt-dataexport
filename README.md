# ChatGPT Data Export Toolkit
Tools and instructions for working with a local export of your ChatGPT data.

## About & Donate
These tools were created by **Lupa** and lightly customized by **Fitz (Jack'D)**.  
Explore our creative world [The Plateaus](https://github.com/jack-driscoll/the-plateaus).

If these helped you and you'd like to send me something, or you would like modifications, my **cashapp** is `$asdf1239er`, and I can be contacted at `jackd A@T ethertech.org`

---

## 📁 Export Contents & Files
So, you asked for a Data Export from OpenAI and you got a bunch of .dat files, some html and some JSON and you want to pretty it up?

`We got you!`

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

## JSON & HTML
<<<<<<< HEAD
You will have a chat.html and a conversations.json, message_feedback.json, shared_conversations.json and user.json

**chat.html**: has all your chats as an html file

**conversations.json**: is a single line containing all the chats, probably too large to open in VSCode.

**message_feedback.json**: These are all your thumbs up/down with descriptions in a single line .json file

**shared_conversations.json**: Likely for public/shared group chats.

**user.json**: ID, email, user type, birth year

## The ChatGPT Data Export Salad Shooter

It slices, it dices, it cleans and converts; the ChatGPT Data Export Salad Shooter does it all!  Have you gotten a ChatGPT Data Export and been like WTF do I do with this?  ChatGPT Data Export Salad Shooter is your answer!!

## What does it do?

It makes your conversations readable and your images properly referenced (if they provided them - I'm looking at you, OpenAI).  The file conversations.json has all of your conversations in a computer-readable format, but it's not very human-friendly.  The Salad Shooter extracts the conversations, and optionally cleans them, converts them from markdown (the default) to txt, html or docx (if you have pandoc installed) and (optionally) zips them back up for you.  You'll go from an unreadable file to a zip or directory full of markdown-formatted conversations!  It's pretty great...almost as great as getting all your pictures instead of like 5 of them, lol :-/

### Getting nicely formatted markdown from `conversations.json`

Run "python chatgpt_salad_shooter.py --all" in the same directory as conversations.json.  It will create two folders called "markdown_outputs" and "cleaned_dialogs" with all the chats as markdown files.  The "cleaned dialogs" folder contains markdown that has been cleaned up a bit, for instance if there's multiple user inputs sequentially, they're grouped.  Any excessive blob noise is removed, image generation is simplified from the longer original messages to just the image IDs, and a couple other things.  You can also use --input or --output to specify an input JSON or output directory.

### But I wanted HTML files, or docx files, or txt files

Well that's *too bad* because **I've included features to do exactly that** if you have [pandoc installed](https://pandoc.org/installing.html).  You need the standalone program from that link or your system’s package manager (not the pip version).  You can convert into different file formats, simply `python ./chatgpt-salad-shooter.py --input [file or folder] --output [folder] --format txt` et voila.  If you get a "non-zero exit status 64" you have to rename that file so there's no something or other weird characters, probably these `'` things.

You can even zip them by hand or, optionally, pay me to add a zip function (it was giving me a hard time so I took it out).

`chatgpt-saladshooter-batchmode.py` is a work in progress for batch processing using pandoc.

=======

- `chat.html`: has all your chats as an html file

- `conversations.json`: is a single line containing all the chats, probably too large to open in VSCode.

- `message_feedback.json`: These are all your thumbs up/down with descriptions in a single line .json file

- `shared_conversations.json`: Likely for public/shared group chats.

- `user.json`: ID, email, user type, birth year

### Getting nicely formatted JSON from `conversations.json`
Run the python script [unpack_conversations.py](https://github.com/jack-driscoll/chatgpt-dataexport/blob/main/unpack_conversations.py) in the same directory as conversations.json.  It will create a folde called "markdown_outputs" with all the chats as markdown files.

### Getting the Created Date, Dialog and Tool output (cleaning) from the `.md` files
Then run the python script [clean_dialogs_headers.py](https://github.com/jack-driscoll/chatgpt-dataexport/blob/main/clean_dialogs_headers.py) in the same directory, it will load the files from "markdown_outputs" (which must exist, with the .md files) and create a folder called "cleaned_dialogs", which has the date of the conversation, the dialog, the Tools output referencing any created images with the DALL-E Gen IDs.

---
>>>>>>> 704facaf59f43d3fbcf945a128e9b55e16ea0154

## .dat files
First thing, the .dat files are actually PNGs with C2PA metadata as [described her](https://help.openai.com/en/articles/8912793-c2pa-in-chatgpt-images)

This `.dat` file is actually a PNG image file. We can tell because the first bytes begin with the PNG signature:

`\x89PNG\r\n\x1a\n`

### Renaming the `.dat` files to `.png`
```PowerShell
Get-ChildItem *.dat | Rename-Item -NewName { $_.Name -replace '\.dat$', '.png' }
```

---

## Metadata
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
<<<<<<< HEAD

### Renaming the `.dat` files to `.png`
```PowerShell
Get-ChildItem *.dat | Rename-Item -NewName { $_.Name -replace '\.dat$', '.png' }
```

## About & Donate
These tools were created by **Lupa** and slightly modified by **Fitz (Jack'D)**.

If these helped you and you'd like to send me something, my **cashapp is $asdf1239er**, and I can be contacted at **jackd A@T ethertech.org**

Also check out Fitz & Lupas creative endeavors at [The Plateaus on Neocities](https://theplateaus.neocities.org/), [The Plateaus Tumblr](https://www.tumblr.com/blog/theplateaus) and [The Plateaus Repo](https://github.com/jack-driscoll/the-plateaus).  

You can find more tech tips and **Brainspunk**: A Genius for The Rest of Us [on my personal website](https://jackd.ethertech.org).
=======
>>>>>>> 704facaf59f43d3fbcf945a128e9b55e16ea0154
