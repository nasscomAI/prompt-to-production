# skills.md — UC-0C Data / Growth Analysis

skills:
  - name: load_dataset
    description: >
      Reads the ward budget CSV, validates that all required columns are present,
      reports the total null count and exactly which rows have null actual_spend
      (with their period, ward, category, and notes) BEFORE returning any data.
      Never silently omits or imputes nulls.
    input: >
      file_path (str): path to ward_budget.csv.
      ward (str, optional): filter to specific ward name. If provided, only rows
      matching this ward are returned.
      category (str, optional): filter to specific category. If provided, only rows
      matching this category are returned.
    output: >
      A Python dict with keys:
        data (list of dicts): all matching rows from the CSV.
        null_report (list of dicts): each null row with keys period, ward, category, notes.
        total_rows (int): total rows after filtering.
        null_count (int): count of null actual_spend rows in filtered set.
      Prints null report to stdout before returning.
    error_handling: >
      If the file is missing, raise FileNotFoundError. If required columns (period,
      ward, category, actual_spend, notes) are missing, raise ValueError listing
      the missing columns. If ward or category filter matches no rows, raise ValueError
      with the exact filter values so the user knows what was specified.

  - name: compute_growth
    description: >
      Takes a filtered dataset (from load_dataset), a growth_type (MoM or YoY),
      and returns a per-period table showing actual_spend, previous period spend,
      growth_pct, formula used, and null_flag for each period. Never computes growth
      across wards or categories. Shows every calculation step explicitly.
    input: >
      data (list of dicts): filtered rows from load_dataset output, sorted by period.
      growth_type (str): exactly "MoM" or "YoY". Any other value causes a refusal.
      ward (str): the ward being analysed (for output labelling only).
      category (str): the category being analysed (for output labelling only).
    output: >
      A list of dicts with keys: period, actual_spend, prev_spend, growth_pct,
      formula, null_flag. growth_pct and formula are None when either period has
      null actual_spend. null_flag contains the notes text when actual_spend is null,
      else empty string.
    error_handling: >
      If growth_type is not "MoM" or "YoY", return error dict immediately:
      {"error": "growth_type must be MoM or YoY — refusing to guess"}.
      If data has fewer than 2 rows, return error dict:
      {"error": "Insufficient data — need at least 2 periods to compute growth"}.

# ── Dataset Structure ─────────────────────────────────────────────────────────
# period        | YYYY-MM   | 2024-01 through 2024-12
# ward          | string    | 5 wards (Ward 1 – Kasba … Ward 5 – Hadapsar)
# category      | string    | 5 categories (Roads & Pothole Repair …)
# budgeted_amount | float   | Always present
# actual_spend  | float/blank | 5 rows are deliberately null
# notes         | string    | Explains null reason when actual_spend is blank
#
# ── The 5 Null Rows ───────────────────────────────────────────────────────────
# 2024-03 · Ward 2 – Shivajinagar · Drainage & Flooding
# 2024-07 · Ward 4 – Warje        · Roads & Pothole Repair
# 2024-11 · Ward 1 – Kasba        · Waste Management
# 2024-08 · Ward 3 – Kothrud      · Parks & Greening
# 2024-05 · Ward 5 – Hadapsar     · Streetlight Maintenance
#
# ── Reference Values for Verification ───────────────────────────────────────
# Ward 1 – Kasba | Roads & Pothole Repair | 2024-07 | 19.7 | MoM +33.1%
# Ward 1 – Kasba | Roads & Pothole Repair | 2024-10 | 13.1 | MoM -34.8%
# Ward 2 – Shivajinagar | Drainage & Flooding | 2024-03 | NULL → must be flagged
# Ward 4 – Warje | Roads & Pothole Repair | 2024-07 | NULL → must be flagged
