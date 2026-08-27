skills:
  - name: retrieve_policy
    description: Loads the policy document and extracts all required numbered clauses while strictly preserving clause IDs, original text, and structural boundaries.
    input: file path to policy text document (.txt)
    output: structured dictionary mapping clause IDs (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) to their exact textual content
    error_handling: Raises explicit error if file is missing, unreadable, or if ANY required clause is missing or cannot be correctly extracted; does not allow partial extraction or silent skipping.

  - name: summarize_policy
    description: Generates a structured summary of policy clauses ensuring complete preservation of all conditions, obligations, and clause references without introducing or omitting information.
    input: structured dictionary of clause IDs and their corresponding text
    output: structured text summary where each clause is represented with its clause ID and meaning-preserving summary
    error_handling: Raises error if any clause is omitted, if obligation strength (must, requires, will, not permitted) is altered, or if multi-condition clauses lose any condition; falls back to verbatim clause text when summarization risks meaning loss.