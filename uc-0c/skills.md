skills:

  - name: load_dataset
    description: >
      Reads the ward budget CSV file, validates required schema (period, ward,
      category, budgeted_amount, actual_spend, notes), identifies and audits all
      deliberately null actual_spend rows, and returns clean structured records.
    input: >
      A string filepath to the budget CSV file (e.g. data/budget/ward_budget.csv).
    output: >
      A dictionary containing: total_rows (int), rows (list of dicts), wards (list of unique strings),
      categories (list of unique strings), and null_rows (list of flagged rows with reasons).
    error_handling: >
      Raises FileNotFoundError if file is missing.
      Raises ValueError if required columns are missing or file is empty.

  - name: compute_growth
    description: >
      Filters dataset records for a single specified ward and category, computes
      period-over-period growth (MoM or YoY) based on explicit growth_type, attaches
      calculation formula and status, and transparently flags null rows.
    input: >
      A dictionary with keys: dataset (from load_dataset), ward (str), category (str),
      growth_type (str: 'MoM' or 'YoY').
    output: >
      A list of structured result rows, each containing: period, ward, category,
      budgeted_amount, actual_spend, growth_type, growth_rate, formula, status, notes.
    error_handling: >
      Refuses and raises ValueError if growth_type is missing or not 'MoM'/'YoY'.
      Refuses and raises ValueError if ward or category is 'ALL', 'Any', or not found.
      Marks rows with missing actual_spend or missing baseline as FLAGGED_NULL rather
      than computing corrupted percentages.
