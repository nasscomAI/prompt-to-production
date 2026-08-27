# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: summarize_document
    description: Summarizes a policy or procedural document, highlighting all changes that alter the original meaning.
    input: Document text as a string.
    output: Summary text as a string, with explicit notes on meaning-changing edits, omissions, or additions.
    error_handling: If the document is missing, unreadable, or ambiguous, returns an error message or flags the section for review.

  - name: compare_sections
    description: Compares sections or clauses between the original and summary to ensure all meaning changes are captured.
    input: Original section text and summary section text as strings.
    output: List of detected changes in meaning, omissions, or additions.
    error_handling: If sections cannot be matched or compared, flags for manual review.
