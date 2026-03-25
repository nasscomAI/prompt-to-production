skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint row into a standardized category, priority, reason, and flag.
    input: A dictionary containing a single complaint row with at least the 'description' field.
    output: A dictionary with exactly four keys - 'category' (string), 'priority' (string), 'reason' (string), and 'flag' (string or none).
    error_handling: Return category 'Other', flag 'NEEDS_REVIEW', priority 'Low', and a reason stating the ambiguity if input is unparsable or ambiguous.

  - name: batch_classify
    description: Reads an input CSV file of complaints, applies classify_complaint to each row, and writes the structured classifications to an output CSV file.
    input: Two string paths - 'input_path' (path to the test CSV file) and 'output_path' (path to save the results CSV file).
    output: None.
    error_handling: Must flag nulls or invalid rows and write them as failed/flagged without crashing the entire batch process.
