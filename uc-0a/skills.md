# skills.md — UC-0A Complaint Classifier

## Skill 1: `classify_complaint`
**Purpose**: Classify a single complaint row into `category`, `priority`, `reason`, and `flag`.

**Input**: A dictionary representing a complaint row (e.g., `{"complaint_id": "PM-202401", "description": "Large pothole 60cm wide causing tyre damage."}`).

**Output**: A dictionary with keys: `category`, `priority`, `reason`, and `flag`.

**Rules**:
- Use the predefined category list and severity keywords.
- Set `flag` to `NEEDS_REVIEW` if the category is ambiguous.
- The `reason` must cite specific words from the description.

---

## Skill 2: `batch_classify`
**Purpose**: Read an input CSV, apply `classify_complaint` to each row, and write the output CSV.

**Input**: Path to the input CSV file (e.g., `../data/city-test-files/test_pune.csv`).

**Output**: A CSV file with columns: `complaint_id`, `category`, `priority`, `reason`, and `flag`.

**Rules**:
- Preserve the `complaint_id` from the input.
- Output file must match the schema and enforcement rules.