# skills.md

skills:
  - name: retrieve_policy
    description: Opens and reads a raw .txt policy file and extracts its contents as structured, identifiable numbered sections.
    input: Filepath to the raw policy document (string).
    output: A structured object mapping clause numbers to their raw text content (dictionary/json).
    error_handling: Handles missing files or unparseable formats by returning an error message and halting execution.

  - name: summarize_policy
    description: Takes the structured sections from retrieve_policy and produces a compliant summary that strictly enforces all conditions and references the original clause numbers.
    input: The structured object of numbered clauses from retrieve_policy.
    output: A formatted, comprehensive summary document (string) where every clause is accounted for.
    error_handling: Refuses to output a summary if it detects it has dropped a multi-condition requirement, instead outputting the raw verse flagged as [VERBATIM].
