# skills.md

skills:
  - name: classify_complaint
    role: >
      A data processing skill that evaluates a single citizen complaint row and applies classification rules.
    intent: >
      To output a dictionary containing the classified `category`, `priority`, `reason`, and `flag`.
    context: >
      Receives a single row's complaint text/data. Must classify according to the defined schema without external assumptions.
    enforcement:
      - "Output must be a dictionary with keys: `category`, `priority`, `reason`, and `flag`."
      - "Return category='Other' and flag='NEEDS_REVIEW' if input is invalid or ambiguous."

  - name: batch_classify
    role: >
      A batch orchestration skill that manages the processing of multiple complaints from a CSV file.
    intent: >
      To read an input CSV, apply the `classify_complaint` skill to each row, and write the aggregated results to an output CSV.
    context: >
      Operates on file paths (input CSV and output CSV) and handles row-by-row execution.
    enforcement:
      - "Must read input CSV and write to output CSV."
      - "Must not crash on malformed rows; instead flag nulls/errors and continue."
      - "Produce final output CSV even if some rows fail."
