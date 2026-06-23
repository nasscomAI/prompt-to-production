# Skills

skills:
  - name: retrieve_policy
    description: Load the HR leave policy text file and return numbered clauses as structured sections.
    input: Text contents of a HR policy document.
    output: Dictionary mapping clause numbers (e.g. "2.3") to full clause text.
    error_handling: Raise an error if required clause numbers are missing or the document cannot be parsed.

  - name: summarize_policy
    description: Produce a compliant summary from structured policy sections.
    input: Dictionary of policy clauses keyed by clause number.
    output: Text summary containing each clause number and its faithful summary.
    error_handling: Preserve exact language for any clause that cannot be safely restated.
