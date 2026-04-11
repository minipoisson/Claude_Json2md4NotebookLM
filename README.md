# Claude Json2md for NotebookLM

![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/github/license/minipoisson/Claude_Json2md4NotebookLM)
[![Release](https://img.shields.io/github/v/release/minipoisson/Claude_Json2md4NotebookLM)](https://github.com/minipoisson/Claude_Json2md4NotebookLM/releases)

This script converts Claude's exported `conversations.json` into sequential Markdown files (e.g. `Claude_History-00.md`) that are easy to import into NotebookLM.

A companion tool to [Gemini_Json2md4NotebookLM](https://github.com/minipoisson/Gemini_Json2md4NotebookLM), sharing the same design philosophy.

[日本語版READMEはこちら](README.ja.md)

## Features

- Removes HTML tags and formats conversations as clean Markdown
- Automatically splits output files to stay within NotebookLM's ingestion limit (default: 1 MB)
- Supports incremental updates via `last_entry_time.txt` — only new conversations are processed on subsequent runs

## Dependencies

No external dependencies required (Python Standard Library only)

## Requirements

- Python 3.9 or higher

## Usage

### 1. Export your Claude chat history

Go to [claude.ai/settings/privacy](https://claude.ai/settings/privacy) and request a data export.  
You will receive a download link by email (typically within minutes to a few days).  
Extract the ZIP and locate `conversations.json`.

### 2. Place the file

Put `conversations.json` in the same directory as this script.

### 3. Run the script

```bash
python convert_claude_history.py [--input_file FILE] [--output_file FILE] [--limit SIZE]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--input_file` | `conversations.json` | Path to the exported JSON file |
| `--output_file` | `Claude_History.md` | Base name for output Markdown files |
| `--limit` | `1000000` | Max bytes per file before splitting |

Example:

```bash
python convert_claude_history.py --input_file conversations.json --output_file Claude_History.md --limit 1000000
```

### 4. Upload to NotebookLM

Upload the generated `Claude_History-00.md`, `-01.md`, ... files as sources in your NotebookLM notebook.

## Notes

- The default `--limit` is set to **1,000,000 bytes** (1 MB). The author found that 1.5 MB occasionally caused ingestion failures in NotebookLM.
- On the first run, all conversations are processed. On subsequent runs, only conversations updated after the last run are appended (incremental update).
- If the JSON structure of your export differs from expected (e.g. field names changed), inspect the keys with:  
  ```bash
  python -c "import json; d=json.load(open('conversations.json')); print(list(d[0].keys())); print(list(d[0]['chat_messages'][0].keys()))"
  ```

## Combining with Gemini History

By loading both Claude and Gemini history into the same NotebookLM notebook, cross-AI analysis becomes possible — for example, tracing how a hallucination in Gemini was detected and verified through a separate Claude conversation.

This cross-AI use case is the primary motivation for this tool existing independently of any official Google product.

## License

MIT License. See [LICENSE](LICENSE) for details.
