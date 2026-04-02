skills:
  - name: classify_complaint
    description: Takes one complaint description and returns category, priority, reason, and flag.
    input: Single complaint description as string.
    output: Dictionary with keys category, priority, reason, flag.
    error_handling: If description is empty or missing, set category=Other, priority=Low, reason=No description provided, flag=NEEDS_REVIEW.

  - name: batch_classify
    description: Reads input CSV row by row, applies classify_complaint to each, and writes results CSV.
    input: Input CSV file path and output CSV file path as strings.
    output: results_hyderabad.csv with all original columns plus category, priority, reason, flag.
    error_handling: If input file is missing, raise FileNotFoundError. If a row fails classification, write flag=NEEDS_REVIEW and continue.
