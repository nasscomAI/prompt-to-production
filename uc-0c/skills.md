# skills.md — UC-0C Ward Budget Growth Calculator

skills:
  - name: load_dataset
    description: >
      Reads the ward budget CSV, validates that all required columns are
      present, and reports every null actual_spend row (count, location,
      and the reason from the notes column) before returning the rows.
    input: >
      input_path (str): path to a CSV file with columns
      period, ward, category, budgeted_amount, actual_spend, notes.
    output: >
      list of row dicts with actual_spend parsed to float or None,
      plus a printed null report: total null count and one line per null
      row showing period · ward · category · notes reason.
    error_handling: >
      If the file cannot be opened, raise FileNotFoundError with the path.
      If any required column is missing, refuse with a message naming the
      missing columns — do not attempt a partial read. A blank or
      non-numeric actual_spend is treated as null, never as zero.

  - name: compute_growth
    description: >
      Takes one ward, one category, and a growth type, and returns a
      per-period growth table. Never aggregates; flags null periods and
      skips their computation; shows the substituted formula on every
      computed row.
    input: >
      rows (list of dicts from load_dataset), ward (str, exact match),
      category (str, exact match), growth_type ('MoM' | 'YoY').
    output: >
      list of dicts with keys: period, ward, category, actual_spend,
      growth_pct (float or ''), formula (str with real numbers substituted),
      status (OK | SKIPPED_NULL | PREV_NULL | NO_PRIOR_PERIOD),
      null_reason (notes text for SKIPPED_NULL rows, else '').
      One row per period in the filtered data — null rows are included
      and flagged, never dropped.
    error_handling: >
      If ward or category matches no rows, refuse and list the valid values
      found in the dataset. If growth_type is not MoM or YoY, refuse and ask
      the user to choose one. If the prior period is null or absent, set
      status PREV_NULL / NO_PRIOR_PERIOD and leave growth_pct empty —
      never substitute zero or interpolate.
