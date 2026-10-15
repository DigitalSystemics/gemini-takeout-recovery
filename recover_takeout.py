#!/usr/bin/env python3
"""
Gemini Takeout Recovery Tool
Transforms Google Takeout chat exports into chronological Markdown
and isolates embedded source code blocks into standalone files.
"""

import json
import re
import sys
from pathlib import Path
from datetime import datetime


def parse_timestamp(raw_timestamp: str) -> str:
    """Standardizes ISO timestamps into readable UTC strings."""
    try:
        dt = datetime.fromisoformat(raw_timestamp.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    except Exception:
        return raw_timestamp


def extract_code_blocks(content: str, entry_index: int, code_dir: Path) -> list:
    """Isolates fenced code blocks and writes them to standalone files."""
    pattern = r"```([a-zA-Z0-9_-]+)?\n(.*?)```"
    matches = list(re.finditer(pattern, content, re.DOTALL))
    extracted_files = []

    extension_map = {
        "python": "py",
        "py": "py",
        "javascript": "js",
        "js": "js",
        "typescript": "ts",
        "ts": "ts",
        "html": "html",
        "css": "css",
        "json": "json",
        "markdown": "md",
        "md": "md",
        "bash": "sh",
        "sh": "sh",
        "xml": "xml",
        "latex": "tex",
        "tex": "tex"
    }

    for block_index, match in enumerate(matches, 1):
        language = (match.group(1) or "txt").lower()
        code_body = match.group(2)
        extension = extension_map.get(language, language if len(language) <= 4 else "txt")
        filename = f"snippet_{entry_index:04d}_{block_index:02d}.{extension}"
        filepath = code_dir / filename
        
        with open(filepath, "w", encoding="utf-8") as file_out:
            file_out.write(code_body.strip() + "\n")
        
        extracted_files.append((filename, language))

    return extracted_files


def run_recovery(source_path: Path, output_dir: Path):
    """Executes the complete reconstruction pipeline."""
    if not source_path.exists():
        print(f"Error: Source file not found: {source_path}")
        sys.exit(1)

    print(f"Reading source data: {source_path} ...")
    with open(source_path, "r", encoding="utf-8") as file_in:
        raw_data = json.load(file_in)

    if not isinstance(raw_data, list):
        print("Error: Input structure is not a JSON array.")
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)
    code_dir = output_dir / "code_snippets"
    code_dir.mkdir(exist_ok=True)

    markdown_file = output_dir / "recovered_project.md"
    
    # Sort chronologically by timestamp
    sorted_records = sorted(raw_data, key=lambda item: item.get("time", ""))

    print(f"Processing {len(sorted_records)} records ...")

    total_code_files = 0

    with open(markdown_file, "w", encoding="utf-8") as md:
        md.write("# Project Reconstruction Archive\n\n")
        md.write(f"- **Source File:** `{source_path.name}`\n")
        md.write(f"- **Extraction Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        md.write(f"- **Total Interactions:** {len(sorted_records)}\n\n")
        md.write("---\n\n")

        for index, record in enumerate(sorted_records, 1):
            raw_time = record.get("time", "Unknown Timestamp")
            formatted_time = parse_timestamp(raw_time)
            title = record.get("title", "")
            
            subtitles = record.get("subtitles", [])
            messages = [sub.get("name", "") for sub in subtitles if "name" in sub]
            
            interaction_text = "\n\n".join(messages) if messages else title

            md.write(f"## [{index:04d}] {formatted_time}\n\n")
            if title and messages:
                md.write(f"**Context:** {title}\n\n")

            md.write(f"{interaction_text}\n\n")

            code_artefacts = extract_code_blocks(interaction_text, index, code_dir)
            if code_artefacts:
                total_code_files += len(code_artefacts)
                md.write("**Extracted Source Code:**\n")
                for filename, lang in code_artefacts:
                    md.write(f"- [`{filename}`](./code_snippets/{filename}) *({lang})*\n")
                md.write("\n")

            md.write("---\n\n")

    print("\nRecovery successfully completed:")
    print(f"- Documentation: {markdown_file}")
    print(f"- Standalone code files: {total_code_files} files in {code_dir}")


def find_default_source() -> Path:
    """Detects available Takeout JSON files automatically."""
    candidates = [
        Path("MyActivity.json"),
        Path("MeineAktivitaeten.json"),
        Path("MeineAktivitäten.json")
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


if __name__ == "__main__":
    source_file = find_default_source()
    target_directory = Path("recovery_output")

    if len(sys.argv) > 1:
        source_file = Path(sys.argv[1])
    if len(sys.argv) > 2:
        target_directory = Path(sys.argv[2])

    run_recovery(source_file, target_directory)
