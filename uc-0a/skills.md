# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Turns one complaint row into a category, priority, cited reason and review flag using a fixed keyword table.
    input: >
      dict with at least complaint_id and description (string); location is optional
      and used only as supporting evidence for Heritage Damage.
    output: >
      dict {complaint_id, category, priority, reason, flag} where category is one of the
      10 allowed strings, priority is Urgent | Standard | Low, reason is one sentence
      quoting matched words, flag is "NEEDS_REVIEW" or "".
    error_handling: >
      Empty/missing description → Other / Standard / NEEDS_REVIEW with reason
      "Description missing". No keyword match → Other + NEEDS_REVIEW. Tie between two
      categories → first-mentioned wins + NEEDS_REVIEW. Never raises on bad text.

  - name: batch_classify
    description: Reads a city test CSV, applies classify_complaint to every row, and writes the results CSV.
    input: >
      input_path (CSV with header complaint_id, date_raised, city, ward, location,
      description, reported_by, days_open) and output_path (string).
    output: >
      CSV at output_path with header complaint_id, category, priority, reason, flag —
      one row per input row, same order. Prints a count summary (rows, Urgent, flagged).
    error_handling: >
      Missing input file or missing description column → exits with a clear message
      and no partial file. An exception on a single row is caught; that row is written
      as Other / Standard / NEEDS_REVIEW with the error in the reason, and the batch continues.
