# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and parses it into structured numbered sections and clauses.
    input: >
      file_path (str) — absolute or relative path to the policy .txt file.
    output: >
      A list of sections, each containing: section_number (str), section_title (str),
      and a list of clauses. Each clause has: clause_number (str), clause_text (str),
      binding_verb (str — the obligation verb used: must, will, requires, may, not permitted, etc.).
    error_handling: >
      If the file does not exist or cannot be read, raises FileNotFoundError with a clear message.
      If no numbered clauses are found, prints a warning and returns the raw text as a single section.

  - name: summarize_policy
    description: Takes structured sections from retrieve_policy and produces a compliant clause-by-clause summary with all obligations and conditions preserved.
    input: >
      sections (list) — structured sections as returned by retrieve_policy.
    output: >
      A formatted text string containing one summary line per clause, preserving:
      clause number, binding verb, all conditions, and key quantities/dates.
      Clauses that cannot be shortened without meaning loss are quoted verbatim
      and flagged with [VERBATIM].
    error_handling: >
      If a clause contains multiple conditions (detected by AND, BOTH, or enumerated requirements),
      all conditions are preserved explicitly. Never silently drops a condition.
