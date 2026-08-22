skills:
  - name: policy_clause_parser
    description: Parses unstructured administrative policy documents into structured individual sections and numbered clauses.
    input: Raw text string containing policy document content.
    output: List of parsed clause objects containing clause titles, identifiers, and body text.
    error_handling: Groups unnumbered paragraphs under a default 'Preamble / General Scope' block if no formal clause heading is identified.

  - name: constraint_preservation_extractor
    description: Extracts critical sentences containing quantitative limits, deadlines, approval thresholds, and statutory penalties.
    input: String containing clause body text.
    output: List of bullet-point strings capturing key rules, days, percentages, caps, and mandatory qualifiers.
    error_handling: Retains full clause text verbatim if keyword filtering produces zero matches to avoid accidental data loss.

  - name: policy_summary_file_generator
    description: Coordinates end-to-end document parsing and writes the complete clause-level summary to disk.
    input: Input text file path and target output file path.
    output: Output summary text file (summary_hr_leave.txt).
    error_handling: Verifies source path existence, creates parent directories if missing, and logs descriptive error on missing file.