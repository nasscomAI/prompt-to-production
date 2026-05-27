# skills.md

skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as a dict
      of section_number -> section_text, keyed by top-level section number.
    input: filepath (str) — absolute or relative path to the policy .txt file.
    output: dict[str, str] — keys are section numbers ("1", "2" …) plus
      "header" for pre-section metadata; values are the raw section text.
    error_handling: Raises FileNotFoundError with a descriptive message if the
      file does not exist. Does not attempt to guess alternative paths.

  - name: summarize_policy
    description: Takes the structured sections dict and produces a compliant
      summary string with every clause referenced and all conditions preserved.
    input: sections (dict[str, str]) — output of retrieve_policy.
    output: str — formatted summary grouped by section, one bullet per clause,
      each prefixed with the clause number (e.g. "  • 2.4: …").
    error_handling: If OPENAI_API_KEY is not set, falls back to a verbatim
      clause extract and prints a warning to stderr. If the openai package is
      missing, exits with an install instruction. Never silently omits clauses.
