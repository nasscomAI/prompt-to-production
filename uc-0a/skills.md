# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single complaint row by determining its category, priority level, and providing justification based on the complaint description.
    input: Dictionary containing complaint data with keys 'complaint_id' (string) and 'description' (string). The description field contains the citizen's complaint text.
    output: Dictionary with keys 'complaint_id' (string), 'category' (string from allowed list), 'priority' (string: Urgent/Standard/Low), 'reason' (string: one sentence), 'flag' (string: NEEDS_REVIEW or empty). All fields are mandatory.
    error_handling: If description is missing or empty, return category='Other', priority='Standard', reason='No description provided', flag='NEEDS_REVIEW'. If category cannot be determined confidently, return category='Other' and flag='NEEDS_REVIEW'. Never crash on malformed input.

  - name: batch_classify
    description: Reads a CSV file containing multiple complaint rows, applies classify_complaint to each row, and writes the classification results to an output CSV file.
    input: Two string parameters - input_path (path to source CSV file with columns 'complaint_id' and 'description') and output_path (path where results CSV should be written).
    output: Creates a CSV file at output_path with columns 'complaint_id', 'category', 'priority', 'reason', 'flag'. Returns nothing but prints completion message to console.
    error_handling: If input file is missing or cannot be read, raise FileNotFoundError with clear message. If a row fails classification, log the error but continue processing remaining rows. Always produce output file even if some rows fail. Flag rows with processing errors with NEEDS_REVIEW.
