# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint into a standard category, priority, and reason, flagging if ambiguous.
    input: A dictionary or string representing a single complaint row, specifically focusing on the 'description' field.
    output: A JSON object containing exactly four keys - 'category' (string), 'priority' (string), 'reason' (string), and 'flag' (string).
    error_handling: Return category 'Other', priority 'Low', reason 'Unparseable or invalid input text.', flag 'NEEDS_REVIEW' if input is fully unparseable.

  - name: batch_classify
    description: Reads a batch of complaints from a CSV, applies classify_complaint to each row, and writes the output to a new CSV.
    input: input_path (string) representing the source CSV, output_path (string) for the destination CSV.
    output: A CSV file containing the original complaint_id plus the new fields category, priority, reason, and flag.
    error_handling: If a row fails to process or API fails, write default error classification for that row but do NOT crash the batch process.
