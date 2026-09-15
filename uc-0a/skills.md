# skills.md

skills:
  - name: classify_complaint
    description: Takes one complaint record and outputs schema-compliant category, priority, reason citation, and ambiguity flag.
    input: Dictionary containing complaint_id, description, location, and metadata.
    output: Dictionary with keys complaint_id, category, priority, reason, flag.
    error_handling: Handles null/missing fields gracefully; assigns category 'Other' and sets flag to 'NEEDS_REVIEW' without throwing exceptions.

  - name: batch_classify
    description: Reads input CSV file, maps classify_complaint across all rows, and exports results CSV.
    input: File path to input CSV (e.g. test_pune.csv) and output destination path.
    output: CSV file containing all classified records with standardized columns.
    error_handling: Catches row-level parsing errors, writes failed records with flag 'NEEDS_REVIEW', and guarantees complete CSV generation.
