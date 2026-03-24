skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into category, priority, reason, and flag based solely on the description field.
    input: A dict representing one CSV row with keys — complaint_id, date_raised, city, ward, location, description, reported_by, days_open.
    output: A dict with keys — complaint_id, category (one of the 9 allowed values or Other), priority (Urgent/Standard/Low), reason (one sentence citing specific words from description), flag (NEEDS_REVIEW or blank string).
    error_handling: If description is empty or None, output category=Other, priority=Low, reason="Description missing — cannot classify", flag=NEEDS_REVIEW. If description is present but genuinely ambiguous across categories, output category=Other and flag=NEEDS_REVIEW with reason explaining ambiguity.

  - name: batch_classify
    description: Reads an input CSV of complaint rows, applies classify_complaint to each, and writes the classified results to an output CSV.
    input: input_path (str) — path to a CSV file with complaint rows; output_path (str) — path where results CSV will be written.
    output: A CSV file at output_path containing all input rows plus four added columns — category, priority, reason, flag. Prints a summary to stdout: total rows processed, rows with NEEDS_REVIEW flag, and any rows that errored.
    error_handling: If a row fails classification (exception), write category=ERROR, priority=Low, reason="Classification failed — see logs", flag=NEEDS_REVIEW and continue to the next row. Never crash the entire batch because of a single bad row. Print count of errored rows at the end.
