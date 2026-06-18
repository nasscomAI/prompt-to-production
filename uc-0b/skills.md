# skills.md

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file from disk and returns its content as structured numbered sections.
    input: >
      File path (string) — absolute or relative path to a .txt policy document.
    output: >
      A list of sections, each containing:
        - section_number (string): the clause number as it appears in the document (e.g., "2.3", "5.2").
        - section_title (string): the heading or label of the section, if present.
        - section_body (string): the full verbatim text of the clause, preserving original wording and formatting.
    error_handling: >
      - If the file path does not exist or is unreadable, return an error: "ERROR: File not found or unreadable at <path>."
      - If the file is empty (zero bytes), return an error: "ERROR: File is empty — nothing to process."
      - If the file does not contain recognisable numbered clauses, return an error: "ERROR: No numbered clauses detected — input may not be a policy document."

  - name: summarize_policy
    description: Takes structured policy sections and produces a clause-by-clause compliant summary with clause references preserved.
    input: >
      A list of structured sections as returned by retrieve_policy (section_number, section_title, section_body).
    output: >
      A summary document where:
        - Every clause from the input appears, prefixed by its original clause number.
        - Binding verbs (must, requires, will, not permitted) match the source exactly.
        - Multi-condition obligations list ALL conditions explicitly (e.g., "requires approval from BOTH Department Head AND HR Director").
        - No phrases are added that do not appear in the source (no scope bleed).
        - Clauses that cannot be shortened without meaning loss are quoted verbatim and flagged with [VERBATIM — meaning loss risk].
    error_handling: >
      - If the input section list is empty, return an error: "ERROR: No sections provided — cannot produce summary."
      - If any section_body is blank or null, flag it in the output: "[MISSING CONTENT] Clause <section_number> has no body text in the source."
      - If the agent detects ambiguity in a clause's binding force, preserve the original wording verbatim rather than paraphrasing.
