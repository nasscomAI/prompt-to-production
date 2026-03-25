# skills.md

skills:
  - name: classify_complaint
    description: Analyzes a single citizen complaint description and determines its category, priority, reason, and flag.
    input: A single complaint row (dictionary or JSON) containing at minimum the complaint description text.
    output: A dictionary or JSON object containing exactly four keys: category (string), priority (string), reason (string), and flag (string).
    error_handling: If the input is empty or completely unreadable, returns category "Other", priority "Low", reason "Invalid input", and flag "NEEDS_REVIEW". If ambiguous, sets flag to "NEEDS_REVIEW".

  - name: batch_classify
    description: Reads an input CSV file of complaints, applies classify_complaint to each row, and writes the results to an output CSV file.
    input: input_path (string path to test_[city].csv) and output_path (string path to results CSV).
    output: Writes a CSV file to the output_path and returns the number of successfully processed rows.
    error_handling: Flags nulls, does not crash on malformed rows, logs errors for bad rows, and produces an output CSV for all successfully processed rows even if some fail.
