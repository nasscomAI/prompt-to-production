skills:
  - name: retrieve_policy
    description: Opens and reads a raw `.txt` policy file and parses its contents into isolated, structured numbered sections.
    input: Filepath string to the target plain `.txt` policy document (e.g., `../data/policy-documents/policy_hr_leave.txt`).
    output: A structured List, Dictionary, or mapped Markdown payload separating the text into numbered clause blocks.
    error_handling: If the file is missing or unreadable, halt extraction and return an explicit file access error. If numbering is malformed, ingest as a single unnumbered block and flag for structural review.

  - name: summarize_policy
    description: Receives the structured policy sections and generates a strict, compliant Markdown table mapping that preserves all conditions, verbs, and clause references.
    input: Structured payload of grouped numbered clauses produced by the 'retrieve_policy' skill.
    output: A rigid Markdown table block containing exact columns for `Clause`, `Core obligation`, and `Binding verb`.
    error_handling: If a specific incoming clause's meaning is highly complex or layered, bypass summarization, explicitly quote the string verbatim linked to its original clause number, and append a warning flag to the output.
