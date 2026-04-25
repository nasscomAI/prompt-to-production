# skills.md

skills:
  - name: classify_complaint
    description: Analyzes a single complaint row to assign category, priority, and justification based on the 'description' field.
    input: Dictionary containing 'complaint_id' and 'description'.
    output: Dictionary with 'complaint_id', 'category', 'priority', 'reason', and 'flag'.
    error_handling: Assigns 'Other' category and 'NEEDS_REVIEW' flag for ambiguous or empty inputs. Ensures exact category strings are used.

  - name: batch_classify
    description: Reads input CSV, applies 'classify_complaint' to each row, and writes the results to an output CSV.
    input: Path to input CSV (e.g., '../data/city-test-files/test_pune.csv').
    output: Path to output CSV (e.g., 'results_pune.csv').
    error_handling: Must flag null/missing descriptions, handle malformed rows without crashing, and ensure output is generated even if specific rows fail.
