# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single complaint row by determining its category, priority, reason, and flag based on its description.
    input: Single complaint row text description.
    output: Structured record with category, priority, reason, and flag.
    error_handling: When input is ambiguous or categorization is uncertain, flags as NEEDS_REVIEW instead of guessing with false confidence.

  - name: batch_classify
    description: Reads an input CSV file, applies the classify_complaint skill to each row, and writes the classification results to an output CSV file.
    input: Path to the input CSV file.
    output: Path to the written output CSV file containing the classifications.
    error_handling: Continues processing remaining rows if an individual row encounters an error; handles missing fields gracefully.
