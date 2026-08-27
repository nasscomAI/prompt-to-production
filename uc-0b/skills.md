skills:
  - name: retrieve_policy
    description: Loads a raw .txt policy file and extracts its content as explicitly structured and numbered clauses.
    input: File path to the raw .txt HR policy document.
    output: A structured text or JSON object containing the verbatim, numbered policy clauses.
    error_handling: Refuses to proceed and alerts the user if the file cannot be found, is unreadable, or contains no numbered clauses.

  - name: summarize_policy
    description: Generates a compliant summary from structured sections while perfectly preserving meaning, multi-condition obligations, and binding verbs without using any external knowledge.
    input: Structured and numbered policy clauses returned by retrieve_policy.
    output: A compliant summary file (.txt) where every original numbered clause is present and verifiable against the source.
    error_handling: Flags and quotes verbatim any clause that cannot be summarized without meaning loss. Refuses to output if instructed to soften obligations, drop conditions, or inject scope bleed/external knowledge.
