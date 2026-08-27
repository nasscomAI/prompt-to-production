skills:
  - name: retrieve_policy
    description: Parses and loads the plain .txt policy document into structured and sequenced sections.
    input: File path of the .txt policy document (e.g., `../data/policy-documents/policy_hr_leave.txt`).
    output: A structured array/object containing the text divided into identified, numbered sections for precise step-by-step reading.
    error_handling: Return a missing-file error if not found, or a parser error if the file is empty or lacks discernable numbered clauses.

  - name: summarize_policy
    description: Generates a dense, meaning-preserving, and compliant summary while maintaining direct references to the original clause numbers.
    input: The structured numbered sections produced by the retrieve_policy skill.
    output: A correctly formatted summary list, retaining strict multi-condition clauses, proper bindings, and no external scope additions.
    error_handling: Return a failure flag if the output lacks mapping to all input clauses, or drop the run if a clause cannot be accurately summarized, reverting to verbatim text instead.
