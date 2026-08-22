skills:
  - name: retrieve_policy
    description: Loads a policy text file and parses it into sections.
    input: Filepath of the policy document (str).
    output: A structured string or dictionary of policy sections.
    error_handling: Raise FileNotFoundError if the path does not exist.

  - name: summarize_policy
    description: Generates a high-fidelity summary of the leave policy covering all mandatory clauses.
    input: Structured policy sections (str).
    output: Compliant summary text (str).
    error_handling: Fall back to direct clause quotes if high-fidelity summary constraints cannot be satisfied.
