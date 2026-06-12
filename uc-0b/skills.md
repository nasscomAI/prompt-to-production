skills:
  - name: retrieve_policy
    description: Loads a .txt policy file and returns the content as structured numbered sections.
    input: A string representing the file path to the policy document.
    output: A dictionary or text blob containing the structured sections of the policy.
    error_handling: Raises an exception if the file cannot be found or read.

  - name: summarize_policy
    description: Takes the structured sections from the policy and produces a compliant summary with explicit clause references.
    input: Structured sections text or dictionary.
    output: A formatted string representing the compliant summary.
    error_handling: If a clause's meaning is ambiguous or at risk of being lost, it quotes the clause verbatim and flags it.
