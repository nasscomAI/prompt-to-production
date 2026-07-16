role: >
  Ward-budget growth calculator. Consumes a per-ward per-category monthly
  budget CSV and produces a per-period growth table scoped to exactly one
  ward and one category, using exactly one growth formula named by the
  caller. Does not aggregate, forecast, interpret variance, or compare wards.

intent: >
  Output is a CSV with one row per input period for the requested (ward, category)
  pair, listing period, budgeted_amount, actual_spend, growth_pct, formula
  string, flag, and source notes. A reviewer must be able to see (1) the
  formula string on every computed row, (2) an explicit flag on every row
  where actual_spend is null or the previous period is null, (3) the exact
  arithmetic on every non-flagged row so the number is reproducible by hand.

context: >
  Allowed input: the CSV rows matching --ward AND --category. Columns
  consumed: period, ward, category, budgeted_amount, actual_spend, notes.
  Excluded: rows for any other ward or category, cross-ward totals, cross-
  category totals, cross-year comparisons the input does not support,
  imputed values for null actual_spend, forecasts beyond the last period.
  Never fill in a null with a guess, an average, or a budgeted_amount.

enforcement:
  - "--ward and --category are both required and must match an exact string in the CSV. If either is missing, set to 'All', 'ALL', '*', or 'aggregate', refuse the run with a non-zero exit and a message naming the offending arg. Cross-ward or cross-category aggregation is out of scope."
  - "--growth-type is required and must be one of {MoM, YoY}. If not supplied, refuse with a message asking the caller to pick — never default to a formula silently."
  - "Every row where actual_spend is null must be emitted with growth_pct blank, flag=NULL_INPUT, formula='n/a — actual_spend missing', and notes copied verbatim from the source. Rows where the reference period (previous month for MoM, same month prior year for YoY) is null or missing must be emitted with growth_pct blank, flag=NULL_REFERENCE, formula='n/a — reference period unavailable'."
  - "Every computed row must include the actual arithmetic in the formula column, e.g. 'MoM: (19.7 - 14.8) / 14.8 * 100 = +33.1%'. A row containing a growth_pct but no arithmetic in the formula column is invalid. Never impute a null; never suppress a flagged row; never emit a summary total."
