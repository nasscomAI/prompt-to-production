skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into category, priority, reason, and review flag using the fixed municipal taxonomy.
    input: A dict with at minimum a 'complaint_id' and 'description' string field, plus optional context fields (city, ward, location).
    output: A dict with keys complaint_id (str), category (one of the 10 allowed values), priority (Urgent/Standard/Low), reason (str, one sentence quoting description words), flag (NEEDS_REVIEW or empty string).
    error_handling: If description is missing or empty, return category=Other, priority=Standard, reason="No description provided", flag=NEEDS_REVIEW.

  - name: batch_classify
    description: Reads an input CSV of complaint rows, applies classify_complaint to each, and writes a results CSV with the four classification fields appended.
    input: input_path (str path to CSV), output_path (str path for results CSV).
    output: Writes a CSV to output_path with columns complaint_id, category, priority, reason, flag. Returns count of rows processed and count flagged NEEDS_REVIEW.
    error_handling: Skips rows that cause exceptions (logs the complaint_id and error), continues processing remaining rows, and still writes the output file with whatever rows succeeded.
