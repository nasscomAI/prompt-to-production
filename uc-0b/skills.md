skills:
  - name: retrieve_policy
    description: Reads the HR leave policy TXT file and returns it as structured numbered clauses.
    input: A text file path to the policy document.
    output: A dictionary keyed by numbered clause, where each value is the verbatim content of that clause and its continuations.
    error_handling: Refuses if the file cannot be read or if the required numbered clauses are missing.

  - name: summarize_policy
    description: Generates a clause-preserving, source-grounded summary with the required clause references.
    input: The structured numbered sections extracted from the policy.
    output: A text summary that includes every required clause and preserves its conditions exactly.
    error_handling: Refuses or quotes verbatim if paraphrasing would weaken the source meaning.
