# skills.md
# INSTRUCTIONS: Generate a draft by prompting AI, then manually refine this file.
# Delete these comments before committing.

skills:
  - name: retrieve_policy
    description: Parses a plain text policy document into a list of numbered clauses and their text.
    input: Absolute path to the .txt file.
    output: List of dictionaries: [{ "clause": "2.3", "content": "..." }, ...]
    error_handling: Return error if file is missing or contains no numbered clauses.

  - name: summarize_policy
    description: Generates a condensed summary of each clause while preserving all binding obligations and conditions.
    input: List of structured sections from retrieve_policy.
    output: Multi-line string with [Clause ID] followed by the summarized rule.
    error_handling: Refuse and quote verbatim if a clause is too complex to summarize without meaning loss.
