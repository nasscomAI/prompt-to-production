# skills.md

skills:
  - name: classify_complaint
    description: Analyzes a single citizen complaint description to determine its category, priority, reason, and flag.
    input: A single dictionary representing a CSV row of a complaint (contains description).
    output: A dictionary containing the target keys 'category', 'priority', 'reason', and 'flag'.
    error_handling: If the text is genuinely ambiguous or missing, classify as 'Other' and set flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Iterates over a dataset of complaints, applying classify_complaint to each, and outputs the final classifications to a CSV.
    input: File paths for both input CSV and output CSV as strings.
    output: Writes a new CSV file to the specified output path containing processed classification fields.
    error_handling: Must flag nulls and must not crash on bad or malformed rows. Continues processing and produces output even if some rows fail.
