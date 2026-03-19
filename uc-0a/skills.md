# skills.md

skills:
  - name: classify_complaint
    description: Classify a single complaint row into the UC-0A schema.
    input: >
      One complaint row (dict/object) containing at minimum a free-text complaint description.
      The row must NOT already contain `category` or `priority_flag` labels (they are stripped in
      the test files).
    output: >
      An object with four fields:
      `category` (one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other),
      `priority` (one of: Urgent, Standard, Low),
      `reason` (exactly one sentence that cites words/phrases from the description),
      `flag` (NEEDS_REVIEW or blank).
    error_handling: >
      If the category is genuinely ambiguous from the description text alone, set `category` to
      Other and `flag` to NEEDS_REVIEW. Never invent new categories or variants; always return an
      allowed value.

  - name: batch_classify
    description: Read an input CSV, classify each row, and write an output CSV.
    input: >
      `input_path` to a CSV like `../data/city-test-files/test_[your-city].csv` and an `output_path`
      like `uc-0a/results_[your-city].csv`. The input contains 15 rows and is missing the `category`
      and `priority_flag` columns.
    output: >
      A CSV written to `output_path` containing the original rows plus appended columns:
      `category`, `priority`, `reason`, and `flag`, where each row obeys the UC-0A allowed values
      and urgency rules.
    error_handling: >
      If a row is missing a description or is otherwise unclassifiable, still emit an output row
      with `category` = Other, `priority` = Standard (unless urgency keywords are present),
      `reason` citing the issue (e.g. "missing description"), and `flag` = NEEDS_REVIEW.
