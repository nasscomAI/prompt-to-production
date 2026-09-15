# skills.md — UC-0C Budget Growth Calculator

skills:
  - name: load_dataset
    description: >
      Reads ward_budget.csv, validates that every required column is present, and
      reports the null actual_spend rows with their stated reasons before any
      arithmetic is allowed to run.
    input: >
      path (str) — path to ../data/budget/ward_budget.csv.
      Read as UTF-8 with BOM tolerance. Ward names contain an en dash (–); the
      loader records the exact source spelling and also indexes a normalised form
      so a hyphen typed on the command line still matches.
    output: >
      dict with keys:
        rows      — list of {period, ward, category, actual_spend (float or None),
                    notes}, in source order; budgeted_amount is read but discarded
        wards     — sorted list of exact ward strings present
        categories— sorted list of exact category strings present
        periods   — sorted list of period strings present
        years     — sorted list of distinct years, used to decide whether YoY is possible
        nulls     — list of the rows whose actual_spend is missing, each with its
                    notes text
      Side effect: prints the null report to stderr — count, then one line per null
      row giving period, ward, category and reason.
    error_handling: >
      File missing or unreadable → message to stderr, exit 1, nothing written.
      A required column absent → exit 1 naming the missing column and listing the
      columns that were found; the program does not proceed on a partial schema.
      A non-numeric actual_spend → treated as null with the parse failure recorded as
      its reason, never coerced to 0 and never dropped from the series.
      A blank notes cell on a null row → reason recorded as "no reason given in
      source", so the absence of an explanation is itself reported.

  - name: resolve_selector
    description: >
      Turns a --ward or --category argument into an exact value present in the data,
      or refuses — the gate that prevents both fuzzy matching and accidental
      aggregation.
    input: >
      selector (str) — a ward or category name, or the literal ALL;
      available (list of str) — the exact values present in the dataset.
    output: >
      list of str — one exact value, or every value when ALL was given. ALL means
      iterate over each value separately, never combine them.
    error_handling: >
      Unrecognised value → exit 2 listing every valid value; never resolved to the
      closest match, because a near-miss ward name silently analysing the wrong ward
      is worse than a failed run. Matching ignores case, surrounding whitespace, and
      en dash versus hyphen, and nothing else. An empty selector is refused rather
      than treated as ALL, so aggregation is never reached by omission.

  - name: compute_growth
    description: >
      Computes period-over-period growth for one ward and one category, returning a
      per-period table with the formula shown alongside every result.
    input: >
      rows (list) for a single ward and category, sorted by period;
      growth_type (str) — MoM or YoY, never defaulted;
      ward (str), category (str) — echoed into every output row.
    output: >
      list of dicts with keys ward, category, period, actual_spend, prior_period,
      prior_spend, growth_type, growth_pct, formula, status, note.
      growth_pct is a signed number to one decimal place, or empty when not computed.
      formula carries the substituted calculation, e.g.
      "(19.7 - 14.8) / 14.8 * 100 = +33.1%", or the reason no calculation was made.
      status is one of OK, NULL_INPUT, NULL_PRIOR, NO_PRIOR_PERIOD, ZERO_BASE.
    error_handling: >
      Current value null → NULL_INPUT, growth_pct empty, note carries the source
      reason from the notes column.
      Prior value null → NULL_PRIOR, growth_pct empty; the gap is never bridged by
      reaching back a further period, which would silently measure two months.
      No prior period exists → NO_PRIOR_PERIOD; the first row of a series is not an
      error and is not omitted.
      Prior value is exactly zero → ZERO_BASE; growth from zero is undefined, not
      infinite and not 100%.
      Every period in the requested range appears in the output exactly once,
      computed or not. Row count out always equals period count in.

  - name: write_growth_table
    description: >
      Writes growth_output.csv and prints a summary the operator can check before
      trusting the file.
    input: "rows (list of dicts from compute_growth) and output_path (str)."
    output: >
      Writes the CSV with the eleven columns in fixed order and returns the row
      count. Prints to stderr: rows written, and counts by status so uncomputed
      rows are visible without opening the file.
    error_handling: >
      Before writing, asserts that no row has a blank, "All", or "Total" ward or
      category — the last gate against an aggregated row reaching the file.
      Asserts that no row has a growth_pct while its status is not OK.
      A failed assertion exits non-zero and writes nothing rather than emitting a
      table that violates the contract in agents.md.
      Unwritable output path → message to stderr and exit 1.