# skills.md

skills:
  - name: classify_complaint
    description: Parses and classifies a single citizen complaint row to produce a structured record with a valid category, priority, citing reason, and review flag.
    input: A dictionary representing a single CSV row, containing at least the `complaint_id` and the unstructured complaint description text.
    output: A dictionary containing `complaint_id` (any), `category` (exactly one of the 10 permitted values), `priority` (Urgent, Standard, or Low), `reason` (exactly one sentence citing specific words from the complaint), and `flag` (NEEDS_REVIEW or blank).
    error_handling: If the description is empty, null, or missing, set the category to Other, priority to Low, reason to an explanatory sentence indicating missing description, and set flag to NEEDS_REVIEW. If the complaint cannot be clearly categorized or is genuinely ambiguous, set category to Other and flag to NEEDS_REVIEW.

  - name: batch_classify
    description: Performs end-to-end processing of a CSV file by applying classify_complaint to each row and writing the verified results to a target output CSV.
    input: String path to the input CSV file containing raw complaint descriptions, and a string path where the output CSV file should be saved.
    output: Writes a CSV file containing columns `complaint_id`, `category`, `priority`, `reason`, and `flag` for every row from the input CSV.
    error_handling: Handles missing input files or read errors gracefully. Flags rows with null values, and ensures the process does not crash on bad rows; if a row fails to process, it writes a default record with category set to Other and flag set to NEEDS_REVIEW, and continues to process the rest of the file.
