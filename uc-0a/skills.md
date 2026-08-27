# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single raw citizen complaint row into the target taxonomy, determines its severity-based priority, provides a citation-backed reason, and flags it if ambiguous.
    input: A dictionary representing a single complaint record, containing at least the keys 'complaint_id' and 'description'.
    output: A dictionary containing the keys 'complaint_id', 'category', 'priority', 'reason', and 'flag'.
    error_handling: If the input row is malformed or description is empty, categories are set to 'Other', priority is 'Standard', reason is 'Missing or invalid description', and flag is set to 'NEEDS_REVIEW'. If the category is ambiguous, category is set to 'Other' and flag is set to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads citizen complaints from an input CSV file, applies the classify_complaint skill to each row, and writes the results to an output CSV file.
    input: Two string arguments: input_path (path to the input CSV file) and output_path (path to write the output CSV file).
    output: None (writes the classified output directly to the specified output file path).
    error_handling: Handles individual row failures gracefully without crashing, flags null values, logs error messages for bad rows, and ensures all other rows are processed and written to the output file.
