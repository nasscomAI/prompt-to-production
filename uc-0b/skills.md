skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as a list of numbered sections with their clause text.
    input: file_path (str) — absolute or relative path to the policy .txt file.
    output: A list of dicts, each with keys section_id (str, e.g. "2.3") and text (str, the clause content).
    error_handling: Raises FileNotFoundError if path does not exist; returns empty list with a warning if file has no recognisable numbered clauses.

  - name: summarize_policy
    description: Takes structured policy sections and produces a clause-complete summary preserving all obligations, conditions, and binding language.
    input: A list of section dicts (from retrieve_policy) with keys section_id and text.
    output: A formatted string summary with one entry per clause, preserving binding verbs and all conditions; verbatim quotes used where meaning-loss risk is detected.
    error_handling: If a clause text is empty or malformed, includes the clause ID in the output with flag [CLAUSE UNREADABLE — manual review required].
