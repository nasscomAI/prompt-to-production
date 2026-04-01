# skills.md — UC-0C Number That Looks Right

skills:
  - name: load_dataset
    description: Opens a CSV, strictly filters a single requested ward and category slice without implicit aggregation, and explicitly identifies any null values and their corresponding note reasons.
    input: Filepath (str), target_ward (str), and target_category (str).
    output: A strictly filtered list of dictionary objects for a single ward/category pair, sorted chronologically.
    error_handling: Throws a definitive `ValueError` or refusal string if `target_ward` or `target_category` is 'Any', missing, or improperly structured (enforcing boundaries against multi-ward sums).

  - name: compute_growth
    description: Calculates period-over-period metrics explicitly while retaining formulas, refusing undefined growth requests, and skipping missing periods with an overt flag.
    input: Filtered chronological list of data records and an explicit `growth_type`.
    output: Processed list of result dictionaries containing actual output, the applied formula string, and overt null flag handling.
    error_handling: Raises configuration errors if `growth_type` is unhandled, replacing calculations inherently with "Must be flagged — not computed" if previous or current variables are missing.
