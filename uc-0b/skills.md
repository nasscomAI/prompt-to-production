skills:
  - name: retrieve_policy
    description: Reads a plain text policy file and structures its contents into numbered sections and individual clauses.
    input: String file path 'input_path' pointing to policy source text file.
    output: Dictionary mapping section titles to lists of numbered clause dictionaries containing section_num, clause_num, and raw_text.
    error_handling: Raises FileNotFoundError if path does not exist; returns empty structure if file is unparseable or empty.

  - name: summarize_policy
    description: Transforms structured policy section data into a complete, non-omissive summary adhering strictly to RICE enforcement rules.
    input: Dictionary of structured policy sections from retrieve_policy.
    output: Formatted plain text string containing the faithful section-by-section summary, preserving all 10 ground-truth binding clauses.
    rule_enforcement:
      completeness: Ensures every numbered clause from 1.1 to 8.2 is represented.
      verb_preservation: Keeps binding terms 'must', 'will', 'requires', and 'not permitted' intact.
      multi_condition: Retains dual approvers (Department Head + HR Director) for Clause 5.2 and Municipal Commissioner for Clause 5.3.
      scope_bleed_prevention: Filters out external boilerplate phrases.
    error_handling: If a clause cannot be concisely summarized without losing critical condition constraints, quotes the clause verbatim.
