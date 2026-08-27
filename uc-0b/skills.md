# skills.md

skills:
  - name: retrieve_policy
    description: Loads a policy .txt file and returns content structured by numbered sections with clause headers.
    input: File path (string) pointing to policy document (.txt).
    output: Dict with keys=clause_numbers, values=clause_text. Example: {"2.3": "14-day advance notice required...", "2.4": "Written approval required..."}
    error_handling: If file not found, raise FileNotFoundError with path. If file contains no numbered sections, raise ValueError with message "No numbered clauses detected".

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary that preserves all obligations, conditions, and binding verbs.
    input: Dict of {clause_number: clause_text} (output from retrieve_policy), plus clause_inventory (mapping of clause → core obligation → binding verb).
    output: Summary text with clause references (e.g., "[2.3]") and list of flagged clauses requiring manual review (if any).
    error_handling: If any clause from inventory is missing from input, raise ValueError with list of missing clauses. If summarization would lose a condition, flag clause instead of including lossy summary.
