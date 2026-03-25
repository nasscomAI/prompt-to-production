# skills.md

skills:
  - name: classify_complaint
    description: Processes a single citizen complaint description to determine its category, priority, reason, and flag based on strict rules.
    input: A string containing the text of a single citizen complaint description.
    output: A JSON object with fields `category` (string, from allowed list), `priority` (string: Urgent, Standard, or Low), `reason` (string, one sentence citing specific words), and `flag` (string: NEEDS_REVIEW or empty).
    error_handling: If the complaint description is completely unreadable or missing, set category to "Other", priority to "Low", and flag to "NEEDS_REVIEW". If ambiguous between two allowed categories, set flag to "NEEDS_REVIEW".

  - name: batch_classify
    description: Reads an input CSV file containing multiple citizen complaints, applies the classify_complaint skill to each row, and writes the results to an output CSV file.
    input: A string representing the file path to an input CSV with citizen complaints.
    output: A string representing the file path to the generated output CSV containing the classification results.
    error_handling: If the input file is not found, raise a FileNotFoundError. For any row that fails classification completely, skip it or record a fallback row with flag set to "NEEDS_REVIEW".
