# skills.md

skills:
  - name: classify_complaint
    description: Classify a single citizen complaint description into category, priority, reason, and flag per the Classification Schema.
    input: Single complaint row object / string `description` (e.g. `{ "description": "..." }`).
    output: Object with exactly `{ category, priority, reason, flag }` where `category` is one of Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other; `priority` is one of Urgent, Standard, Low; `reason` is one sentence quoting words from the description; `flag` is NEEDS_REVIEW or blank.
    error_handling: If description is empty, missing, or too vague to map to a single category, return `category: Other` with `flag: NEEDS_REVIEW` and a reason stating the ambiguity; never invent a sub-category or leave a field blank.

  - name: batch_classify
    description: Read an input city CSV, apply classify_complaint to each row, and write results to the output CSV.
    input: Input CSV path `../data/city-test-files/test_[your-city].csv` (15 rows, `category` and `priority_flag` stripped) and output CSV path `uc-0a/results_[your-city].csv`; invoked as `python classifier.py --input <in> --output <out>`.
    output: Output CSV with one row per input row containing `category, priority, reason, flag` conforming to the schema; preserves input row order and count.
    error_handling: If input file is missing, malformed, or a row has no usable description, emit that row as `category: Other, priority: Standard, reason: <one sentence noting missing/unclear description>, flag: NEEDS_REVIEW` and continue processing remaining rows; fail loudly if output cannot be written.
