---
name: Complaint Classification Skills
description: Deterministic methods to process and classify incoming civic complaints
---

# Skills

## 1. classify_complaint
**Description:** Evaluates a raw complaint and returns a classified schema mapping its contents deterministically.
**Input:** `dict` (A CSV row mapping with `complaint_id` and `description`).
**Output:** `dict` (Classified row containing `complaint_id`, `category`, `priority`, `reason`, and `flag`).
**Constraints:** 
- Must handle missing/invalid descriptions.
- Ensure all dictionary keys match the required output format.
- Catch anomalies and flag properly instead of crashing.

## 2. batch_classify
**Description:** Iterates through an unclassified CSV row-by-row and writes evaluations to a destination path safely.
**Input:** 
- `input_csv_path`: path to source file
- `output_csv_path`: path where result is saved
**Output:** Writes directly to the `output_csv_path` CSV.
**Constraints:**
- Must not crash on bad or structurally malformed rows.
- Handle nulls naturally resulting in review flags.
- Always produce an output file with identical row counts to the source elements even under failure.
skills:
  - name: classify_complaint
    description: >
      Classifies a single complaint row into category, priority, reason, and flag using deterministic keyword rules.
    input: >
      A dictionary representing a CSV row with at least 'complaint_id' and 'description' fields.
    output: >
      A dictionary with keys: complaint_id, category, priority, reason, flag.
    error_handling: >
      If description is missing or empty, returns category as 'Other', priority as 'Low',
      reason as 'No description provided', and flag as 'NEEDS_REVIEW'. Ensures no crashes.

  - name: batch_classify
    description: >
      Processes an input CSV file of complaints, applies classification to each row, and writes results to an output CSV file.
    input: >
      Input file path (string) and output file path (string).
    output: >
      Writes a CSV file with classified complaint rows including complaint_id, category, priority, reason, and flag.
    error_handling: >
      Handles file not found errors gracefully. Continues processing even if individual rows fail,
      marking failed rows as 'Other' with 'NEEDS_REVIEW'. Ensures output file is always generated.