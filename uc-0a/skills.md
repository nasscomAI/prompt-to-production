# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: classify_complaint 
    description:Classifies a single citizen complaint by determining its exact category, severity priority, citing a one-sentence reason, and setting a review flag if needed.
    input: type: object format: A single text description or record representing one citizen complaint.
    output: type: object format: Exact category, priority (Urgent, Standard, Low), reason (one sentence citing description keywords), and flag (NEEDS_REVIEW or blank).
    error_handling: When the input is ambiguous, sets the flag to NEEDS_REVIEW to prevent false confidence; strictly enforces the allowed category list to prevent hallucinated sub-categories and taxonomy drift; sets priority to Urgent if severity keywords are detected to fix severity blindness; strictly requires the reason field to prevent missing justifications.

  - name: batch_classify 
    description: Reads a batch of citizen complaints from a CSV file, applies the classify_complaint skill iteratively per row, and writes the structured classification results to an output CSV
    input: type: file format: File path to the input CSV containing stripped city complaint rows.
    output: type: file format: File path to the output CSV containing classified rows with category, priority, reason, and flag
    error_handling: Validates the uniform application of the taxonomy schema across all rows to prevent taxonomy drift; aborts or logs an error if the input CSV cannot be read or lacks necessary description columns; verifies that every processed row includes a reason to prevent missing justifications in the final dataset.
