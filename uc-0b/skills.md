# skills.md

skills:
  - name: retrieve_policy
    description: Loads a policy .txt file and extracts it into numbered sections for high-fidelity auditing.
    input: File path to a policy document.
    output: A collection of clauses where each maintains its original number and verbatim text for grounding.
    error_handling: Return early with an error if the file cannot be accessed.

  - name: summarize_policy
    description: Transforms policy clauses into a compliant summary that preserves all binding obligations and conditions.
    input: Structured policy sections with section numbers.
    output: A structured text summary, one line per clause, starting with the original clause number.
    error_handling: Flag clauses that cannot be safely summarized without data loss as [FLAG: Verbatim Quote] and include the full text.
