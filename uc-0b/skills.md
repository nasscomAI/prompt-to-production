# skills.md

skills:
  - name: retrieve_policy
    description: Loads a policy .txt file and splits it into structured numbered sections for easier analysis.
    input: File path to the policy .txt file.
    output: A dictionary mapping section numbers (e.g., '2.3') to their full text content.
    error_handling: Reports an error if the file is missing or lacks clear numbering.

  - name: summarize_policy
    description: Generates a summary that preserves all 10 key clauses and their exact binding requirements.
    input: Dictionary of numbered policy sections.
    output: A formatted string summary listing all 10 clauses with their binding verbs and terms.
    error_handling: Quotes the clause verbatim if it detects multiple approvers or complex negative conditions.
