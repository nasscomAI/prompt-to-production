# skills.md — UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: >
      Reads ward_budget.csv, validates required columns are present, reports
      the count and identity of null actual_spend rows before returning data.
    input: >
      file_path (string) — path to ward_budget.csv
    output: >
      Dict containing:
        - rows        : list of dicts, one per CSV row, all columns preserved
        - null_rows   : list of dicts identifying each null actual_spend row
                        (period, ward, category, notes)
        - null_count  : int
      Null rows are reported regardless of ward/category filter — caller
      decides which are relevant.
    error_handling: >
      If file_path does not exist or required columns (period, ward, category,
      budgeted_amount, actual_spend, notes) are missing, return:
        { "error": "LOAD_FAILED", "message": "<reason>" }
      Never proceed with partial data. Never impute missing column values.

  - name: compute_growth
    description: >
      Takes a filtered dataset for a single ward + category, computes
      per-period growth using the specified growth_type, and returns a table
      with formula and null flags on every row.
    input: >
      - rows        : list of dicts filtered to one ward + one category,
                      sorted by period ascending
      - growth_type : string — exactly "MoM" or "YoY"
      - ward        : string — used for output labelling and scope validation
      - category    : string — used for output labelling and scope validation
    output: >
      List of dicts, one per period, each containing:
        - period       (string, YYYY-MM)
        - actual_spend (float or None)
        - prior_spend  (float or None — previous month for MoM, same month
                        prior year for YoY)
        - growth_pct   (float rounded to 1dp, or "NULL_FLAGGED")
        - formula      (string — exact arithmetic shown, e.g.
                        "(19.7 - 14.8) / 14.8 × 100 = +33.1%")
        - null_reason  (string from notes column, or "")
    error_handling: >
      If growth_type is not "MoM" or "YoY", raise ValueError:
        "growth_type must be 'MoM' or 'YoY' — received: '<value>'"
      If rows contain more than one ward or category value, raise ValueError:
        "compute_growth received mixed ward/category data — scope violation."
      If actual_spend or prior_spend is null for a row, set growth_pct to
      "NULL_FLAGGED" and populate null_reason. Never compute a result from
      a null input.
