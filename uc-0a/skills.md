skills:
  - name: classify_complaint
    description: >
      Assigns a category, a priority, a cited reason and an ambiguity flag to exactly
      one complaint row, using only that row's own fields.
    input: >
      dict — one CSV row with keys complaint_id, date_raised, city, ward, location,
      description, reported_by, days_open. Only description is treated as deciding
      evidence; complaint_id is carried through to the output.
    output: >
      dict with exactly five keys — complaint_id (str), category (one of the ten
      permitted strings), priority (Urgent | Standard | Low), reason (one sentence
      containing a literal substring of the description), flag (NEEDS_REVIEW or "").
    error_handling: >
      Missing or blank description, or a description matching no category keyword,
      returns category Other, priority Standard, flag NEEDS_REVIEW and a reason
      stating that the text does not support a determination. Two competing explicit
      defect phrases return the first-mentioned category plus NEEDS_REVIEW naming the
      runner-up. Never raises, never returns None, never emits a category outside
      the permitted ten.

  - name: batch_classify
    description: >
      Reads an input complaints CSV, applies classify_complaint to every row in file
      order, writes the five-column results CSV, and reports a per-run summary of
      counts, urgent rows and flagged rows.
    input: >
      input_path (str) — path to test_[city].csv;
      output_path (str) — path for results_[city].csv.
    output: >
      Writes CSV with header complaint_id,category,priority,reason,flag — one row per
      input row, in input order. Returns a summary dict with rows_in, rows_out,
      urgent, flagged, and failed_rows for stdout reporting.
    error_handling: >
      A row that raises during classification is caught, counted in failed_rows, and
      still written as Other / NEEDS_REVIEW — so one bad row can never cost the whole
      batch. A missing input file or a file lacking the description column fails fast
      with an explicit message before any output is written, rather than producing a
      silently empty results file. Asserts rows_out == rows_in before exiting.
