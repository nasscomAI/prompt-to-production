skills:
  - name: load_dataset
    description: Reads the budget CSV file, validates expected columns, and proactively scans for and reports all null values before returning the dataset.
    input: >
      A string representing the file path to the budget dataset (e.g.,
      "../data/budget/ward_budget.csv").
    output: >
      A structured dataset (list of dicts) containing the parsed CSV rows.
      Before returning, the skill must print to stdout: the total row count,
      the total null actual_spend count, and the specific location of each null
      row (period · ward · category) plus its reason from the notes column.
      Nulls are never imputed — they are surfaced and returned as-is.
    error_handling: >
      If the file is missing or unreadable, raise a descriptive error and halt
      without returning partial data.
      If expected columns (period, ward, category, budgeted_amount, actual_spend,
      notes) are absent, refuse to load and list the missing column names.
      When null actual_spend values are found, they must never be silently
      imputed (zeroed, averaged, or forward-filled); the exact count and
      per-row locations must be reported to stdout before returning.

  - name: compute_growth
    description: Computes the requested growth metric for a specific ward and category, returning a per-period table that includes the explicit formula used.
    input: >
      The structured dataset from load_dataset, plus four required parameters:
      ward (string, e.g. "Ward 1 – Kasba"), category (string, e.g.
      "Roads & Pothole Repair"), growth_type (string, e.g. "MoM" or "YoY"),
      and output_path (string — the file path supplied via --output).
    output: >
      A CSV file written to output_path filtered to the specific ward and
      category, containing columns: period, ward, category, actual_spend,
      growth_percentage, formula_used. Every row must have a non-empty
      formula_used value — either the full arithmetic expression used, a
      NULL flag with the reason from notes, or an explicit n/a explanation.
    error_handling: >
      growth_type missing: refuse immediately with an explicit error message
      asking the user to specify MoM or YoY — never guess or default silently.
      Wrong aggregation level: if ward or category is absent or set to a
      wildcard/all value, refuse with an explicit error message — never produce
      a combined multi-ward or multi-category number.
      Null actual_spend: if the current or previous period's actual_spend is
      NULL, the growth for that row must be flagged as NULL and must not be
      computed — per the README: "Must be flagged — not computed". The output
      row must include the reason from the notes column in the formula_used field.
      Previous period unavailable: output growth_percentage as n/a and explain
      in formula_used (e.g. "First period; no previous period available").
