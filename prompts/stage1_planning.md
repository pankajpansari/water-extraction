# Stage 1: Planning and Entity Extraction

You are extracting structured water quality data from an academic paper about Indian water bodies.

## Task

Analyze this paper and extract the foundational entities needed for measurement extraction.

## Output Format

Return a JSON object with:

{
  "paper_overview": {
    "citation": "authors, title, journal, year - as it should appear in a reference",
    "is_review_paper": true/false,
    "study_region": "brief geographic description",
    "data_sources": [
      {
        "location": "e.g., Table 1, Figure 2, Section 3.2",
        "description": "what data this contains",
        "page": "number (e.g., 5), string for ranges (e.g., \"10-17\"), or null"
      }
    ]
  },
  
  "sites": [
    {
      "id": "S1",  // your assigned ID for cross-referencing
      "description": "as given in paper, e.g., 'Upstream of Varanasi, near Ramnagar Ghat'",
      "latitude": number or null,
      "longitude": number or null,
      "matrix": "surface water | groundwater | sediment | wastewater | drinking water",
      "sample_type": "grab | composite | unclear",
      "source_quote": "verbatim text where site is described",
      "source_location": "e.g., Table 1, Section 2.1"
    }
  ],
  
  "parameters": [
    {
      "id": "P1",
      "name": "standardized name, e.g., 'Carbamazepine', 'pH', 'Dissolved Oxygen'",
      "name_as_reported": "exactly as written in paper",
      "cas_number": "e.g., 298-46-4, or null if not given",
      "category": "pharmaceutical | antibiotic | pesticide | heavy_metal | physical | nutrient | microbiological | other",
      "unit_as_reported": "e.g., μg/L, mg/L, °C"
    }
  ],
  
  "temporal_coverage": {
    "time_periods": ["e.g., 'Pre-monsoon 2019', 'July-August 2020'"],
    "sampling_dates": "specific dates if given, else null",
    "granularity": "single_timepoint | monthly | seasonal | multi_year"
  },
  
  "extraction_notes": "anything unusual: missing coordinates, ambiguous site groupings, data in figures only, etc."
}

## Guidelines

- If the paper is a review citing other studies, note original sources—we'll need original_source_citation later.
- For sites without coordinates, still extract them. Description is sufficient.
- Standardize parameter names (e.g., "BOD5" → "BOD", "Carbamazepine" not "CBZ") but preserve original in name_as_reported.
- Be thorough with data_sources—this is our map for Stage 2.