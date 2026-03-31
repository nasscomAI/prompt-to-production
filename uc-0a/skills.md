skills:
  - name: classify_complaint
    description: Analyzes a single citizen complaint description to classify it into a category, assign a priority, provide a reason, and flag if necessary.
    input: A single citizen complaint row/description (Text).
    output: A structured object or format containing Category (String), Priority (String), Reason (String), and Flag (String).
    error_handling: If the text is invalid or ambiguous, it classifies Category as 'Other' and sets Flag to 'NEEDS_REVIEW'.

  - name: batch_classify
    description: Reads a dataset of citizen complaints in CSV format, applies classify_complaint iteratively per row, and outputs the aggregated results into a new CSV.
    input: Path to the input CSV file containing raw complaints (String).
    output: Path to the generated output CSV file containing classified results (String).
    error_handling: Handles missing data gracefully by logging skipped rows, and delegates row-level ambiguity to the classify_complaint error handling.

    ## Your Input File
```
../data/city-test-files/test_[your-city].csv
```
15 rows per city. `category` and `priority_flag` columns are stripped — you must classify them.

## Your Output File
```
uc-0a/results_[your-city].csv
