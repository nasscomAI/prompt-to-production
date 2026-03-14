# UC-0A Complaint Classifier — Agent Definition

## Role

A **Complaint Classification Agent** that reads city complaint data from CSV files and assigns each complaint to exactly one category. The agent operates within a rule-based keyword classification boundary — no external APIs or ML models. It must produce deterministic, reproducible outputs.

## Intent

A correct output is:

- **Structured JSON** for each complaint with: `complaint_id`, `category`, `reason`, `confidence`
- **Category** is exactly one of: `sanitation`, `roads`, `water`, `electricity`, `others`
- **Reason** cites specific words or phrases from the complaint description that justify the category
- **Confidence** is `high`, `medium`, or `low` based on keyword match strength
- Classification results are printed to console and optionally written to JSON file

## Context

The agent may use:

- The `description` field from each complaint row (primary input)
- Optionally the `location` field for disambiguation
- A predefined keyword map for each category
- Only the columns present in the input CSV; it must not assume additional columns exist

Exclusions:

- The agent does not use `complaint_id`, `date_raised`, `city`, `ward`, `reported_by`, or `days_open` for classification logic
- No external data sources or APIs

## Task Flow

1. **Load** — Read CSV file(s) from `data/city-test-files/` or user-specified path
2. **Extract** — For each row, extract `complaint_id` and `description` (and `location` if needed)
3. **Classify** — Apply rule-based keyword matching against category definitions
4. **Output** — Produce JSON structure and print results
5. **Persist** — Write full results to output file (CSV or JSON)

## Reasoning Approach

- **Keyword priority**: Check categories in order: sanitation, roads, water, electricity. First strong match wins.
- **Multi-signal**: If a complaint contains keywords from multiple categories, the category with the strongest/most specific match takes precedence.
- **Fallback**: If no keyword matches, assign `others` with `confidence: low` and `reason: "No matching keywords found"`.
- **Transparency**: Always include a `reason` field citing the matched keywords so output is auditable.

## Enforcement Rules

- Category must be exactly one of: `sanitation`, `roads`, `water`, `electricity`, `others`
- Every output must include `complaint_id`, `category`, `reason`, `confidence`
- If `description` is empty or null, output `category: others`, `confidence: low`, `reason: "Empty description"`
- If CSV has no `description` column, skip row and add to error log
- Output must be valid JSON (when writing JSON) or valid CSV (when writing CSV)
