skills:
  - name: classify_complaint
    description: Takes a single citizen complaint row as input and produces a strictly classified output mapping its category, priority level, justification reason, and required ambiguity flags.
    input: dict containing at least a description field with the citizen complaint text.
    output: dict containing complaint_id, category, priority, reason, and flag.
    error_handling: Maps category to 'Other' and sets flag to 'NEEDS_REVIEW' when the description lacks clear context or keywords.

  - name: batch_classify
    description: Reads a source CSV containing hundreds of complaint rows, executes classify_complaint per row, and outputs a formatted result CSV safely.
    input: input_path (string) for the source CSV and output_path (string) for the destination CSV.
    output: Writes parsed results into a CSV with specified fieldnames.
    error_handling: Wraps individual row processing and file IO blocks in try-except statements so valid rows still proceed and write output rather than throwing a system-halting crash.
