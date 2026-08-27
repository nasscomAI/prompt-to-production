# skills.md

skills:
  - name: retrieve_policy
    description: Parse the input text strictly into a dictionary representing the 10 specific mandatory clauses for HR-POL-001. 
    input: File path to a policy .txt document.
    output: A dictionary mapping the 10 required mandatory clauses to their text statements.
    error_handling: Raise an exception if any of the 10 mandatory clauses are missing from the parsed document.

  - name: summarize_policy
    description: Apply compliance rules (binding verbs, multi-conditions, scope bleed prevention) and build a summary.
    input: Dictionary of mapped clauses from retrieve_policy.
    output: A compliant markdown summary of the required clauses.
    error_handling: If a clause fails the complexity check or meaning loss is feared (e.g., missing multi-conditions), generate a warning and quote the clause verbatim.
