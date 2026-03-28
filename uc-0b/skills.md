skills:
  - name: retrieve_policy
    description: Loads the .txt policy file and returns the content as structured numbered sections.
    input: string (file path)
    output: structured text (numbered sections extracted from the policy)
    error_handling: Return an error message if the file cannot be read or parsed.

  - name: summarize_policy
    description: Takes structured numbered sections of a policy and produces a compliant summary that strictly preserves all conditions and clause references.
    input: structured text (numbered sections)
    output: string (compliant summary of the policy)
    error_handling: If a clause cannot be summarized without altering its meaning or dropping conditions, output the strict verbatim text and flag it.
