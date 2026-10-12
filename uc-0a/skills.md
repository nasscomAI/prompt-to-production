skills:
  - name: classify_complaint
    description: Classifies one complaint row into category, priority, reason and flag using only the description text and the fixed UC-0A schema.
    input: >
      dict representing one CSV row with string keys complaint_id and description
      (other columns such as ward, location, reported_by are passed through but ignored).
    output: >
      dict with keys complaint_id (str), category (str, one of the 10 allowed values),
      priority (str, Urgent | Standard | Low), reason (str, one sentence citing words
      from the description), flag (str, NEEDS_REVIEW or empty string).
    error_handling: >
      Missing or blank description -> category Other, priority Low, flag NEEDS_REVIEW,
      reason states the description was empty. No category keyword matched -> category
      Other, flag NEEDS_REVIEW (no guessing, avoids hallucinated sub-categories).
      Keywords for two or more categories matched -> primary category chosen by the
      documented precedence order, flag NEEDS_REVIEW (avoids false confidence).
      Severity keyword present -> priority forced to Urgent regardless of category
      (avoids severity blindness).

  - name: batch_classify
    description: Reads the input city CSV, applies classify_complaint to every row and writes the results CSV.
    input: >
      input_path (str) to a UTF-8 CSV with header complaint_id,date_raised,city,ward,
      location,description,reported_by,days_open; output_path (str) for the results CSV.
    output: >
      UTF-8 CSV at output_path with header complaint_id,category,priority,reason,flag
      and exactly one row per input row, in input order. Returns a summary dict of
      row count, Urgent count and NEEDS_REVIEW count.
    error_handling: >
      Input file missing or missing the description/complaint_id columns -> stop with a
      clear error before writing anything. A single bad row (exception during
      classification) -> write a row with category Other, priority Low, flag
      NEEDS_REVIEW and the error in reason, then continue with the next row. Never
      silently skip a row.
