# skills.md — UC-0C Budget Growth Calculator

skills:
  - name: load_dataset
    description: >
      Reads the ward budget CSV, validates that every required column is present,
      and reports the null actual_spend rows WITH their stated reasons before any
      calculation is attempted.
    input: >
      path (str) — path to data/budget/ward_budget.csv
      Required columns: period, ward, category, budgeted_amount, actual_spend, notes
    output: >
      dict:
        rows       — list of row dicts, source order preserved, with
                     actual_spend parsed to float or None (never 0.0 for blank)
        nulls      — list of {period, ward, category, note} for every null
                     actual_spend, printed to stdout before returning
        wards      — sorted unique ward names as spelled in the source
        categories — sorted unique category names
        periods    — sorted unique periods
      The null report is emitted whether or not the caller asks for it, so a
      downstream consumer cannot be unaware of the gaps.
    error_handling: >
      - file missing / unreadable -> raises; caller exits non-zero, writes nothing.
      - any required column absent -> raises naming the missing column; a CSV with
        the wrong shape is never partially processed.
      - blank actual_spend -> parsed as None, NEVER 0.0. This is the whole point:
        zero is a real spend figure and must not be confused with "not reported".
      - non-numeric actual_spend (e.g. "N/A", "-") -> treated as None and added to
        the null report with the raw text preserved, rather than crashing.
      - duplicate ward+category+period -> reported as a warning; not silently
        deduplicated or summed.

  - name: compute_growth
    description: >
      Computes period-over-period growth for exactly one ward and one category,
      returning a per-period table in which every row shows the arithmetic used
      and every uncomputable row states why.
    input: >
      dataset (dict) — output of load_dataset
      ward (str), category (str) — both MANDATORY, matched against source values
        (a plain hyphen is accepted as an alias for the en-dash)
      growth_type (str) — "MoM" or "YoY", MANDATORY, never defaulted
    output: >
      list of row dicts, one per period in chronological order:
        ward, category, period, budgeted_amount, actual_spend, growth_type,
        base_period, base_value, formula, growth_pct, status, note
      status is one of:
        COMPUTED        — growth_pct present, formula shows real operands
        NO_PRIOR_PERIOD — first period, or prior calendar month absent
        NULL_VALUE      — this period's actual_spend is null; note gives the
                          source reason verbatim
        NULL_BASE       — prior period's value is null, so the denominator is
                          missing; this is the second period a null damages
        NOT_COMPUTABLE  — YoY requested but no prior-year data exists
      growth_pct is left EMPTY (not 0) for every non-COMPUTED status.
    error_handling: >
      - ward or category omitted, or set to ALL / * / "all wards" / "all"
        -> REFUSES, raises AggregationRefused; caller exits non-zero. Cross-ward
        aggregation is not supported and has no override.
      - growth_type omitted -> REFUSES, raises GrowthTypeNotSpecified listing the
        valid options. Never defaults to MoM.
      - ward+category matching zero rows -> REFUSES and lists valid values rather
        than writing an empty CSV that looks like a legitimate empty result.
      - base value of exactly 0.0 -> status NO_PRIOR_PERIOD with an explicit note;
        division by zero is reported, not rendered as infinity or a crash.
      - YoY on a single-year dataset -> every row NOT_COMPUTABLE plus a stdout
        banner; the table is still written so the refusal is visible in the file.
