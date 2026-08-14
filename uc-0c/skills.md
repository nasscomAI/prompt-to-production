# skills.md — UC-0C Budget Growth Calculator

skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates its columns, and reports how many actual_spend values are null and exactly which rows.
    input: input_path (str) to ward_budget.csv with columns period, ward, category, budgeted_amount, actual_spend, notes.
    output: >
      A list of parsed rows (period, ward, category, budgeted_amount,
      actual_spend as float-or-None, notes) plus a null report listing each
      null row's period, ward, category, and notes reason.
    error_handling: >
      If a required column is missing, it raises a clear error before any
      computation. Blank actual_spend becomes None (never 0 and never dropped);
      unparseable numbers are treated as null and surfaced in the null report.

  - name: compute_growth
    description: For one ward and one category, returns a per-period table of growth with the formula shown, refusing on out-of-scope or ambiguous requests.
    input: >
      the loaded rows, a ward (str), a category (str), and a growth_type
      ("MoM" or "YoY").
    output: >
      An ordered per-period table; each row is either COMPUTED (period, spend,
      comparison period, comparison value, formula, growth %) or FLAGGED (period
      with null spend or null comparison, plus the null reason).
    error_handling: >
      Refuses (returns an error result, computes nothing) if the ward or
      category is "all"/"total"/blank, or if growth_type is not MoM or YoY.
      Growth into or out of a null value is never computed — it is flagged.
      The first period (MoM) or first year (YoY) with no comparison is flagged,
      not computed.
