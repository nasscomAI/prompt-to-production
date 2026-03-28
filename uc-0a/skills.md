skills:
  - name: classify_complaint
    description: Classifies a single civic complaint row into its appropriate category, priority, reason, and review flag.
    input: A single raw complaint row or text description.
    output: A structured record containing exact category, priority severity, one-sentence reason, and an optional NEEDS_REVIEW flag.
    error_handling: If the input is completely ambiguous or incomprehensible, output category "Other", flag "NEEDS_REVIEW", and cite the reason as ambiguous text.

  - name: batch_classify
    description: Reads an input CSV containing missing classifications, applies the classify_complaint skill per row, and writes the output CSV.
    input: File path to the input CSV containing citizen complaints (e.g., ../data/city-test-files/test_[your-city].csv).
    output: File path to the newly written output CSV (e.g., uc-0a/results_[your-city].csv) containing all row classifications.
    error_handling: If the input file is missing or corrupted, report a file read error and halt; for individual malformed rows, mark with NEEDS_REVIEW instead of crashing the batch process.
