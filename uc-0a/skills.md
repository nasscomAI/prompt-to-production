skills:
  - name: classify_complaint
    description: Processes a single text description of a municipal complaint to extract its structured category, priority status, justification reason, and review flag.
    input: String containing the raw text description of the citizen's complaint.
    output: A structured tuple containing exactly (category: String, priority: String, reason: String, flag: String).
    error_handling: If the input is empty or shorter than 15 characters, it assigns the category 'Other' and sets the flag to 'NEEDS_REVIEW' instead of crashing.

  - name: batch_classify
    description: Reads an input CSV file containing multiple citizen complaints, iterates through each row using the single complaint classifier skill, and exports a fully populated results CSV file.
    input: File paths for both the raw input CSV file and the target output destination CSV file.
    output: A physically saved CSV file containing all original data columns alongside the four newly appended classification fields.
    error_handling: Validates the physical existence of the input file before execution; terminates gracefully with an explicit console message if the target file is missing.

