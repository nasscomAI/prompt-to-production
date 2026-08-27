skills:
  - name: retrieve_policy
    description: Load the HR leave policy text and return structured numbered clauses.
    input: Path to the source policy text file.
    output: A mapping of clause numbers to clause text.
    error_handling: If a required clause cannot be found, stop and report which clause number is missing.

  - name: summarize_policy
    description: Produce a clause-complete summary from the structured policy clauses.
    input: Structured numbered clauses from the HR leave policy.
    output: A text summary with clause references and preserved conditions.
    error_handling: If a clause cannot be safely compressed, include its exact wording rather than paraphrasing away conditions.
