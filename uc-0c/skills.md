# skills.md

skills:
  - name: load_dataset
    description: >
      Reads the ward budget CSV, validates its structure, and reports every
      null actual_spend row (with its notes reason) before any computation runs.
    input: >
      Path to a CSV file (--input) with columns period (YYYY-MM), ward,
      category, budgeted_amount, actual_spend (float or blank), notes.
    output: >
      List of validated row records plus a pre-compute report printed to
      console: total row count, null count, and each null row's
      period/ward/category with its reason from notes.
    error_handling: >
      Missing file, missing required columns, empty key fields, malformed
      periods (not YYYY-MM), or non-numeric amounts abort immediately with a
      message naming the exact problem and line. Null spends are never
      dropped, imputed, or filled silently.

  - name: compute_growth
    description: >
      Computes MoM or YoY growth per period for exactly one ward-category
      pair, showing the formula used alongside every computed result.
    input: >
      Filtered rows for one ward and one category, and an explicit
      growth_type of MoM or YoY (refuses to proceed if absent).
    output: >
      Per-period records with period, ward, category, actual_spend,
      growth_result (the percentage, e.g. +33.1%, when computable; otherwise
      the flag itself: "NULL — not computed" or an N/A reason such as
      "N/A (no prior period)"), a literal formula string such as
      "(19.7 - 14.8) / 14.8 * 100 = +33.1%" alongside every computed result,
      and the original notes.
    error_handling: >
      Unknown ward or category refuses with the list of valid values;
      missing --growth-type refuses and asks rather than defaulting; first
      periods and prior-year gaps are marked N/A; null spends are flagged,
      never interpolated or computed against.
