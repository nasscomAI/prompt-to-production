# skills.md — UC-0A Complaint Classifier

## Skill: classify_complaint
- **Input**: A dictionary representing a single complaint row (keys: `complaint_id`, `description`, etc.)
- **Process**:
  1. Inspect `description` against the strict category list: `Pothole`, `Flooding`, `Streetlight`, `Waste`, `Noise`, `Road Damage`, `Heritage Damage`, `Heat Hazard`, `Drain Blockage`, `Other`.
  2. Check for severity trigger keywords: `injury`, `child`, `school`, `hospital`, `ambulance`, `fire`, `hazard`, `fell`, `collapse`. If present, set priority to `Urgent`. Otherwise, default to `Standard` or `Low` based on urgency.
  3. Extract a single-sentence reason citing exact phrase/words from `description`.
  4. If category is ambiguous, mark `flag` as `NEEDS_REVIEW`.
- **Output**: Dictionary with keys `complaint_id`, `category`, `priority`, `reason`, `flag`.

## Skill: batch_classify
- **Input**: `input_path` (CSV path), `output_path` (CSV target path)
- **Process**: Read input CSV, run `classify_complaint` for each row, handle nulls/errors gracefully, and write results CSV.
- **Output**: Writes CSV to `output_path`.
