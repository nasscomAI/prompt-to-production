# skills.md — UC-0C Budget Growth Analysis Agent

skills:
  - name: load_dataset
    description: Reads the ward_budget CSV, validates required columns, reports null count and which rows are null before returning the filtered slice for the requested ward and category.
    input: >
      file_path (str) — path to ward_budget.csv.
      ward (str) — exact ward name to filter on (e.g. "Ward 1 – Kasba").
      category (str) — exact category name to filter on (e.g. "Roads & Pothole Repair").
    output: >
      A dict:
        {
          "rows": list[dict],          # filtered rows sorted by period, all original columns
          "null_rows": list[dict],     # subset where actual_spend is null/blank
          "null_count": int,           # total nulls in the filtered slice
          "total_count": int,          # total rows in the filtered slice
          "all_wards": list[str],      # distinct ward values in full dataset (for validation)
          "all_categories": list[str]  # distinct category values in full dataset (for validation)
        }
    error_handling: >
      If file_path does not exist: raise FileNotFoundError with the path.
      If required columns (period, ward, category, actual_spend, notes) are missing:
        raise ValueError listing the missing column names.
      If the ward or category filter matches zero rows: raise ValueError with a helpful message
        listing the available ward and category values found in the dataset.
      Never silently return an empty result — zero rows is always an error.

  - name: compute_growth
    description: Takes the loaded dataset slice and growth_type, computes per-period growth with explicit formula strings, flags nulls, and returns a table ready to write to CSV.
    input: >
      data (dict) — the dict returned by load_dataset (uses "rows" and "null_rows").
      growth_type (str) — must be exactly "MoM" or "YoY"; any other value triggers refusal.
      ward (str) — ward name, used for output labelling.
      category (str) — category name, used for output labelling.
    output: >
      A list of dicts, one per period, with keys:
        period (str), ward (str), category (str),
        actual_spend (float or "NULL"),
        prior_period (str or "N/A"),
        prior_spend (float or "NULL" or "N/A"),
        growth_pct (str),        # e.g. "+33.1%" or "NULL — flagged" or "N/A (first period)"
        formula_used (str),      # e.g. "(19.7 − 14.8) / 14.8 × 100" or "N/A" or "NULL — not computed"
        null_flag (str),         # "NULL" if actual_spend is null, else ""
        null_reason (str)        # verbatim from notes column if null, else ""
    error_handling: >
      If growth_type is not "MoM" or "YoY": print a refusal message to stderr and raise
        SystemExit(2) — never default to a formula.
      If growth_type is "YoY" and the dataset covers only a single calendar year:
        print a refusal message explaining YoY requires at least 2 years of data,
        then raise SystemExit(2).
      If either the current or prior period has a null actual_spend: set growth_pct to
        "NULL — flagged" and formula_used to "NULL — not computed"; never compute over a null.
      If the prior period row is missing (gap in data): set growth_pct to "N/A (gap in data)"
        and formula_used to "N/A — prior period missing".
