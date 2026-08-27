# skills.md — UC-0C Number That Looks Right

# Implements: agents.md · core failure modes: wrong aggregation level, silent null handling, formula assumption

skills:
  - name: load_dataset
    description: >
      Reads ward_budget.csv from the path in agents.md io_contract, validates required columns
      (period, ward, category, budgeted_amount, actual_spend, notes), and reports how many
      actual_spend values are null and which rows (period · ward · category) before any growth
      logic runs—so nulls are never silently ignored.
    input: >
      Filesystem path to CSV (default: ../data/budget/ward_budget.csv). Expected shape: 300 rows,
      5 wards, 5 categories, periods 2024-01 through 2024-12 per agents.md context.
    output: >
      Parsed table (e.g. DataFrame or rows) plus a null report: count of blank/null actual_spend,
      and a list identifying each null row aligned with agents.md dataset_nulls (period, ward,
      category, notes text for reason).
    error_handling: >
      If the file is missing, not CSV, or columns are wrong/insufficient, fail with a clear error.
      If encoding is invalid, fail. Do not drop null rows or impute actual_spend. Empty file → error
      or explicit empty dataset signal with zero rows validated.

  - name: compute_growth
    description: >
      For exactly one ward and one category (and a required growth_type such as MoM or YoY), filters
      load_dataset output to that series ordered by period and emits a per-period table with growth
      values—never a single all-ward number. Every row that includes a computed growth must show the
      formula used (e.g. MoM definition in plain text). Rows with null actual_spend are flagged with
      reason from notes; those periods are not used as numeric inputs to growth without explicit policy.
    input: >
      Filtered monthly series for one ward + one category; growth_type (required—must not be guessed).
      If growth_type is missing, callers must refuse per agents.md enforcement before invoking this skill.
    output: >
      Per-period rows suitable for growth_output.csv: period, ward, category, optional actual_spend,
      growth result or FLAG/NULL state, and a formula column or inline formula text for every computed
      row. Structure must remain per-ward per-category—no aggregation across wards or categories.
    error_handling: >
      If ward/category not in data, error. If growth_type absent, refuse upstream (do not default).
      On null actual_spend: flag and cite notes; do not fabricate spend or growth across that gap
      unless the product explicitly defines skip rules consistent with agents.md. If the user or caller
      requests all-ward aggregation, refuse (agents.md reference_verification aggregation_refusal).

alignment:
  agent_spec: "agents.md"
  enforcement: >
    load_dataset MUST report null count and which rows before compute_growth runs. compute_growth MUST
    include the formula alongside each growth result, flag nulls with notes, never aggregate across
    wards/categories without explicit instruction, and callers MUST pass growth_type—never guess when
    unspecified.
