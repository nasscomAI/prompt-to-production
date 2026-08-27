skills:
  - name: classify_complaint
    description: Classifies a single complaint record's description into standard category and priority values, providing a one-sentence reason and flagging ambiguous entries.
    input: A dictionary representing a single complaint row (keys: complaint_id, description).
    output: A dictionary representing the classification results (keys: complaint_id, category, priority, reason, flag).
    error_handling: >
      If the description field is empty, null, or genuinely ambiguous, it sets category to 'Other', priority to 'Low' or 'Standard', flag to 'NEEDS_REVIEW', and provides a reason noting the input issue. It must not catch or suppress internal programming bugs or code exceptions (e.g., TypeError, AttributeError); these must propagate to the caller.

  - name: batch_classify
    description: Reads complaint records from an input CSV file, applies classify_complaint to each row, and writes the results to an output CSV file.
    input: A string input_path (path to the input CSV file) and a string output_path (path to the output CSV file).
    output: Writes a CSV file containing columns: complaint_id, category, priority, reason, flag.
    error_handling: >
      Handles invalid, malformed, or missing row data structure (e.g., missing 'description' or 'complaint_id' columns in the input CSV) by generating a default 'Other' category and 'NEEDS_REVIEW' flag for those rows. Does not catch or suppress system errors, writing permission issues, or python exceptions occurring within the classification logic; all such programming/system failures must raise exceptions and halt execution to prevent silent failures.
