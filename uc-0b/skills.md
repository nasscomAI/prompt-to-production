# skills.md

skills:
  - name: retrieve_policy
    description: Loads the .txt policy file and returns the content parsed as structured, numbered sections.
    input: File path to the policy document (.txt format).
    output: A structured listing of numbered clauses and their text.
    error_handling: Return an explicit error if the file cannot be found, read, or if no clauses can be extracted.

  - name: summarize_policy
    description: Takes structured sections and produces a compliant summary that explicitly references each numbered clause and preserves all multi-condition obligations.
    input: Structured, numbered sections.
    output: A text summary containing all required clauses with exact clause references, with no external information added.
    error_handling: If a clause cannot be confidently summarized without losing precise meaning, conditions, or obligations, quote it verbatim and flag it instead of attempting to summarize.
