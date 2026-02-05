CREATE TABLE measurements (
    measurement_id INTEGER PRIMARY KEY AUTOINCREMENT,

    paper_citation TEXT,
    original_source_citation TEXT, -- for review papers
    source_location TEXT,          -- e.g., 'Table 2', 'Abstract', 'Fig 3'

    -- Site info
    site_description TEXT,
    latitude REAL,                 -- NULLABLE
    longitude REAL,                -- NULLABLE

    -- Chemical Identity
    parameter_name TEXT NOT NULL,
    cas_number TEXT,               -- NULLABLE, e.g., '298-46-4'

    -- Taxonomy
    category TEXT,                 -- 'pharmaceutical', 'physical', etc.
    matrix TEXT,                   -- e.g. 'surface water', 'sediment'
    sample_type TEXT,              -- e.g. 'grab', 'composite'

    -- Temporal
    time_period TEXT,              -- e.g. 'Pre-monsoon', 'July 2024'
    time_granularity TEXT,         -- 'monthly', 'multi-year'

    -- Values
    raw_value REAL,                -- NULLABLE
    mean_value REAL,               -- NULLABLE
    std_dev REAL,                  -- NULLABLE
    min_value REAL,                -- NULLABLE
    max_value REAL,                -- NULLABLE
    n_observations INTEGER CHECK (n_observations >= 0),

    aggregation_level TEXT,        -- 'Site level', 'Study aggregate'

    -- Censored Data Handling
    limit_qualifier TEXT CHECK (limit_qualifier IN ('<', '>', '=') OR limit_qualifier IS NULL),
    detection_limit REAL,          -- NULLABLE

    unit TEXT,
    notes TEXT
);
