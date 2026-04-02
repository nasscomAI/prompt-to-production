# skills.md

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content segmented into structured numbered sections.
    input: File path string pointing to the policy document.
    output: A structured map or list of sections and their respective plain text.
    error_handling: Exits and reports if the document cannot be read or is missing section numbers.

  - name: summarize_policy
    description: Receives structured section data and synthesizes a compliant summary that strictly enforces multi-condition retention.
    input: Structured policy sections.
    output: A plain text summary referencing critical clauses.
    error_handling: Validates output against the inventory of mandatory clauses before returning; fails explicitly if conditions are dropped.
