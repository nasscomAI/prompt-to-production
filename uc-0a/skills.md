skills:
  - name: classify_complaint
    description: Classifies a single complaint description into one of ten allowed categories and a priority level, including severity flags and a citation reason.
    input: A dictionary representing a single row from the complaint data, with keys like 'complaint_id' and 'description'.
    output: A dictionary containing the keys 'complaint_id', 'category', 'priority', 'reason', and 'flag'.
    error_handling: If the description is missing or null, output category 'Other', priority 'Standard', reason 'Missing description', and flag 'NEEDS_REVIEW'. If the category is ambiguous, set flag to 'NEEDS_REVIEW' and category to 'Other'.

  - name: batch_classify
    description: Reads citizen complaints from an input CSV file, applies the single complaint classifier per row, and writes the results to an output CSV file.
    input: An input file path to a CSV containing citizen complaints, and an output file path to write results.
    output: Writes a CSV file at the specified output path containing 'complaint_id', 'category', 'priority', 'reason', and 'flag' for each row.
    error_handling: Catches errors on invalid or malformed rows without crashing. Missing descriptions in rows are flagged, and output is generated even if some rows fail to classify.
