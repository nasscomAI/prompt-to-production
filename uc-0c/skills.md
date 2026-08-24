skills:
  - name: load_dataset
    description: Reads the input CSV, validates required columns, and returns a
      structured dataset plus a null-report describing rows with missing
      `actual_spend` values.
    input:
      - `input_path` (string): path to the CSV file (expected columns: `period`,
        `ward`, `category`, `budgeted_amount`, `actual_spend`, `notes`).
    output:
      - `dataset` (list[dict] or DataFrame-like): ordered rows parsed from CSV.
      - `null_report` (list[dict]): rows where `actual_spend` is null; each
        entry must include `period`, `ward`, `category`, and `notes`.
      - `validation_errors` (list[string]): empty on success; contains messages
        if required columns are missing or file cannot be read.
    error_handling:
      - If file not found -> return `validation_errors` with a clear message.
      - If required columns missing -> return `validation_errors` listing
        missing columns and do not return `dataset` for computation.

  - name: compute_growth
    description: Computes growth values for a single `ward` + `category` across
      periods using the requested `growth_type` and attaches the formula used
      to each computed row.
    input:
      - `dataset` (as returned from `load_dataset`).
      - `ward` (string): exact ward name to filter by.
      - `category` (string): exact category name to filter by.
      - `growth_type` (string): one of `MoM` or `YoY`. Required; agent must
        refuse if missing.
    output:
      - `results` (list[dict]): each dict contains `period`, `ward`, `category`,
        `actual_spend`, `growth` (numeric or null), `formula` (text),
        `null_flag` (bool), `notes` (string).
      - `meta` (dict): includes `ward`, `category`, `growth_type`, and `formula` text.
    error_handling:
      - If `growth_type` is missing -> raise a refusal error explaining that
        `--growth-type` is required.
      - If `ward` or `category` selection would require aggregation across
        multiple wards/categories -> raise a refusal per enforcement rules.
      - For rows with null `actual_spend` -> set `null_flag` true, copy `notes`,
        and do not compute `growth` (leave it null).
      - Include the formula string used for each numeric row (e.g. for `MoM`:
        `(this - prev) / prev * 100`).
