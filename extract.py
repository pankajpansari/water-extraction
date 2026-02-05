#!/usr/bin/env python3
"""
Water Quality Extraction Pipeline

Two-stage extraction:
1. Stage 1: PDF → paper structure, sites, parameters, temporal coverage
2. Stage 2: Stage 1 output + PDF → individual measurements

Usage:
    python extract.py path/to/paper.pdf
"""

import argparse
import base64
import json
import sqlite3
import sys
from pathlib import Path

import anthropic


def load_pdf_as_base64(pdf_path: Path) -> str:
    """Load PDF file and encode as base64."""
    with open(pdf_path, "rb") as f:
        return base64.standard_b64encode(f.read()).decode("utf-8")


def load_prompt(prompt_name: str) -> str:
    """Load a prompt from the prompts directory."""
    prompt_path = Path(__file__).parent / "prompts" / prompt_name
    return prompt_path.read_text()


def call_claude_with_pdf(
    client: anthropic.Anthropic,
    pdf_base64: str,
    prompt: str,
    model: str = "claude-opus-4-5-20251101",
) -> str:
    """Call Claude API with a PDF document and prompt using streaming."""
    # Use streaming for large responses
    response_text = ""
    with client.messages.stream(
        model=model,
        max_tokens=64000,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "document",
                        "source": {
                            "type": "base64",
                            "media_type": "application/pdf",
                            "data": pdf_base64,
                        },
                    },
                    {
                        "type": "text",
                        "text": prompt,
                    },
                ],
            }
        ],
    ) as stream:
        for text in stream.text_stream:
            response_text += text

    return response_text


def parse_json_response(response: str) -> dict:
    """Extract JSON from Claude's response, handling markdown code blocks."""
    text = response.strip()

    # Handle markdown code blocks
    if text.startswith("```"):
        lines = text.split("\n")
        # Remove first line (```json or ```) and last line (```)
        lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines)

    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        # Save the problematic response for debugging
        debug_path = Path("data/debug_response.txt")
        debug_path.parent.mkdir(parents=True, exist_ok=True)
        debug_path.write_text(f"Error: {e}\n\nRaw response:\n{response}")
        print(f"JSON parse error. Raw response saved to {debug_path}", file=sys.stderr)
        raise


def run_stage1(client: anthropic.Anthropic, pdf_base64: str) -> dict:
    """Run Stage 1: Planning and Entity Extraction."""
    prompt = load_prompt("stage1_planning.md")
    response = call_claude_with_pdf(client, pdf_base64, prompt)
    return parse_json_response(response)


def run_stage2(client: anthropic.Anthropic, pdf_base64: str, stage1_output: dict) -> dict:
    """Run Stage 2: Measurement Extraction."""
    prompt_template = load_prompt("stage2_extraction.md")
    prompt = prompt_template.replace("{{stage1_output}}", json.dumps(stage1_output, indent=2))
    response = call_claude_with_pdf(client, pdf_base64, prompt)
    return parse_json_response(response)


def init_database(db_path: Path) -> sqlite3.Connection:
    """Initialize SQLite database with schema."""
    conn = sqlite3.connect(db_path)
    schema_path = Path(__file__).parent / "schema.sql"
    conn.executescript(schema_path.read_text())
    return conn


def insert_measurements(
    conn: sqlite3.Connection,
    stage1: dict,
    stage2: dict,
) -> int:
    """Insert measurements into database, denormalizing site/parameter info."""
    # Build lookup dicts from stage1
    sites_by_id = {s["id"]: s for s in stage1.get("sites", [])}
    params_by_id = {p["id"]: p for p in stage1.get("parameters", [])}
    paper_citation = stage1.get("paper_overview", {}).get("citation", "")

    cursor = conn.cursor()
    inserted = 0

    for m in stage2.get("measurements", []):
        site = sites_by_id.get(m.get("site_id"), {})
        param = params_by_id.get(m.get("parameter_id"), {})

        cursor.execute(
            """
            INSERT INTO measurements (
                paper_citation,
                original_source_citation,
                source_location,
                site_description,
                latitude,
                longitude,
                parameter_name,
                cas_number,
                category,
                matrix,
                sample_type,
                time_period,
                time_granularity,
                raw_value,
                mean_value,
                std_dev,
                min_value,
                max_value,
                n_observations,
                aggregation_level,
                limit_qualifier,
                detection_limit,
                unit,
                notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                paper_citation,
                m.get("original_source_citation"),
                m.get("source_location"),
                site.get("description"),
                site.get("latitude"),
                site.get("longitude"),
                param.get("name"),
                param.get("cas_number"),
                param.get("category"),
                site.get("matrix"),
                site.get("sample_type"),
                m.get("time_period"),
                stage1.get("temporal_coverage", {}).get("granularity"),
                m.get("raw_value"),
                m.get("mean_value"),
                m.get("std_dev"),
                m.get("min_value"),
                m.get("max_value"),
                m.get("n_observations"),
                m.get("aggregation_level"),
                m.get("limit_qualifier"),
                m.get("detection_limit"),
                m.get("unit"),
                m.get("source_quote"),  # Store source_quote in notes for verification
            ),
        )
        inserted += 1

    conn.commit()
    return inserted


def save_json_output(data: dict, output_path: Path) -> None:
    """Save JSON output to file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="Extract water quality measurements from academic PDFs"
    )
    parser.add_argument("pdf_path", type=Path, help="Path to the PDF file")
    parser.add_argument(
        "--db",
        type=Path,
        default=Path("data/water_quality.db"),
        help="Path to SQLite database (default: data/water_quality.db)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/outputs"),
        help="Directory for JSON outputs (default: data/outputs)",
    )
    args = parser.parse_args()

    if not args.pdf_path.exists():
        print(f"Error: PDF not found: {args.pdf_path}", file=sys.stderr)
        sys.exit(1)

    # Initialize
    client = anthropic.Anthropic()
    pdf_base64 = load_pdf_as_base64(args.pdf_path)
    pdf_stem = args.pdf_path.stem

    print(f"Processing: {args.pdf_path.name}")

    # Stage 1: Planning
    print("Running Stage 1 (Planning)...")
    stage1_output = run_stage1(client, pdf_base64)
    stage1_path = args.output_dir / f"{pdf_stem}_stage1.json"
    save_json_output(stage1_output, stage1_path)
    print(f"  Saved: {stage1_path}")
    print(f"  Found {len(stage1_output.get('sites', []))} sites, {len(stage1_output.get('parameters', []))} parameters")

    # Stage 2: Extraction
    print("Running Stage 2 (Extraction)...")
    stage2_output = run_stage2(client, pdf_base64, stage1_output)
    stage2_path = args.output_dir / f"{pdf_stem}_stage2.json"
    save_json_output(stage2_output, stage2_path)
    print(f"  Saved: {stage2_path}")
    print(f"  Extracted {len(stage2_output.get('measurements', []))} measurements")

    # Database insertion
    print("Inserting into database...")
    args.db.parent.mkdir(parents=True, exist_ok=True)
    conn = init_database(args.db)
    inserted = insert_measurements(conn, stage1_output, stage2_output)
    conn.close()
    print(f"  Inserted {inserted} records into {args.db}")

    # Report any extraction issues
    issues = stage2_output.get("extraction_issues", [])
    if issues:
        print(f"\nExtraction issues ({len(issues)}):")
        for issue in issues:
            print(f"  - {issue.get('location')}: {issue.get('issue')}")

    print("\nDone!")


if __name__ == "__main__":
    main()
