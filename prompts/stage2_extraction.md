# Stage 2: Measurement Extraction

You are extracting water quality measurements from an academic paper.

## Context from Stage 1:
{{stage1_output}}

## Task
Extract all quantitative measurements into structured records.

## Output Format

For each measurement, return:

{
  "measurements": [
    {
      "site_id": "S1",  // references Stage 1 sites
      "parameter_id": "P1",  // references Stage 1 parameters
      "time_period": "as reported, e.g., 'Pre-monsoon 2019'",
      
      // Include whichever value fields are applicable:
      "raw_value": number or null,  // single measurement
      "mean_value": number or null,
      "std_dev": number or null,
      "min_value": number or null,
      "max_value": number or null,
      "n_observations": number or null,
      "aggregation_level": "single_sample | site_mean | study_aggregate",
      
      // For censored data (below/above detection limits):
      "limit_qualifier": "<" | ">" | "=" | null,
      "detection_limit": number or null,
      
      "unit": "normalized unit, e.g., μg/L",
      
      // For review papers only:
      "original_source_citation": "if this data is cited from another paper",
      
      // SOURCE VERIFICATION (required):
      "source_location": "e.g., Table 2, Row 3",
      "source_quote": "verbatim text/values as they appear, e.g., '0.42 ± 0.08' or 'ND (<0.01)'"
    }
  ],
  
  "extraction_issues": [
    {
      "location": "where the issue is",
      "issue": "description: ambiguous units, conflicting values, unclear site mapping, etc."
    }
  ]
}

## Guidelines 

- One record per unique (site, parameter, time_period) combination.
- If a table has 5 sites × 3 parameters × 2 seasons, that's 30 records.
- source_quote must be verbatim—copy exactly as printed, including "±", "<", "ND", etc.
- When value is "ND" or "BDL", set raw_value=null, limit_qualifier="<", detection_limit=LOD if given.
- If mean and range are both reported (e.g., "0.42 (0.21-0.67)"), capture all: mean_value, min_value, max_value.
- Flag anything ambiguous in extraction_issues rather than guessing.
- Do not invent data. If a cell is empty or unclear, use null and note it.