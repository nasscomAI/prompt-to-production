skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections with clause references.
    input: Path to a .txt policy file (string).
    output: Dict with keys "sections" (list of {section_number, section_title, clauses}) and "raw_text" (full original content).
    error_handling: Returns an error dict if the file does not exist, is not a .txt file, or contains no numbered clauses. Does not fall back to any other file.

  - name: summarize_policy
    description: Takes structured policy sections and produces a compliant summary preserving every numbered clause with its exact conditions.
    input: Dict from retrieve_policy — sections with numbered clauses.
    output: String containing the summary with each clause referenced by number, multi-condition obligations preserved in full, no external information added, and [VERBATIM] flags where summarisation would risk meaning loss.
    error_handling: Returns an error if input contains no clauses. Never generates placeholder or default text. Never adds content not present in the input clauses.
