skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as a structured list of numbered sections, each with a section number and full text.
    input: file_path (str, absolute or relative path to a .txt policy document)
    output: list of dicts, each with keys — section_number (str, e.g. "2.3"), section_text (str, full text of that clause); also returns document metadata (title, reference, version)
    error_handling: Raises FileNotFoundError with a clear message if the path does not exist; raises ValueError if the file cannot be parsed into numbered sections; never returns partial data silently

  - name: summarize_policy
    description: Takes the structured sections from retrieve_policy and produces a compliant summary where every numbered clause is present, all conditions are preserved, and no information is added beyond the source.
    input: list of section dicts as returned by retrieve_policy, plus document metadata
    output: str — a formatted summary with each clause on its own line, prefixed by its clause number, followed by the binding obligation; clauses at risk of meaning loss are quoted verbatim and flagged
    error_handling: If any numbered clause is missing from the input sections, raises ValueError listing the missing clause numbers; never produces a summary that omits a clause silently
