# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single complaint into a predefined category and priority level while providing a specific reason and setting a review flag if ambiguous.
    input: dictionary format containing complaint data string fields (e.g. description, date, location).
    output: dictionary format with exactly five keys: complaint_id, category, priority, reason, flag.
    error_handling: Return category 'Other', flag 'NEEDS_REVIEW', and note the ambiguity in the reason if the description is invalid or vague.

  - name: batch_classify
    description: Reads an input CSV of complaints, safely applies classify_complaint to each row, and writes the results to an output CSV.
    input: input_path (string to input CSV), output_path (string to output CSV).
    output: None (writes a CSV file to the file system).
    error_handling: If a row fails to process, catches the exception, logs the error in the reason, flags it as NEEDS_REVIEW, and continues to the next row without crashing the program.
