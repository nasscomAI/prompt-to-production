# skills.md — UC-0A Complaint Classifier Skills

skills:
  - name: classify_complaint
    description: >
      **Role**: Core classification logic for a single row.
      **Intent**: Returns a dictionary (category, priority, reason, flag) for one complaint.
      **Context**: Receives a single complaint description or row data.
      **Enforcement**: Correctly identifies ambiguity and sets 'NEEDS_REVIEW' flag when appropriate.
    input: String (complaint description) or Dictionary (row data).
    output: Dictionary containing category, priority, reason, and flag.
    error_handling: Assigns 'Other' category and 'NEEDS_REVIEW' flag for ambiguous inputs.

  - name: batch_classify
    description: >
      **Role**: Orchestrator for processing multiple complaints.
      **Intent**: Reads an input CSV and produces a results CSV with all rows classified.
      **Context**: Takes input and output file paths.
      **Enforcement**: Ensures valid file reading and writing, maintaining consistent CSV schema across all 15 rows.
    input: CSV file path (string).
    output: Results CSV file path (string).
    error_handling: Handles file system errors and ensures output file integrity.
