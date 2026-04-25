# skills.md

skills:
  - name: load_dataset
    description: >
      Reads `../data/budget/ward_budget.csv`, validates that all required columns
      are present, detects null `actual_spend` rows, and returns the validated
      DataFrame along with a null-row report — before any computation begins.
    input: >
      - file_path (str): Path to the CSV file, e.g. `../data/budget/ward_budget.csv`.
    output: >
      - A pandas DataFrame containing all 300 rows with columns:
        period, ward, category, budgeted_amount, actual_spend, notes.
      - A printed summary reporting:
        (a) total row count (expected: 300),
        (b) count of null `actual_spend` rows (expected: 5),
        (c) a listing of each null row with its period, ward, category,
            and reason from the `notes` column.
        Example null-row report line:
          "NULL → 2024-03 | Ward 2 – Shivajinagar | Drainage & Flooding | Reason: <notes value>"
    error_handling: >
      - If the file is not found at the given path, raise FileNotFoundError with the attempted path.
      - If any expected column (period, ward, category, budgeted_amount, actual_spend, notes)
        is missing, refuse to proceed and list the missing column(s).
      - If the CSV is empty (0 rows), refuse and report "Empty dataset".

  - name: compute_growth
    description: >
      Filters the dataset for a specific ward + category combination, sorts by
      period, computes MoM or YoY growth on `actual_spend`, writes the result
      to `growth_output.csv`, and shows the arithmetic formula for every
      computed growth value.
    input: >
      - df (DataFrame): The validated DataFrame returned by `load_dataset`.
      - ward (str): Ward name to filter, e.g. `"Ward 1 – Kasba"`.
      - category (str): Category to filter, e.g. `"Roads & Pothole Repair"`.
      - growth_type (str): Must be explicitly `"MoM"` or `"YoY"` — never inferred.
      - output_path (str): Path for the output CSV, e.g. `uc-0c/growth_output.csv`.
      CLI entry point: `python app.py --input ../data/budget/ward_budget.csv
        --ward "Ward 1 – Kasba" --category "Roads & Pothole Repair"
        --growth-type MoM --output growth_output.csv`
    output: >
      A CSV file (`growth_output.csv`) with the following columns:
        - period: YYYY-MM
        - ward: ward name
        - category: category name
        - actual_spend: the value (or "NULL" if missing)
        - growth_pct: computed growth percentage (empty for NULL rows and the first row)
        - formula: the arithmetic derivation shown in full,
            e.g. "(19.7 − 14.8) / 14.8 × 100 = +33.1 %"
        - null_flag: "Y" if actual_spend is null, otherwise blank
        - null_reason: reason from the `notes` column if flagged, otherwise blank
      Example output rows (Ward 1 – Kasba | Roads & Pothole Repair | MoM):
        | period  | actual_spend | growth_pct | formula                                  | null_flag | null_reason |
        |---------|-------------|------------|------------------------------------------|-----------|-------------|
        | 2024-06 | 14.8        |  …         | …                                        |           |             |
        | 2024-07 | 19.7        | +33.1 %    | (19.7 − 14.8) / 14.8 × 100 = +33.1 %    |           |             |
        | 2024-10 | 13.1        | −34.8 %    | (13.1 − 20.1) / 20.1 × 100 = −34.8 %    |           |             |
      Example null-flagged rows (from README § Reference Values):
        | period  | actual_spend | growth_pct | formula | null_flag | null_reason              |
        |---------|-------------|------------|---------|-----------|--------------------------|
        | 2024-03 | NULL        |            |         | Y         | Ward 2 – Shivajinagar, Drainage & Flooding  |
        | 2024-07 | NULL        |            |         | Y         | Ward 4 – Warje, Roads & Pothole Repair       |
    error_handling: >
      - If `growth_type` is not provided or is not one of "MoM" / "YoY",
        refuse and ask: "Please specify --growth-type as MoM or YoY."
      - If the ward + category combination yields 0 rows, refuse and report
        "No data found for the specified ward and category."
      - If a null `actual_spend` is encountered, flag it in the output and
        skip growth computation for that row AND the immediately following row
        (since the formula would reference the null value).
      - Never zero-fill, interpolate, or assume a default for missing `actual_spend`.
