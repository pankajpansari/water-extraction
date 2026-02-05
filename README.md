# Water Quality Extraction Pipeline

Two-stage pipeline that extracts water quality measurements from academic PDFs into a SQLite database using Claude.

## Overview
- Stage 1 (Planning) extracts paper structure, sites, parameters, and temporal coverage.
- Stage 2 (Extraction) converts those entities into individual measurement records.
- Outputs are saved as JSON and inserted into a flat `measurements` table.

## Requirements
- Python 3.10+ (recommended)
- An Anthropic API key available as `ANTHROPIC_API_KEY`

## Quick Start
1. Install dependencies:
   `pip install anthropic`
1. Run the pipeline on a PDF:
   `python src/extract.py data/sample/vaid_2022.pdf`

## Outputs
- JSON outputs are written to `data/outputs/`:
  `*_stage1.json` and `*_stage2.json`
- SQLite database (default):
  `data/water_quality.db`

## Database Schema
The schema lives in `schema.sql` and stores a denormalized measurement record per row, including:
- Paper citation and source location
- Site description and coordinates
- Parameter identity and category
- Temporal coverage
- Values (raw, mean, range, std dev, n)
- Censored data handling (limit qualifier, detection limit)

## Project Structure
- `src/extract.py` main pipeline script
- `prompts/` Stage 1 and Stage 2 prompts
- `schema.sql` SQLite schema
- `data/sample/` sample PDF and example outputs

## Notes
- If the model response is invalid JSON, the raw response is saved to `data/debug_response.txt`.
- For review papers, Stage 2 records can include `original_source_citation`.
