skills:
  - name: classify_complaint
    description: Classifies citizen complaints to assign a category, priority level, reason, and an optional review flag based on predefined schema rules.
    input: File path to a CSV file (e.g., test_[city].csv) containing unclassified complaint rows.
    output: File path to an output CSV file (e.g., results_[city].csv) containing the classified rows with new columns appended.
    error_handling: If an individual description is genuinely ambiguous or a category cannot be definitively determined, assign the `category` to "Other" and set the `flag` to "NEEDS_REVIEW".

  - name: batch_classify
    description: Reads an input CSV file of citizen complaints, processes each row individually applying the classify_complaint logic, and generates an output CSV enriched with the structured metadata.
    input: File path to the input CSV containing complaint rows.
    output: File path to the newly written output CSV file containing all original rows appended with `category`, `priority`, `reason`, and `flag` columns.
    error_handling: If an individual row cannot be processed due to a malformed description or parsing error, safely log the error, populate the row's output with fallback values (e.g. category "Other", flag "NEEDS_REVIEW"), and continue processing subsequent rows.
