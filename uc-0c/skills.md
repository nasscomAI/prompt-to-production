# skills.md

skills:
  - name: load_dataset
    description: Reads a budget CSV, validates its columns, and reports the null count and which rows are null before returning the data.
    input: >
      A file path to a CSV with columns period (YYYY-MM), ward (string), category (string),
      budgeted_amount (float, always present), actual_spend (float or blank), and notes
      (string), e.g. ../data/budget/ward_budget.csv.
    output: >
      A structured dataset (list of row objects with period, ward, category,
      budgeted_amount, actual_spend, notes) plus a null report listing the total null count
      and each null actual_spend row with its period, ward, category, and the null reason
      taken from the notes column.
    error_handling: >
      If the file does not exist or cannot be read, returns an error and does not fabricate
      data. If required columns are missing, reports which columns are missing and refuses to
      proceed. If actual_spend is null but notes is empty or missing, flags that the null
      reason cannot be resolved and refuses to proceed rather than guessing. Never imputes or
      drops null rows silently; a dataset with 5 deliberately null actual_spend rows is
      expected and must be reported, not treated as an error.

  - name: compute_growth
    description: Takes a ward, a category, and a growth type and returns a per-period growth table with the formula shown in every row.
    input: >
      The structured dataset returned by load_dataset, the ward string (e.g. "Ward 1 – Kasba"),
      the category string (e.g. "Roads & Pothole Repair"), the growth type (e.g. MoM).
    output: >
      A per-ward, per-category table with one row per period for the requested ward and category
      only. Each row includes the period, the formula used (for example,
      MoM = (current − previous) / previous × 100), the computed growth, and a not-computed
      marker with the null reason for any period whose actual_spend is null. The CLI writes this
      table to the requested output CSV path.
    error_handling: >
      If the requested ward or category does not exist in the dataset, refuses to compute and
      reports the mismatch. If the growth type is missing, empty, or not one of the supported
      explicit types, refuses and asks rather than guessing a default. If any actual_spend in
      the requested series is null, marks that row's growth as not computed and includes the
      null reason from notes. If the output path cannot be written, raises an error without
      producing partial output. Refuses any request that would aggregate across wards or
      categories.