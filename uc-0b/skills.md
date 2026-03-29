skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content parsed into numbered sections.
    input: file_path (str) — path to .txt policy document
    output: dict mapping section_number (str e.g. "2.3") to section_text (str) — preserves original wording
    error_handling: if file not found, raise FileNotFoundError with clear message; if file is empty, raise ValueError

  - name: summarize_policy
    description: Takes structured sections and produces a compliant summary with every clause referenced and all conditions preserved.
    input: sections (dict from retrieve_policy), output_path (str)
    output: writes .txt summary file with one entry per numbered clause, each prefixed with its clause number
    error_handling: if a clause is ambiguous to summarise, include it verbatim and mark [VERBATIM]; never skip a clause silently