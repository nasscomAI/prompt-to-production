# skills.md

skills:
  - name: retrieve_policy
    description: Reads the raw HR leave policy document and returns its contents structured into readable numbered sections.
    input: String file path pointing to the `.txt` policy document.
    output: A dictionary or contiguous text block mapping each numbered clause accurately.
    error_handling: Halt execution if the file is missing or contains no text.

  - name: summarize_policy
    description: Analyzes structured policy sections and produces a compliant summary containing all mandatory clauses, ensuring no conditions are lost or external scope is injected.
    input: Structured policy text from retrieve_policy.
    output: A finalized summary string preserving clauses and obligations cleanly.
    error_handling: Validate internally that no mandatory clause was dropped; if missing, fail gracefully or insert the verbatim rule.
