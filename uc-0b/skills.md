# skills.md

skills:
  - name: retrieve_policy
    description: Loads a structured .txt policy file and systematically parses it into an actionable dictionary of numbered sections.
    input: Filepath pointing to the raw text policy document.
    output: A structured dictionary mapping clause numbers (e.g. '2.3') to their raw string content.
    error_handling: Handles encoding differences softly and skips irrelevant or unnumbered header strings.

  - name: summarize_policy
    description: Sequentially translates the extracted structured clauses into a compliant, condition-safe summary.
    input: The parsed structured section dictionary from retrieve_policy.
    output: A consolidated formatted text summary matching all source clauses.
    error_handling: Reverts to quoting verbatim if multi-condition approval strings aren't easily summarizable.
