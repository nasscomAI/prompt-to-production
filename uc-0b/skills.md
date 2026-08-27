# skills.md

skills:
  - name: retrieve_policy
    description: Loads a policy text file and parses it into a structured dictionary of numbered sections and clauses.
    input: Path to the .txt policy document (e.g., ../data/policy-documents/policy_hr_leave.txt).
    output: A dictionary where keys are clause numbers and values are the corresponding text content.
    error_handling: Return an error if the file is missing or if numbering cannot be parsed.

  - name: summarize_policy
    description: Generates a point-by-point summary of policy clauses while strictly preserving all obligations and conditions as defined in agents.md.
    input: A structured dictionary of policy clauses.
    output: A markdown-formatted summary including every clause number, its core obligation, and any specific conditions (e.g., summary_hr_leave.txt).
    error_handling: Flag the output if a clause's conditions are too complex to summarize without meaning loss.
