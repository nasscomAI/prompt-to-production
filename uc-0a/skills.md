# Complaint Classifier Skills

- `classify_complaint`
  - Input: a single complaint text string.
  - Output: category, priority, reason, flag (as per enforcement rules).
- `batch_classify`
  - Input: path to input CSV file.
  - Output: reads input, applies `classify_complaint` to each row, writes to output CSV file with columns: `category`, `priority_flag`, `reason`, `flag`.
