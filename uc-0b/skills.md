# skills.md

skills:
  - name: retrieve_policy
    description: Loads a plain-text policy document and segments it into a structured dictionary of numbered clauses and their content.
    input: Path to a .txt file (e.g., policy_hr_leave.txt).
    output: A dictionary where keys are clause numbers and values are the text of the clause.
    error_handling: Raises an error if the file format is not .txt or if numbering is inconsistent.

  - name: summarize_policy
    description: Evaluates structured clauses against enforcement rules to produce a summary that preserves all binding conditions and approvers.
    input: A dictionary of numbered clauses.
    output: A plain-text summary file with clause-by-clause breakdowns.
    error_handling: Verbatim quotes any clause that cannot be safely summarized without dropping conditions.
