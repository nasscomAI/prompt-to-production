# skills.md — UC-0C Growth Calculator

skills:
  - name: load_dataset
    description: >
      Reads the ward budget CSV, validates that every column the tool depends on
      is present, and returns the rows unmodified.
    input: >
      path (str) — filesystem path to the budget CSV.
    output: >
      list[dict] — one dict per row, values left as strings so that a blank
      actual_spend stays distinguishable from a zero.
    error_handling: >
      Missing file, empty file, or any missing required column raises
      DatasetError and the run exits 2. Values are deliberately NOT cast to float
      at load time: casting a blank to 0.0 here would erase the distinction
      between "spent nothing" and "we do not know what was spent", which is the
      entire subject of this use case.

  - name: null_report
    description: >
      Names every row with a blank actual_spend — period, ward, category and the
      reason from the notes column — and prints it before any arithmetic runs.
    input: >
      rows (list[dict]) from load_dataset.
    output: >
      tuple (report_text: str, null_rows: list[dict]). Five rows on the supplied
      dataset.
    error_handling: >
      A null with an empty notes cell is reported as "no reason given in notes"
      rather than omitted. The report runs unconditionally, including on runs
      where the requested ward/category pair contains no nulls at all, so the
      reader always knows what is missing from the file as a whole.

  - name: check_scope
    description: >
      Enforces the SCOPE rule — one ward, one category, both named explicitly.
    input: >
      rows (list[dict]), ward (str or None), category (str or None).
    output: >
      None on success.
    error_handling: >
      Raises ScopeRefusal on a missing value, on an aggregate token
      (all / any / total / overall / combined / *), or on a name not present in
      the data; the unknown-name refusal lists the valid values. Exit code 3.

  - name: check_formula
    description: >
      Enforces the FORMULA rule — the growth type must be stated, never inferred.
    input: >
      growth_type (str or None).
    output: >
      None on success.
    error_handling: >
      Raises FormulaRefusal when absent or unrecognised. Exit code 4. There is
      deliberately no default: MoM is the obvious guess and the obvious guess is
      what makes the wrong number look right.

  - name: compute_growth
    description: >
      Returns a per-period table for one ward + category pair, each row carrying
      its status and the arithmetic used.
    input: >
      rows (list[dict]), ward (str), category (str), growth_type ("MoM" | "YoY").
    output: >
      list[dict] with ward, category, period, growth_type, budgeted_amount,
      actual_spend, prior_period, prior_value, growth_pct, formula, status, note.
      One row per source period — no period is dropped for any reason.
    error_handling: >
      The comparison period is looked up by calendar arithmetic, not by list
      position, so a gap in the series cannot be closed by accident. A null
      current value yields NULL_FLAGGED; an absent comparison period yields
      NO_PRIOR; a null comparison value yields PRIOR_NULL. In all three cases
      growth_pct is blank and formula reads "not computed", never 0.
