# Skills: Complaint Classification

- `classify_complaint(description)`: 
    - Analyzes the `description` string.
    - Matches against keyword list for `Urgent` priority.
    - Maps to the specific civic category taxonomy.
    - Returns: `{category, priority, reason, flag}`.

- `batch_classify(input_csv, output_csv)`:
    - Reads complaints from `input_csv`.
    - Iterates through each row, calling `classify_complaint`.
    - Appends results to a new CSV file `output_csv`.
