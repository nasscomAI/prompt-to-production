# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category, priority, reason, and flag using only the complaint description.
    input: >
      A dict representing one CSV row, with at least the keys `complaint_id`
      and `description` (other columns such as city, ward, location may be
      present but are ignored for category/priority decisions).
    output: >
      A dict with exactly these keys — complaint_id, category, priority, reason,
      flag. category is one of the ten allowed strings; priority is Urgent /
      Standard / Low; reason is a one-sentence justification citing words from
      the description; flag is "NEEDS_REVIEW" or "".
    error_handling: >
      If the description is missing, empty, or unrecognisable, return
      category "Other", priority "Standard", flag "NEEDS_REVIEW", and a reason
      explaining that the description was insufficient. Never raises on a single
      bad row. If a severity keyword is present, priority is forced to Urgent
      even when the category is ambiguous.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to every row, and writes a results CSV.
    input: >
      input_path (str) to a CSV with a header row including `complaint_id` and
      `description`; output_path (str) for the results file.
    output: >
      A CSV written to output_path with columns
      complaint_id, category, priority, reason, flag — one row per input row,
      in the same order. Returns a small summary (rows processed, rows flagged).
    error_handling: >
      Rows that fail to classify are still written with category "Other",
      flag "NEEDS_REVIEW", and a reason describing the error — the run never
      crashes on a bad row and always produces a complete output file. If the
      input file is missing or has no `description` column, it raises a clear
      error before processing rather than writing a partial file.
