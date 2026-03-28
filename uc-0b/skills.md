# skills.md
# UC-0B — Summary That Changes Meaning

skills:
  - name: retrieve_policy
    description: Loads the raw .txt policy file and parses it, returning the content as structured numbered sections.
    input: File path to the raw .txt policy document.
    output: A structured dictionary/JSON mapping section headers to their constituent numbered clauses.
    error_handling: If the file is missing or unreadable, logs an error and halts execution.

  - name: summarize_policy
    description: Takes structured sections and produces a compliant summary with clause references.
    input: Structured dictionary/JSON of policy sections and clauses.
    output: A formatted string representing the compliant summary, ensuring all numbered clauses and multi-conditions are preserved.
    error_handling: Quotes clauses verbatim and flags them if they cannot be safely condensed without meaning loss.
