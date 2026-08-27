# skills.md

skills:
  - name: classify_complaint
    description: Parses a single civic complaint row and applies strict lexical rules to classify the complaint into a valid category, determine standard/urgent priority, and provide a cited reasoning.
    input: Dictionary mapping single row headers (complaint_id, description, etc.) to string values.
    output: Dictionary with exact keys (complaint_id, category, priority, reason, flag) containing string values.
    error_handling: If the description is missing or invalid, it gracefully assigns the category 'Other', priority 'Low', and sets flag 'NEEDS_REVIEW' with a default missing reason.

  - name: batch_classify
    description: Orchestrates reading a CSV of complaints, applying classify_complaint sequentially, and writing the structured output results back to a target CSV path.
    input: Two strings representing the input file path and the output file path.
    output: Writes directly to the file system. Does not return an object.
    error_handling: Emits clear warning messages if the input file does not exist. Survives exceptions linearly across row processing, ensuring partial success by writing out as many classifications as possible and logging errors for failures with 'NEEDS_REVIEW' flags.
