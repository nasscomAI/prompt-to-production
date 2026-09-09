# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: classify_complaint
    description: Analyzes a single civic complaint row to determine category, priority, justification reason, and review flag.
    input:
      type: record
      format: Dictionary or row object containing complaint text and metadata
    output:
      type: classification_result
      format: Dictionary containing category, priority, reason, and flag
    error_handling: Falls back to category 'Other' and sets flag to 'NEEDS_REVIEW' if complaint text is empty, unparseable, or completely ambiguous.

  - name: batch_classify
    description: Iterates through the entire input CSV, applies classify_complaint to each row, and writes the enriched dataset to the output CSV.
    input:
      type: file_paths
      format: Input CSV file path and target Output CSV file path
    output:
      type: file
      format: CSV file containing all original columns along with category, priority, reason, and flag
    error_handling: Validates input file existence and header presence; gracefully handles missing columns and logs skipped rows.