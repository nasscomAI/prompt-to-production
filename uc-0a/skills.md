# skills.md

skills:
  - name: classify_complaint
    description: Analyzes a single citizen complaint row and determines its standardized category and priority.
    input: dict representing a CSV row with fields like 'description'.
    output: dict with 'complaint_id', 'category', 'priority', 'reason', 'flag'.
    error_handling: Maps ambiguous complaints to 'Other' category and sets 'flag' to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads an input CSV of complaints and iteratively applies the classify_complaint skill, writing results to an output CSV.
    input: input_path (string) representing the read file and output_path (string) for the destination.
    output: Writes parsed elements directly into the destination CSV file format.
    error_handling: Flags invalid rows with 'Error processing' and uses 'Other' as category, ensuring pipeline continues.
