skills:
  - name: classify_complaint
    description: Classifies a single complaint row into category, priority, reason, and review flag.
    input: dict with at least a "description" key (string); other row fields are ignored.
    output: dict with keys complaint_id, category, priority, reason, flag.
    error_handling: Missing/blank description → category "Other", priority "Standard", flag "NEEDS_REVIEW", reason explains the row was unclassifiable.

  - name: batch_classify
    description: Reads an input CSV, classifies every row, and writes a results CSV — never crashes on a bad row.
    input: input_path (str, path to test_[city].csv), output_path (str, path to write results).
    output: Writes a CSV with one classified row per input row; returns nothing.
    error_handling: A row that raises during classification is still written to output with category "Other", priority "Standard", flag "NEEDS_REVIEW", and a reason describing the error — batch never aborts partway.
