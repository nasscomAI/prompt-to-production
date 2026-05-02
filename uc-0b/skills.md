skills:
  - name: retrieve_policy
    description: Loads the raw .txt policy file and converts it into structured, numbered sections.
    input: File path to the policy document (string).
    output: A list of objects containing clause numbers and their raw text.
    error_handling: Return an error message if the file is missing or not a .txt format.

  - name: summarize_policy
    description: Produces a summary that preserves every clause and all specific conditions from the original text.
    input: Structured list of numbered policy clauses.
    output: A summary text file where every clause is accounted for and multi-condition rules are preserved.
    error_handling: If a clause is too complex to summarize, quote it verbatim rather than guessing.
