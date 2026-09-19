skills:
  - name: load_dataset
    description: Reads the ward budget CSV, validates its columns, and reports the null count and exactly which rows are null before returning any data.
    input: >
      File path (string) to a UTF-8 CSV with header
      period,ward,category,budgeted_amount,actual_spend,notes.
      period is YYYY-MM; amounts are floats; actual_spend may be blank.
    output: >
      A dataset object containing (1) rows: list of records with period, ward,
      category, budgeted (float), actual (float or None), notes, and source line
      number; (2) null_rows: every record whose actual_spend is blank or
      non-numeric, each with its reason taken from the notes column; (3)
      bad_rows: records excluded for a malformed period. The null report
      (total count, then period / ward / category / reason for each) is printed
      BEFORE the function returns.
    error_handling: >
      If the file is missing, unreadable, or lacks any required column, stop and
      raise an error naming the problem - never continue with partial data.
      A blank or non-numeric actual_spend is kept as a null and reported, never
      dropped, zero-filled, or imputed. If a null has an empty notes cell, report
      the reason as "no reason given in notes column". Rows with a malformed
      period are excluded and listed in the report rather than silently ignored.

  - name: compute_growth
    description: Takes one ward, one category and a growth type, and returns a per-period growth table with the formula shown on every row.
    input: >
      dataset (output of load_dataset); ward (string, exactly one ward);
      category (string, exactly one category); growth_type (string, MoM or YoY).
      Ward and category are matched ignoring case and dash style (- versus en
      dash) but must otherwise match a value in the data.
    output: >
      List of per-period rows sorted by period, each with: ward, category,
      period, actual_spend, prior_period, prior_actual_spend, growth_type,
      formula (numbers substituted, or NOT COMPUTED plus reason), growth_pct
      (one decimal, blank when not computed), flag, and note. Written to
      growth_output.csv by the caller.
    error_handling: >
      REFUSE (raise a refusal, write no output) when growth_type is missing or
      not MoM/YoY; when ward or category is missing, or is all / any / * / total
      (cross-ward or cross-category aggregation is not permitted); when ward or
      category matches nothing in the data (the valid values are listed); or
      when a ward + category + period appears more than once. Never guess a
      formula or a scope. Null current value -> flag NULL_ACTUAL_SPEND with the
      notes reason. Null prior value -> flag NULL_PRIOR_SPEND. Missing
      comparison period (first month for MoM, all months for YoY as the file
      holds 2024 only) -> flag NO_PRIOR_PERIOD. Prior value of zero -> flag
      ZERO_BASE. Flagged rows stay in the table with no growth value.
