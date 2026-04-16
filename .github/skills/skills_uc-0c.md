# skills.md
# skills.md — UC-0C Budget Growth Analysis Agent

skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates required columns, reports the
      total null count and the exact identity of every null actual_spend row before
      returning the data.
    input: A string — file_path (path to ward_budget.csv). Expected columns:
      period (YYYY-MM), ward (string), category (string), budgeted_amount (float),
      actual_spend (float or blank), notes (string).
    output: A dict with two keys — (1) null_report: a list of dicts, one per null
      actual_spend row, each containing period, ward, category, and notes (the
      verbatim null reason from the CSV); (2) data: a list of all row dicts with
      null actual_spend preserved as None (never coerced to 0 or interpolated).
      The null_report is always printed to stdout before data is returned.
    error_handling: If the file does not exist, raises FileNotFoundError with the
      path in the message. If any required column is missing, raises ValueError
      naming the missing column. If the file has zero data rows after the header,
      raises ValueError stating the dataset is empty. Never returns data silently
      with missing columns or a suppressed null report.

  - name: compute_growth
    description: Takes a filtered ward+category slice of the dataset and returns a
      per-period growth table with the formula shown explicitly for every row.
    input: A dict with four keys — data (list of row dicts as returned by
      load_dataset, already filtered to a single ward and single category),
      ward (string, must match exactly one ward in the data),
      category (string, must match exactly one category in the data),
      growth_type (string, must be exactly "MoM" or "YoY" — no other values
      accepted).
    output: A list of dicts, one per period in the filtered slice, each with:
      period (YYYY-MM), actual_spend (float or None), prior_period (YYYY-MM or
      None for the first row), prior_spend (float or None), formula (string showing
      the exact arithmetic with real values, e.g.
      "(19.7 − 14.8) / 14.8 × 100 = +33.1%"), growth_pct (float rounded to 1
      decimal place, or None), and flag (one of: OK, NULL_NOT_COMPUTED,
      PRIOR_NULL_NOT_COMPUTED, FIRST_PERIOD_NO_PRIOR).
    error_handling: If growth_type is not "MoM" or "YoY", raises ValueError:
      'Growth type not specified. Please rerun with --growth-type MoM or
      --growth-type YoY.' If the filtered data slice is empty (ward or category
      not found), raises ValueError naming the unmatched ward or category. If
      actual_spend is None for a row, sets growth_pct to None and flag to
      NULL_NOT_COMPUTED with the null reason from the notes column appended. If
      the prior period's actual_spend is None, sets growth_pct to None and flag
      to PRIOR_NULL_NOT_COMPUTED. Never computes growth using 0 as a substitute
      for a null value.
