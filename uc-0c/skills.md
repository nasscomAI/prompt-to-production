# skills.md — UC-0C Budget Growth Analyser

skills:
  - name: load_dataset
    description: >
      Read ward_budget.csv, validate all required columns are present, report
      the count and details of null actual_spend rows before returning the data.
    input: >
      file_path (string): absolute or relative path to ward_budget.csv.
      Required columns: period, ward, category, budgeted_amount, actual_spend, notes.
    output: >
      A dict with two keys:
      - data: list of dicts (one per row), each with period, ward, category,
        budgeted_amount, actual_spend (None if null), and notes.
      - null_report: list of dicts for each null actual_spend row, containing
        period, ward, category, and null_reason (from the notes column).
      The null_report is always printed/logged before any computation proceeds.
    error_handling: >
      If the file does not exist or cannot be read, raise FileNotFoundError with
      the file path — do not return partial data. If any required column is
      missing, raise ValueError listing the missing column names. If actual_spend
      cannot be parsed as float (and is not blank/null), flag the row in the
      null_report with null_reason: "Unparseable value" rather than crashing.

  - name: compute_growth
    description: >
      Filter the dataset to a single ward and category, then compute per-period
      growth rates (MoM or YoY) with the formula shown on every output row.
    input: >
      data (list of dicts): the data key from load_dataset output.
      ward (string): exact ward name to filter to (e.g. "Ward 1 – Kasba").
      category (string): exact category name to filter to (e.g. "Roads & Pothole Repair").
      growth_type (string): must be either "MoM" (month-on-month) or "YoY"
      (year-on-year) — no other values accepted.
    output: >
      A list of dicts, one per period in sorted order, each containing:
      period (string), actual_spend (float or None), growth_rate (float or None),
      formula (string showing the exact formula applied, e.g.
      "(19.7 - 14.8) / 14.8 × 100"), and null_reason (string or blank).
      Null rows have growth_rate: None and a populated null_reason — they are
      never skipped or interpolated.
    error_handling: >
      If growth_type is not "MoM" or "YoY", raise ValueError:
      "Growth type not specified. Please provide --growth-type MoM or
      --growth-type YoY." — never default silently. If the ward+category
      combination returns zero rows, raise ValueError:
      "No data found for ward '{ward}' and category '{category}'.
      Check exact spelling." If growth cannot be computed for a period
      (e.g. first row has no prior period), set growth_rate to None and
      formula to "N/A — no prior period".
