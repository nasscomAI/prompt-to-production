skills:
  - name: classify_complaint
    description: Analyzes a single citizen complaint description and categorizes it strictly based on the provided taxonomy and severity rules.
    input: A single string or dictionary containing the citizen complaint description and location details.
    output: A dictionary containing 'category', 'priority', 'reason', and 'flag'.
    error_handling: If the complaint description cannot be classified properly or is ambiguous, output category as "Other", calculate priority based on severity keywords, output the reason citing the text, and flag as "NEEDS_REVIEW".

  - name: batch_classify
    description: Reads a batch of complaints from an input CSV file and processes them row by row using the classify_complaint skill, then writes the results to an output CSV.
    input: File paths to the input CSV containing rows of complaints (with a 'description' column).
    output: Writes a new CSV to the specified output path with columns for 'complaint_id', 'category', 'priority', 'reason', and 'flag'.
    error_handling: Flags null rows, doesn't crash on bad rows, and ensures an output row is still produced even if the underlying classification step fails for a specific input row.
