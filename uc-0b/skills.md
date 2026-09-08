# skills.md

skills:
  - name: retrieve_policy
    description: Load a plain-text HR leave policy file and return the numbered sections as structured clause content for downstream summarization.
    input: A file path string pointing to a .txt policy document containing numbered sections and clause text.
    output: A structured section or clause list, preserving clause numbers such as 2.3, 2.4, 2.5, 2.6, 2.7, 3.2, 3.4, 5.2, 5.3, and 7.2 as plain text sections keyed by clause number.
    error_handling: If the file is missing, unreadable, or has no numbered clauses, raise a clean input error or return an empty structured section and require the downstream summarizer to flag that section as unverifiable only from the source.

  - name: summarize_policy
    description: Convert the structured policy sections into a compliant plain-text summary that preserves all numbered clauses and all multi-condition obligations without adding outside knowledge.
    input: A structured list of numbered sections from retrieve_policy, each containing source text and clause numbers from the policy file.
    output: A plain-text summary containing every relevant numbered clause, preserving conditions and all approver requirements and marking any unverifiable or meaning-losing clause as a quoted verbatim preservation.
    error_handling: If a clause cannot be represented without meaning loss or if a condition is dropped in the draft, quote the source sentence verbatim and flag the clause as NEEDS_REVIEW or preserved quotation instead of paraphrasing it into a weaker statement.
