skills:
  - name: retrieve_policy
    description: Loads a simple .txt policy file and returns the content grouped efficiently as structured numbered sections.
    input: The file path to the text document containing policy information.
    output: A sequence of text blocks categorized by their respective clause numbers.
    error_handling: Notifies the operator if a file is malformed or inaccessible without silent failures.

  - name: summarize_policy
    description: Takes structured sections from a policy document and produces a fully compliant summary with accurate clause references and zero condition omissions.
    input: Structured clause data mapping to specific rules or obligations.
    output: A clean text summary citing the clause numbers and their respective preserved rules.
    error_handling: Marks specific clauses as 'Flagged for meaning loss' and outputs them verbatim if they are too complex to summarize.
