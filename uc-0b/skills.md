skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections (e.g., dict of clause numbers to text).
    input: File path to a .txt policy document (e.g., "../data/policy-documents/policy_hr_leave.txt").
    output: Dict where keys are clause numbers (e.g., "2.3") and values are the full clause text.
    error_handling: If file not found or unreadable, raise FileNotFoundError or IOError with descriptive message.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary that includes all clauses with references, preserving conditions.
    input: Dict of clause numbers to clause texts (output from retrieve_policy).
    output: String summary text that covers all clauses, quotes verbatim if needed, and flags meaning loss.
    error_handling: If input dict is empty or malformed, return empty string and log warning; never invent clauses.
