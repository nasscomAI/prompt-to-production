# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

# skills.md — UC-0C Budget Growth Calculator

skills:
  - name: load_dataset
    description: Reads ward_budget.csv, validates required columns, reports the count
      and details of null actual_spend rows before returning the filtered dataset.
    input: >
      file_path (str) — path to ward_budget.csv
      ward (str) — exact ward name to filter, e.g. "Ward 1 – Kasba"
      category (str) — exact category name to filter, e.g. "Roads & Pothole Repair"
    output: >
      dict with keys:
        rows (list of dicts) — filtered rows sorted by period ascending
        null_rows (list of dicts) — rows where actual_spend is null/blank,
          each with period, ward, category, notes
        total_rows (int) — count of rows after filtering
    error_handling: >
      File not found: exits with descriptive message.
      Missing required columns: exits listing the missing column names.
      Ward or category not found in dataset: exits with available options listed.
      Empty result after filtering: exits with message naming the filter applied.

  - name: compute_growth
    description: Takes the filtered dataset from load_dataset and returns a per-period
      growth table with the formula shown for every computed row.
    input: >
      rows (list of dicts) — filtered rows from load_dataset, sorted by period
      null_rows (list of dicts) — null rows from load_dataset
      growth_type (str) — must be exactly "MoM" or "YoY" — any other value is refused
    output: >
      list of dicts per period, each with keys:
        period (str) — YYYY-MM
        actual_spend (str) — value or "NULL"
        formula (str) — e.g. "(19.7-14.8)/14.8*100" or "NULL — not computed"
        growth (str) — e.g. "+33.1%" or "NOT_COMPUTED (2024-03 is null)"
        null_reason (str) — from notes column if null, else blank
    error_handling: >
      growth_type not MoM or YoY: REFUSE with exact message:
        "Please specify --growth-type MoM or YoY. This system will not guess."
      First period of a growth_type range (no prior period): growth = "N/A (first period)"
      Either required period is null: growth = NOT_COMPUTED with explanation.
