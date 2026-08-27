skills:
  - name: load_dataset
    description: >
      Reads the ward budget ledger and reports its data quality before any
      arithmetic happens, so that a reader knows what is missing before they
      see a number derived from what remains.
    input: >
      input_path -- path to data/budget/ward_budget.csv, with columns period,
      ward, category, budgeted_amount, actual_spend, notes.
    output: >
      A tuple of (all rows as dicts, the subset whose actual_spend is empty).
      Before returning it prints the row count, the count of missing
      actual_spend cells, and one line per missing cell giving its period,
      ward, category and the verbatim notes text explaining the absence.
    error_handling: >
      A missing actual_spend is reported, never repaired. It is not filled from
      budgeted_amount, not carried forward from the previous period, not
      interpolated and not coerced to zero -- each of those produces a total
      that looks complete and is not. A row whose notes field is empty is
      reported as "(no reason given)" rather than omitted from the report, so
      an unexplained gap is still visible. An unreadable input file raises
      rather than returning an empty ledger, because zero rows and a failed
      read look identical downstream.

  - name: compute_growth
    description: >
      Computes period-over-period growth in actual spend for one ward and one
      category, or for every ward-category pair reported separately, showing
      the formula behind each figure.
    input: >
      rows -- the ledger as returned by load_dataset.
      ward -- one exact ward name, or None for every ward reported separately.
      category -- one exact category name, or None for every category.
      growth_type -- MoM or YoY. Required; there is no default.
    output: >
      A list of dicts, one per ward-category-period, each carrying ward,
      category, period, actual_spend, growth_type, growth_pct, formula and the
      source note. growth_pct is a signed percentage rounded to one decimal, or
      NO_PRIOR_PERIOD for the first period of a series, or MISSING_DATA where
      either the period or its comparison base has no spend figure. formula
      restates the arithmetic with both values substituted in, so any row can
      be recomputed by hand without the ledger or this code.
    error_handling: >
      Four conditions raise Refusal rather than returning a number.
      One: growth_type absent -- MoM and YoY answer different questions and a
      default would be misread as the type the caller asked for.
      Two: a request to aggregate across wards or categories -- a citywide
      growth figure is arithmetically valid and operationally useless, since no
      ward office can act on it.
      Three: an unrecognised ward or category name -- refused with the list of
      valid values, never matched to the nearest name and never returned as an
      empty result, which would read as "no spending" rather than "no such
      ward".
      Four: YoY against this ledger -- it spans 2024 only, so no row has a base
      twelve months earlier. Returning 300 uncomputable rows would look like a
      defect in the tool rather than a limit of the data.

  - name: write_results
    description: >
      Writes the computed rows to a results CSV in which every row is
      attributable to a single ward and category.
    input: >
      results -- rows from compute_growth. output_path -- destination CSV.
      missing_count -- number of missing cells found in the source ledger.
    output: >
      A CSV with the header ward,category,period,actual_spend,growth_type,
      growth_pct,formula,note,source_missing_rows and one row per input row.
      Returns None; the file is the product.
    error_handling: >
      The missing-row count is written as a column on every row, not as a
      trailing comment line. A "# 5 rows were missing" footer reads correctly
      to a human and makes the file unparseable to a CSV reader, which counts
      the comment as an extra data row -- a results file that silently corrupts
      its own consumer is the same class of failure as a total that silently
      excludes a ward.
