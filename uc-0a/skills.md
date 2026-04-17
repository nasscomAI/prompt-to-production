# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Analyzes a single complaint description to determine its category, priority, and justification.
    input: String containing the citizen's complaint description.
    output: |
      Object containing:
      - category: One of the 10 allowed taxonomic strings.
      - priority: "Urgent", "Standard", or "Low".
      - reason: A one-sentence justification citing specific words from the description.
      - flag: "NEEDS_REVIEW" (if ambiguous) or empty string.
    error_handling: Return category "Other" and flag "NEEDS_REVIEW" if the description is blank or the complaint type is completely unrecognizable.

  - name: batch_classify
    description: Automates the classification process for an entire dataset from a CSV file.
    input: File path to the input CSV (e.g., `../data/city-test-files/test_pune.csv`).
    output: File path to the generated output CSV (e.g., `results_pune.csv`) with `category`, `priority`, `reason`, and `flag` columns appended or updated.
    error_handling: Handle file not found errors gracefully; log and skip malformed rows without interrupting the entire batch process.
