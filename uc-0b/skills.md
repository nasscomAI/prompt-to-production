# skills.md — UC-0B Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: Loads a .txt policy document and returns its content parsed into structured numbered sections with clause text preserved verbatim.
    input: File path to a .txt policy document.
    output: A list of dictionaries, each with keys: section_number (e.g. "2.3"), section_title (if present), clause_text (verbatim text from the document).
    error_handling: If the file is missing or unreadable, raise a clear error with the file path. If a section cannot be parsed into numbered format, include it as a raw text block with section_number set to "unnumbered" and log a warning.

  - name: summarize_policy
    description: Takes the structured sections from retrieve_policy and produces a compliant summary that preserves all binding obligations, cites clause numbers, and never adds external information.
    input: A list of section dictionaries from retrieve_policy plus the list of 10 critical clause numbers that must be preserved.
    output: A text string containing the structured summary with clause references, where each critical clause is either accurately summarised or quoted verbatim with a flag.
    error_handling: If a critical clause is missing from the input sections, raise an explicit error naming the missing clause number. If summarisation would lose binding meaning, quote verbatim and append a flag note.
