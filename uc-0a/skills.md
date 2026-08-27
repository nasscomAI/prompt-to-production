# skills.md
# Defines the UC-0A skills used by the complaint classifier agent.

skills:
  - name: classify_complaint
    description: Classify a single complaint row into the UC-0A schema with category, priority, reason, and flag.
    input: |
      A single complaint record containing fields such as `description` and any other relevant row data.
    output: |
      An object with keys `category`, `priority`, `reason`, and `flag`.
      - `category`: one of the allowed UC-0A categories
      - `priority`: Urgent, Standard, or Low
      - `reason`: a one-sentence explanation citing specific words from the description
      - `flag`: `NEEDS_REVIEW` or blank
    error_handling: If the complaint is ambiguous, set `category: Other`, `flag: NEEDS_REVIEW`, and still return a reason citing the ambiguity.

  - name: batch_classify
    description: Read the input CSV file, apply `classify_complaint` to each row, and write the output CSV file.
    input: |
      A path to the input CSV file and a path to the desired output CSV file.
    output: |
      A completed output CSV containing the original rows plus the enforced `category`, `priority`, `reason`, and `flag` columns.
    error_handling: If input data is missing required fields or is malformed, report the issue and do not produce partial output.
