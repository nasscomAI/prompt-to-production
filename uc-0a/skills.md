skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category, priority, reason, and flag.
    input: A single citizen complaint data row containing the complaint description.
    output: A dictionary containing `category` (string), `priority` (string), `reason` (string), and `flag` (string).
    error_handling: If input is null or unreadable, return category: Other, flag: NEEDS_REVIEW, and a generic error reason. Do not crash.

  - name: batch_classify
    description: Reads an input CSV of complaints, applies classify_complaint to each row, and writes the results to an output CSV.
    input: `input_path` (string) and `output_path` (string).
    output: A completed CSV file saved at `output_path`.
    error_handling: Must flag nulls, skip or handle bad rows gracefully without crashing, and produce an output file even if some rows fail.
