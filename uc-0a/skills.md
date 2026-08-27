# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single complaint into category, priority, reason, and flag.
    input: A single data row object (dictionary/JSON) representing the raw complaint description string, explicitly missing the stripped `category` and `priority_flag` columns.
    output: A structured classification object containing exactly four bounded fields - `category` (a string from the exact allowed taxonomy), `priority` (Urgent, Standard, Low), `reason` (a single sentence string citing the description), and `flag` ('NEEDS_REVIEW' or blank).
    error_handling: Addresses core UC failure modes by enforcing taxonomy limits to prevent "taxonomy drift" and "hallucinated sub-categories", overriding priority based on keywords to prevent "severity blindness", enforcing sentence structure to prevent "missing justification", and defaulting to 'Other'/'NEEDS_REVIEW' to prevent "false confidence on ambiguity".

  - name: batch_classify
    description: Reads an input CSV file, applies classify_complaint per row, and writes results to an output CSV file.
    input: A string specifying the input CSV file path (e.g., `../data/city-test-files/test_pune.csv`) and a string specifying the output CSV file path (`uc-0a/results_pune.csv`).
    output: A newly generated CSV file written to the output path, which preserves all 15 input rows and appends the 4 evaluated classification columns (`category`, `priority`, `reason`, `flag`) for each.
    error_handling: Handles malformed rows, null descriptions, or API hallucination errors by gracefully returning the fallback state (`Other`, `NEEDS_REVIEW`) to ensure the batch pipeline completes without crashing or data loss.
