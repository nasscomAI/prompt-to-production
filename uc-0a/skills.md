# skills.md
# Skill definitions for UC-0A Complaint Classifier.

skills:
  - name: classify_complaint
    description: Classify a single complaint row into the UC-0A output schema.
    input: A mapping/dict representing one CSV row with keys including
      `description` (string) and optionally `complaint_id` (string).
    output: A dict with keys: `complaint_id` (string), `category` (one of the exact allowed strings),
      `priority` (Urgent|Standard|Low), `reason` (one-sentence string citing words from the description),
      and `flag` ("NEEDS_REVIEW" or empty string).
    error_handling: If `description` is missing or empty, return `category: Other`,
      `flag: NEEDS_REVIEW`, and a reason that states the description is empty. If multiple category
      keywords are present and equally plausible, set `category: Other`, `flag: NEEDS_REVIEW`,
      and include the matched keywords in the reason. Do not invent category values outside the
      allowed list. If severity keywords appear (injury, child, school, hospital, ambulance, fire, hazard, fell, collapse), set `priority: Urgent`.

  - name: batch_classify
    description: Read an input CSV, apply `classify_complaint` to each row, and write a results CSV.
    input: `input_path` (string path to CSV with header including `description`) and
      `output_path` (string path to write results CSV).
    output: Writes `output_path` CSV with header `complaint_id,category,priority,reason,flag` and returns
      a small report (dict) with `rows_processed` (int) and `rows_flagged` (int).
    error_handling: Continue processing when individual rows fail; for rows that trigger exceptions,
      write a result row with `category: Other`, `priority: Low`, `reason: "Error during classification; marked for review."`,
      and `flag: NEEDS_REVIEW`. Ensure output CSV always has the required header even if all rows fail.
