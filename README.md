# Gemini Takeout Recovery Tool

Standalone Python tool to recover, chronologicalize, and structure Google Takeout chat exports (`MyActivity.json`). 

This utility transforms large session histories into clean, hierarchically structured Markdown documents and automatically isolates embedded source code blocks into modular files.

---

## Background

Extensive development sessions in browser-based AI workspaces eventually hit client-side memory limits:
* **Error 1013:** Session payload overload and Document Object Model (DOM) rendering stops.
* **Error (1):** Immediate cessation of the virtual rendering thread when handling massive conversation histories.

Standard browser workarounds (reloading with `Ctrl + F5`, clearing cache, or opening incognito sessions) focus on local browser storage, whereas the root cause resides in the massive payload volume delivered to the client renderer.

This tool provides a reliable path to full data sovereignty. It processes the raw JSON export directly from Google Takeout, reconstructs the timeline, and produces clean Markdown alongside standalone code files.

---

## Core Features

* **Complete Data Autonomy:** Runs entirely locally on your machine using only the Python standard library. Zero external dependencies.
* **Deterministic Chronology:** Restores the exact temporal sequence from ISO timestamps.
* **Automated Code Extraction:** Detects embedded languages (`Python`, `TypeScript`, `JavaScript`, `HTML`, `CSS`, `JSON`, `Shell`, `LaTeX`) and saves each snippet into dedicated files.
* **Structured Markdown Output:** Generates a unified, easily searchable document for reference archives and documentation.

---

## Workflow

### 1. Download Google Takeout Data

1. Open [takeout.google.com](https://takeout.google.com).
2. Select **Deselect all** at the top of the product list.
3. Scroll down and check exclusively **Gemini Apps**.
4. Confirm **JSON** as the export format.
5. Create the export and download the resulting archive.
6. Extract the archive; your target file is `MeineAktivitäten.json`.

---

### 2. Execution

Place `MyActivity.json` in the same directory as `recover_takeout.py` and run:

```bash
python recover_takeout.py
