skills:
  - name: classify_complaint
    description: Analyzes a single citizen complaint description to determine its category, priority, reason, and ambiguity flag.
    input: A dictionary containing a single complaint row (must include 'description').
    output: A dictionary with keys 'category', 'priority', 'reason', and 'flag'.
    error_handling: If the text is genuinely ambiguous or the category cannot be confidently determined, sets 'flag' to 'NEEDS_REVIEW' and ensures a default fallback output without crashing.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint sequentially, and writes the results to an output CSV.
    input: The file path to the input CSV and the desired file path for the output CSV.
    output: A new CSV file saved at the output path containing the classified results.
    error_handling: Flags null rows, catches row-level exceptions to avoid crashing, and ensures an output file is produced even if some individual rows fail.
