# skills.md — UC-0A Complaint Classifier

## Skill: classify_complaint
- **Input**: A dictionary representing a single complaint row (keys: `complaint_id`, `description`, etc.)
- **Process**:
  1. Inspect `description` against the strict category list: `Pothole`, `Flooding`, `Streetlight`, `Waste`, `Noise`, `Road Damage`, `Heritage Damage`, `Heat Hazard`, `Drain Blockage`, `Other`.
  2. Check for severity trigger keywords: `injury`, `child`, `school`, `hospital`, `ambulance`, `fire`, `hazard`, `fell`, `collapse`. If present, set priority to `Urgent`. Else set `Low` when the category is a nuisance class (`Noise`, `Heritage Damage`) and the description carries no risk signal (`risk`, `unsafe`, `safety`, `danger`, `accident`, `health`, `concern`, `injured`, `burns`, `structural`). Otherwise `Standard`.
  3. Build a single-sentence reason quoting the same keywords that selected the category, so justification and decision cannot diverge. Never emit a generic reason.
  4. If category is ambiguous, mark `flag` as `NEEDS_REVIEW`. `Other` always carries `NEEDS_REVIEW`.
- **Output**: Dictionary with keys `complaint_id`, `category`, `priority`, `reason`, `flag`.

## Skill: selftest
- **Input**: `data_dir` (directory of city test files; defaults to `../data/city-test-files`)
- **Process**: Classify every row of every city file and assert all four enforcement rules — allowed category, allowed priority, severity keywords force `Urgent`, and every reason quotes words present in that row's description.
- **Output**: Raises `AssertionError` naming the offending `complaint_id` on any violation; otherwise prints the row and file count. Run with `python classifier.py --selftest`.

## Skill: batch_classify
- **Input**: `input_path` (CSV path), `output_path` (CSV target path)
- **Process**: Read input CSV, run `classify_complaint` for each row, handle nulls/errors gracefully, and write results CSV.
- **Output**: Writes CSV to `output_path`.
