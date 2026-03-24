skills:
  - name: retrieve_policy
    description: Extracts raw text from the policy document and parses it into a structured dictionary keyed by clause numbers.
    input: File path to a .txt policy file.
    output: A dictionary where keys are clause numbers (e.g., "2.3") and values are the raw text strings.
    error_handling: If a clause number is missing or the file is unreadable, raise a FileNotFoundError and halt execution.

  - name: summarize_policy
    description: Transforms structured clause data into a condensed summary while maintaining 100% of the binding obligations and verbs.
    input: Structured dictionary of clauses and their text.
    output: A summary document where each entry maps back to a specific clause ID (e.g., "[2.3] 14-day notice required").
    error_handling: If a multi-condition clause (detected by keywords 'and', 'both', 'plus') is reduced to a single condition, the skill must re-process the string to include the missing actor/condition.