# skills.md — UC-0B Policy Summarizer

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections.
    input: file_path (str) — path to a .txt policy document.
    output: A list of sections, each containing a section heading (e.g., "2. ANNUAL LEAVE") and a list of clauses with their numbers and full text.
    error_handling: If file not found, prints error to stderr and exits with code 1. If file is empty or has no recognizable clause structure, returns empty list and logs a warning.

  - name: summarize_policy
    description: Takes structured sections and produces a compliant clause-by-clause summary preserving all conditions, binding verbs, and numerical values.
    input: A list of structured sections (as returned by retrieve_policy).
    output: A formatted text summary organized by section, with every clause represented. Each clause summary preserves binding verbs, all conditions, and exact numbers. Clauses that cannot be simplified are quoted verbatim with a flag.
    error_handling: If a clause is empty or malformed, includes it in output with note "[CLAUSE UNREADABLE — original text preserved]" and the raw text. Never silently drops a clause.
