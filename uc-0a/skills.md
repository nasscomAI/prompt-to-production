skills:
  - name: classify_complaint
    description: Analyzes a single citizen complaint description and maps it to a category, priority level, and reason based on strict rules.
    input: A dictionary representing a single complaint row (contains description, etc).
    output: A dictionary object with `category` (string), `priority` (string), `reason` (string), and `flag` (string, either 'NEEDS_REVIEW' or empty).
    error_handling: Return category 'Other' and flag 'NEEDS_REVIEW' if the input description is unreadable, empty, or highly ambiguous.

  - name: batch_classify
    description: Processes an entire dataset of complaints by applying classify_complaint to each row individually and records the results.
    input: Path to an input CSV file containing complaint rows.
    output: A modified CSV file saved to an output path with classification fields populated.
    error_handling: If a row fails to process due to formatting issues or missing fields, log the error, leave classification blank or flagged, and proceed to the next row without crashing.
