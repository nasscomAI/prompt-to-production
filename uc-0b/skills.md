# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections with clause identifiers preserved.
    input: file_path (string — path to a policy .txt file).
    output: A list of section objects, each containing section_number (e.g., "2.3"), section_title (parent section heading), and text (the full clause text). Preserves all whitespace-significant formatting.
    error_handling: If file is not found or unreadable, exit with a clear error message. If file has no detectable clause structure, return the entire content as a single section with a warning.

  - name: summarize_policy
    description: Takes structured sections from retrieve_policy and produces a compliant summary preserving every clause, all conditions, and all binding language.
    input: A list of section objects (from retrieve_policy) containing section_number, section_title, and text.
    output: A structured text summary with one entry per clause, each prefixed with its clause reference [Clause X.Y], preserving all binding verbs, numeric values, multi-condition obligations, and deadlines. Flagged items marked with [VERBATIM] where summarization would lose meaning.
    error_handling: If a clause contains complex multi-condition language, flag it [VERBATIM] rather than risk meaning loss. Never silently drop conditions.
