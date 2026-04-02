# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: classify_complaint
    description: Classifies one complaint row into a valid category, priority, reason, and flag using only the complaint text and schema rules.
    input: A dictionary representing one CSV row, including complaint_id and complaint description text.
    output: A dictionary with keys complaint_id, category, priority, reason, and flag.
    error_handling: If the row is missing key fields or the description is empty, return category as Other, priority as Low, a reason explaining the missing or unusable text, and flag as NEEDS_REVIEW.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to each row, and writes a results CSV without crashing on bad rows.
    input: Input CSV file path and output CSV file path.
    output: A CSV file where every input row produces one output row with complaint_id, category, priority, reason, and flag.
    error_handling: If a row causes an exception, the function must still write an output row for that complaint with safe fallback values and NEEDS_REVIEW instead of stopping the entire batch.
