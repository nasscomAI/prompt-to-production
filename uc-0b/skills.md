# skills.md

skills:
  - name: retrieve_policy
    description: Read and parse policy text into numbered clauses mapping.
    input: Path to plain text policy file (policy_hr_leave.txt).
    output: A list of clause dicts with keys: section, clause_number, text.
    error_handling: Raises error if file missing or if required clause numbers are not found.

  - name: summarize_policy
    description: Generate a safe clause-accurate summary from clause inventory.
    input: List of clause dict objects from retrieve_policy.
    output: One-line summaries per clause, with explicit clause numbers and exact obligations.
    error_handling: If input lacks required clauses, include a warning summary line and set 'NEEDS_REVIEW'.

