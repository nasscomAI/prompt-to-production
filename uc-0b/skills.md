# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: extract_policy_clauses
    description: Identify and separate individual rules or clauses from the HR policy document.
    input: Raw policy document text (string).
    output: A list of policy clauses or rule statements.
    error_handling: If the document structure is unclear, return the entire text as a single clause and flag it for review.

  - name: summarize_policy_clauses
    description: Generate a concise summary while preserving all rules, numbers, deadlines, and approval conditions.
    input: List of policy clauses extracted from the document.
    output: A structured summary text that retains the meaning of every clause.
    error_handling: If summarization removes important conditions or changes meaning, return FULL_TEXT_REQUIRED instead of producing an incomplete summary.