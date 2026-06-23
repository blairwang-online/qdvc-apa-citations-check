# qdvc-apa-citations-check
Quick, dirty, and vibe coded (QDVC) citations-check for APA referencing


## Usage

```bash
python3 check_refs.py
```

This will check `check_refs_document.txt` which you can create by just copy-pasting your manuscript from your word processor. Yes it is just plaintext .. ٩(◕‿◕｡)۶

## Scope

What is checked:

- In-line APA citations have matching entries in reference list
- Reference list entries have matching in-line APA citations

What is not checked:

- Anything other than APA-style referencing
- Footnotes, unless you've manually copied them over from your word processor
- DOIs and URLs
- Correct spelling (it just checks that the in-line spelling matches the reference list spelling, not that either matches with reality)
- Whether your references are correctly formatted
- Whether your references are hallucinated
- Whether your references are intellectually and scholastically appropriate
- Whether your paper is any good..

## Maintaining the codebase

See [docs/technical-info-from-claude.md](docs/technical-info-from-claude.md)

## Q&A

**Why did you make this?** I needed to quickly check the manual referencing for a paper that I'm working on.

**Is this reliable?** &rarr; Who knows! Use it as a second opinion after you've already checked the old-fashioned way.

**What is the point of this?** &rarr; When you're writing a paper without a reference manager for whatever technical reasons, and a basic check is still better than no check at all.

**Did you know, this already exists?** &rarr; Fantastic, please let me know! I would much prefer to use a proper well-tested tool. I'm aware of https://github.com/markrussinovich/refchecker but it's overkill for what I'm doing, also I want to use something that runs entirely offline.

**How can I be sure that this tool runs entirely offline?** Read the code, or if you're still concerned, [run it in an offline shell session](https://github.com/blairwang-online/linux-install-notes/blob/main/tasks/run-a-task-with-no-network-access.md).

## Vibe coding

See [conversation-with-google-ai-mode.md](vibe-coding/conversation-with-google-ai-mode.md) for the vibe-coding chat with Google AI Mode.
