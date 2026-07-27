# skills.md

skills:
  - name: retrieve_policy
    description: Load a policy document and structure it into numbered clauses with section headings for downstream clause preservation.
    input: File path (string) to a .txt policy document with numbered sections, subsections, and clauses.
    output: JSON object with keys "sections" (list of section headers), "clauses" (dict mapping clause ID e.g. "2.3" to full text), "raw" (original unmodified text).
    error_handling: If file not found, return error with file path and exit. If no numbered clauses detected (regex pattern \d+\.\d+), return error with line count and first 500 characters for debugging.

  - name: summarize_policy
    description: Condense structured policy sections into a compliant summary that preserves all clauses, conditions, and binding verbs without softening or omission.
    input: JSON from retrieve_policy (sections, clauses dict, raw text) plus required_clauses list ["2.3", "2.4", etc.] and optional target_word_count.
    output: Markdown summary with each required clause numbered and explicitly referenced (e.g., "**Clause 2.3:**"), condition tokens marked ("AND", "OR", "BOTH REQUIRED"), and flags for verbatim quotes ("[VERBATIM: reason]").
    error_handling: If any required clause is missing from input clauses dict, refuse summarization and return list of missing clause IDs. If clause text is too complex to summarise without meaning loss, flag with [VERBATIM: reason] and include full text instead of paraphrase.
