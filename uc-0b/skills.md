skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns its content as structured numbered sections.
    input: "File path to the .txt policy document (String)."
    output: "A structured representation of the policy content as numbered sections (List/JSON Array)."
    error_handling: "Raises a file missing error if the path is invalid, or returns an error structure if the content cannot be clearly parsed into numbered sections."

  - name: summarize_policy
    description: Takes structured numbered sections and produces a compliant summary with explicit clause references, maintaining all multi-condition obligations.
    input: "Structured numbered sections extracted from the policy document (List/JSON Array)."
    output: "A comprehensive, compliant summary text with clear references to original clause numbers ensuring no obligations are softened (String)."
    error_handling: "If a clause is ambiguous or cannot be summarized without meaning loss, quotes it verbatim and flags it in the output instead of attempting to summarize."
