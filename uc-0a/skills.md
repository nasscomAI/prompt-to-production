skills:
  - name: classify_complaint
    description: Maps a single citizen complaint to category, priority, reason, and flag based on the council taxonomy.
    input: Dictionary containing 'description' and 'complaint_id' from the city CSV.
    output: Dictionary { complaint_id: string, category: string, priority: string, reason: string, flag: string }.
    error_handling: 
      - Set category to 'Other' and flag to 'NEEDS_REVIEW' if the description is ambiguous or does not map to a taxonomy category.
      - Reason must cite specific keywords from the description.

  - name: batch_classify
    description: Orchestrates the classification process for an entire CSV file.
    input: Input file path (--input) and path for the resulting CSV (--output).
    output: A CSV file containing 'complaint_id', 'category', 'priority', 'reason', and 'flag' for all input rows.
    error_handling: Continues processing if individual rows fail; ensures all rows have a category and priority assigned.
