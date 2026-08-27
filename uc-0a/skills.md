# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classify a single complaint row into a fixed-taxonomy category and a priority, with a cited reason.
    input: A dict representing one CSV row. Must contain at least complaint_id and description.
    output: A dict with keys complaint_id, category, priority, reason, flag. category is one of the 10 allowed values; priority is Urgent/Standard/Low; flag is "NEEDS_REVIEW" or "".
    error_handling: Empty/missing description -> category Other, flag NEEDS_REVIEW. No category keyword match -> Other, flag NEEDS_REVIEW. Tie between categories -> deterministic pick by declaration order, flag NEEDS_REVIEW. Severity keyword always forces Urgent regardless of category.

  - name: batch_classify
    description: Read an input CSV of complaints, classify every row, and write a results CSV.
    input: input_path (path to test_[city].csv), output_path (path to write results CSV).
    output: A CSV with columns complaint_id, category, priority, reason, flag — one row per input row. Also prints a summary count of Urgent and NEEDS_REVIEW rows.
    error_handling: Any row that raises is caught and written as Other / NEEDS_REVIEW with the error in the reason field; the batch always completes and always writes output.
