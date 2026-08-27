skills:
  - name: classify_complaint
    description: Classify a single civic complaint into a predefined category and priority based on public safety keywords, providing a one-sentence reason and flagging ambiguous cases.
    input: A single dictionary representing a CSV row with a `description` field containing the complaint text.
    output: A dictionary with keys `complaint_id`, `category`, `priority`, `reason`, and `flag` containing the exact classification strings.
    error_handling: If the description is empty or missing, return the `complaint_id` with category 'Other' and flag 'NEEDS_REVIEW'. If classification confidence is low, set the flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Opens a CSV file of complaints, iterates through each row, applies the `classify_complaint` skill, and writes the results to a new CSV file.
    input: `input_path` (string path to the source CSV file) and `output_path` (string path for the destination CSV file).
    output: A new CSV file saved at `output_path` containing the processed results for all rows. Does not return a programmatic value.
    error_handling: Handles missing files with an error message. Specifically designed not to crash on corrupted or malformed rows; it will flag those rows as null or empty and continue processing the remaining valid rows.
