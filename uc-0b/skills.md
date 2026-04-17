skills:
  - name: retrieve_policy
    description: Loads a .txt policy document and returns the content parsed into structured, numbered sections.
    input: File path (string) pointing to the policy document.
    output: A dictionary mapping clause numbers (e.g., "2.3") to their exact text.
    error_handling: Raise an error if the file is not found or cannot be read.

  - name: summarize_policy
    description: Takes structured clauses and produces a compliant summary preserving all required clauses and multi-part conditions.
    input: Structured sections (dictionary mapping clause numbers to text).
    output: A formatted text string containing the summary of the target clauses, flagged with [VERBATIM] if required.
    error_handling: Explicitly flag [VERBATIM] if meaning loss or ambiguity is detected during summarization.
