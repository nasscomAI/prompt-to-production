skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into an exact category, assigns priority based on severity keywords, produces a one-sentence reason citing specific words from the description, and sets a NEEDS_REVIEW flag when the category is genuinely ambiguous.
    input: A dict representing one CSV row with at minimum a `complaint_id` and `description` field (string, plain text complaint description from a citizen).
    output: A dict with four keys — `category` (one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other), `priority` (Urgent | Standard | Low), `reason` (one sentence quoting specific words from the input description), `flag` (NEEDS_REVIEW or empty string).
    error_handling: If `description` is missing, null, or empty → set category to Other, priority to Low, reason to "No description provided", flag to NEEDS_REVIEW. If the description matches multiple categories equally → set flag to NEEDS_REVIEW and choose the closest match. Never hallucinate a category outside the allowed list.

  - name: batch_classify
    description: Reads an input CSV of citizen complaints (with stripped category and priority_flag columns), applies classify_complaint to each row, and writes a results CSV with all classification fields appended.
    input: Two string arguments — `input_path` (path to test_[city].csv, a CSV with columns including `complaint_id` and `description`) and `output_path` (desired path for the results CSV).
    output: A CSV file written to `output_path` containing all original columns plus `category`, `priority`, `reason`, and `flag` for every row. Produces output even if individual rows fail.
    error_handling: Rows that raise an exception during classification are caught individually — they are written to output with category=Other, priority=Low, reason="Classification error", flag=NEEDS_REVIEW. The batch never crashes; it logs row-level errors to stderr and continues processing remaining rows.
