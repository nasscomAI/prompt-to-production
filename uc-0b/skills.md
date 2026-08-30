skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as a list of structured numbered sections, preserving clause numbers and verbatim text.
    input: file_path (str, path to .txt policy document). The file must be UTF-8 encoded.
    output: A list of dicts, each with keys — section_number (str, e.g. "2.3"), section_title (str), clause_text (str, verbatim text of the clause). Returns the full content as a single entry if the document is not structured with numbered sections.
    error_handling: If file is not found, raise FileNotFoundError with the path. If file is empty, return empty list and print a warning to stderr. If a section cannot be parsed, include it as-is under section_number="UNPARSED".

  - name: summarize_policy
    description: Takes the structured sections from retrieve_policy and produces a compliant summary that preserves every clause, all binding verbs, and all multi-condition obligations — with clause number citations.
    input: sections (list of dicts from retrieve_policy), output_path (str, path to write the summary .txt file).
    output: A .txt file at output_path containing the summary. Each section has a heading citing the clause number. Clauses that cannot be summarised without meaning loss are quoted verbatim and flagged with [VERBATIM — meaning-critical clause].
    error_handling: If sections list is empty, write a file with content "ERROR: No policy sections found — cannot produce summary." and raise ValueError. If output_path cannot be written, raise IOError with the path.
