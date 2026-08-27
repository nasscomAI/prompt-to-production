skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns the content organized into structured numbered sections.
    input: File path to a .txt policy document.
    output: Structured text format containing the policy content mapped to clearly numbered sections.
    error_handling: Return an error if the file is not found, cannot be read, or if the text cannot be parsed into numbered sections.

  - name: summarize_policy
    description: Generates a compliant summary of the policy ensuring every numbered clause is referenced without softening obligations or dropping multi-condition requirements.
    input: Structured numbered sections of a policy document.
    output: A text summary containing explicit references to every clause, quoting verbatim if meaning loss is a risk.
    error_handling: Flag an error or refuse to summarize if a clause is missing or if any multi-condition obligation is dropped.
