skills:
  - name: load_dataset
    description: >
      Reads ward_budget.csv, validates that all required columns are present,
      and reports the null count and the exact rows (period / ward / category /
      notes) where actual_spend is missing — before returning the dataset for
      further processing.
    input: >
      file_path (string) — absolute or relative path to the CSV file.
    output: >
      Tuple of (DataFrame with validated schema, null_report list).
      null_report entries: {period, ward, category, notes} for each null row.
      Raises ValueError if any required column is absent.
    error_handling: >
      Missing required column → raise ValueError listing the absent column names.
      Zero data rows after loading → raise ValueError.
      Null rows are never silently dropped; they are always surfaced in
      null_report and excluded from downstream computations.

  - name: compute_growth
    description: >
      Takes a ward, category, and explicit growth_type (MoM or YoY), filters
      the dataset to that slice, and returns a per-period table with the
      computed growth rate and the exact formula used for each row.
    input: >
      ward (string), category (string), growth_type (string — "MoM" or "YoY"),
      dataset (validated DataFrame from load_dataset).
    output: >
      DataFrame with columns: period, actual_spend, formula (string showing
      the arithmetic e.g. "(19.7 − 14.8) / 14.8 × 100"), growth_rate (float,
      percent). Null-period rows are included as flagged/skipped entries with
      growth_rate = null and formula = "SKIPPED — null actual_spend".
    error_handling: >
      growth_type absent or not in {"MoM", "YoY"} → refuse with message
      "growth_type must be 'MoM' or 'YoY' — please specify explicitly."
      Ward or category not found in dataset → raise ValueError naming the
      missing value. Never fall back to a default growth type or aggregate
      scope silently.
