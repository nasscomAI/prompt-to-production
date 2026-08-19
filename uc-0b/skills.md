skills:
  - name: retrieve_policy
    description: Reads the raw policy text file and parses all numbered sections into a structured policy document.
    input: File path to policy text file (e.g. policy_hr_leave.txt).
    output: Structured representation of policy sections, sub-clauses, and binding conditions.
    error_handling: Raises FileNotFoundError if file is missing, or reports unparsed lines.

  - name: summarize_policy
    description: Processes structured policy sections into a complete, non-lossy summary adhering to RICE enforcement rules.
    input: Structured policy sections.
    output: Text summary guaranteeing coverage of all numbered clauses and multi-condition obligations.
    error_handling: Flags ambiguous clauses and preserves verbatim quotes when reduction risks meaning loss.
