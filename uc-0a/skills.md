# skills.md

skills:
  - name: classify_complaint
    description: Transforms a single citizen complaint description into a structured classification consisting of a category, priority, justification, and review flag.
    input:
      type: string
      format: Raw text description from a single CSV row.
    output:
      type: object
      format: "{ category: string, priority: string, reason: string, flag: string }"
    error_handling: Returns NEEDS_REVIEW in the flag field if the category is ambiguous; defaults to Standard priority unless specific severity keywords are detected; enforces exact taxonomy strings to prevent drift or hallucinated sub-categories.

  - name: batch_classify
    description: Orchestrates the end-to-end processing of a city-specific test file by reading input data and writing the final classified results to a CSV.
    input:
      type: file
      format: CSV file located at ../data/city-test-files/test_[city].csv with stripped columns.
    output:
      type: file
      format: CSV file saved at uc-0a/results_[city].csv containing the original data plus category, priority, reason, and flag columns.
    error_handling: Validates input CSV structure before processing; logs instances of missing justifications or taxonomy violations; ensures consistent category naming across all processed rows to prevent taxonomy drift.
