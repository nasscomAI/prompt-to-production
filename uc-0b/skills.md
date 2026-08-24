skills:
  - name: retrieve_policy
    description: Ingests the policy text file, parses each major section and numbered clause, and validates complete structural capture.
    input: File path input_path (str) to policy text document.
    output: List of structured clause objects containing section_num, clause_num, title, and raw text.
    error_handling: Raises FileNotFoundError if missing; flags unparsed or unnumbered paragraphs.

  - name: summarize_policy
    description: Generates a rigorous, clause-mapped summary enforcing binding verbs, dual approvals, notice periods, and zero scope bleed.
    input: List of structured clause objects.
    output: String summary formatted by sections with exact clause cross-references and obligation indicators.
    error_handling: Automatically inserts verbatim quotes and warning flags for complex multi-condition clauses to prevent meaning loss.
