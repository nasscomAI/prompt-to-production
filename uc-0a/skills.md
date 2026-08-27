# skills.md — UC-0A Complaint Classifier

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint according to the predefined taxonomy and evaluates its priority based on severity keywords.
    input: A single complaint row (dictionary/object) containing the complaint details, primarily the text description.
    output: A structured classification mapped to exactly four fields (category, priority, reason, flag).
    error_handling: If the category is ambiguous or impossible to definitively infer, it flags the row with `NEEDS_REVIEW` instead of halting.

  - name: batch_classify
    description: Reads an input CSV file, iterates through the rows applying classify_complaint to each, and streams the results to an output CSV.
    input: The file path strings for the input CSV and the intended output CSV destination.
    output: A generated CSV file containing the parsed and classified complaints mapping to their complaint_id.
    error_handling: Flags missing or null values and elegantly skips or records bad rows, ensuring the script does not crash entirely and still produces an output file for the valid records.
