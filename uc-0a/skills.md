# skills.md

skills:
  - name: classify_complaint
    description: Classify one complaint row into normalized `category`, `priority`, `reason`, and `flag` using the UC-0A closed taxonomy and severity keyword enforcement.
    input:
      - One CSV row as a dict (e.g., `dict[str, str]`) containing the complaint’s description text in one or more columns (the implementation may concatenate text fields or pick the relevant description column).
      - The row may include an identifier column (e.g., `complaint_id`) but the agent must not rely on it being present.
    output:
      - A dict with keys: `complaint_id`, `category`, `priority`, `reason`, `flag`
      - `category`: one of {Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other} (exact strings)
      - `priority`: one of {Urgent, Standard, Low}
      - `reason`: exactly one sentence that cites specific words from the complaint description
      - `flag`: either "NEEDS_REVIEW" or blank ("")
    error_handling:
      - If the description is empty/missing or provides no discriminating evidence for category, return the refusal condition mapping:
        category = "Other", priority = "Standard", flag = "NEEDS_REVIEW", and `reason` must explain the unclear evidence using available text.
      - If required fields for output are not derivable, prefer safe defaults (Other/Standard) and set NEEDS_REVIEW instead of guessing confidently.

  - name: batch_classify
    description: Read the UC-0A input CSV, classify each row using `classify_complaint`, and write a results CSV with the required output columns.
    input:
      - `input_path: str` path to `../data/city-test-files/test_[city].csv`
      - Must read CSV rows even when some rows are malformed.
    output:
      - `output_path: str` CSV written to `uc-0a/results_[city].csv` (path is provided by caller)
      - Output rows must include columns consistent with `classifier.py` expectations: `complaint_id`, `category`, `priority`, `reason`, `flag`.
      - For each input row, produce an output row (even on per-row failures) by using error-handling defaults and/or NEEDS_REVIEW.
    error_handling:
      - If a row cannot be parsed or lacks a description field, still emit an output row for that input row with refusal-condition defaults (category=Other, priority=Standard, flag=NEEDS_REVIEW) and a grounded one-sentence reason.
      - Must not crash the whole batch on a single bad row; continue processing remaining rows.
      - Ensure CSV writing does not drop rows; keep row order stable if possible.

