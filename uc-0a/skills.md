skills:
  - name: classify_complaint
    description: Classify a single complaint record into category, priority, reason, and flag fields according to schema constraints.
    input: string (complaint description text)
    output: object with fields {category: string, priority: string, reason: string, flag: string}
    error_handling: If category is ambiguous, set flag to NEEDS_REVIEW instead of hallucinating confidence. If severity keywords (injury, child, school, hospital, ambulance, fire, hazard, fell, collapse) are present, force priority to Urgent. If description contains no clear fit to allowed categories, use Other and flag NEEDS_REVIEW. Reject any category not in allowed list. Reject reason field that does not cite specific words from description.

  - name: batch_classify
    description: Read a CSV file of citizen complaints, apply classify_complaint to each row, and write results to output CSV with all four classification fields.
    input: file path (string) pointing to CSV with complaint descriptions
    output: file path (string) pointing to output CSV with columns {id, description, category, priority, reason, flag}
    error_handling: If input file is not valid CSV or missing description column, raise error. If any row fails classify_complaint validation (taxonomy drift, severity blindness, missing reason, hallucinated category, false confidence), flag that row with NEEDS_REVIEW and include diagnostic reason. Enforce that all output rows contain all four fields with no missing or null values in category or priority. Write output file with complete records or fail the entire batch rather than partial write.
