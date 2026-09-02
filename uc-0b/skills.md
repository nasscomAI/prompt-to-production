skills:
  - name: retrieve_policy
    description: Reads a policy document and extracts numbered clauses into a structured map keyed by clause number.
    input: A UTF-8 text file path to the policy document.
    output: A dictionary-like structure of clause IDs and their associated text, preserving clause numbering and original wording in context.
    error_handling: If the file is missing, empty, or unreadable, raise a clear validation error and stop instead of guessing.

  - name: summarize_policy
    description: Converts structured policy clauses into a faithful summary that includes all required numbered clauses and preserves crucial conditions without adding unsupported statements.
    input: A mapping of clause IDs to clause text extracted from the source document.
    output: A numbered summary list, with exact quotations used when a clause cannot be safely paraphrased without losing meaning.
    error_handling: If any required clause is missing or conditions are dropped, fail the summary and request a correction rather than returning a softened interpretation.
