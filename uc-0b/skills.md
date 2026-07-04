# skills.md

skills:
  - name: retrieve_policy
    description: Loads a policy text file and returns the numbered clauses as a structured dictionary.
    input: A path to a .txt policy file.
    output: A dictionary keyed by clause number with the clause text as the value.
    error_handling: If a required clause is missing, raise an error so the summary generation stops rather than guessing.

  - name: summarize_policy
    description: Produces a compliant clause-by-clause summary for the required leave policy clauses.
    input: A dictionary of policy clauses.
    output: A plain-text summary containing each required clause in order.
    error_handling: If a clause cannot be summarised without loss, preserve the original wording verbatim.
