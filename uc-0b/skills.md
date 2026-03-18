skills:
  - name: retrieve_policy
    description: Loads a policy text file and returns structured numbered sections for faithful summarization.
    input: "policy file path (.txt), expected to contain numbered clauses and section headings."
    output: "structured object/list of clauses with section number, clause text, and extracted binding verbs/conditions."
    error_handling: "If file is missing, unreadable, or not parseable into numbered sections, return an explicit error and stop downstream summarization instead of inferring structure."

  - name: summarize_policy
    description: Converts structured policy clauses into a concise summary while preserving all obligations and conditions.
    input: "structured clauses from retrieve_policy including section number and source text."
    output: "summary text with clause references that preserves all mandatory conditions and prohibitions from source."
    error_handling: "If a clause cannot be condensed without meaning loss, output that clause verbatim and mark NEEDS_REVIEW; never omit or weaken obligations."
