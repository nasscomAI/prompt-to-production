# skills.md

skills:
  - name: classify_complaint
    description: Analyzes a single citizen complaint to determine its category and priority, extracting an evidence-based reason.
    input: A single complaint row with a text description.
    output: Category, priority, reason, and flag fields conforming to the enforcement schema.
    error_handling: Handles ambiguous complaints by classifying as best effort but explicitly setting the flag to NEEDS_REVIEW.

  - name: batch_classify
    description: Reads an input CSV file containing multiple complaint rows, processes each row via classify_complaint, and writes to an output CSV.
    input: Path to an input CSV file (e.g. `../data/city-test-files/test_[your-city].csv`).
    output: Path to an output CSV file (e.g. `uc-0a/results_[your-city].csv`) with all required schema fields included.
    error_handling: Reports processing failures for malformed rows but continues processing the rest of the batch.
