# skills.md

skills:
  - name: retrieve_policy
    description: Load a policy text file and structure it as numbered sections for analysis.
    input: A file path to a `.txt` policy document.
    output: A list of numbered clauses, each with its section number and original text.
    error_handling: If the file cannot be read or is not in the expected format, return a clear error message and do not attempt summary generation.

  - name: summarize_policy
    description: Generate a faithful summary of mapped policy clauses while preserving every obligation and condition.
    input: Structured numbered clauses from `retrieve_policy`.
    output: A compliant summary that references each clause number and preserves meaning without adding new information.
    error_handling: If a clause cannot be paraphrased safely, quote it verbatim and mark it for review rather than changing its meaning.
