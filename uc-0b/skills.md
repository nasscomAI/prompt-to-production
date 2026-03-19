# skills.md

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file from disk and returns its content as structured, numbered sections.
    input: >
      A file path string pointing to a plain-text policy document
      (e.g., "../data/policy-documents/policy_hr_leave.txt").
    output: >
      A list of section objects, each containing:
        - section_number (str): e.g., "2.3"
        - section_title (str): the heading of the parent section (e.g., "ANNUAL LEAVE")
        - text (str): the full verbatim text of that clause
      Preserves all whitespace-significant formatting. Returns sections
      in document order.
    error_handling: >
      If the file path does not exist, is not readable, or the file is
      empty, return a structured error with code FILE_NOT_FOUND,
      FILE_UNREADABLE, or FILE_EMPTY. Do not attempt to guess content
      or fall back to a default document.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary with clause references, preserving all obligations and conditions.
    input: >
      A list of section objects as returned by retrieve_policy
      (section_number, section_title, text).
    output: >
      A summary string where each clause is represented as a bullet
      with its clause reference (e.g., "§2.3 — …"). The summary must:
        - Include every numbered clause from the input
        - Preserve all binding verbs exactly (must, will, requires, may, not permitted)
        - Retain all conditions in multi-condition obligations
        - Add no information beyond what is in the source
        - Flag any verbatim-quoted clauses with [VERBATIM — meaning loss risk]
    error_handling: >
      If the input section list is empty or contains malformed entries,
      return a structured error with code NO_SECTIONS or MALFORMED_INPUT.
      Never produce a partial summary — either all clauses are covered
      or the skill returns an error.
