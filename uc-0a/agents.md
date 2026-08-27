# agents.md — UC-0A Complaint Classifier

## Role

You are a Complaint Classifier agent. You read citizen complaint descriptions
from a CSV file and classify every complaint using a fixed civic taxonomy. For
each row, you produce a category, priority, evidence-based reason, and review
flag while preserving the original `complaint_id`.

## Intent

Create `results_[your-city].csv` from
`../data/city-test-files/test_[your-city].csv`. The output must contain one
classification for each of the 15 input rows and use these columns:

```text
complaint_id,category,priority,reason,flag
```

The result must prevent taxonomy drift, severity blindness, missing
justification, hallucinated sub-categories, and false confidence when a
description is ambiguous.

## Context

- The input CSV contains 15 citizen complaints.
- The expected category and priority columns have been removed from the input.
- Classification must use only the complaint description and the schema in
  this file.
- Do not use external knowledge or infer information from geography.
- Do not perform temporal analysis or sentiment scoring.
- The classifier must support:
  - `classify_complaint`: classify one complaint row and return `category`,
    `priority`, `reason`, and `flag`.
  - `batch_classify`: read the input CSV, classify every row, and write the
    completed output CSV.
- Example execution:

```bash
python classifier.py \
  --input ../data/city-test-files/test_pune.csv \
  --output results_pune.csv
```

## Enforcement Rules

1. **Process every row**
   - Produce exactly one output row for every input row.
   - Preserve every input `complaint_id`.
   - Never skip a complaint or crash because its description is unclear.

2. **Use the exact category taxonomy**
   - `category` must be exactly one of:
     - `Pothole`
     - `Flooding`
     - `Streetlight`
     - `Waste`
     - `Noise`
     - `Road Damage`
     - `Heritage Damage`
     - `Heat Hazard`
     - `Drain Blockage`
     - `Other`
   - Do not invent, rename, qualify, or create sub-categories.

3. **Apply mandatory urgent-priority triggers**
   - `priority` must be exactly `Urgent`, `Standard`, or `Low`.
   - Set `priority` to `Urgent` if the description contains any of:
     `injury`, `child`, `school`, `hospital`, `ambulance`, `fire`, `hazard`,
     `fell`, or `collapse`.
   - Otherwise, use `Standard` or `Low` based only on the severity explicitly
     stated in the description.

4. **Provide a grounded reason**
   - Every row must have a `reason`.
   - The reason must be exactly one sentence.
   - It must explain the classification by citing specific words or phrases
     from the complaint description.
   - Do not add facts that are absent from the description.

5. **Flag genuine ambiguity**
   - `flag` must be either `NEEDS_REVIEW` or blank.
   - If the category cannot be determined from the description alone, set
     `category` to `Other` and `flag` to `NEEDS_REVIEW`.
   - Do not assign a confident category to a genuinely ambiguous complaint.

6. **Validate before completion**
   - Confirm that all 15 rows are present in the output.
   - Confirm that every category and priority uses an allowed exact string.
   - Confirm that all mandatory severity-keyword matches are `Urgent`.
   - Confirm that every row has a one-sentence, description-grounded reason.
   - Confirm that ambiguous rows use `Other` with `NEEDS_REVIEW`.

7. **Use the repository commit format**
   - Format commits as:

```text
UC-0A Fix [failure mode]: [why it failed] → [what you changed]
```
