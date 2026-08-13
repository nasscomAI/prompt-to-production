# skills.md — UC-0B Skills

skills:
  - name: retrieve_policy
    description: Loads an unstructured policy text file and parses it line-by-line to isolate structured, numbered section identifiers and their respective texts.
    input: Path to policy text file.
    output: Dict mapping section numbers (e.g. "2.3") to their corresponding full-sentence text.
    error_handling: Raises standard FileNotFoundError if the path is invalid or cannot be read.

  - name: validate_clause_summary
    description: Performs deterministic checks on single clause summaries to ensure no softening of obligation verbs and complete condition preservation.
    input: clause_id (string) and candidate summary text (string).
    output: boolean value indicating whether the summary complies with all safety rules.
    error_handling: Returns False for unknown clause IDs or missing values.

  - name: generate_and_validate_summary
    description: Generates a full summary of all 10 clauses, checking each against the validation rules and falling back to verbatim quoting if any violation is detected.
    input: Dict of extracted policy sections.
    output: String of the compiled, validated summary.
    error_handling: Replaces missing sections with a standard flagged placeholder warning.
