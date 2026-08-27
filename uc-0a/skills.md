skills:
  - name: classify_complaint
    description: Analyzes a single complaint description and returns a structured dictionary based on taxonomy and priority rules.
    input: dictionary (single CSV row) containing 'complaint_id' and 'description'.
    output: dictionary with keys [complaint_id, category, priority, reason, flag].
    error_handling: If description is missing or empty, output category: Other, priority: Low, reason: "Empty input", flag: NEEDS_REVIEW.

  - name: batch_classify
    description: Reads a source CSV of compliant strings, applies classification per row, and writes to a target CSV.
    input: input_path (str), output_path (str).
    output: Writes CSV file with 5 defined columns; returns True on success.
    error_handling: Gracefully handle file I/O errors; if a specific row fails calculation, it should still be written to CSV with its ID and a NEEDS_REVIEW flag.
