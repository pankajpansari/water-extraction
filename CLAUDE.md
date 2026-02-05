# Water Quality Extraction Pipeline

## Goal
Extract water quality measurements from academic PDFs into a SQLite database.

## Two-stage pipeline
1. **Stage 1 (Planning):** PDF → paper structure, sites, parameters, temporal coverage
2. **Stage 2 (Extraction):** Stage 1 output + PDF → individual measurements with source quotes

Prompts are in `prompts/`. Stage 2 prompt has `{{stage1_output}}` placeholder.

## Key files
- `schema.sql` - target database schema (flat measurements table)
- `prompts/stage1_planning.md` - entity extraction prompt
- `prompts/stage2_extraction.md` - measurement extraction prompt
- `data/pdfs/` - input papers

## API
Using Anthropic Claude API with PDF support. Expect structured JSON output.

## Design notes
- `source_quote` field captures verbatim text for verification
- `source_location` tracks where in paper (e.g., "Table 2") data came from
- Handle censored data: ND/BDL values use limit_qualifier and detection_limit fields