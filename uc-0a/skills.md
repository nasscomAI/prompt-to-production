skills:
  - name: classify_complaint
    description: Classifies a single civic complaint based on text description using explicit severity keywords and categories.
    input: dictionary representing variables in the CSV row, specifically the `description` text.
    output: dictionary containing `category` (str), `priority` (str), `reason` (str), and `flag` (blank or NEEDS_REVIEW).
    error_handling: Output category 'Other' and flag 'NEEDS_REVIEW' if classification rules fail, is indeterminate, or if input is invalid.

  - name: batch_classify
    description: Opens a CSV of complaints, applies classify_complaint logic sequentially to every row, and exports the results to a new target CSV.
    input: path to input CSV file, path to output CSV file
    output: generates standard output CSV file containing appended classification columns.
    error_handling: Yield an indeterminate classification with NEEDS_REVIEW flag for bad data rows and continue execution without crashing the entire batch.
