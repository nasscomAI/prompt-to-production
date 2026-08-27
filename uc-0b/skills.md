skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as a structured list of numbered sections with section headers and clause text preserved.
    input: file_path (str — absolute or relative path to .txt policy document)
    output: list of dicts, each with keys section_number (str), section_title (str), clauses (list of dicts with clause_number str and clause_text str)
    error_handling: If file not found, raise FileNotFoundError with message "Policy file not found: [path]"; if file is empty, raise ValueError with message "Policy file is empty: [path]"

  - name: summarize_policy
    description: Takes structured sections from retrieve_policy and produces a clause-by-clause compliant summary with section headers, clause references, and preserved binding language.
    input: structured_sections (list of dicts as returned by retrieve_policy), output_path (str — path to write the summary .txt file)
    output: .txt file written to output_path containing all numbered clauses summarised with clause reference, preserved binding verbs, and [VERBATIM] flag where needed; returns count of clauses processed
    error_handling: If a clause text is ambiguous or cannot be summarised without loss, output the verbatim clause text followed by [VERBATIM — summarisation would alter meaning]; never skip a clause silently
