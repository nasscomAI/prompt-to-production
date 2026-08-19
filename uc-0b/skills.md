skills:
  - name: retrieve_policy
    description: Loads a policy text file and parses it into structured numbered clauses and sections.
    input: Path to a policy .txt document.
    output: Structured collection of sections and numbered clauses with binding verbs intact.
    error_handling: Raise error if file cannot be read or contains missing mandatory sections.

  - name: summarize_policy
    description: Generates a complete, non-softened policy summary covering all 10 mandatory clauses with exact references and preserved multi-condition approvals.
    input: Parsed policy text structure.
    output: Summary text containing every target clause (2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, 7.2) with preserved conditions and binding verbs.
    error_handling: Refuse to output if any required clause or multi-condition approver is dropped.
