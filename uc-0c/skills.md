skills:
  - name: load_dataset
    description: Reads ward_budget.csv, validates required columns, and returns the dataset together with a null report listing every blank actual_spend row before any computation proceeds.
    input:
      type: file
      format: CSV
      path: string — absolute or relative path to ward_budget.csv (e.g. ../data/budget/ward_budget.csv)
      required_columns:
        - period
        - ward
        - category
        - budgeted_amount
        - actual_spend
        - notes
      notes: 300 rows expected — 5 wards, 5 categories, 12 months (2024-01 through 2024-12); 5 deliberate null actual_spend values
    output:
      type: dict
      fields:
        - rows: list — all parsed CSV rows as dicts with period, ward, category, budgeted_amount, actual_spend (float or null), notes
        - null_report: list — each item contains {period, ward, category, notes} for every row where actual_spend is blank or null
        - null_count: integer — total number of null actual_spend rows (must be 5 for the reference dataset)
      notes: null_report must be produced before returning — compute_growth must not be called until null rows are identified
    error_handling:
      - "if file path does not exist: raise FileNotFoundError with the full attempted path — do not proceed"
      - "if file exists but cannot be parsed as CSV: raise ValueError stating the file is not valid CSV — do not proceed"
      - "if any required column (period, ward, category, budgeted_amount, actual_spend, notes) is absent from the CSV header: raise ValueError naming the missing column — do not proceed"
      - "if the file parses but contains zero data rows: raise ValueError stating the dataset is empty — do not proceed"
      - "if actual_spend is blank on any row: include that row in null_report with period, ward, category, and notes — do not drop, impute, or coerce blank values to zero"
      - "if a row has null actual_spend but an empty notes field: still include the row in null_report with notes set to empty string — do not skip it"
      - "if the caller requests aggregation across all wards or all categories at load time: refuse with an error stating that load_dataset returns raw rows only and aggregation requires explicit per-ward per-category scoping"

  - name: compute_growth
    description: Takes a loaded dataset plus ward, category, and growth_type, and returns a per-period table with actual spend, growth result, and formula shown — flagging null rows without computing growth for them.
    input:
      type: dict
      fields:
        - rows: list — dataset rows as returned by load_dataset
        - null_report: list — null rows as returned by load_dataset
        - ward: string — exact ward name (e.g. Ward 1 – Kasba)
        - category: string — exact category name (e.g. Roads & Pothole Repair)
        - growth_type: string — MoM | YoY (required; must not be omitted or guessed)
    output:
      type: file
      format: CSV
      path: string — output file path (e.g. growth_output.csv)
      columns:
        - period
        - ward
        - category
        - actual_spend
        - growth_pct
        - formula
        - null_flag
        - null_reason
      notes: per-period table for one ward and one category only — not a single aggregated number; formula column must be populated on every row where growth_pct is computed
    error_handling:
      - "if growth_type is missing, empty, or None: refuse with an error asking the caller to specify MoM or YoY — do not default to either formula"
      - "if growth_type is not MoM or YoY: raise ValueError naming the unsupported value — do not proceed"
      - "if ward is missing or does not match any row in the dataset: raise ValueError naming the invalid ward — do not fall back to another ward"
      - "if category is missing or does not match any row for the specified ward: raise ValueError naming the invalid category — do not fall back to another category"
      - "if the caller requests growth across all wards or all categories without specifying both ward and category: refuse with an error stating per-ward per-category granularity is required"
      - "if a period's actual_spend is null: set null_flag to TRUE, copy null_reason from the notes column, leave growth_pct and formula blank — do not compute growth for that period"
      - "if growth cannot be computed because the comparison period's actual_spend is null (e.g. MoM after a null month): set growth_pct to NOT_COMPUTED, include the formula that would have been used, and note which comparison period was missing — do not impute the missing value"
      - "if rows input is empty or None: raise ValueError stating no dataset rows were provided — do not call the LLM or write output"
      - "if output file path directory does not exist or is not writable: raise IOError before processing any periods — do not silently discard results"
      - "if the LLM or computation layer returns a single aggregated number instead of a per-period table: reject the result and refuse to write the output file — a city-wide or category-wide summary is a failure mode"
      - "if the LLM call raises an exception (timeout, API error, rate limit): do not write a partial output file — propagate the error to the caller with a message stating growth computation failed"
