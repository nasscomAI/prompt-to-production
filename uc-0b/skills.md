# skills.md

skills:
  - name: retrieve_policy
    description: Loads the .txt policy file and returns content as structured numbered sections
    input: File path to the policy document (string)
    output: Structured representation of policy clauses (list of dicts or text blocks mapped by clause number)
    error_handling: Raise an error if the file cannot be found or read.

  - name: summarize_policy
    description: Takes structured sections and produces a compliant summary preserving all conditions and references
    input: Structured policy sections (from retrieve_policy)
    output: Formatted text file output string where every critical clause is summarized or quoted verbatim
    error_handling: Flag verbatim quotes if summarization risks losing conditions, or raise an error if a clause is unparseable without dropping context.
