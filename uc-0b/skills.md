skills:
  - name: retrieve_policy
    description: Loads a policy text file and parses its contents into structured numbered sections for easier analysis.
    input: Path to the policy text file (string).
    output: A collection or list of structured sections, each with its section/clause number and raw text.
    error_handling: Raises an error if the file cannot be read or is empty.

  - name: summarize_policy
    description: Takes the structured sections and produces a compliant summary that references all specified clauses, preserves all conditions, and uses correct binding verbs.
    input: Structured sections from retrieve_policy.
    output: A summary text string referencing each mandatory clause.
    error_handling: Quotes the clause verbatim in the summary and flags it if the obligation/meaning cannot be safely simplified.
