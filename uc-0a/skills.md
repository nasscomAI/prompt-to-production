skills:
  - name: classify_complaint
    description: Classifies a single complaint record into standard categories, determines its priority based on severity keywords, generates a supporting reason citing the text, and flags ambiguity.
    input: A dictionary containing the keys `complaint_id`, `date_raised`, `city`, `ward`, `location`, `description`, `reported_by`, and `days_open`.
    output: A dictionary with the keys `complaint_id`, `category`, `priority`, `reason`, and `flag`.
    error_handling: If critical inputs are missing, or if the category cannot be resolved due to conflict/lack of keywords, returns category 'Other' and flags the record with 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads a CSV of complaints, applies `classify_complaint` to each row, and writes the structured classification results to a target CSV.
    input: Paths to the input CSV file (`input_path`) and the output CSV file (`output_path`).
    output: Writes a CSV file containing headers `complaint_id,category,priority,reason,flag`.
    error_handling: Handles missing files, logs row-level exceptions, and ensures the output is written even if specific rows fail.
