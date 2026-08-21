# skills.md — UC-0C Ward Budget Growth Calculator

skills:
  - name: load_dataset
    description: >
      Reads the ward budget CSV, validates that every required column is
      present, and reports the null actual_spend rows — with the reason quoted
      from the notes column — before returning any data for computation.
    input: >
      path : str — path to ../data/budget/ward_budget.csv
    output: >
      dict —
        rows      : list of {period, ward, category, budgeted_amount,
                    actual_spend (float or None), notes}
        wards     : sorted list of distinct ward names
        categories: sorted list of distinct category names
        periods   : sorted list of distinct YYYY-MM periods
        nulls     : list of {period, ward, category, reason} — one per null
                    actual_spend, reason taken verbatim from notes
      The null report is returned as data and printed by the caller before the
      first growth figure is computed, so a reader meets the gaps before the
      numbers.
    error_handling: >
      A missing file exits non-zero naming the path. A missing required column
      is a fatal schema error — the run aborts rather than treating an absent
      actual_spend column as 300 nulls. A non-numeric actual_spend that is not
      blank is reported as a data error with its period and ward, not coerced
      to zero. A blank actual_spend becomes None and is never coerced to 0.0 —
      the difference between "spent nothing" and "we do not know what was
      spent" is the whole point of this UC, and the two must never collapse
      into the same value.

  - name: compute_growth
    description: >
      Takes a resolved ward, category and growth type and returns the
      per-period table, one row per period, each carrying its own formula,
      operands, result and status.
    input: >
      dataset     : dict — as returned by load_dataset
      ward        : str — one exact ward name
      category    : str — one exact category name
      growth_type : str — "MoM" or "YoY". Never defaulted.
    output: >
      list of dicts, one per period in chronological order, each with:
      period, ward, category, budgeted_amount, actual_spend, prior_period,
      prior_actual_spend, growth_type, formula, growth_pct, status, note
      status is one of COMPUTED, NULL_CURRENT, NULL_PRIOR, NO_PRIOR_PERIOD,
      UNDEFINED_ZERO_BASE. formula shows the substituted operands, e.g.
      "(19.7 - 14.8) / 14.8 * 100".
    error_handling: >
      Refuses rather than guesses. An absent growth_type is a refusal, not a
      default. An unknown ward or category is a refusal that prints the valid
      values, never a nearest-match fallback. A selector matching more than one
      value where one was required is a refusal listing the candidates. A null
      current value yields NULL_CURRENT; a null prior value yields NULL_PRIOR —
      both emitted as rows, so the period count is preserved and no month
      disappears from the table. A zero prior value yields UNDEFINED_ZERO_BASE
      with an empty growth figure rather than a division error or an infinity.
      A ward and category combination with no rows at all is reported as such
      rather than returning an empty table that reads as "no growth".
