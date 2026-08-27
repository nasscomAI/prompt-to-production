skills:
  - name: retrieve_policy
    description: Loads a text policy document and parses it into structured numbered sections and individual clauses.
    input: File path to policy document (string).
    output: List of section objects containing section titles and dictionaries of numbered clauses.
    error_handling: Raises FileNotFoundError if file does not exist, or ValueError if document has no valid numbered clauses.

  - name: summarize_policy
    description: Processes structured policy sections to generate a zero-information-loss summary with explicit clause citations, binding verbs, and condition lists.
    input: Structured section/clause data from retrieve_policy.
    output: Complete plain text summary formatted by section and numbered clauses.
    error_handling: If a clause contains complex multi-condition rules or potential ambiguity, it is quoted verbatim and flagged to prevent meaning loss.
