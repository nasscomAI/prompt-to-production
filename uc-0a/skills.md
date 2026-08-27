# skills.md

skills:
  - name: classify_complaint
    description: Classify a single complaint row using the description to assign category, priority, reason, and review flag according to strict guidelines.
    input: A dictionary representing a single complaint row containing at least `complaint_id` and `description`.
    output: A dictionary containing keys `complaint_id`, `category`, `priority`, `reason`, and `flag`.
    error_handling: If the description is empty/null, or if the category is genuinely ambiguous, classify `category` as "Other" and set `flag` to "NEEDS_REVIEW".

  - name: batch_classify
    description: Read an input CSV file of citizen complaints, classify each row using the classify_complaint skill, and write the output to a results CSV file.
    input: The file path to the input CSV file (`input_path`) and the file path to write the output CSV file (`output_path`).
    output: Writes a CSV file containing columns `complaint_id`, `category`, `priority`, `reason`, and `flag`.
    error_handling: Skip malformed rows, handle missing or null fields gracefully without crashing, and ensure results are written even if individual rows fail to classify.
