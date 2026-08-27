# skills.md

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections.
    input: >
      File path to a .txt policy document (e.g., ../data/policy-documents/policy_hr_leave.txt).
    output: >
      A structured list of sections, each containing:
        - section_number (e.g., "2.3")
        - section_title (e.g., "ANNUAL LEAVE") — the parent heading
        - clause_text — the full, unmodified text of the clause
        - binding_verb — the obligation verb used (must, will, requires, may, not permitted)
    error_handling: >
      If the file does not exist, return: "ERROR: File not found at [path]."
      If the file is empty or contains no recognizable numbered clauses, return:
      "ERROR: No structured policy clauses found in input."

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant clause-by-clause summary with clause references.
    input: >
      A structured list of policy sections as returned by retrieve_policy,
      containing section_number, section_title, clause_text, and binding_verb for each clause.
    output: >
      A plain-text summary where each entry follows this format:
        - [Clause X.X] — one-line summary preserving the binding verb and all conditions.
      Grouped under their parent section headings (e.g., "2. ANNUAL LEAVE").
      Multi-condition clauses must list ALL conditions explicitly.
      Binding verbs must match the source exactly (must, will, requires, not permitted).
    error_handling: >
      If the input is empty or malformed, return: "ERROR: Invalid input — expected structured policy sections."
      If a clause cannot be summarized without meaning loss, quote it verbatim and flag with
      "[VERBATIM — meaning loss risk]".
