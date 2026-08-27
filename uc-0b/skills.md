skills:
  - name: retrieve_policy
    description: Loads a .txt policy file from ../data/policy-documents/ and returns its content as structured numbered sections.
    input: A string path (relative to project root) to a .txt file.
    output: A list of numbered clause strings parsed from the file.
    error_handling: Refuses if the file path is missing, unreadable, or not a .txt file — never guesses or falls back to external knowledge.

  - name: summarize_policy
    description: Takes structured numbered sections and produces a compliant summary preserving all clauses with exact obligations.
    input: A list of numbered clause strings (output of retrieve_policy).
    output: A text summary covering every clause per AGENTS.md enforcement — never adds external information, never drops multi-condition requirements, and flags any clause quoted verbatim.
    error_handling: Refuses to generate if input sections list is empty or malformed. Never hallucinates clause content.
